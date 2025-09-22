#!/usr/bin/env python3
"""
Dry run to show which files would be processed in order.
"""

import os
import sys
from pathlib import Path
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Supabase_Storage'))

from dotenv import load_dotenv
load_dotenv()

from storage_watcher import SupabaseStorageWatcher

bucket_name = 'meetings'

print(f"DRY RUN - Processing files from '{bucket_name}' bucket")
print("=" * 60)

# Create config
config = {
    "supported_mime_types": ["application/pdf", "text/plain", "text/html", "text/csv", "text/markdown"],
    "text_processing": {"default_chunk_size": 400, "default_chunk_overlap": 0},
    "rate_limit": {"max_files_per_run": 5, "delay_between_files": 0.1},
    "meetings_bucket": bucket_name,
    "documents_bucket": bucket_name
}

# Save config temporarily
config_path = 'temp_dry_run_config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)

# Initialize watcher in DRY RUN mode
watcher = SupabaseStorageWatcher(config_path=config_path, dry_run=True)

# Get list of files from bucket
files_list = watcher.supabase.storage.from_(bucket_name).list()

# Filter and prepare files
files_to_process = []
for file_info in files_list:
    if file_info.get('metadata'):
        file_name = file_info.get('name', '')

        if file_name == 'transcripts':
            continue

        # Check if already processed
        file_id = f"{bucket_name}/{file_name}"
        existing = watcher.supabase.from_('documents') \
            .select('id') \
            .eq('file_id', file_id) \
            .limit(1) \
            .execute()

        if not existing.data:
            files_to_process.append(file_info)

# Sort by most recent first
def get_file_timestamp(file_info):
    updated_at = file_info.get('updated_at', '')
    created_at = file_info.get('created_at', '')
    return max(updated_at, created_at) if updated_at or created_at else ''

files_to_process.sort(key=get_file_timestamp, reverse=True)

print(f"\nFound {len(files_to_process)} files to process")
print("Files will be processed in this order (MOST RECENT FIRST):")
print("-" * 60)

# Show what would be processed
for i, file_info in enumerate(files_to_process[:10], 1):
    file_name = file_info.get('name', '')
    updated_at = file_info.get('updated_at', 'N/A')
    size = file_info.get('metadata', {}).get('size', 0) / 1024

    print(f"\n{i}. {file_name[:60]}")
    print(f"   Updated: {updated_at}")
    print(f"   Size: {size:.1f} KB")

    if i <= 5:
        print(f"   ✅ Would be processed (within first 5)")
    else:
        print(f"   ⏸️  Would wait for next batch")

# Clean up
os.remove(config_path)

print("\n" + "=" * 60)
print("This was a DRY RUN - no files were actually processed")
print("The files shown with ✅ would be processed first (most recent)")