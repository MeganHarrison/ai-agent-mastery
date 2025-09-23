# RAG Pipeline Scripts

This directory contains organized utility scripts for managing the RAG pipeline.

## Directory Structure

### `/processing`
Scripts for processing documents and creating embeddings:
- `clean_metadata_test.py` - Extract and save metadata from bucket files with all fields
- `process_all_bucket_files.py` - Process all files from storage bucket with vectorization
- `process_files_with_embeddings.py` - Create embeddings for files without them
- `process_remaining_transcripts.py` - Process only unprocessed transcript files

### `/verification`
Scripts for verifying data integrity:
- `verify_embeddings.py` - Check which documents have embeddings and identify orphans

### `/insights`
Scripts for generating AI insights from documents:
- `generate_insights_now.py` - Generate insights for recent documents
- `manual_insights.py` - Manually generate insights for specific documents

## Usage Examples

### Process new files and create embeddings
```bash
cd scripts/processing
python process_files_with_embeddings.py
```

### Verify embedding coverage
```bash
cd scripts/verification
python verify_embeddings.py
```

### Generate insights from meetings
```bash
cd scripts/insights
python generate_insights_now.py
```

## Important Notes

- All scripts require proper environment variables set in `.env`
- Scripts process files with most recent first
- Embeddings include project_id when available
- Metadata extraction includes Fireflies IDs, duration, participants, etc.