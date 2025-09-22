#!/usr/bin/env python3
"""
Fix transcript documents that have file_id and source in metadata but not in columns.
"""

import os
import json
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

def fix_transcript_metadata():
    print("Fixing transcript document metadata")
    print("=" * 60)

    # Get all documents with transcript in metadata
    result = supabase.from_('documents') \
        .select('id, metadata, created_at') \
        .is_('file_id', 'null') \
        .execute()

    print(f"Found {len(result.data)} documents with null file_id")

    # Group by unique files
    unique_files = {}
    for doc in result.data:
        metadata = doc.get('metadata')
        if metadata:
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            file_id = metadata.get('file_id')
            file_title = metadata.get('file_title', metadata.get('source'))

            if file_id and 'transcript' in file_id:
                if file_id not in unique_files:
                    unique_files[file_id] = {
                        'docs': [],
                        'file_title': file_title
                    }
                unique_files[file_id]['docs'].append(doc['id'])

    print(f"Found {len(unique_files)} unique transcript files to fix")

    # Update each group
    fixed = 0
    for file_id, info in unique_files.items():
        file_title = info['file_title']
        doc_ids = info['docs']

        print(f"\nFixing: {file_title}")
        print(f"  File ID: {file_id}")
        print(f"  Chunks: {len(doc_ids)}")

        # Extract date from filename
        file_date = None
        if file_title and '20' in file_title:
            # Try to extract YYYY-MM-DD from filename
            parts = file_title.split('/')[-1] if '/' in file_title else file_title
            if parts.startswith('20'):
                file_date = parts[:10]

        # Update all chunks
        for doc_id in doc_ids:
            update_data = {
                'file_id': file_id,
                'source': file_title
            }
            if file_date:
                update_data['file_date'] = file_date

            try:
                supabase.from_('documents') \
                    .update(update_data) \
                    .eq('id', doc_id) \
                    .execute()
                fixed += 1
            except Exception as e:
                print(f"  Error updating {doc_id[:8]}...: {e}")

    print("\n" + "=" * 60)
    print(f"✅ Fixed {fixed} document chunks")

    # Verify the fix
    print("\nVerifying transcript documents...")
    result = supabase.from_('documents') \
        .select('file_id, source') \
        .like('file_id', '%transcript%') \
        .limit(5) \
        .execute()

    if result.data:
        print(f"Sample of fixed transcript documents:")
        for doc in result.data:
            print(f"  ✓ {doc['source'][:50]}...")

if __name__ == "__main__":
    fix_transcript_metadata()