"""
Project Insights Service for PM RAG Agent

This service generates AI-driven insights from meeting transcripts and project documents,
automatically extracting actionable intelligence for project management.

Adapted from alleato-rag-vectorize insights service for Agent Deployment module.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from pathlib import Path

from openai import AsyncOpenAI
from supabase import Client
from dotenv import load_dotenv

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


class InsightType(Enum):
    """Types of insights that can be extracted from meetings."""
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    RISK = "risk"
    MILESTONE = "milestone"
    BLOCKER = "blocker"
    DEPENDENCY = "dependency"
    BUDGET_UPDATE = "budget_update"
    TIMELINE_CHANGE = "timeline_change"
    STAKEHOLDER_FEEDBACK = "stakeholder_feedback"
    TECHNICAL_ISSUE = "technical_issue"
    OPPORTUNITY = "opportunity"
    CONCERN = "concern"


class InsightPriority(Enum):
    """Priority levels for insights."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InsightStatus(Enum):
    """Status of insight items."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ProjectInsight:
    """Structured representation of a project insight."""
    insight_type: str  # InsightType.value
    title: str
    description: str
    confidence_score: float
    priority: str  # InsightPriority.value
    status: str = "open"  # InsightStatus.value
    project_name: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None  # ISO format
    source_document_id: Optional[str] = None
    source_meeting_title: Optional[str] = None
    source_date: Optional[str] = None
    speakers: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    related_insights: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class MeetingInsightsGenerator:
    """Service for extracting and managing project insights from meeting transcripts."""
    
    def __init__(self, supabase: Client, openai_client: AsyncOpenAI):
        self.supabase = supabase
        self.openai_client = openai_client
        self.model = os.getenv('LLM_CHOICE', 'gpt-4o-mini')
        
    async def extract_insights_from_meeting(
        self,
        document_id: str,
        title: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[ProjectInsight]:
        """
        Extract structured insights from a meeting transcript.
        
        Args:
            document_id: Unique identifier for the document
            title: Meeting title
            content: Full meeting transcript content
            metadata: Document metadata including speakers, date, etc.
            
        Returns:
            List of ProjectInsight objects
        """
        
        # Detect if this is a meeting transcript
        if not self._is_meeting_transcript(title, content):
            logger.info(f"Document {document_id} does not appear to be a meeting transcript")
            return []
        
        # Extract basic meeting information
        meeting_info = self._extract_meeting_info(title, metadata)
        
        # Generate insights using LLM
        insights_data = await self._generate_insights_with_llm(content, meeting_info)
        
        # Convert to structured insights
        insights = []
        for insight_data in insights_data:
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
                        'extraction_timestamp': datetime.now().isoformat()
                    }
                )
                insights.append(insight)
            except Exception as e:
                logger.warning(f"Failed to create insight from data {insight_data}: {e}")
                continue
                
        return insights

    def _is_meeting_transcript(self, title: str, content: str) -> bool:
        """Detect if content is a meeting transcript."""
        title_lower = title.lower()
        meeting_indicators = [
            'meeting', 'call', 'session', 'standup', 'sync', 'review', 
            'discussion', 'conference', 'huddle', 'briefing', 'kickoff'
        ]
        
        # Check title for meeting indicators
        if any(indicator in title_lower for indicator in meeting_indicators):
            return True
        
        # Check content for conversation patterns
        conversation_patterns = [
            r'\b[A-Z][a-zA-Z\s]+:\s',  # "John Doe: "
            r'\b[A-Z_]+\d*:\s',        # "SPEAKER_1: "
            r'^\[([^]]+)\]\s*([A-Z])', # "[10:30] Text"
            r'>\s*[A-Z][a-zA-Z\s]+:',  # "> John Doe:"
        ]
        
        speaker_matches = sum(len(re.findall(pattern, content, re.MULTILINE)) for pattern in conversation_patterns)
        total_lines = len([line for line in content.split('\n') if line.strip()])
        
        # If more than 15% of lines have speaker patterns, likely a transcript
        return total_lines > 0 and (speaker_matches / total_lines) > 0.15

    def _extract_meeting_info(self, title: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meeting information from title and metadata."""
        meeting_info = {
            'title': title,
            'date': None,
            'speakers': [],
            'project_hints': []
        }
        
        # Extract date from metadata or title
        if 'created_at' in metadata:
            meeting_info['date'] = metadata['created_at']
        elif 'file_title' in metadata:
            # Try to extract date from title
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\w+ \d{1,2}, \d{4})'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, title)
                if match:
                    meeting_info['date'] = match.group(1)
                    break
        
        # Extract speakers from metadata
        if 'speakers' in metadata and metadata['speakers']:
            if isinstance(metadata['speakers'], str):
                meeting_info['speakers'] = [s.strip() for s in metadata['speakers'].split(',')]
            elif isinstance(metadata['speakers'], list):
                meeting_info['speakers'] = metadata['speakers']
        
        # Extract project hints from title
        project_patterns = [
            r'(\w+\s+project)',
            r'(project\s+\w+)',
            r'(\w+\s+warehouse)',
            r'(ASRS\s+\w+)',
            r'(\w+\s+construction)'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, title, re.IGNORECASE)
            meeting_info['project_hints'].extend(matches)
        
        return meeting_info

    async def _generate_insights_with_llm(
        self,
        content: str,
        meeting_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate insights using LLM analysis."""
        
        # Prepare the system prompt for insight extraction
        system_prompt = """You are an expert project management AI that extracts actionable insights from meeting transcripts.

Your task is to analyze meeting content and identify:
1. Action items with owners and due dates
2. Decisions made and their implications
3. Risks, blockers, and dependencies identified
4. Budget updates and timeline changes
5. Technical issues and opportunities
6. Stakeholder feedback and concerns

For each insight, provide:
- type: One of [action_item, decision, risk, milestone, blocker, dependency, budget_update, timeline_change, stakeholder_feedback, technical_issue, opportunity, concern]
- title: Clear, concise summary (max 100 chars)
- description: Detailed explanation with context
- confidence: Float 0.0-1.0 indicating confidence in extraction
- priority: One of [critical, high, medium, low]
- project_name: If identifiable from context
- assigned_to: Person responsible (if mentioned)
- due_date: ISO date format if mentioned
- keywords: Relevant terms for searchability

Focus on actionable, specific insights that would be valuable for project tracking and management.

Return ONLY a JSON array of insight objects. No additional text or formatting."""

        user_prompt = f"""Meeting Information:
Title: {meeting_info.get('title', 'Unknown')}
Date: {meeting_info.get('date', 'Unknown')}
Speakers: {', '.join(meeting_info.get('speakers', []))}

Meeting Transcript:
{content[:8000]}  # Limit content to avoid token limits

Please extract actionable project insights from this meeting transcript."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                insights_data = json.loads(response_text)
                if not isinstance(insights_data, list):
                    logger.warning("LLM returned non-list response, wrapping in list")
                    insights_data = [insights_data] if insights_data else []
                    
                return insights_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                logger.debug(f"Response text: {response_text}")
                
                # Attempt to extract JSON from response
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate insights with LLM: {e}")
            return []

    async def store_insights(self, insights: List[ProjectInsight]) -> List[str]:
        """
        Store insights in the database.
        
        Args:
            insights: List of ProjectInsight objects
            
        Returns:
            List of stored insight IDs
        """
        stored_ids = []
        
        for insight in insights:
            try:
                # Prepare insight data for storage
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
                
                # Insert into project_insights table
                result = self.supabase.table('project_insights').insert(insight_data).execute()
                
                if result.data:
                    insight_id = result.data[0]['id']
                    stored_ids.append(insight_id)
                    logger.info(f"Stored insight: {insight.title} (ID: {insight_id})")
                
            except Exception as e:
                logger.error(f"Failed to store insight '{insight.title}': {e}")
                continue
        
        return stored_ids

    async def get_insights_for_project(
        self,
        project_name: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve insights with filters.
        
        Args:
            project_name: Filter by project name
            insight_types: Filter by insight types
            priorities: Filter by priority levels
            status_filter: Filter by status
            date_from: Filter from date (ISO format)
            date_to: Filter to date (ISO format)
            limit: Maximum results to return
            
        Returns:
            List of insight dictionaries
        """
        query = self.supabase.table('project_insights').select('*')
        
        # Apply filters
        if project_name:
            query = query.ilike('project_name', f'%{project_name}%')
        
        if insight_types:
            query = query.in_('insight_type', insight_types)
        
        if priorities:
            query = query.in_('priority', priorities)
            
        if status_filter:
            query = query.in_('status', status_filter)
        
        if date_from:
            query = query.gte('source_date', date_from)
            
        if date_to:
            query = query.lte('source_date', date_to)
        
        # Order by creation date and limit
        query = query.order('created_at', desc=True).limit(limit)
        
        try:
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to retrieve insights: {e}")
            return []

    async def get_insights_summary(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a summary of insights over the specified period.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Summary statistics and key insights
        """
        date_from = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        try:
            # Get all insights in the period
            insights = await self.get_insights_for_project(date_from=date_from, limit=1000)
            
            if not insights:
                return {
                    'period_days': days_back,
                    'total_insights': 0,
                    'insights_by_type': {},
                    'insights_by_priority': {},
                    'insights_by_status': {},
                    'active_projects': [],
                    'top_concerns': [],
                    'recent_decisions': []
                }
            
            # Calculate statistics
            total_insights = len(insights)
            insights_by_type = {}
            insights_by_priority = {}
            insights_by_status = {}
            project_counts = {}
            
            for insight in insights:
                # By type
                insight_type = insight.get('insight_type', 'unknown')
                insights_by_type[insight_type] = insights_by_type.get(insight_type, 0) + 1
                
                # By priority
                priority = insight.get('priority', 'medium')
                insights_by_priority[priority] = insights_by_priority.get(priority, 0) + 1
                
                # By status
                status = insight.get('status', 'open')
                insights_by_status[status] = insights_by_status.get(status, 0) + 1
                
                # By project
                project_name = insight.get('project_name')
                if project_name:
                    project_counts[project_name] = project_counts.get(project_name, 0) + 1
            
            # Get top concerns and recent decisions
            top_concerns = [
                insight for insight in insights 
                if insight.get('insight_type') in ['risk', 'blocker', 'concern']
                and insight.get('priority') in ['critical', 'high']
            ][:5]
            
            recent_decisions = [
                insight for insight in insights 
                if insight.get('insight_type') == 'decision'
            ][:5]
            
            return {
                'period_days': days_back,
                'total_insights': total_insights,
                'insights_by_type': insights_by_type,
                'insights_by_priority': insights_by_priority,
                'insights_by_status': insights_by_status,
                'active_projects': sorted(project_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                'top_concerns': top_concerns,
                'recent_decisions': recent_decisions,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate insights summary: {e}")
            return {'error': str(e)}


async def process_meeting_document_for_insights(
    supabase: Client,
    openai_client: AsyncOpenAI,
    document_id: str,
    force_reprocess: bool = False
) -> List[str]:
    """
    Process a single document for insights extraction.
    
    Args:
        supabase: Supabase client
        openai_client: OpenAI client
        document_id: ID of document to process
        force_reprocess: Whether to reprocess even if already processed
        
    Returns:
        List of stored insight IDs
    """
    generator = MeetingInsightsGenerator(supabase, openai_client)
    
    try:
        # Get document from database
        result = supabase.table('documents').select('*').eq('id', document_id).execute()
        
        if not result.data:
            logger.warning(f"Document {document_id} not found")
            return []
        
        doc = result.data[0]
        
        # Check if already processed (unless forced)
        if not force_reprocess:
            existing_insights = supabase.table('project_insights') \
                .select('id') \
                .eq('source_document_id', document_id) \
                .execute()
            
            if existing_insights.data:
                logger.info(f"Document {document_id} already has {len(existing_insights.data)} insights")
                return [insight['id'] for insight in existing_insights.data]
        
        # Extract insights
        insights = await generator.extract_insights_from_meeting(
            document_id=document_id,
            title=doc['metadata'].get('file_title', 'Unknown Document'),
            content=doc['content'],
            metadata=doc['metadata']
        )
        
        if not insights:
            logger.info(f"No insights extracted from document {document_id}")
            return []
        
        # Store insights
        stored_ids = await generator.store_insights(insights)
        logger.info(f"Processed document {document_id}: extracted {len(insights)} insights, stored {len(stored_ids)}")
        
        return stored_ids
        
    except Exception as e:
        logger.error(f"Failed to process document {document_id} for insights: {e}")
        return []


def get_insights_generator(supabase: Client, openai_client: AsyncOpenAI) -> MeetingInsightsGenerator:
    """Factory function to create insights generator."""
    return MeetingInsightsGenerator(supabase, openai_client)