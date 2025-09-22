#!/usr/bin/env python3
"""
Fix the remaining documents that weren't updated in the first pass,
specifically the Superior Beverage and ArcEdge documents.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json
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

def update_remaining_documents():
    """Update documents that still have None in critical fields."""

    print("Updating Remaining Documents")
    print("=" * 60)

    try:
        # Get all documents with missing source or file_id
        result = supabase.from_('documents') \
            .select('id, metadata, created_at') \
            .or_('source.is.null,file_id.is.null,file_date.is.null') \
            .execute()

        if not result.data:
            print("No documents need updating")
            return

        print(f"Found {len(result.data)} documents needing updates")

        # Group by unique documents
        unique_docs = {}
        for doc in result.data:
            metadata = doc.get('metadata')

            # Parse metadata if it's a string
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            elif metadata is None:
                metadata = {}

            # Get file info from metadata
            file_id = metadata.get('file_id')
            file_title = metadata.get('file_title', metadata.get('source', 'Unknown'))

            unique_key = file_id if file_id else file_title

            if unique_key not in unique_docs:
                unique_docs[unique_key] = {
                    'file_id': file_id,
                    'file_title': file_title,
                    'docs': []
                }

            unique_docs[unique_key]['docs'].append(doc['id'])

        print(f"Processing {len(unique_docs)} unique documents")
        print("-" * 60)

        # Update each group
        updates_made = 0
        for unique_key, info in unique_docs.items():
            file_id = info['file_id']
            file_title = info['file_title']

            # Use created_at as default date (convert to date only)
            # We'll use the first doc's created_at
            first_doc_id = info['docs'][0]
            for doc in result.data:
                if doc['id'] == first_doc_id:
                    default_date = doc['created_at'][:10]  # YYYY-MM-DD
                    break

            print(f"\nUpdating: {file_title}")
            print(f"  File ID: {file_id}")
            print(f"  Chunks: {len(info['docs'])}")

            # Update all chunks for this document
            for doc_id in info['docs']:
                update_data = {
                    'source': file_title,
                    'file_date': default_date
                }

                if file_id:
                    update_data['file_id'] = file_id

                try:
                    supabase.from_('documents') \
                        .update(update_data) \
                        .eq('id', doc_id) \
                        .execute()
                    updates_made += 1
                except Exception as e:
                    print(f"  Error updating {doc_id[:8]}...: {e}")

        print("\n" + "=" * 60)
        print(f"✅ Updated {updates_made} document chunks")

        # Verify Superior Beverage specifically
        print("\nVerifying Superior Beverage and ArcEdge documents...")

        # Check by searching in all documents
        all_docs = supabase.from_('documents') \
            .select('source, file_date, file_id') \
            .not_.is_('source', 'null') \
            .execute()

        superior_found = False
        arc_found = False

        for doc in all_docs.data:
            if doc.get('source'):
                if 'Superior Beverage' in doc['source'] and not superior_found:
                    print(f"\n✓ Superior Beverage: {doc['source']}")
                    print(f"  Date: {doc['file_date']}")
                    print(f"  ID: {doc['file_id']}")
                    superior_found = True
                elif 'ArcEdge' in doc['source'] and not arc_found:
                    print(f"\n✓ ArcEdge: {doc['source']}")
                    print(f"  Date: {doc['file_date']}")
                    print(f"  ID: {doc['file_id']}")
                    arc_found = True

        if not superior_found:
            print("\n⚠️  Superior Beverage documents not found in source column")
        if not arc_found:
            print("\n⚠️  ArcEdge documents not found in source column")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    update_remaining_documents()