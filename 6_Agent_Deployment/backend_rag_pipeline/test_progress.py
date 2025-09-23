"""
Test script for Enhanced Business Insights Engine with Progress Monitoring

Run this script to test the enhanced insights system with sample business documents.
"""

import asyncio
import os
import json
from datetime import datetime
import time

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

# Sample business document for testing (shorter version)
SAMPLE_DOC = {
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
}

async def test_enhanced_insights_with_progress():
    """Test the enhanced business insights engine with progress monitoring."""
    
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
    
    doc = SAMPLE_DOC
    
    print(f"\n📄 Testing Document: {doc['title']}")
    print("-" * 50)
    print(f"📝 Content length: {len(doc['content'])} characters")
    
    try:
        # Step 1: Document Analysis
        print("\n🔍 Step 1: Analyzing document type...")
        start_time = time.time()
        
        doc_analysis = await insights_engine._analyze_document_type(
            doc['content'], doc['title'], doc['metadata']
        )
        
        analysis_time = time.time() - start_time
        print(f"   ⏱️  Analysis completed in {analysis_time:.2f} seconds")
        print(f"   📋 Document type: {doc_analysis.get('document_type', 'unknown')}")
        print(f"   🏢 Business domain: {doc_analysis.get('business_domain', 'unknown')}")
        print(f"   🚨 Urgency level: {doc_analysis.get('urgency_level', 'unknown')}")
        print(f"   👥 Key stakeholders: {doc_analysis.get('key_stakeholders', [])}")
        
        # Step 2: Extract Insights
        print("\n🧠 Step 2: Extracting business insights with GPT-5...")
        print("   ⚡ This may take 15-30 seconds for GPT-5 processing...")
        
        start_time = time.time()
        
        insights = await insights_engine.extract_business_insights(
            document_id=doc['id'],
            content=doc['content'],
            title=doc['title'],
            metadata=doc['metadata']
        )
        
        extraction_time = time.time() - start_time
        print(f"   ⏱️  Extraction completed in {extraction_time:.2f} seconds")
        print(f"   📊 Raw insights found: {len(insights)}")
        
        if insights:
            print("\n   📋 Sample insights extracted:")
            for i, insight in enumerate(insights[:3], 1):  # Show first 3
                print(f"      {i}. {insight.insight_type}: {insight.title}")
                print(f"         Severity: {insight.severity}")
                print(f"         Confidence: {insight.confidence_score:.2f}")
                if insight.financial_impact:
                    print(f"         Financial Impact: ${insight.financial_impact}")
                print()
        
        # Step 3: Save to Database
        print("💾 Step 3: Saving insights to database...")
        start_time = time.time()
        
        saved_ids = await insights_engine.save_insights_to_database(insights)
        
        save_time = time.time() - start_time
        print(f"   ⏱️  Save completed in {save_time:.2f} seconds")
        print(f"   💾 Insights saved: {len(saved_ids)}")
        
        # Step 4: Verify in Database
        print("\n🔍 Step 4: Verifying saved insights...")
        
        db_insights = supabase.table('document_insights')\
            .select('*')\
            .eq('document_id', doc['id'])\
            .execute()
        
        print(f"   ✅ Found {len(db_insights.data or [])} insights in database")
        
        if db_insights.data:
            sample_insight = db_insights.data[0]
            print(f"\n   📋 Sample Database Insight:")
            print(f"      ID: {sample_insight['id']}")
            print(f"      Type: {sample_insight['insight_type']}")
            print(f"      Title: {sample_insight['title']}")
            print(f"      Severity: {sample_insight['severity']}")
            print(f"      Confidence: {sample_insight['confidence_score']}")
            if sample_insight.get('business_impact'):
                print(f"      Business Impact: {sample_insight['business_impact'][:100]}...")
        
        print(f"\n✅ Test completed successfully!")
        
        total_time = analysis_time + extraction_time + save_time
        print(f"📊 Performance Summary:")
        print(f"   Analysis: {analysis_time:.2f}s")
        print(f"   Extraction: {extraction_time:.2f}s") 
        print(f"   Database save: {save_time:.2f}s")
        print(f"   Total: {total_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Exception during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_insights_with_progress())
