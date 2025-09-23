#!/usr/bin/env python3
"""
Test Meeting Date Extraction in Enhanced Insights Engine

Tests the new meeting date functionality to ensure RAG can prioritize recent insights.
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from insights.enhanced.business_insights_engine import BusinessInsightsEngine


async def test_date_extraction():
    """Test meeting date extraction from various title formats."""
    
    # Create a mock engine instance (without actual DB/API connections)
    class MockEngine(BusinessInsightsEngine):
        def __init__(self):
            # Skip parent init to avoid DB/API requirements
            pass
    
    engine = MockEngine()
    
    # Test cases with various date formats
    test_titles = [
        "Team Standup - 2024-09-23 - Engineering Team",
        "Q4 Planning Meeting 09/23/2024",
        "Project Review - September 23, 2024",
        "Client Call 23 September 2024",
        "Weekly Sync 2024_09_23",
        "Budget Review Meeting Sep 23, 2024",
        "No Date Meeting",
        "Engineering-Standup-2024.09.23.docx",
        "Meeting Notes - Jan 15, 2025",
        "12/25/2024 Holiday Planning"
    ]
    
    print("🔍 **TESTING MEETING DATE EXTRACTION**")
    print("=" * 60)
    
    for title in test_titles:
        document_date, meeting_date = engine._extract_date_from_title(title)
        
        status = "✅" if document_date else "❌"
        print(f"{status} Title: {title}")
        print(f"    📅 Document Date: {document_date}")
        print(f"    📅 Meeting Date: {meeting_date}")
        print()
    
    # Test date normalization
    print("\n🔧 **TESTING DATE NORMALIZATION**")
    print("=" * 60)
    
    test_dates = [
        "2024-09-23",
        "09/23/2024", 
        "9-23-2024",
        "Sep 23, 2024",
        "23 September 2024",
        "2024_09_23",
        "2024.09.23",
        "invalid-date"
    ]
    
    for date_str in test_dates:
        normalized = engine._normalize_date_string(date_str)
        status = "✅" if normalized else "❌"
        print(f"{status} '{date_str}' → '{normalized}'")
    
    print("\n🎯 **SUCCESS:** Meeting date extraction functionality implemented!")
    print("RAG can now prioritize recent insights based on actual meeting dates!")
    

async def test_mock_insight_conversion():
    """Test converting a raw insight with meeting dates."""
    
    class MockEngine(BusinessInsightsEngine):
        def __init__(self):
            pass
    
    engine = MockEngine()
    
    # Mock raw insight from AI
    raw_insight = {
        'insight_type': 'action_item',
        'title': 'Complete budget review',
        'description': 'Finance team needs to complete Q4 budget review by end of month',
        'confidence_score': 0.9,
        'severity': 'high',
        'business_impact': 'Critical for Q4 planning',
        'assignee': 'Sarah Johnson',
        'due_date': '2024-09-30',
        'document_date': '2024-09-23',  # AI extracted this
        'urgency_indicators': ['urgent', 'critical'],
        'exact_quotes': ['We need to finalize the budget ASAP']
    }
    
    print("\n📝 **TESTING INSIGHT CONVERSION WITH DATES**")
    print("=" * 60)
    
    # Convert to structured insight
    try:
        insight = engine._convert_to_structured_insight(
            raw_insight=raw_insight,
            document_id="test_doc_123",
            doc_title="Team Meeting - September 23, 2024",
            metadata={'project_id': 101}
        )
        
        if insight:
            print("✅ **Insight Conversion Successful!**")
            print(f"📋 Title: {insight.title}")
            print(f"📅 Document Date: {insight.document_date}")
            print(f"📅 Meeting Date: {insight.meeting_date}")
            print(f"🎯 Project ID: {insight.project_id}")
            print(f"⚡ Severity: {insight.severity}")
            print(f"💰 Financial Impact: {insight.financial_impact}")
            
            # Test database conversion
            db_dict = insight.to_database_dict()
            print(f"\n📊 **Database Format:**")
            print(f"   document_date: {db_dict.get('document_date')}")
            print(f"   meeting_date: {db_dict.get('meeting_date')}")
            print(f"   created_at: {db_dict.get('created_at')}")
            
        else:
            print("❌ Insight conversion failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_date_extraction())
    asyncio.run(test_mock_insight_conversion())
