#!/usr/bin/env python3
"""
Script to fix future-dated documents in the database.
This will update documents with dates in the future to have more reasonable dates.
"""

import os
from datetime import datetime, timedelta
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

def fix_future_dates():
    """Fix documents with future dates in the database."""

    # Get current date
    now = datetime.now()

    print(f"Current date: {now.strftime('%Y-%m-%d')}")
    print("-" * 50)

    # Query documents with future dates
    print("Fetching documents with future dates...")

    try:
        # Get all documents with created_at in the future
        future_docs = supabase.from_('documents') \
            .select('id, metadata, created_at') \
            .gt('created_at', now.isoformat()) \
            .execute()

        if future_docs.data:
            print(f"Found {len(future_docs.data)} documents with future dates")

            # Update each document with a corrected date
            for doc in future_docs.data:
                doc_id = doc['id']
                old_date = doc['created_at']

                # Convert the future date to a past date (e.g., 2024 instead of 2025)
                future_dt = datetime.fromisoformat(old_date.replace('Z', '+00:00'))

                # Replace year 2025 with 2024
                if future_dt.year == 2025:
                    new_dt = future_dt.replace(year=2024)
                else:
                    # For other future years, set to 30 days ago
                    new_dt = now - timedelta(days=30)

                # Update the document
                update_result = supabase.from_('documents') \
                    .update({'created_at': new_dt.isoformat()}) \
                    .eq('id', doc_id) \
                    .execute()

                print(f"Updated document {doc_id}: {old_date} -> {new_dt.isoformat()}")
        else:
            print("No documents with future dates found")

        # Also check document_metadata table
        print("\nChecking document_metadata table...")
        future_metadata = supabase.from_('document_metadata') \
            .select('id, document_metadata, created_at') \
            .gt('created_at', now.isoformat()) \
            .execute()

        if future_metadata.data:
            print(f"Found {len(future_metadata.data)} metadata entries with future dates")

            for meta in future_metadata.data:
                meta_id = meta['id']
                old_date = meta['created_at']
                metadata_obj = meta.get('document_metadata', {})

                # Convert the future date
                future_dt = datetime.fromisoformat(old_date.replace('Z', '+00:00'))
                if future_dt.year == 2025:
                    new_dt = future_dt.replace(year=2024)
                else:
                    new_dt = now - timedelta(days=30)

                # Update created_at
                update_result = supabase.from_('document_metadata') \
                    .update({'created_at': new_dt.isoformat()}) \
                    .eq('id', meta_id) \
                    .execute()

                # If metadata contains meeting_date, update that too
                if metadata_obj and 'meeting_date' in metadata_obj:
                    meeting_date = metadata_obj['meeting_date']
                    if '2025' in meeting_date:
                        new_meeting_date = meeting_date.replace('2025', '2024')
                        metadata_obj['meeting_date'] = new_meeting_date

                        # Update the metadata JSON
                        supabase.from_('document_metadata') \
                            .update({'document_metadata': metadata_obj}) \
                            .eq('id', meta_id) \
                            .execute()

                        print(f"Updated metadata {meta_id}: meeting_date {meeting_date} -> {new_meeting_date}")

                print(f"Updated metadata {meta_id}: {old_date} -> {new_dt.isoformat()}")
        else:
            print("No metadata entries with future dates found")

        print("\n✅ Date correction complete!")

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Future Date Correction Script")
    print("=" * 50)
    fix_future_dates()