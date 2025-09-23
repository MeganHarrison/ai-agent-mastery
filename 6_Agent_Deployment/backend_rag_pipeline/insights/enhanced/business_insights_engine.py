"""
Enhanced Business Insights Engine

Advanced AI-powered insights generation for business documents using GPT models.
Generates high-quality, actionable insights that map to the sophisticated document_insights schema.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from decimal import Decimal

from openai import AsyncOpenAI
from supabase import Client

logger = logging.getLogger(__name__)


class BusinessInsightType(Enum):
    """Business-focused insight types that align with strategic decision making."""
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    MILESTONE = "milestone"
    BLOCKER = "blocker"
    DEPENDENCY = "dependency"
    BUDGET_IMPACT = "budget_impact"
    TIMELINE_CHANGE = "timeline_change"
    STAKEHOLDER_CONCERN = "stakeholder_concern"
    TECHNICAL_DEBT = "technical_debt"
    RESOURCE_NEED = "resource_need"
    COMPLIANCE_ISSUE = "compliance_issue"
    STRATEGIC_PIVOT = "strategic_pivot"
    PERFORMANCE_METRIC = "performance_metric"


class BusinessSeverity(Enum):
    """Business impact severity levels."""
    CRITICAL = "critical"    # Immediate action required, business-stopping
    HIGH = "high"           # Urgent attention needed, significant impact
    MEDIUM = "medium"       # Important but not urgent, moderate impact
    LOW = "low"            # Nice to have, minimal impact


@dataclass
class EnhancedBusinessInsight:
    """Sophisticated business insight that maps to document_insights schema."""
    # Core fields
    document_id: str
    project_id: Optional[int]
    insight_type: str
    title: str
    description: str
    confidence_score: float
    generated_by: str = "gpt-4o-mini"
    doc_title: Optional[str] = None
    
    # Business impact fields
    severity: str = "medium"
    business_impact: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None  # YYYY-MM-DD format
    financial_impact: Optional[Decimal] = None
    urgency_indicators: Optional[List[str]] = None
    resolved: bool = False
    
    # Context and relationships
    source_meetings: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    stakeholders_affected: Optional[List[str]] = None
    exact_quotes: Optional[List[str]] = None
    numerical_data: Optional[Dict[str, Any]] = None
    critical_path_impact: bool = False
    cross_project_impact: Optional[List[int]] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    
    def to_database_dict(self) -> Dict[str, Any]:
        """Convert to database-compatible dictionary."""
        
        # Helper function to ensure arrays are properly formatted
        def ensure_array(value):
            if value is None:
                return None
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                # If it's a string that looks like an array element, wrap it in a list
                return [value]
            return value
        
        data = {
            'document_id': self.document_id,
            'project_id': self.project_id,
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'confidence_score': float(self.confidence_score),
            'generated_by': self.generated_by,
            'doc_title': self.doc_title,
            'severity': self.severity,
            'business_impact': self.business_impact,
            'assignee': self.assignee,
            'due_date': self.due_date,
            'financial_impact': float(self.financial_impact) if self.financial_impact else None,
            'urgency_indicators': ensure_array(self.urgency_indicators),
            'resolved': self.resolved,
            'source_meetings': ensure_array(self.source_meetings),
            'dependencies': ensure_array(self.dependencies),
            'stakeholders_affected': ensure_array(self.stakeholders_affected),
            'exact_quotes': ensure_array(self.exact_quotes),
            'numerical_data': self.numerical_data,
            'critical_path_impact': self.critical_path_impact,
            'cross_project_impact': ensure_array(self.cross_project_impact),
            'metadata': self.metadata or {},
            'created_at': datetime.now().isoformat()
        }
        return data


class BusinessInsightsEngine:
    """
    Advanced AI engine for generating sophisticated business insights from documents.
    
    Uses GPT models with carefully crafted prompts to extract actionable business intelligence
    that executives and project managers can immediately act upon.
    """
    
    def __init__(self, supabase: Client, openai_client: Optional[AsyncOpenAI] = None):
        self.supabase = supabase
        
        # Initialize OpenAI client
        if openai_client is None:
            api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("LLM_API_KEY or OPENAI_API_KEY environment variable is required")
            self.openai_client = AsyncOpenAI(api_key=api_key)
        else:
            self.openai_client = openai_client
        
        # Use GPT-4o-mini for superior insight quality
        self.model = os.getenv('LLM_CHOICE', 'gpt-4o-mini')
        
        # Business context configuration
        self.business_context_prompt = self._load_business_context()
        
    def _load_business_context(self) -> str:
        """Load or generate business context for better insights."""
        return """
        You are analyzing business documents for a professional services consulting firm.
        Focus on extracting insights that directly impact:
        - Project delivery and timelines
        - Financial performance and budget management
        - Risk management and mitigation
        - Stakeholder relationships and communication
        - Resource allocation and team performance
        - Strategic decision making
        - Operational efficiency improvements
        """
        
    async def extract_business_insights(
        self,
        document_id: str,
        content: str,
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[EnhancedBusinessInsight]:
        """
        Extract sophisticated business insights from document content.
        
        Uses advanced prompting techniques with GPT models to identify actionable
        business intelligence that maps to the document_insights schema.
        """
        
        if not content or len(content.strip()) < 50:
            logger.info(f"Content too short for meaningful insights: {document_id}")
            return []
            
        metadata = metadata or {}
        
        # Analyze document type for context-specific processing
        doc_analysis = await self._analyze_document_type(content, title, metadata)
        
        # Extract insights using specialized prompts based on document type
        raw_insights = await self._extract_insights_with_gpt(
            content, title, metadata, doc_analysis
        )
        
        # Convert to structured insights
        structured_insights = []
        for raw_insight in raw_insights:
            try:
                insight = self._convert_to_structured_insight(
                    raw_insight, document_id, title, metadata
                )
                if insight:
                    structured_insights.append(insight)
            except Exception as e:
                logger.warning(f"Failed to convert insight: {e}")
                continue
        
        # Post-process for quality and business relevance
        filtered_insights = self._filter_and_rank_insights(structured_insights)
        
        logger.info(f"Extracted {len(filtered_insights)} business insights from {document_id}")
        return filtered_insights
    
    async def _analyze_document_type(
        self, 
        content: str, 
        title: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze document to determine type and appropriate extraction strategy."""
        
        # Quick analysis prompt
        analysis_prompt = f"""
        Analyze this document and classify its type and business context:
        
        Title: {title}
        Content preview: {content[:1000]}...
        
        Return JSON with:
        - document_type: meeting_transcript, project_plan, status_report, proposal, contract, email, etc.
        - business_domain: technology, consulting, finance, marketing, operations, etc.
        - urgency_level: low, medium, high, critical
        - key_stakeholders: list of roles/people mentioned
        - contains_decisions: boolean
        - contains_action_items: boolean
        - contains_financial_data: boolean
        - contains_timeline_info: boolean
        - project_references: list of project names/IDs mentioned
        """
        
        try:
            # Use appropriate parameters for different models
            completion_params = {
                "model": self.model,
                "messages": [{"role": "user", "content": analysis_prompt}]
            }
            
            # Handle model-specific parameters
            if "gpt-5" in self.model.lower():
                completion_params["max_completion_tokens"] = 800
                # GPT-5 only supports default temperature of 1
            else:
                completion_params["max_tokens"] = 800
                completion_params["temperature"] = 0.1
            
            response = await self.openai_client.chat.completions.create(**completion_params)
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                try:
                    return json.loads(analysis_text)
                except:
                    # Fallback analysis
                    return self._fallback_document_analysis(content, title)
                    
        except Exception as e:
            logger.warning(f"Document analysis failed: {e}")
            return self._fallback_document_analysis(content, title)
    
    def _fallback_document_analysis(self, content: str, title: str) -> Dict[str, Any]:
        """Fallback document analysis using pattern matching."""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Document type detection
        if any(word in title_lower for word in ['meeting', 'call', 'standup', 'sync']):
            doc_type = "meeting_transcript"
        elif any(word in title_lower for word in ['plan', 'roadmap', 'schedule']):
            doc_type = "project_plan"
        elif any(word in title_lower for word in ['status', 'update', 'report']):
            doc_type = "status_report"
        elif any(word in title_lower for word in ['proposal', 'sow', 'statement']):
            doc_type = "proposal"
        else:
            doc_type = "general_document"
        
        # Extract stakeholders
        stakeholder_patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # Full names
            r'\b([A-Z][a-z]+):\s',              # Speaker patterns
        ]
        
        stakeholders = set()
        for pattern in stakeholder_patterns:
            matches = re.findall(pattern, content)
            stakeholders.update(matches[:10])  # Limit to 10
        
        return {
            'document_type': doc_type,
            'business_domain': 'consulting',
            'urgency_level': 'medium',
            'key_stakeholders': list(stakeholders),
            'contains_decisions': 'decision' in content_lower or 'decided' in content_lower,
            'contains_action_items': 'action' in content_lower or 'todo' in content_lower,
            'contains_financial_data': '$' in content or 'budget' in content_lower,
            'contains_timeline_info': 'deadline' in content_lower or 'due' in content_lower,
            'project_references': []
        }
    
    async def _extract_insights_with_gpt(
        self,
        content: str,
        title: str,
        metadata: Dict[str, Any],
        doc_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract insights using GPT with sophisticated business prompting."""
        
        # Build context-aware system prompt
        system_prompt = f"""
        You are an elite business intelligence analyst and management consultant with 20+ years of experience.
        You specialize in extracting actionable insights from business documents that drive executive decision-making.
        
        {self.business_context_prompt}
        
        Document Context:
        - Type: {doc_analysis.get('document_type', 'unknown')}
        - Domain: {doc_analysis.get('business_domain', 'business')}
        - Urgency: {doc_analysis.get('urgency_level', 'medium')}
        - Key Stakeholders: {', '.join(doc_analysis.get('key_stakeholders', []))}
        
        INSTRUCTIONS:
        1. Extract ONLY insights that have clear business impact and are actionable
        2. Focus on insights that affect revenue, costs, timelines, risks, or strategic objectives
        3. Include specific financial impacts when mentioned (extract exact numbers)
        4. Identify critical path impacts and cross-project dependencies
        5. Capture exact quotes that support each insight
        6. Assign realistic urgency and business severity levels
        
        For each insight, provide:
        - insight_type: {[t.value for t in BusinessInsightType]}
        - title: Clear, executive-level summary (max 100 chars)
        - description: Detailed business impact and recommended actions (max 500 chars)
        - business_impact: Specific impact on business objectives
        - severity: critical/high/medium/low based on business urgency
        - confidence_score: 0.0-1.0 based on evidence quality
        - assignee: Specific person mentioned (if any)
        - due_date: YYYY-MM-DD format if timeline mentioned
        - financial_impact: Numeric value if money mentioned (positive or negative)
        - urgency_indicators: List of phrases that indicate urgency
        - stakeholders_affected: People/roles impacted
        - exact_quotes: Verbatim text that supports this insight
        - numerical_data: Any numbers, percentages, or metrics mentioned
        - critical_path_impact: true if affects project critical path
        - dependencies: Other tasks/projects this depends on
        
        Return JSON array of insights. Only include insights with clear business value.
        """
        
        # Prepare content for analysis (truncate if too long)
        max_content_length = 12000  # Leave room for prompts
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n[Content truncated...]"
        
        user_prompt = f"""
        Document Title: {title}
        
        Document Content:
        {content}
        
        Extract all business-critical insights from this document. Focus on actionable intelligence
        that a CEO, project manager, or department head could immediately act upon.
        """
        
        try:
            # Use appropriate parameters for different models
            completion_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            # Handle model-specific parameters
            if "gpt-5" in self.model.lower():
                completion_params["max_completion_tokens"] = 6000
                # GPT-5 only supports default temperature of 1
            else:
                completion_params["max_tokens"] = 6000
                completion_params["temperature"] = 0.1  # Low temperature for consistent, factual extraction
            
            response = await self.openai_client.chat.completions.create(**completion_params)
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            return self._parse_insights_json(response_text)
            
        except Exception as e:
            logger.error(f"GPT insights extraction failed: {e}")
            return []
    
    def _parse_insights_json(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse insights JSON from GPT response with error recovery."""
        
        # Log the response for debugging
        logger.info(f"GPT Response (first 200 chars): {response_text[:200]}...")
        
        try:
            # Try direct JSON parsing first
            insights = json.loads(response_text)
            if isinstance(insights, list):
                return insights
            elif isinstance(insights, dict) and 'insights' in insights:
                return insights['insights']
            else:
                return []
                
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks (most common case)
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
                r'```\s*([\s\S]*?)\s*```',     # ``` ... ``` 
                r'\[\s*\{[\s\S]*?\}\s*\]'     # Find any array of objects
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, response_text, re.DOTALL)
                if json_match:
                    try:
                        json_text = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group(0)
                        parsed = json.loads(json_text)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            logger.info(f"Successfully parsed JSON from pattern: {pattern[:20]}...")
                            return parsed
                    except json.JSONDecodeError:
                        continue
            
            # If no JSON found, try to create insights from structured text
            logger.warning("No valid JSON found, attempting text parsing...")
            return self._parse_insights_from_text(response_text)
    
    def _parse_insights_from_text(self, response_text: str) -> List[Dict[str, Any]]:
        """Fallback: Parse insights from structured text when JSON parsing fails."""
        insights = []
        
        try:
            # Look for insight patterns in the text
            lines = response_text.split('\n')
            current_insight = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for key-value patterns
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip().strip('"\'')
                    
                    if key in ['type', 'insight_type']:
                        if current_insight:  # Save previous insight
                            insights.append(current_insight)
                        current_insight = {'insight_type': value}
                    elif key in ['title']:
                        current_insight['title'] = value
                    elif key in ['description']:
                        current_insight['description'] = value
                    elif key in ['severity', 'priority']:
                        current_insight['severity'] = value
                    elif key in ['confidence', 'confidence_score']:
                        try:
                            current_insight['confidence_score'] = float(value)
                        except:
                            current_insight['confidence_score'] = 0.7
                    elif key in ['assignee', 'assigned_to']:
                        current_insight['assignee'] = value
                    elif key in ['financial_impact']:
                        try:
                            # Extract number from financial impact
                            numbers = re.findall(r'[\d,]+', value.replace('$', '').replace(',', ''))
                            if numbers:
                                current_insight['financial_impact'] = float(numbers[0])
                        except:
                            pass
            
            # Add the last insight
            if current_insight and 'title' in current_insight:
                insights.append(current_insight)
            
            # If we still don't have insights, create some basic ones from key content
            if not insights:
                insights = self._create_fallback_insights(response_text)
                
        except Exception as e:
            logger.warning(f"Text parsing failed: {e}")
            insights = self._create_fallback_insights(response_text)
        
        logger.info(f"Text parsing extracted {len(insights)} insights")
        return insights
    
    def _create_fallback_insights(self, response_text: str) -> List[Dict[str, Any]]:
        """Create basic insights when all parsing fails."""
        insights = []
        
        # Look for key business terms and create basic insights
        text_lower = response_text.lower()
        
        if '$' in response_text or 'budget' in text_lower or 'cost' in text_lower:
            insights.append({
                'insight_type': 'budget_impact',
                'title': 'Financial Impact Identified',
                'description': 'Document contains financial implications that require review.',
                'severity': 'medium',
                'confidence_score': 0.6
            })
        
        if any(word in text_lower for word in ['urgent', 'critical', 'emergency', 'immediate']):
            insights.append({
                'insight_type': 'risk',
                'title': 'Urgent Issue Identified', 
                'description': 'Document contains urgent or critical issues requiring attention.',
                'severity': 'high',
                'confidence_score': 0.7
            })
        
        if any(word in text_lower for word in ['action', 'todo', 'task', 'deadline']):
            insights.append({
                'insight_type': 'action_item',
                'title': 'Action Items Identified',
                'description': 'Document contains action items or tasks that need to be completed.',
                'severity': 'medium', 
                'confidence_score': 0.6
            })
        
        return insights
    
    def _convert_to_structured_insight(
        self,
        raw_insight: Dict[str, Any],
        document_id: str,
        doc_title: str,
        metadata: Dict[str, Any]
    ) -> Optional[EnhancedBusinessInsight]:
        """Convert raw GPT insight to structured EnhancedBusinessInsight."""
        
        try:
            # Extract and validate required fields
            insight_type = raw_insight.get('insight_type', 'action_item')
            title = raw_insight.get('title', '').strip()
            description = raw_insight.get('description', '').strip()
            
            if not title or not description:
                return None
            
            # Parse financial impact
            financial_impact = None
            if raw_insight.get('financial_impact'):
                try:
                    # Handle various formats: "$1000", "1000", "-500", etc.
                    financial_str = str(raw_insight['financial_impact']).replace('$', '').replace(',', '')
                    financial_impact = Decimal(financial_str)
                except:
                    pass
            
            # Parse due date
            due_date = None
            if raw_insight.get('due_date'):
                due_date_str = str(raw_insight['due_date'])
                # Validate date format (YYYY-MM-DD)
                if re.match(r'\d{4}-\d{2}-\d{2}', due_date_str):
                    due_date = due_date_str
            
            # Extract project ID from metadata or title
            project_id = metadata.get('project_id')
            if not project_id:
                # Try to extract from document title or content
                project_patterns = [
                    r'project[_\s]+(\d+)',
                    r'proj[_\s]+(\d+)',
                    r'#(\d+)'
                ]
                for pattern in project_patterns:
                    match = re.search(pattern, f"{doc_title} {description}", re.IGNORECASE)
                    if match:
                        try:
                            project_id = int(match.group(1))
                            break
                        except:
                            pass
            
            insight = EnhancedBusinessInsight(
                document_id=document_id,
                project_id=project_id,
                insight_type=insight_type,
                title=title[:100],  # Ensure max length
                description=description[:500],  # Ensure max length
                confidence_score=float(raw_insight.get('confidence_score', 0.7)),
                doc_title=doc_title,
                severity=raw_insight.get('severity', 'medium'),
                business_impact=raw_insight.get('business_impact', ''),
                assignee=raw_insight.get('assignee'),
                due_date=due_date,
                financial_impact=financial_impact,
                urgency_indicators=raw_insight.get('urgency_indicators', []),
                resolved=False,
                source_meetings=[doc_title] if 'meeting' in doc_title.lower() else None,
                dependencies=raw_insight.get('dependencies', []),
                stakeholders_affected=raw_insight.get('stakeholders_affected', []),
                exact_quotes=raw_insight.get('exact_quotes', []),
                numerical_data=raw_insight.get('numerical_data'),
                critical_path_impact=bool(raw_insight.get('critical_path_impact', False)),
                cross_project_impact=raw_insight.get('cross_project_impact'),
                metadata={
                    'original_metadata': metadata,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'model_used': self.model,
                    'confidence_factors': raw_insight.get('confidence_factors', [])
                }
            )
            
            return insight
            
        except Exception as e:
            logger.warning(f"Failed to convert raw insight to structured: {e}")
            return None
    
    def _filter_and_rank_insights(
        self, 
        insights: List[EnhancedBusinessInsight]
    ) -> List[EnhancedBusinessInsight]:
        """Filter and rank insights by business value and quality."""
        
        if not insights:
            return []
        
        # Filter out low-quality insights
        quality_insights = []
        for insight in insights:
            # Quality criteria
            if (insight.confidence_score >= 0.6 and
                len(insight.title) > 10 and
                len(insight.description) > 20 and
                insight.insight_type in [t.value for t in BusinessInsightType]):
                quality_insights.append(insight)
        
        # Rank by business impact (critical > high > medium > low)
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        def insight_score(insight):
            severity_score = severity_order.get(insight.severity, 1)
            confidence_score = insight.confidence_score
            urgency_score = 1.2 if insight.urgency_indicators else 1.0
            financial_score = 1.3 if insight.financial_impact else 1.0
            critical_path_score = 1.5 if insight.critical_path_impact else 1.0
            
            return severity_score * confidence_score * urgency_score * financial_score * critical_path_score
        
        # Sort by score (highest first) and limit to top insights
        ranked_insights = sorted(quality_insights, key=insight_score, reverse=True)
        
        # Return top 20 insights to avoid overwhelming users
        return ranked_insights[:20]
    
    async def save_insights_to_database(
        self, 
        insights: List[EnhancedBusinessInsight]
    ) -> List[str]:
        """Save insights to the document_insights table."""
        
        saved_ids = []
        
        for insight in insights:
            try:
                data = insight.to_database_dict()
                
                # Insert into document_insights table
                result = self.supabase.table('document_insights').insert(data).execute()
                
                if result.data and len(result.data) > 0:
                    insight_id = result.data[0]['id']
                    saved_ids.append(insight_id)
                    logger.info(f"Saved insight: {insight.title[:50]}...")
                else:
                    logger.warning(f"Failed to save insight: {insight.title}")
                    
            except Exception as e:
                logger.error(f"Error saving insight '{insight.title}': {e}")
                continue
        
        logger.info(f"Successfully saved {len(saved_ids)}/{len(insights)} insights to database")
        return saved_ids
    
    async def process_document(
        self,
        document_id: str,
        content: str,
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete document processing pipeline: extract and save insights.
        
        Returns:
            Processing results including insight IDs and statistics
        """
        start_time = datetime.now()
        
        try:
            # Extract insights
            insights = await self.extract_business_insights(
                document_id=document_id,
                content=content,
                title=title,
                metadata=metadata
            )
            
            # Save to database
            saved_ids = []
            if insights:
                saved_ids = await self.save_insights_to_database(insights)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'document_id': document_id,
                'insights_extracted': len(insights),
                'insights_saved': len(saved_ids),
                'insight_ids': saved_ids,
                'processing_time_seconds': processing_time,
                'insights_by_type': self._count_insights_by_type(insights),
                'insights_by_severity': self._count_insights_by_severity(insights)
            }
            
            logger.info(f"Document processing completed: {document_id} -> {len(saved_ids)} insights")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Document processing failed for {document_id}: {e}")
            
            return {
                'success': False,
                'document_id': document_id,
                'insights_extracted': 0,
                'insights_saved': 0,
                'insight_ids': [],
                'processing_time_seconds': processing_time,
                'error': str(e)
            }
    
    def _count_insights_by_type(self, insights: List[EnhancedBusinessInsight]) -> Dict[str, int]:
        """Count insights by type for analytics."""
        counts = {}
        for insight in insights:
            counts[insight.insight_type] = counts.get(insight.insight_type, 0) + 1
        return counts
    
    def _count_insights_by_severity(self, insights: List[EnhancedBusinessInsight]) -> Dict[str, int]:
        """Count insights by severity for analytics."""
        counts = {}
        for insight in insights:
            counts[insight.severity] = counts.get(insight.severity, 0) + 1
        return counts
