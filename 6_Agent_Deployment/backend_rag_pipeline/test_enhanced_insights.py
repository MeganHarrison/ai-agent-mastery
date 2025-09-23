"""
Test script for Enhanced Business Insights Engine

Run this script to test the enhanced insights system with sample business documents.
"""

import asyncio
import os
import json
from datetime import datetime

# Load environment variables from .env file
from pathlib import Path
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from openai import AsyncOpenAI
from supabase import create_client

# Add the insights path
import sys
sys.path.append('/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/backend_rag_pipeline')

from insights.enhanced.business_insights_engine import BusinessInsightsEngine

# Sample business documents for testing
SAMPLE_DOCUMENTS = [
    {
        "id": "test_meeting_001",
        "title": "Q4 Project Status Meeting - December 2024",
        "content": """
        Meeting: Q4 Project Status Review
        Date: December 15, 2024
        Attendees: Sarah Johnson (PM), Mike Chen (Dev Lead), Lisa Rodriguez (Design), Tom Wilson (QA)
        
        Sarah Johnson: Let's start with the website redesign project. Mike, what's the current status?
        
        Mike Chen: We're about 70% complete with the backend API development. However, we've identified a critical security vulnerability in the authentication system that needs immediate attention. This could delay our launch by 2-3 weeks.
        
        Sarah Johnson: That's concerning. What's the financial impact of this delay?
        
        Mike Chen: Based on our contract with the client, we'll face a $50,000 penalty for missing the January 15th deadline. Plus we'll need to allocate an additional developer for 3 weeks at $8,000 per week.
        
        Lisa Rodriguez: From the design perspective, we've completed all mockups and prototypes. The client approved the final designs yesterday. No blockers on our end.
        
        Tom Wilson: QA testing has revealed 23 bugs so far, with 3 classified as critical path blockers. The user authentication flow is completely broken in the current build.
        
        Sarah Johnson: This sounds like we need to escalate to the steering committee. The client, TechCorp, is expecting a demo next week. We need to decide if we should inform them about the potential delay now or try to resolve it internally first.
        
        Mike Chen: I recommend we bring in Jennifer Lee from the security team immediately. She's available starting Monday and can help us resolve the authentication issues faster.
        
        Tom Wilson: Agreed. Also, we should consider implementing the security fix as a hotfix after launch rather than delaying the entire project.
        
        Sarah Johnson: That's risky. Let's schedule an emergency meeting with the CTO tomorrow to discuss our options. 
        
        ACTION ITEMS:
        - Mike to provide detailed security vulnerability report by COB today
        - Sarah to schedule emergency meeting with CTO for Friday 
        - Tom to prioritize critical path testing 
        - Lisa to prepare client communication strategy for potential delay
        
        DECISIONS MADE:
        - Bring in Jennifer Lee from security team starting Monday
        - Do not inform client of delay until we have a concrete resolution plan
        - Reassess timeline after security review on Monday
        """,
        "metadata": {
            "file_type": "transcript",
            "project_id": 12345,
            "created_at": "2024-12-15T14:30:00Z"
        }
    },
    {
        "id": "test_status_002", 
        "title": "Weekly Sales Report - Marketing Campaign Performance",
        "content": """
        Weekly Sales Performance Report
        Week Ending: December 20, 2024
        Prepared by: Marketing Analytics Team
        
        EXECUTIVE SUMMARY:
        Our Q4 marketing campaign has generated significant results, but we're seeing some concerning trends that require immediate attention.
        
        PERFORMANCE METRICS:
        - Total Revenue: $2.8M (target: $3.2M) - 12.5% below target
        - New Customer Acquisitions: 1,247 (target: 1,500) - 16.9% below target  
        - Customer Acquisition Cost (CAC): $127 (target: $95) - 33.7% above target
        - Conversion Rate: 2.3% (previous week: 3.1%) - declining trend
        - Email Campaign Open Rate: 18.2% (industry average: 24.1%)
        
        CRITICAL ISSUES IDENTIFIED:
        
        1. BUDGET OVERRUN ALERT: Our digital advertising spend has exceeded the quarterly budget by $180,000. The Google Ads campaign is burning through budget 40% faster than projected due to increased competition in our core keywords.
        
        2. CONVERSION FUNNEL BREAKDOWN: There's a significant drop-off at the pricing page (67% exit rate). Customer feedback indicates our pricing is 15-20% higher than competitors for similar services.
        
        3. SALES TEAM CAPACITY: With the current lead volume, our sales team is overwhelmed. Average response time to leads has increased from 2 hours to 8 hours, directly impacting conversion rates.
        
        IMMEDIATE ACTION REQUIRED:
        - Review and adjust Google Ads bidding strategy by December 23rd
        - Emergency pricing strategy meeting scheduled for December 21st  
        - Hire 2 additional sales reps or redistribute leads to prevent further degradation
        
        FINANCIAL IMPACT:
        If current trends continue, we'll miss Q4 revenue targets by approximately $800,000, which represents 15% of our annual growth target. This could affect our ability to secure Series B funding in Q1 2025.
        
        STAKEHOLDER IMPACT:
        - Investors expecting 25% QoQ growth will see only 12% 
        - Sales team morale declining due to impossible lead volumes
        - Marketing team under pressure to deliver results with reduced budget
        
        RECOMMENDATIONS:
        1. Immediate budget reallocation from underperforming channels
        2. Emergency hiring of 2 sales development reps  
        3. Pricing strategy review with competitive analysis
        4. Enhanced lead scoring to prioritize high-value prospects
        """,
        "metadata": {
            "file_type": "report",
            "project_id": 67890,
            "created_at": "2024-12-20T09:15:00Z"
        }
    }
]

async def test_enhanced_insights():
    """Test the enhanced business insights engine."""
    
    print("🔍 Checking environment variables...")
    
    # Check for environment variables
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
    
    print(f"   SUPABASE_URL: {'✅ Found' if SUPABASE_URL else '❌ Missing'}")
    print(f"   SUPABASE_SERVICE_KEY: {'✅ Found' if SUPABASE_SERVICE_KEY else '❌ Missing'}")
    print(f"   LLM_API_KEY: {'✅ Found' if api_key else '❌ Missing'}")
    
    if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, api_key]):
        print("\n❌ Missing required environment variables. Please ensure your .env file is configured.")
        print("Required variables:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_KEY (or SUPABASE_SERVICE_ROLE_KEY)")
        print("  - LLM_API_KEY (or OPENAI_API_KEY)")
        return
    
    try:
        # Create clients
        print("🔗 Initializing connections...")
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        openai_client = AsyncOpenAI(api_key=api_key)
        
        # Test database connection
        print("🗃️  Testing database connection...")
        test_result = supabase.table('document_insights').select('id').limit(1).execute()
        print("   ✅ Database connection successful")
        
        # Test OpenAI connection
        print("🤖 Testing OpenAI connection...")
        models = await openai_client.models.list()
        print(f"   ✅ OpenAI connection successful (found {len(models.data)} models)")
        
        # Initialize insights engine
        insights_engine = BusinessInsightsEngine(
            supabase=supabase,
            openai_client=openai_client
        )
        
        print(f"   ✅ Using model: {insights_engine.model}")
        
    except Exception as e:
        print(f"❌ Failed to initialize connections: {e}")
        return
    
    print("\n🚀 Testing Enhanced Business Insights Engine")
    print("=" * 60)
    
    total_insights = 0
    
    for i, doc in enumerate(SAMPLE_DOCUMENTS, 1):
        print(f"\n📄 Testing Document {i}: {doc['title']}")
        print("-" * 50)
        
        try:
            # Extract insights
            start_time = datetime.now()
            
            result = await insights_engine.process_document(
                document_id=doc['id'],
                content=doc['content'],
                title=doc['title'],
                metadata=doc['metadata']
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if result['success']:
                insights_count = result['insights_saved']
                total_insights += insights_count
                
                print(f"✅ Successfully processed document {doc['id']}")
                print(f"   📊 Insights extracted: {result['insights_extracted']}")
                print(f"   💾 Insights saved: {insights_count}")
                print(f"   ⏱️  Processing time: {processing_time:.2f} seconds")
                
                if result.get('insights_by_type'):
                    print(f"   📈 By type: {result['insights_by_type']}")
                
                if result.get('insights_by_severity'):
                    print(f"   🚨 By severity: {result['insights_by_severity']}")
                
                # Fetch and display a sample insight
                if insights_count > 0:
                    try:
                        sample_insight_result = supabase.table('document_insights')\
                            .select('*')\
                            .eq('document_id', doc['id'])\
                            .limit(1)\
                            .execute()
                        
                        if sample_insight_result.data:
                            insight = sample_insight_result.data[0]
                            print(f"\n   📋 Sample Insight:")
                            print(f"      Type: {insight['insight_type']}")
                            print(f"      Title: {insight['title']}")
                            print(f"      Severity: {insight['severity']}")
                            print(f"      Description: {insight['description'][:100]}...")
                            if insight.get('financial_impact'):
                                print(f"      Financial Impact: ${insight['financial_impact']:,.2f}")
                            if insight.get('assignee'):
                                print(f"      Assignee: {insight['assignee']}")
                    except Exception as e:
                        print(f"   ⚠️  Could not fetch sample insight: {e}")
                
            else:
                print(f"❌ Failed to process document {doc['id']}")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception processing document {doc['id']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Summary:")
    print(f"   Documents processed: {len(SAMPLE_DOCUMENTS)}")
    print(f"   Total insights generated: {total_insights}")
    print(f"   Average insights per document: {total_insights / len(SAMPLE_DOCUMENTS):.1f}")
    
    # Get overall system stats
    try:
        all_insights_result = supabase.table('document_insights')\
            .select('*', count='exact')\
            .execute()
        
        total_system_insights = all_insights_result.count or 0
        print(f"   Total system insights: {total_system_insights}")
        
        # Count by severity
        if all_insights_result.data:
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for insight in all_insights_result.data:
                severity = insight.get('severity', 'medium')
                if severity in severity_counts:
                    severity_counts[severity] += 1
            print(f"   Severity breakdown: {severity_counts}")
        
    except Exception as e:
        print(f"   ⚠️  Could not fetch system stats: {e}")
    
    print("\n✅ Enhanced insights testing completed!")
    print("\n🔗 Next steps:")
    print("   1. Start the API server: python insights_api.py")
    print("   2. Process existing documents: POST /insights/process-pending")
    print("   3. View insights: GET /api/enhanced-insights/insights")

if __name__ == "__main__":
    asyncio.run(test_enhanced_insights())
