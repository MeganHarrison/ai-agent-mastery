#!/usr/bin/env python3
"""
Test script to verify files will be processed in most recent first order.
"""

import os
import sys
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

bucket_name = 'meetings'

# Get list of files from bucket
files_list = supabase.storage.from_(bucket_name).list()

# Filter out directories
files_to_process = []
for file_info in files_list:
    if file_info.get('metadata'):  # Skip directories
        file_name = file_info.get('name', '')

        # Skip transcripts directory
        if file_name == 'transcripts':
            continue

        # Check if already processed
        file_id = f"{bucket_name}/{file_name}"
        existing = supabase.from_('documents') \
            .select('id') \
            .eq('file_id', file_id) \
            .limit(1) \
            .execute()

        if not existing.data:
            files_to_process.append(file_info)

# Sort files by updated_at or created_at in DESCENDING order (most recent first)
def get_file_timestamp(file_info):
    updated_at = file_info.get('updated_at', '')
    created_at = file_info.get('created_at', '')
    return max(updated_at, created_at) if updated_at or created_at else ''

files_to_process.sort(key=get_file_timestamp, reverse=True)

print(f"Files to be processed (sorted by MOST RECENT first):")
print("=" * 70)
print(f"Total unprocessed files: {len(files_to_process)}")
print("-" * 70)

# Show first 10 and last 5
if files_to_process:
    print("\nFIRST 10 files (MOST RECENT - will be processed first):")
    for i, file_info in enumerate(files_to_process[:10], 1):
        name = file_info.get('name', 'Unknown')[:50]
        updated = file_info.get('updated_at', 'N/A')
        print(f"{i:2}. {name:50} | Updated: {updated}")

    if len(files_to_process) > 10:
        print("\n...")
        print(f"\nLAST 5 files (OLDEST - will be processed last):")
        for i, file_info in enumerate(files_to_process[-5:], len(files_to_process)-4):
            name = file_info.get('name', 'Unknown')[:50]
            updated = file_info.get('updated_at', 'N/A')
            print(f"{i:2}. {name:50} | Updated: {updated}")
else:
    print("No unprocessed files found!")

print("\n" + "=" * 70)
print("To process these files in this order, run:")
print("  python process_all_bucket_files.py --bucket meetings")