"""
Automated Insights Pipeline for PM RAG Agent

This module provides automated processing of new documents uploaded to the RAG system,
with special handling for multi-project meetings like executive and operations meetings.

Key features:
- Automatic processing when new documents are uploaded
- Multi-project insight assignment for executive meetings
- Retroactive processing of existing meetings
- Project name inference and assignment
- Duplicate detection and prevention
"""

import os
import re
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from openai import AsyncOpenAI
from supabase import Client
from dotenv import load_dotenv
from pathlib import Path

from insights_service import MeetingInsightsGenerator, ProjectInsight
from clients import get_agent_clients

# Check if we're in production
is_production = os.getenv("ENVIRONMENT") == "production"

if not is_production:
    # Development: prioritize .env file
    project_root = Path(__file__).resolve().parent
    dotenv_path = project_root / '.env'
    load_dotenv(dotenv_path, override=True)
else:
    # Production: use cloud platform env vars only
    load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ProjectMatch:
    """Represents a project match with confidence score."""
    project_name: str
    confidence: float
    evidence: List[str]
    project_id: Optional[int] = None


class MultiProjectInsightsProcessor:
    """Enhanced insights processor that handles multi-project meetings."""
    
    def __init__(self, supabase: Client, openai_client: AsyncOpenAI):
        self.supabase = supabase
        self.openai_client = openai_client
        self.model = os.getenv('LLM_CHOICE', 'gpt-4o-mini')
        
        # Load project patterns for better matching
        self.project_patterns = self._load_project_patterns()
        
    def _load_project_patterns(self) -> Dict[str, List[str]]:
        """Load known project patterns from database or configuration."""
        patterns = {
            # Common project indicators
            'general_patterns': [
                r'(\w+\s+project)',
                r'(project\s+\w+)', 
                r'(\w+\s+warehouse)',
                r'(\w+\s+construction)',
                r'(\w+\s+build)',
                r'(job\s+\#?\d+)',
                r'(\w+\s+facility)',
                r'(\w+\s+site)'
            ],
            # ASRS specific patterns
            'asrs_patterns': [
                r'(ASRS\s+\w+)',
                r'(\w+\s+ASRS)',
                r'(automated\s+storage\s+\w+)',
                r'(retrieval\s+system\s+\w+)',
                r'(\w+\s+sprinkler\s+system)',
                r'(\w+\s+fire\s+protection)'
            ],
            # Client/location patterns  
            'client_patterns': [
                r'(\w+\s+logistics)',
                r'(\w+\s+distribution)',
                r'(\w+\s+fulfillment)',
                r'(\w+\s+center)',
                r'(\w+\s+campus)'
            ]
        }
        
        try:
            # Try to load actual project names from database
            result = self.supabase.table('projects').select('id, name, aliases, keywords').execute()
            if result.data:
                patterns['known_projects'] = []
                for project in result.data:
                    patterns['known_projects'].append(project['name'])
                    if project.get('aliases'):
                        patterns['known_projects'].extend(project['aliases'])
        except Exception as e:
            logger.warning(f"Could not load project names from database: {e}")
            
        return patterns
    
    async def process_document_with_multi_project_insights(
        self,
        document_id: str,
        title: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a document and extract insights with multi-project assignment.
        
        Returns:
            Dictionary with processing results, insights, and project assignments
        """
        
        # Step 1: Detect if this is a meeting transcript
        if not self._is_meeting_transcript(title, content):
            logger.info(f"Document {document_id} is not a meeting transcript")
            return {
                'processed': False,
                'reason': 'Not a meeting transcript',
                'insights': [],
                'projects': []
            }
        
        # Step 2: Check if already processed
        existing_insights = self.supabase.table('project_insights') \
            .select('id') \
            .eq('source_document_id', document_id) \
            .execute()
        
        if existing_insights.data:
            logger.info(f"Document {document_id} already has {len(existing_insights.data)} insights")
            return {
                'processed': False,
                'reason': 'Already processed',
                'insights': existing_insights.data,
                'projects': []
            }
        
        # Step 3: Extract meeting information
        meeting_info = self._extract_meeting_info(title, metadata)
        
        # Step 4: Identify potential projects mentioned
        project_matches = await self._identify_projects_in_content(title, content)
        
        # Step 5: Determine if this is a multi-project meeting
        is_multi_project = len(project_matches) > 1 or self._is_executive_meeting(title, meeting_info)
        
        # Step 6: Extract insights with project context
        if is_multi_project:
            insights = await self._extract_multi_project_insights(
                content, meeting_info, project_matches
            )
        else:
            # Single project or general meeting
            insights = await self._extract_single_project_insights(
                content, meeting_info, project_matches[0] if project_matches else None
            )
        
        # Step 7: Store insights with project assignments
        stored_insights = []
        for insight_data in insights:
            try:
                insight = ProjectInsight(
                    insight_type=insight_data.get('type', 'action_item'),
                    title=insight_data.get('title', ''),
                    description=insight_data.get('description', ''),
                    confidence_score=float(insight_data.get('confidence', 0.7)),
                    priority=insight_data.get('priority', 'medium'),
                    project_name=insight_data.get('project_name'),
                    assigned_to=insight_data.get('assigned_to'),
                    due_date=insight_data.get('due_date'),
                    source_document_id=document_id,
                    source_meeting_title=title,
                    source_date=meeting_info.get('date'),
                    speakers=meeting_info.get('speakers'),
                    keywords=insight_data.get('keywords', []),
                    metadata={
                        'original_metadata': metadata,
                        'meeting_info': meeting_info,
                        'project_matches': [p.__dict__ for p in project_matches],
                        'is_multi_project': is_multi_project,
                        'extraction_timestamp': datetime.now().isoformat()
                    }
                )
                
                stored_insights.append(insight)
                
            except Exception as e:
                logger.warning(f"Failed to create insight from data {insight_data}: {e}")
                continue
        
        # Step 8: Store insights in database
        stored_ids = await self._store_insights_batch(stored_insights)
        
        return {
            'processed': True,
            'insights_count': len(stored_ids),
            'insights': stored_insights,
            'projects': project_matches,
            'is_multi_project': is_multi_project,
            'stored_ids': stored_ids
        }
    
    async def _identify_projects_in_content(self, title: str, content: str) -> List[ProjectMatch]:
        """Use AI to identify and rank project mentions in the content."""
        
        # First, try pattern-based detection
        pattern_matches = self._extract_project_patterns(title + " " + content)
        
        # Then use AI for more sophisticated detection
        ai_matches = await self._ai_project_identification(title, content[:4000])  # Limit for API
        
        # Combine and score matches
        all_matches = {}
        
        # Add pattern matches
        for match in pattern_matches:
            key = match.lower().strip()
            if key not in all_matches:
                all_matches[key] = ProjectMatch(
                    project_name=match,
                    confidence=0.6,
                    evidence=['pattern_match']
                )
        
        # Add/enhance with AI matches
        for ai_match in ai_matches:
            key = ai_match['name'].lower().strip()
            confidence = float(ai_match.get('confidence', 0.7))
            evidence = ai_match.get('evidence', [])
            
            if key in all_matches:
                # Enhance existing match
                all_matches[key].confidence = max(all_matches[key].confidence, confidence)
                all_matches[key].evidence.extend(evidence)
            else:
                all_matches[key] = ProjectMatch(
                    project_name=ai_match['name'],
                    confidence=confidence,
                    evidence=evidence
                )
        
        # Return sorted by confidence
        matches = list(all_matches.values())
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        # Filter out low-confidence matches
        return [m for m in matches if m.confidence >= 0.5]
    
    def _extract_project_patterns(self, text: str) -> List[str]:
        """Extract project names using regex patterns."""
        matches = []
        
        for category, patterns in self.project_patterns.items():
            if category == 'known_projects':
                # Direct string matching for known projects
                for project_name in patterns:
                    if project_name.lower() in text.lower():
                        matches.append(project_name)
            else:
                # Regex pattern matching
                for pattern in patterns:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    matches.extend([match.strip() for match in found if len(match.strip()) > 2])
        
        # Clean and deduplicate
        cleaned_matches = []
        for match in matches:
            match = re.sub(r'\s+', ' ', match).strip()
            if match and len(match) > 2 and match not in cleaned_matches:
                cleaned_matches.append(match)
        
        return cleaned_matches
    
    async def _ai_project_identification(self, title: str, content: str) -> List[Dict[str, Any]]:
        """Use AI to identify project names and contexts."""
        
        system_prompt = """You are an expert at identifying project names and contexts from meeting transcripts.

Analyze the meeting content and identify any projects, clients, facilities, or specific work initiatives mentioned.

For each project identified, provide:
- name: The project/client/facility name
- confidence: Float 0.0-1.0 indicating confidence
- evidence: List of specific phrases/context that indicate this project
- type: One of [construction_project, client_facility, internal_initiative, maintenance_work]

Focus on:
- Named construction projects
- Client facilities or warehouses
- Specific job numbers or project codes
- ASRS installations or upgrades
- Location-specific work

Return ONLY a JSON array of project objects. No additional text."""

        user_prompt = f"""Meeting Title: {title}

Meeting Content (first 4000 chars):
{content}

Identify all projects, clients, or facilities mentioned in this meeting."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            try:
                projects_data = json.loads(response_text)
                if not isinstance(projects_data, list):
                    projects_data = [projects_data] if projects_data else []
                    
                return projects_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI project identification response: {e}")
                
                # Try to extract JSON from response
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                
                return []
                
        except Exception as e:
            logger.error(f"Failed AI project identification: {e}")
            return []
    
    def _is_executive_meeting(self, title: str, meeting_info: Dict[str, Any]) -> bool:
        """Detect if this is an executive or multi-project meeting."""
        title_lower = title.lower()
        
        executive_indicators = [
            'executive', 'leadership', 'operations', 'weekly', 'status', 
            'overview', 'review', 'planning', 'strategy', 'board',
            'management', 'directors', 'leads', 'team meeting'
        ]
        
        return any(indicator in title_lower for indicator in executive_indicators)
    
    async def _extract_multi_project_insights(
        self,
        content: str,
        meeting_info: Dict[str, Any],
        project_matches: List[ProjectMatch]
    ) -> List[Dict[str, Any]]:
        """Extract insights from multi-project meetings with project assignments."""
        
        system_prompt = """You are an expert project manager analyzing a multi-project meeting transcript.

This meeting discusses multiple projects. For each insight you extract, you MUST assign it to the most relevant project(s) based on context.

Available projects in this meeting:
""" + "\n".join([f"- {p.project_name} (confidence: {p.confidence:.2f})" for p in project_matches]) + """

For each insight, provide:
- type: One of [action_item, decision, risk, milestone, blocker, dependency, budget_update, timeline_change, stakeholder_feedback, technical_issue, opportunity, concern]
- title: Clear, concise summary (max 100 chars)
- description: Detailed explanation with context
- confidence: Float 0.0-1.0 indicating confidence in extraction
- priority: One of [critical, high, medium, low]
- project_name: The specific project this insight relates to (REQUIRED)
- assigned_to: Person responsible (if mentioned)
- due_date: ISO date format if mentioned
- keywords: Relevant terms for searchability

CRITICAL: Every insight must be assigned to a specific project. If an insight affects multiple projects, create separate insights for each project.

Return ONLY a JSON array of insight objects. No additional text."""

        user_prompt = f"""Meeting Information:
Title: {meeting_info.get('title', 'Unknown')}
Date: {meeting_info.get('date', 'Unknown')}
Speakers: {', '.join(meeting_info.get('speakers', []))}

Meeting Content:
{content[:6000]}  # Limit for context

Extract insights and assign each to the appropriate project."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            try:
                insights_data = json.loads(response_text)
                if not isinstance(insights_data, list):
                    insights_data = [insights_data] if insights_data else []
                    
                return insights_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse multi-project insights response: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to extract multi-project insights: {e}")
            return []
    
    async def _extract_single_project_insights(
        self,
        content: str,
        meeting_info: Dict[str, Any],
        project_match: Optional[ProjectMatch]
    ) -> List[Dict[str, Any]]:
        """Extract insights from single-project meetings."""
        
        # Use the existing single-project extraction logic
        generator = MeetingInsightsGenerator(self.supabase, self.openai_client)
        insights_data = await generator._generate_insights_with_llm(content, meeting_info)
        
        # Add project assignment if we have a match
        if project_match:
            for insight in insights_data:
                if not insight.get('project_name'):
                    insight['project_name'] = project_match.project_name
        
        return insights_data
    
    async def _store_insights_batch(self, insights: List[ProjectInsight]) -> List[str]:
        """Store a batch of insights efficiently."""
        stored_ids = []
        
        # Prepare batch insert data
        batch_data = []
        for insight in insights:
            insight_data = {
                'insight_type': insight.insight_type,
                'title': insight.title,
                'description': insight.description,
                'confidence_score': insight.confidence_score,
                'priority': insight.priority,
                'status': insight.status,
                'project_name': insight.project_name,
                'assigned_to': insight.assigned_to,
                'due_date': insight.due_date,
                'source_document_id': insight.source_document_id,
                'source_meeting_title': insight.source_meeting_title,
                'source_date': insight.source_date,
                'speakers': insight.speakers,
                'keywords': insight.keywords,
                'metadata': insight.metadata,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            batch_data.append(insight_data)
        
        try:
            # Batch insert
            result = self.supabase.table('project_insights').insert(batch_data).execute()
            
            if result.data:
                stored_ids = [item['id'] for item in result.data]
                logger.info(f"Batch stored {len(stored_ids)} insights")
            
        except Exception as e:
            logger.error(f"Failed to batch store insights: {e}")
            
            # Fallback to individual inserts
            for insight in insights:
                try:
                    individual_result = self.supabase.table('project_insights').insert(insight.to_dict()).execute()
                    if individual_result.data:
                        stored_ids.append(individual_result.data[0]['id'])
                except Exception as ie:
                    logger.error(f"Failed to store individual insight: {ie}")
        
        return stored_ids
    
    def _is_meeting_transcript(self, title: str, content: str) -> bool:
        """Detect if content is a meeting transcript."""
        # Reuse logic from MeetingInsightsGenerator
        generator = MeetingInsightsGenerator(self.supabase, self.openai_client)
        return generator._is_meeting_transcript(title, content)
    
    def _extract_meeting_info(self, title: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meeting information."""
        # Reuse logic from MeetingInsightsGenerator
        generator = MeetingInsightsGenerator(self.supabase, self.openai_client)
        return generator._extract_meeting_info(title, metadata)


class AutomatedInsightsPipeline:
    """Automated pipeline for processing new documents and generating insights."""
    
    def __init__(self):
        self.supabase = None
        self.openai_client = None
        self.processor = None
        
    async def initialize(self):
        """Initialize the pipeline with clients."""
        try:
            self.openai_client, self.supabase = get_agent_clients()
            self.processor = MultiProjectInsightsProcessor(self.supabase, self.openai_client)
            logger.info("Automated Insights Pipeline initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise
    
    async def process_new_document(self, document_id: str) -> Dict[str, Any]:
        """Process a newly uploaded document for insights."""
        
        if not self.processor:
            await self.initialize()
        
        try:
            # Get document from database
            result = self.supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if not result.data:
                return {'error': f'Document {document_id} not found'}
            
            doc = result.data[0]
            
            # Process with multi-project insights
            processing_result = await self.processor.process_document_with_multi_project_insights(
                document_id=document_id,
                title=doc['metadata'].get('file_title', 'Unknown Document'),
                content=doc['content'],
                metadata=doc['metadata']
            )
            
            logger.info(f"Processed document {document_id}: {processing_result}")
            return processing_result
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            return {'error': str(e)}
    
    async def process_all_unprocessed_documents(self) -> Dict[str, Any]:
        """Retroactively process all documents that don't have insights yet."""
        
        if not self.processor:
            await self.initialize()
        
        try:
            # Find documents that don't have insights yet
            result = self.supabase.from_('documents') \
                .select('id, metadata') \
                .execute()
            
            if not result.data:
                return {'processed': 0, 'errors': 0}
            
            # Get documents that already have insights
            insights_result = self.supabase.table('project_insights') \
                .select('source_document_id') \
                .execute()
            
            processed_docs = set()
            if insights_result.data:
                processed_docs = {item['source_document_id'] for item in insights_result.data}
            
            # Filter to unprocessed documents
            unprocessed_docs = [
                doc for doc in result.data 
                if doc['id'] not in processed_docs
            ]
            
            logger.info(f"Found {len(unprocessed_docs)} unprocessed documents")
            
            # Process each document
            processed_count = 0
            error_count = 0
            
            for doc in unprocessed_docs:
                try:
                    processing_result = await self.process_new_document(doc['id'])
                    
                    if processing_result.get('processed'):
                        processed_count += 1
                        logger.info(f"Successfully processed document {doc['id']}")
                    elif processing_result.get('error'):
                        error_count += 1
                        logger.warning(f"Error processing document {doc['id']}: {processing_result['error']}")
                    
                    # Small delay to avoid overwhelming the API
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Exception processing document {doc['id']}: {e}")
            
            return {
                'total_documents': len(unprocessed_docs),
                'processed': processed_count,
                'errors': error_count,
                'success_rate': processed_count / len(unprocessed_docs) if unprocessed_docs else 0
            }
            
        except Exception as e:
            logger.error(f"Failed retroactive processing: {e}")
            return {'error': str(e)}


# Singleton pipeline instance
_pipeline_instance = None

async def get_pipeline() -> AutomatedInsightsPipeline:
    """Get or create the pipeline instance."""
    global _pipeline_instance
    
    if _pipeline_instance is None:
        _pipeline_instance = AutomatedInsightsPipeline()
        await _pipeline_instance.initialize()
    
    return _pipeline_instance


async def process_document_for_automated_insights(document_id: str) -> Dict[str, Any]:
    """Main entry point for automated insights processing."""
    pipeline = await get_pipeline()
    return await pipeline.process_new_document(document_id)


async def process_all_documents_retroactively() -> Dict[str, Any]:
    """Process all existing documents retroactively."""
    pipeline = await get_pipeline()
    return await pipeline.process_all_unprocessed_documents()