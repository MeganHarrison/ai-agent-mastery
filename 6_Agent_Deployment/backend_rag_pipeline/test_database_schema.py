#!/usr/bin/env python3
"""
Simple Database Schema Test

Quick test to determine if you need to run SQL to add meeting date columns.
"""

import json

def create_test_insight():
    """Create a sample insight with the new date fields."""
    
    test_insight = {
        'document_id': 'test_doc_123',
        'project_id': 12345,
        'insight_type': 'action_item',
        'title': 'Test insight with meeting date',
        'description': 'This is a test insight to verify the database schema supports meeting dates',
        'confidence_score': 0.9,
        'generated_by': 'gpt-4o-mini',
        'doc_title': 'Test Meeting - September 23, 2024',
        'severity': 'medium',
        'business_impact': 'Test business impact',
        'assignee': None,
        'due_date': None,
        'financial_impact': None,
        'urgency_indicators': [],
        'resolved': False,
        # NEW DATE FIELDS - These are what we need to check
        'document_date': '2024-09-23',  # When meeting occurred
        'meeting_date': '2024-09-23',   # Alias for document_date
        'source_meetings': [],
        'dependencies': [],
        'stakeholders_affected': [],
        'exact_quotes': [],
        'numerical_data': None,
        'critical_path_impact': False,
        'cross_project_impact': [],
        'metadata': {'test': True},
        'created_at': '2024-09-23T12:00:00Z'
    }
    
    return test_insight

if __name__ == "__main__":
    print("🧪 **DATABASE SCHEMA TEST PREPARATION**")
    print("=" * 60)
    
    test_data = create_test_insight()
    
    print("📋 **Test Insight Data Prepared:**")
    for key, value in test_data.items():
        if key in ['document_date', 'meeting_date']:
            print(f"   🆕 {key}: {value}")
        else:
            print(f"   ✅ {key}: {str(value)[:50]}...")
    
    print(f"\n🎯 **TO TEST YOUR DATABASE:**")
    print("1. Open your Python environment with Supabase installed")
    print("2. Try to insert this test record:")
    print()
    print("```python")
    print("from supabase import create_client")
    print("import os")
    print()
    print("supabase = create_client(")
    print("    os.getenv('SUPABASE_URL'),")
    print("    os.getenv('SUPABASE_SERVICE_KEY')")
    print(")")
    print()
    print("# Try to insert test record")
    print("try:")
    print("    result = supabase.table('document_insights').insert({")
    for key, value in test_data.items():
        if isinstance(value, str):
            print(f"        '{key}': '{value}',")
        else:
            print(f"        '{key}': {value},")
    print("    }).execute()")
    print("    print('✅ SUCCESS: Database accepts new date fields!')")
    print("    print(f'Created insight ID: {result.data[0][\"id\"]}')")
    print("except Exception as e:")
    print("    if 'column \"document_date\" does not exist' in str(e):")
    print("        print('❌ NEED SQL: document_date column missing')")
    print("    elif 'column \"meeting_date\" does not exist' in str(e):")  
    print("        print('❌ NEED SQL: meeting_date column missing')")
    print("    else:")
    print("        print(f'❌ OTHER ERROR: {e}')")
    print("```")
    
    print(f"\n🛠️ **IF YOU GET COLUMN ERRORS, RUN THIS SQL:**")
    print("```sql")
    print("ALTER TABLE document_insights")
    print("ADD COLUMN IF NOT EXISTS document_date DATE,")
    print("ADD COLUMN IF NOT EXISTS meeting_date DATE;")
    print("```")
    
    print(f"\n💡 **TIP:**")
    print("The easiest way is to check your Supabase dashboard:")
    print("1. Go to Table Editor -> document_insights")  
    print("2. Look for 'document_date' and 'meeting_date' columns")
    print("3. If missing, use SQL Editor to add them")
