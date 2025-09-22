#!/usr/bin/env python3
"""
Script to process all files in the transcripts subfolder of the meetings bucket.
These are the most recent files (2025).
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the backend_rag_pipeline to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Supabase_Storage'))

from dotenv import load_dotenv
load_dotenv()

def process_transcript_files(force_reprocess=False):
    """
    Process all files in the transcripts subfolder.

    Args:
        force_reprocess: If True, reprocess even already processed files
    """
    print(f"Processing files from 'meetings/transcripts' folder")
    print("=" * 60)

    try:
        # Import storage watcher
        from storage_watcher import SupabaseStorageWatcher

        # Create config for the watcher
        config = {
            "supported_mime_types": [
                "application/pdf",
                "text/plain",
                "text/html",
                "text/csv",
                "text/markdown",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/json",
                "audio/mpeg",
                "audio/wav",
                "application/x-transcript",
                "video/mp4",
                "video/webm"
            ],
            "text_processing": {
                "default_chunk_size": 400,
                "default_chunk_overlap": 0,
                "min_chunk_size": 100,
                "max_chunk_size": 1000
            },
            "rate_limit": {
                "max_files_per_run": 500,
                "delay_between_files": 0.1
            },
            "meetings_bucket": "meetings",
            "documents_bucket": "meetings",
            "backfill": {
                "enabled": True,
                "batch_size": 50,
                "initial_delay": 1
            }
        }

        # Save config temporarily
        config_path = 'temp_transcripts_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Initialize watcher
        watcher = SupabaseStorageWatcher(
            config_path=config_path,
            dry_run=False
        )

        # Get list of files from transcripts subfolder
        files_list = watcher.supabase.storage.from_('meetings').list(path='transcripts')

        # Process each file
        files_to_process = []
        for file_info in files_list:
            if file_info.get('metadata'):  # Skip directories
                file_name = file_info.get('name', '')
                full_path = f"transcripts/{file_name}"

                # Check if already processed (unless force_reprocess is True)
                if not force_reprocess:
                    # Use the full path as file_id
                    file_id = f"meetings/{full_path}"
                    existing = watcher.supabase.from_('documents') \
                        .select('id') \
                        .eq('file_id', file_id) \
                        .limit(1) \
                        .execute()

                    if existing.data:
                        print(f"⏭️  Skipping (already processed): {file_name}")
                        continue

                # Add full path to file_info
                file_info['name'] = full_path
                file_info['bucket'] = 'meetings'
                files_to_process.append(file_info)

        # Sort by date in filename (2025-09-xx files first)
        def get_file_date(file_info):
            name = file_info.get('name', '')
            # Extract date from filename if it starts with YYYY-MM-DD
            if '/' in name:
                name = name.split('/')[-1]
            if name.startswith('20'):
                return name[:10]
            return '0000-00-00'

        files_to_process.sort(key=get_file_date, reverse=True)

        print(f"\nFound {len(files_to_process)} transcript files to process")
        print("-" * 60)

        if files_to_process and len(files_to_process) > 0:
            first_file = files_to_process[0]
            last_file = files_to_process[-1]
            print(f"First file: {first_file.get('name', 'Unknown')}")
            if len(files_to_process) > 1:
                print(f"Last file: {last_file.get('name', 'Unknown')}")
            print("-" * 60)

        # Process each file
        processed_count = 0
        error_count = 0

        for i, file_info in enumerate(files_to_process, 1):
            file_name = file_info.get('name', '')
            file_size = file_info.get('metadata', {}).get('size', 0)

            print(f"\n[{i}/{len(files_to_process)}] Processing: {file_name}")
            print(f"  Size: {file_size / 1024:.1f} KB")

            try:
                # Process the file
                if watcher.process_file(file_info):
                    processed_count += 1
                    print(f"  ✅ Successfully processed")
                else:
                    error_count += 1
                    print(f"  ❌ Failed to process")

            except Exception as e:
                error_count += 1
                print(f"  ❌ Error: {e}")
                continue

        # Clean up temp config
        if os.path.exists(config_path):
            os.remove(config_path)

        # Summary
        print("\n" + "=" * 60)
        print("Processing Complete!")
        print(f"✅ Successfully processed: {processed_count} files")
        print(f"❌ Errors: {error_count} files")

        # Update the watcher state
        watcher.save_state()

        return processed_count, error_count

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process transcript files from meetings/transcripts folder')
    parser.add_argument('--force', action='store_true',
                        help='Force reprocess even if files are already processed')

    args = parser.parse_args()

    # Process the files
    processed, errors = process_transcript_files(
        force_reprocess=args.force
    )

    # Exit with appropriate code
    if errors > 0:
        sys.exit(1)
    sys.exit(0)