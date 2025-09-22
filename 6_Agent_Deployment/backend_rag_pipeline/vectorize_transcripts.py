#!/usr/bin/env python3
"""
Direct script to vectorize all transcript files.
"""

import os
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Supabase_Storage'))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
from common.text_processor import extract_text_from_file, chunk_text, create_embeddings
from common.db_handler import process_file_for_rag

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(supabase_url, supabase_key)

def main():
    print("Vectorizing transcript files")
    print("=" * 60)

    # Get all transcript files
    files = supabase.storage.from_('meetings').list(path='transcripts')

    # Filter actual files
    transcript_files = []
    for f in files:
        if f.get('metadata'):
            name = f.get('name', '')
            # Only process 2025 files and recent 2024 files
            if '2025' in name or '2024-11' in name or '2024-12' in name:
                transcript_files.append({
                    'name': name,
                    'full_path': f'transcripts/{name}',
                    'metadata': f.get('metadata', {})
                })

    # Sort by name (which contains date)
    transcript_files.sort(key=lambda x: x['name'], reverse=True)

    print(f"Found {len(transcript_files)} recent transcript files to process")
    print("-" * 60)

    processed = 0
    errors = 0

    for i, file_info in enumerate(transcript_files, 1):
        name = file_info['name']
        full_path = file_info['full_path']

        print(f"\n[{i}/{len(transcript_files)}] Processing: {name[:60]}")

        # Check if already processed
        file_id = f"meetings/{full_path}"
        existing = supabase.from_('documents').select('id').eq('file_id', file_id).limit(1).execute()

        if existing.data:
            print("  ⏭️ Already processed")
            continue

        try:
            # Download file
            print("  📥 Downloading...")
            file_content = supabase.storage.from_('meetings').download(full_path)

            if not file_content:
                print("  ❌ Failed to download")
                errors += 1
                continue

            # Extract text
            print("  📝 Extracting text...")
            text = extract_text_from_file(file_content, 'text/markdown', full_path)

            if not text:
                print("  ❌ No text extracted")
                errors += 1
                continue

            # Process for RAG
            print("  🔄 Vectorizing...")
            file_url = supabase.storage.from_('meetings').get_public_url(full_path)

            config = {
                'text_processing': {
                    'default_chunk_size': 400,
                    'default_chunk_overlap': 0
                }
            }

            success = process_file_for_rag(
                file_content=file_content,
                text=text,
                file_id=file_id,
                file_url=file_url,
                file_title=name,
                mime_type='text/markdown',
                config=config
            )

            if success:
                processed += 1
                print("  ✅ Success!")
            else:
                errors += 1
                print("  ❌ Failed to process")

        except Exception as e:
            errors += 1
            print(f"  ❌ Error: {e}")

    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"✅ Processed: {processed} files")
    print(f"❌ Errors: {errors} files")

if __name__ == "__main__":
    main()