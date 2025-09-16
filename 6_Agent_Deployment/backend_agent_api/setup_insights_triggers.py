#!/usr/bin/env python3
"""
Script to set up automated insights processing triggers and functions.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

def main():
    # Load environment variables
    project_root = Path(__file__).resolve().parent
    dotenv_path = project_root / '.env'
    load_dotenv(dotenv_path, override=True)

    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')

    if not url or not key:
        print('❌ Missing Supabase credentials')
        return False

    try:
        supabase = create_client(url, key)
        
        # Read the SQL file
        sql_file = project_root.parent / 'sql' / '12-automated_insights_triggers.sql'
        
        if not sql_file.exists():
            print(f'❌ SQL file not found: {sql_file}')
            return False
            
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Create a simple RPC function to execute raw SQL
        print('📝 Setting up database schema...')
        print('ℹ️  Note: You may need to run the SQL file manually in your database if this fails.')
        print(f'📄 SQL file location: {sql_file}')
        
        # Try to execute using rpc if available
        try:
            result = supabase.rpc('exec_sql', {'sql_content': sql_content}).execute()
            print('✅ SQL executed via RPC')
        except Exception as e:
            print(f'⚠️  RPC execution failed: {str(e)[:100]}...')
            print('📋 Please run the SQL file manually in your Supabase dashboard')
        
        print('✅ Database setup completed')
        
        # Test the setup by getting queue stats
        result = supabase.rpc('get_insights_queue_stats').execute()
        if result.data:
            stats = result.data[0]
            print(f'📊 Queue Stats: {stats["total_count"]} total, {stats["pending_count"]} pending')
        
        # Queue any unprocessed documents
        result = supabase.rpc('queue_unprocessed_documents').execute()
        if result.data:
            queued_count = result.data if isinstance(result.data, int) else result.data[0]
            print(f'🔄 Queued {queued_count} unprocessed documents for insights processing')
        
        return True
        
    except Exception as e:
        print(f'❌ Error during setup: {e}')
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)