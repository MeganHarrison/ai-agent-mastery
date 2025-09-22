#!/usr/bin/env python3
"""
Script to properly organize document metadata:
1. Extract meeting dates from content and save to file_date column
2. Save file titles to source column
3. Save Google Drive IDs to file_id column
"""

import os
import re
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def extract_date_from_content(content: str, file_title: str) -> str:
    """
    Extract meeting date from document content or title.
    Returns ISO format date string or None.
    """
    # Check title first for dates like "2024-10-22 - Meeting Name"
    title_date_pattern = r'(\d{4}-\d{2}-\d{2})'
    title_match = re.search(title_date_pattern, file_title)
    if title_match:
        return title_match.group(1)

    # Common date patterns to search for in content
    date_patterns = [
        # ISO format: 2024-10-22
        (r'(\d{4}-\d{2}-\d{2})', lambda x: x),
        # US format: 10/22/2024 or 10-22-2024
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', lambda m: f"{m[2]}-{m[0]:0>2}-{m[1]:0>2}"),
        # Month name: October 22, 2024 or Oct 22, 2024
        (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2}),? (\d{4})',
         lambda m: convert_month_date(m)),
        # Meeting Date: followed by date
        (r'[Mm]eeting [Dd]ate:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
         lambda m: convert_us_date(m[0])),
    ]

    # Search for dates in first 2000 characters
    search_content = content[:2000] if len(content) > 2000 else content

    for pattern, converter in date_patterns:
        match = re.search(pattern, search_content, re.IGNORECASE)
        if match:
            try:
                if callable(converter):
                    date_str = converter(match.groups() if pattern != date_patterns[0][0] else match.group(1))
                else:
                    date_str = match.group(1)

                # Validate the date
                datetime.fromisoformat(date_str)
                return date_str
            except:
                continue

    return None

def convert_month_date(match_groups):
    """Convert month name date to ISO format."""
    month_map = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }
    month_str = match_groups[0].lower()[:3]
    month = month_map.get(month_str, '01')
    day = match_groups[1].zfill(2)
    year = match_groups[2]
    return f"{year}-{month}-{day}"

def convert_us_date(date_str):
    """Convert US format date to ISO format."""
    # Remove "Meeting Date:" part if present
    date_str = re.sub(r'[Mm]eeting [Dd]ate:?\s*', '', date_str)

    # Try to parse MM/DD/YYYY or MM-DD-YYYY
    match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', date_str)
    if match:
        month, day, year = match.groups()
        # Handle 2-digit years
        if len(year) == 2:
            year = '20' + year if int(year) < 50 else '19' + year
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return None

def fix_document_metadata():
    """Fix document metadata in the database."""

    print("Fixing Document Metadata")
    print("=" * 60)

    try:
        # Get all unique documents (grouped by file_id or file_title)
        print("Fetching all documents...")
        all_docs = supabase.from_('documents') \
            .select('id, content, metadata, created_at, file_id, file_date, source') \
            .execute()

        if not all_docs.data:
            print("No documents found")
            return

        print(f"Found {len(all_docs.data)} document chunks")

        # Group by unique documents
        unique_documents = {}
        for doc in all_docs.data:
            metadata = doc.get('metadata', {})

            # Parse metadata if it's a string
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            elif metadata is None:
                metadata = {}

            # Get file info from metadata
            meta_file_id = metadata.get('file_id')
            meta_file_title = metadata.get('file_title', metadata.get('source', 'Unknown'))

            # Use metadata file_id as the unique key
            unique_key = meta_file_id if meta_file_id else meta_file_title

            if unique_key not in unique_documents:
                unique_documents[unique_key] = {
                    'docs': [],
                    'file_id': meta_file_id,
                    'file_title': meta_file_title,
                    'content': ''
                }

            unique_documents[unique_key]['docs'].append(doc)

            # Accumulate content from first few chunks for date extraction
            chunk_index = metadata.get('chunk_index', 999)
            if chunk_index <= 3:  # Use first 3 chunks for date extraction
                unique_documents[unique_key]['content'] += doc.get('content', '')

        print(f"Found {len(unique_documents)} unique documents")
        print("-" * 60)

        # Process each unique document
        updates_made = 0
        for unique_key, doc_info in unique_documents.items():
            file_title = doc_info['file_title']
            file_id = doc_info['file_id']
            combined_content = doc_info['content']

            print(f"\nProcessing: {file_title}")

            # Extract meeting date
            extracted_date = extract_date_from_content(combined_content, file_title)

            if extracted_date:
                print(f"  Found date: {extracted_date}")
            else:
                print(f"  No date found, using created_at date")
                # Use the created_at date as fallback
                extracted_date = doc_info['docs'][0]['created_at'][:10]

            # Update all chunks for this document
            for doc in doc_info['docs']:
                doc_id = doc['id']

                # Prepare update data
                update_data = {}

                # Only update if values are different or missing
                if doc.get('file_date') != extracted_date:
                    update_data['file_date'] = extracted_date

                if doc.get('source') != file_title:
                    update_data['source'] = file_title

                if file_id and doc.get('file_id') != file_id:
                    update_data['file_id'] = file_id

                # Perform update if there are changes
                if update_data:
                    try:
                        supabase.from_('documents') \
                            .update(update_data) \
                            .eq('id', doc_id) \
                            .execute()
                        updates_made += 1
                    except Exception as e:
                        print(f"  Error updating doc {doc_id[:8]}...: {e}")

            print(f"  Updated {len(doc_info['docs'])} chunks")

        print("\n" + "=" * 60)
        print(f"✅ Metadata fix complete! Updated {updates_made} document chunks.")

        # Show sample of updated documents
        print("\nSample of updated documents:")
        sample = supabase.from_('documents') \
            .select('file_date, source, file_id') \
            .not_.is_('file_date', 'null') \
            .limit(5) \
            .execute()

        for doc in sample.data:
            print(f"  - {doc['source']}: {doc['file_date']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    fix_document_metadata()