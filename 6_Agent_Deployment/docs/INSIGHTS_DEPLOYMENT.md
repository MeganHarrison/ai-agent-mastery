# Automated Insights Processing - Deployment Guide

## Overview

The automated insights processing system has been successfully implemented and integrated with the existing RAG agent. This system automatically extracts project insights from meeting transcripts and assigns them to relevant projects.

## ✅ Features Implemented

### 1. Automated Pipeline (`automated_insights_pipeline.py`)
- **Multi-Project Assignment**: Executive meetings are analyzed to assign insights to specific projects
- **Content Analysis**: Uses AI to determine if documents are meeting transcripts
- **Intelligent Processing**: Handles both single-project and multi-project meeting scenarios

### 2. Background Worker (`insights_worker.py`)
- **Continuous Processing**: Monitors queue and processes documents automatically
- **Concurrent Processing**: Handles multiple documents simultaneously
- **Error Recovery**: Retry logic with exponential backoff
- **Graceful Shutdown**: Properly handles application lifecycle

### 3. Database Integration (`sql/12-automated_insights_triggers.sql`)
- **Automatic Queueing**: New documents are automatically queued for processing
- **Meeting Detection**: Smart identification of meeting transcripts vs other documents
- **Processing Queue**: Robust queue system with status tracking
- **Project Matching**: Links insights to projects based on content analysis

### 4. API Integration (`agent_api.py`)
- **Background Worker**: Integrated with FastAPI application lifecycle
- **Management Endpoints**: API endpoints for monitoring and control
- **Queue Statistics**: Real-time processing status and metrics

### 5. Agent Tools (`agent.py` & `tools.py`)
- **Insights Generation**: `generate_meeting_insights_tool()`
- **Project Queries**: `get_project_insights_tool()`
- **Search Functionality**: `search_insights_tool()`
- **Summary Reports**: `get_insights_summary_tool()`

## 🔧 Deployment Steps

### Step 1: Database Setup (Required)

The SQL schema must be applied to your Supabase database. You have two options:

#### Option A: Manual SQL Execution (Recommended)
1. Open your Supabase dashboard
2. Go to SQL Editor
3. Copy and paste the contents of `sql/12-automated_insights_triggers.sql`
4. Execute the SQL

#### Option B: Automated Script (If you have RPC access)
```bash
cd backend_agent_api
python setup_insights_triggers.py
```

### Step 2: Verify Database Schema

After running the SQL, verify these tables and functions exist:
- Tables: `insights_processing_queue`, `projects`, `project_insights`
- Functions: `get_insights_queue_stats()`, `queue_document_for_insights()`, etc.
- Triggers: `trigger_new_document_insights` on the `documents` table

### Step 3: Application Deployment

The insights worker is automatically integrated with your FastAPI application. When you start the server, you should see:

```
✅ Insights worker started successfully
🔄 Insights Worker initialized successfully
📊 Starting Insights Worker (polling every 30s)
```

### Step 4: Initial Setup

1. **Queue Existing Documents**: The system will automatically queue unprocessed meeting transcripts
2. **Monitor Processing**: Check `/api/insights/queue/stats` for queue status
3. **Trigger Retroactive Processing**: Use `/api/insights/process/retroactive` if needed

## 📊 API Endpoints

### Queue Management
- `GET /api/insights/queue/stats` - View processing queue statistics
- `POST /api/insights/process/retroactive` - Process all unprocessed documents
- `POST /api/insights/queue/reset-failed` - Reset failed processing attempts

### Health Check
- `GET /health` - Application health including worker status

## 🔍 Monitoring & Troubleshooting

### Worker Status
The insights worker logs its activity:
```
INFO - Insights Worker initialized successfully
INFO - Starting Insights Worker (polling every 30s)
INFO - Processing document 123: Weekly Team Meeting
INFO - Successfully processed document 123: 5 insights in 2.3s
```

### Queue Statistics
Monitor processing with the stats endpoint:
```json
{
  "pending_count": 3,
  "processing_count": 1,
  "completed_count": 15,
  "failed_count": 0,
  "total_count": 19,
  "oldest_pending_age": "00:02:30"
}
```

### Common Issues

#### 1. Missing Database Functions
**Error**: `Could not find the function public.get_insights_queue_stats`
**Solution**: Run the SQL schema file in your Supabase dashboard

#### 2. Worker Not Processing
**Symptoms**: Documents stuck in "pending" status
**Check**: 
- Database triggers are installed
- Worker is running (check logs)
- Documents are detected as meeting transcripts

#### 3. Multi-Project Assignment Issues
**Symptoms**: Executive meeting insights not assigned to projects
**Check**: 
- Projects table has correct project names
- Meeting content mentions project names
- AI model has sufficient context

## 🚀 Production Considerations

### Environment Variables
Ensure these are set for production:
```bash
ENVIRONMENT=production
SUPABASE_URL=your_production_url
SUPABASE_SERVICE_KEY=your_service_key
OPENAI_API_KEY=your_openai_key
```

### Performance Tuning
Adjust worker settings in `insights_worker.py`:
```python
InsightsWorker(
    polling_interval=30,      # How often to check queue (seconds)
    batch_size=5,            # Documents per batch
    max_concurrent=3         # Concurrent processing limit
)
```

### Scaling
For high-volume processing:
1. **Increase Concurrency**: Raise `max_concurrent` limit
2. **Multiple Workers**: Deploy separate worker instances
3. **Database Optimization**: Add indexes for your query patterns
4. **AI Rate Limits**: Monitor OpenAI API usage

## 📈 Usage Examples

### Agent Queries
The chat agent is now fully aware of the insights system as a key RAG resource. Users can ask:

**Action Item Tracking:**
- "What action items came out of yesterday's meeting?"
- "Show me all open action items for the Phoenix project"
- "Who is responsible for the permit coordination task?"

**Project Intelligence:**
- "What are the current blockers on all active projects?"
- "Show me risk patterns across our warehouse projects"
- "What decisions were made in recent executive meetings?"

**Executive Reporting:**
- "Generate a summary of this week's project insights"  
- "What are the top priorities flagged in executive meetings this quarter?"
- "Show me completion rates for action items by project"

**Pattern Recognition:**
- "What themes keep coming up in our project meetings?"
- "Which projects have the most risk alerts this month?"
- "Are we seeing similar issues across multiple projects?"

### Multi-Project Meetings
The system automatically handles:
- Executive weekly meetings discussing multiple projects
- Operations meetings with cross-project updates
- Client calls covering multiple initiatives
- Strategic planning sessions

### Project Linking
Insights are automatically assigned to projects when:
- Meeting content mentions project names
- Context indicates project relevance  
- AI analysis identifies project connections

## ✅ Success Metrics

The automated insights system is now:
- **Automatically Processing**: New meeting transcripts
- **Multi-Project Aware**: Executive meetings with multiple project insights
- **Retroactively Available**: Can process existing meetings
- **Fully Integrated**: Available through agent queries
- **Production Ready**: Robust error handling and monitoring

## 🎯 Next Steps

1. **Monitor Performance**: Watch processing times and success rates
2. **Tune Project Matching**: Refine project detection algorithms if needed
3. **Scale as Needed**: Adjust worker concurrency based on volume
4. **Add Custom Logic**: Extend insight types or processing rules
5. **Dashboard Integration**: Build UI for insights management

The system is now fully operational and will automatically process meeting transcripts going forward while providing comprehensive project insights through the RAG agent interface.