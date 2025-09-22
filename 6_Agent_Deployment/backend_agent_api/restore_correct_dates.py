#!/usr/bin/env python3
"""
EMERGENCY FIX: Restore the correct 2025 dates that were mistakenly changed to 2024.
It's currently 2025-09-22, not 2024!
"""

import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def restore_correct_dates():
    """Restore documents that were incorrectly changed from 2025 to 2024."""

    print("RESTORING CORRECT 2025 DATES")
    print("Current actual date: 2025-09-22")
    print("-" * 50)

    try:
        # Find documents with 2024-09-22 dates (these were incorrectly changed)
        wrong_docs = supabase.from_('documents') \
            .select('id, created_at') \
            .gte('created_at', '2024-09-22T00:00:00') \
            .lt('created_at', '2024-09-23T00:00:00') \
            .execute()

        if wrong_docs.data:
            print(f"Found {len(wrong_docs.data)} documents to restore to 2025")

            for doc in wrong_docs.data:
                doc_id = doc['id']
                old_date = doc['created_at']

                # Convert 2024 back to 2025 (restore the correct date)
                wrong_dt = datetime.fromisoformat(old_date.replace('Z', '+00:00'))
                correct_dt = wrong_dt.replace(year=2025)

                # Update the document back to the correct date
                update_result = supabase.from_('documents') \
                    .update({'created_at': correct_dt.isoformat()}) \
                    .eq('id', doc_id) \
                    .execute()

                print(f"Restored document {doc_id}: {old_date} -> {correct_dt.isoformat()}")
        else:
            print("No documents found to restore")

        print("\n✅ Date restoration complete! Documents are now correctly dated for 2025.")

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("DATE RESTORATION SCRIPT - FIXING MY MISTAKE")
    print("=" * 50)
    restore_correct_dates()