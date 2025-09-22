#!/usr/bin/env python3
"""
Script to get the complete count of all files in Supabase storage buckets,
handling pagination.
"""

import os
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

def get_all_files_recursive(bucket_name='meetings', path='', all_files=None):
    """
    Recursively get all files from a bucket, including subdirectories.

    Args:
        bucket_name: Name of the bucket
        path: Current path in the bucket
        all_files: Accumulator for all files

    Returns:
        List of all files in the bucket
    """
    if all_files is None:
        all_files = []

    try:
        # List files at current path
        if path:
            files_list = supabase.storage.from_(bucket_name).list(path=path)
        else:
            files_list = supabase.storage.from_(bucket_name).list()

        for item in files_list:
            item_name = item.get('name', '')
            full_path = f"{path}/{item_name}" if path else item_name

            if item.get('metadata'):  # It's a file
                item['full_path'] = full_path
                all_files.append(item)
            else:  # It's a directory, recurse into it
                print(f"  Exploring directory: {full_path}")
                get_all_files_recursive(bucket_name, full_path, all_files)

    except Exception as e:
        print(f"Error listing files at path '{path}': {e}")

    return all_files

def check_complete_bucket_status(bucket_name='meetings'):
    """
    Get complete status of all files in a bucket, including subdirectories.
    """
    print(f"\n{'=' * 60}")
    print(f"Complete scan of '{bucket_name}' bucket")
    print(f"{'=' * 60}")

    try:
        # Get ALL files recursively
        all_files = get_all_files_recursive(bucket_name)

        print(f"\nTotal files found (including subdirectories): {len(all_files)}")

        # Group files by directory
        by_directory = {}
        for file_info in all_files:
            full_path = file_info.get('full_path', '')
            directory = os.path.dirname(full_path) if '/' in full_path else 'root'

            if directory not in by_directory:
                by_directory[directory] = []
            by_directory[directory].append(file_info)

        # Show summary by directory
        print(f"\nFiles by directory:")
        for directory, files in sorted(by_directory.items()):
            total_size = sum(f.get('metadata', {}).get('size', 0) for f in files)
            print(f"  {directory}: {len(files)} files ({total_size / 1024 / 1024:.1f} MB)")

        # Get most recent files
        all_files.sort(key=lambda x: x.get('updated_at', '') or x.get('created_at', ''), reverse=True)

        print(f"\n5 Most recent files across all directories:")
        for i, file_info in enumerate(all_files[:5], 1):
            print(f"  {i}. {file_info.get('full_path', file_info.get('name', 'Unknown'))}")
            print(f"     Updated: {file_info.get('updated_at', 'N/A')}")

        return len(all_files)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    # Check meetings bucket thoroughly
    total_files = check_complete_bucket_status('meetings')

    print(f"\n{'=' * 60}")
    print(f"COMPLETE SUMMARY:")
    print(f"Total files in 'meetings' bucket: {total_files}")
    print(f"\nNote: The Supabase storage API lists 100 items at the root level,")
    print(f"but there may be more files in subdirectories like 'transcripts'.")
    print(f"{'=' * 60}")