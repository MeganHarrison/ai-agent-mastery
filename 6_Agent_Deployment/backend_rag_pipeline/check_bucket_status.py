#!/usr/bin/env python3
"""
Script to check the status of all files in Supabase storage buckets.
Shows total count, processed vs unprocessed files.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def check_bucket_status(bucket_name='meetings'):
    """
    Check the status of files in a Supabase storage bucket.

    Args:
        bucket_name: Name of the bucket to check
    """
    print(f"\nChecking '{bucket_name}' bucket")
    print("=" * 60)

    try:
        # Get list of all files from bucket
        files_list = supabase.storage.from_(bucket_name).list()

        # Count actual files (skip directories)
        actual_files = []
        directories = []

        for file_info in files_list:
            if file_info.get('metadata'):  # It's a file
                actual_files.append(file_info)
            else:  # It's a directory
                directories.append(file_info.get('name', 'Unknown'))

        print(f"Total items in bucket: {len(files_list)}")
        print(f"Actual files: {len(actual_files)}")
        print(f"Directories: {len(directories)}")

        if directories:
            print(f"\nDirectories found: {', '.join(directories)}")

        # Check how many are already processed
        processed_count = 0
        unprocessed_files = []

        for file_info in actual_files:
            file_name = file_info.get('name', '')

            # Check if file is already in documents table
            existing = supabase.from_('documents') \
                .select('id') \
                .eq('source', file_name) \
                .limit(1) \
                .execute()

            if existing.data:
                processed_count += 1
            else:
                unprocessed_files.append({
                    'name': file_name,
                    'created_at': file_info.get('created_at', 'N/A'),
                    'updated_at': file_info.get('updated_at', 'N/A'),
                    'size': file_info.get('metadata', {}).get('size', 0)
                })

        print(f"\nProcessing Status:")
        print(f"  Processed files: {processed_count}")
        print(f"  Unprocessed files: {len(unprocessed_files)}")
        if len(actual_files) > 0:
            print(f"  Processing rate: {(processed_count / len(actual_files) * 100):.1f}%")
        else:
            print(f"  Processing rate: N/A (no files)")

        # Sort unprocessed files by updated_at (most recent first)
        unprocessed_files.sort(key=lambda x: x['updated_at'], reverse=True)

        # Show sample of unprocessed files
        if unprocessed_files:
            print(f"\nMost recent unprocessed files (top 10):")
            for i, file_info in enumerate(unprocessed_files[:10], 1):
                size_kb = file_info['size'] / 1024 if file_info['size'] else 0
                print(f"  {i}. {file_info['name'][:50]}")
                print(f"     Updated: {file_info['updated_at']}, Size: {size_kb:.1f} KB")

        # Check document_metadata table
        print("\n" + "=" * 60)
        print("Database Status:")

        # Count unique documents in documents table
        all_docs = supabase.from_('documents').select('metadata').execute()
        unique_docs = set()
        for doc in all_docs.data:
            metadata = doc.get('metadata', {})
            if isinstance(metadata, dict):
                file_id = metadata.get('file_id')
                file_title = metadata.get('file_title', metadata.get('source', 'Unknown'))
                unique_key = file_id if file_id else file_title
                unique_docs.add(unique_key)

        print(f"  Documents table: {len(all_docs.data)} chunks from {len(unique_docs)} unique documents")

        # Count document_metadata table
        metadata_result = supabase.from_('document_metadata').select('id', count='exact').execute()
        print(f"  Document_metadata table: {metadata_result.count if hasattr(metadata_result, 'count') else len(metadata_result.data)} rows")

        # Get recent document_metadata entries
        recent_metadata = supabase.from_('document_metadata') \
            .select('id, title, created_at') \
            .order('created_at', desc=True) \
            .limit(5) \
            .execute()

        if recent_metadata.data:
            print(f"\nMost recent document_metadata entries:")
            for meta in recent_metadata.data:
                print(f"  - {meta.get('title', 'Unknown')[:50]}")
                print(f"    ID: {meta.get('id')[:20]}... Created: {meta.get('created_at')}")

        return len(actual_files), processed_count, len(unprocessed_files)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0, 0

if __name__ == "__main__":
    # Check both buckets
    for bucket in ['meetings', 'documents']:
        total, processed, unprocessed = check_bucket_status(bucket)

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"To process all unprocessed files in 'meetings' bucket:")
    print(f"  cd backend_rag_pipeline")
    print(f"  python process_all_bucket_files.py --bucket meetings")
    print(f"\nFiles will be processed in reverse chronological order (most recent first)")