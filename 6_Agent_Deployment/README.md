# Dynamous AI Agent Mastery - Module 6: Agent Deployment

A modular, production-ready deployment setup for the Dynamous AI Agent Mastery agent and application. This module restructures the code from previous modules into independently deployable components: the AI agent API, RAG pipeline, and frontend application. Each component can be deployed, scaled, and maintained separately (or together!) while working together as a cohesive system.

## Modular Architecture

The deployment structure has been designed for maximum flexibility and scalability:

```
6_Agent_Deployment/
├── backend_agent_api/      # AI Agent with FastAPI - The brain of the system
├── backend_rag_pipeline/   # Document processing pipeline - Handles knowledge ingestion
├── frontend/               # React application - User interface
└── sql/                    # Database schemas - Foundation for all components
```

Each component is self-contained with its own:
- Dependencies and virtual environment
- Environment configuration
- README with specific instructions
- Deployment capabilities

This modular approach allows you to:
- Deploy components to different services (e.g., agent on GCP Cloud Run, RAG on DigitalOcean, frontend on Render)
- Scale components independently based on load
- Update and maintain each component without affecting others
- Choose different deployment strategies for each component

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Supabase account (or self-hosted instance)
- LLM provider account (OpenAI, OpenRouter, or local Ollama)
- Optional: Brave API key for web search (or local SearXNG)
- Optional: Google Drive API credentials for Google Drive RAG

## Quick Start Overview

### Option A: Docker Compose (Recommended)
1. **Set up the database** - Run SQL scripts to create all necessary tables
2. **Configure environment variables** - Copy and fill out the `.env` file
3. **Run with Docker Compose** - Start all services with one command

### Option B: Development Mode
1. **Set up the database** - Run SQL scripts to create all necessary tables
2. **Configure each component** - Set up environment variables and install dependencies
3. **Start all services** - Run each component in its own process

## 1. Database Setup

The database is the foundation for all components. Set it up first:

### Cloud Supabase

1. Create a Supabase project at [https://supabase.com](https://supabase.com)

2. Navigate to the SQL Editor in your Supabase dashboard

3. Run the SQL scripts in order from the `sql/` directory:
   ```
   1-user_profiles_requests.sql     # User management tables
   2-user_profiles_requests_rls.sql  # Row-level security for users
   3-conversations_messages.sql      # Conversation storage
   4-conversations_messages_rls.sql  # Row-level security for conversations
   5-documents.sql                   # Document storage with vectors
   6-document_metadata.sql           # Document metadata
   7-document_rows.sql               # Tabular document data
   8-execute_sql_rpc.sql             # SQL query execution function
   ```

### Local Supabase

1. Navigate to http://localhost:8000 (default Supabase dashboard)
2. Run the same SQL scripts in order

> **Note**: For local Ollama implementations, modify vector dimensions in `5-documents.sql` from 1536 to match your embedding model (e.g., 768 for nomic-embed-text)

## 2. Backend Agent API Setup

The AI agent API is the core intelligence of the system:

```bash
cd backend_agent_api
```

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   - LLM provider settings (OpenAI/OpenRouter/Ollama)
   - Database connection (Supabase URL and service key)
   - Embedding model configuration
   - Web search settings (Brave API or SearXNG)

4. **Start the agent API:**
   ```bash
   uvicorn agent_api:app --reload --port 8001
   ```

The API will be available at http://localhost:8001

## 3. Backend RAG Pipeline Setup

The RAG pipeline processes and indexes documents for the agent:

```bash
cd backend_rag_pipeline
```

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Use the same database and embedding settings as the agent API.

4. **Configure your pipeline:**
   - For local files: Edit `Local_Files/config.json`
   - For Google Drive: Edit `Google_Drive/config.json` and add credentials

5. **Run the pipeline:**
   ```bash
   # For local files
   python Local_Files/main.py
   
   # For Google Drive
   python Google_Drive/main.py
   ```

The pipeline will continuously monitor and process documents.

## 4. Frontend Setup

The React frontend turns our agent into a full application:

```bash
cd frontend
```

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent
   VITE_ENABLE_STREAMING=true
   ```
   
   **Important**: The `VITE_AGENT_ENDPOINT` must match your agent API URL:
   - Local development: `http://localhost:8001/api/pydantic-agent`
   - Production: `https://your-deployed-agent-url/api/pydantic-agent`
   - If using n8n instead of Python: Update to your n8n webhook URL

3. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:8081

## Docker Compose Deployment (Recommended)

The easiest way to run the entire stack is with Docker Compose:

### 1. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_api_key_here
LLM_CHOICE=gpt-4o-mini

# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Frontend Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent

# RAG Pipeline Configuration
PIPELINE_TYPE=local  # or google_drive
RUN_MODE=continuous  # or single for scheduled runs
```

### 2. Start All Services

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### 3. Access the Application

- **Frontend**: http://localhost:8082
- **Agent API**: http://localhost:8001
- **Health Check**: http://localhost:8001/health

### 4. Add Documents to RAG Pipeline

For local files:
```bash
# Copy documents to the RAG pipeline directory
cp your-documents/* ./rag-documents/
```

For Google Drive:
```bash
# Place your Google Drive credentials
cp credentials.json ./google-credentials/
```

### Docker Compose Commands

```bash
# Start services
docker compose up -d

# View logs for specific service
docker compose logs -f agent-api
docker compose logs -f rag-pipeline
docker compose logs -f frontend

# Rebuild and restart services
docker compose up -d --build

# Scale RAG pipeline (if using single-run mode)
docker compose up -d --scale rag-pipeline=0  # Stop for scheduled runs

# Check service health
docker compose ps
```

## Development Mode

For development with live reloading, run each component separately.

### Running Services Individually

You'll need 3-4 terminal windows:

1. **Terminal 1 - Agent API:**
   ```bash
   cd backend_agent_api
   venv\Scripts\activate  # or source venv/bin/activate
   uvicorn agent_api:app --reload --port 8001
   ```

2. **Terminal 2 - RAG Pipeline:**
   ```bash
   cd backend_rag_pipeline
   venv\Scripts\activate  # or source venv/bin/activate
   python Local_Files/main.py
   ```

3. **Terminal 3 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Terminal 4 (Optional) - Code Execution MCP server:**
   ```bash
   deno run -N -R=node_modules -W=node_modules --node-modules-dir=auto jsr:@pydantic/mcp-run-python sse
   ```

## Deployment Options

We provide three deployment strategies, from simple to enterprise-grade:

### Option 1: DigitalOcean with Docker Compose (Simplest)
Deploy the entire stack on a single DigitalOcean Droplet using Docker Compose:
- **Pros**: Simple setup, everything in one place, easy to manage
- **Cons**: All components scale together, single point of failure
- **Best for**: Small teams, prototypes, and getting started quickly
- **Setup**: Use the provided `docker compose.yml` to deploy all services together

### Option 2: Render Platform (Recommended)
Deploy each component separately on Render for better scalability:
- **Agent API**: Deploy as a Docker container with autoscaling
- **RAG Pipeline**: Set up as a scheduled job (cron)
- **Frontend**: Deploy as a static site from the build output
- **Pros**: Automatic scaling, managed infrastructure, good free tier
- **Cons**: Requires configuring each service separately
- **Best for**: Production applications with moderate traffic

### Option 3: Google Cloud Platform (Enterprise)
For enterprise deployments with maximum flexibility:
- **Agent API**: Cloud Run for serverless, auto-scaling containers
- **RAG Pipeline**: Cloud Scheduler + Cloud Run for scheduled processing
- **Frontend**: Cloud Storage + Cloud CDN for global static hosting
- **Database**: Consider Cloud SQL for Postgres instead of Supabase
- **Pros**: Enterprise features, global scale, fine-grained control
- **Cons**: More complex setup, requires GCP knowledge
- **Best for**: Large-scale production deployments

### Deployment Decision Matrix

| Feature | DigitalOcean | Render | Google Cloud |
|---------|--------------|---------|--------------|
| Setup Complexity | ⭐ (Easiest) | ⭐⭐ (Still Pretty Easy) | ⭐⭐⭐ (Moderate) |
| Cost for Small Apps | $$ | $ (Free tier) | $ (Free tier) |
| Scalability | Manual | Automatic | Automatic |
| Geographic Distribution | Single region | Multi-region | Global |
| Best For | Quick start or Local AI | Most cloud based projects | Enterprise |

## Environment Variables Reference

### Agent API & RAG Pipeline
```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_CHOICE=gpt-4o-mini

# Embedding Configuration  
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your_api_key
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# Web Search
BRAVE_API_KEY=your_brave_key
SEARXNG_BASE_URL=http://localhost:8080
```

### Frontend
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent
VITE_ENABLE_STREAMING=true
```

## Troubleshooting

### Docker Compose Issues

1. **Services won't start**:
   ```bash
   # Check service logs
   docker compose logs -f
   
   # Rebuild images
   docker compose build --no-cache
   ```

2. **Port conflicts**:
   ```bash
   # Check what's using ports
   netstat -tlnp | grep :8001
   
   # Stop conflicting services or change ports in docker compose.yml
   ```

3. **Environment variables not loading**:
   ```bash
   # Verify .env file exists and has correct format
   cat .env
   
   # Check environment in container
   docker compose exec agent-api env | grep LLM_
   ```

4. **Volume permission issues**:
   ```bash
   # Fix permissions for document volumes
   sudo chown -R $USER:$USER ./rag-documents
   ```

### Common Issues

1. **Database connection**: Verify Supabase credentials and network access
2. **Vector dimensions**: Ensure embedding model dimensions match database schema
3. **CORS errors**: Check API endpoint configuration in frontend `.env`
4. **Memory issues**: Increase Docker memory limits for large models

### Verification Steps

1. **Database**: Check Supabase dashboard for table creation
2. **Agent API Health**: Visit http://localhost:8001/health
3. **API Documentation**: Visit http://localhost:8001/docs
4. **RAG Pipeline**: Check logs with `docker compose logs rag-pipeline`
5. **Frontend**: Open browser console for any errors

### Health Checks

Monitor service health:
```bash
# Check all service health
docker compose ps

# Check specific service logs
docker compose logs -f agent-api

# Test API health endpoint
curl http://localhost:8001/health

# Test frontend
curl http://localhost:8082/health
```

## Next Steps

Once everything is running locally:

1. **Test the full flow**: Upload documents → Process with RAG → Query through frontend
2. **Monitor performance**: Check response times and resource usage
3. **Plan deployment**: Choose platforms for each component
4. **Set up CI/CD**: Automate testing and deployment
5. **Add monitoring**: Implement logging and error tracking

## Support

For detailed instructions on each component, refer to their individual README files:
- `backend_agent_api/README.md` - Agent API specifics
- `backend_rag_pipeline/README.md` - RAG pipeline details  
- `frontend/README.md` - Frontend development guide

Remember: The modular structure allows you to start with local deployment and gradually move components to the cloud as needed!