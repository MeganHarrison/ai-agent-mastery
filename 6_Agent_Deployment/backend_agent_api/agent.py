from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerHTTP
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import AsyncOpenAI
from httpx import AsyncClient
from supabase import Client
from pathlib import Path
from typing import List
import os

# Check if we're in production
is_production = os.getenv("ENVIRONMENT") == "production"

if not is_production:
    # Development: prioritize .env file
    project_root = Path(__file__).resolve().parent
    dotenv_path = project_root / '.env'
    load_dotenv(dotenv_path, override=True)
else:
    # Production: use cloud platform env vars only
    load_dotenv()

from prompt import AGENT_SYSTEM_PROMPT
from tools import (
    web_search_tool,
    image_analysis_tool,
    retrieve_relevant_documents_tool,
    list_documents_tool,
    get_document_content_tool,
    execute_sql_query_tool,
    execute_safe_code_tool,
    semantic_search_tool,
    hybrid_search_tool,
    get_recent_documents_tool,
    generate_meeting_insights_tool,
    get_project_insights_tool,
    get_insights_summary_tool,
    search_insights_tool,
    strategic_business_analysis_tool
)

# ========== Helper function to get model configuration ==========
def get_model():
    llm = os.getenv('LLM_CHOICE') or 'gpt-5'
    base_url = os.getenv('LLM_BASE_URL') or 'https://api.openai.com/v1'
    api_key = os.getenv('LLM_API_KEY') or 'ollama'

    return OpenAIModel(llm, provider=OpenAIProvider(base_url=base_url, api_key=api_key))

# ========== Pydantic AI Agent ==========
@dataclass
class AgentDeps:
    supabase: Client
    embedding_client: AsyncOpenAI
    http_client: AsyncClient
    brave_api_key: str | None
    searxng_base_url: str | None
    memories: str

# To use the code execution MCP server:
# First uncomment the line below that defines 'code_execution_server', then also uncomment 'mcp_servers=[code_execution_server]'
# Start this in a separate terminal with this command after installing Deno:
# deno run -N -R=node_modules -W=node_modules --node-modules-dir=auto jsr:@pydantic/mcp-run-python sse
# Instructions for installing Deno here: https://github.com/denoland/deno/
# Pydantic AI docs for this MCP server: https://ai.pydantic.dev/mcp/run-python/
# code_execution_server = MCPServerHTTP(url='http://localhost:3001/sse')  

agent = Agent(
    get_model(),
    system_prompt=AGENT_SYSTEM_PROMPT,
    deps_type=AgentDeps,
    retries=2,
    instrument=True,
    # mcp_servers=[code_execution_server]
)

@agent.system_prompt  
def add_memories(ctx: RunContext[str]) -> str:
    return f"\nUser Memories:\n{ctx.deps.memories}"

@agent.tool
async def web_search(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Search the web with a specific query and get a summary of the top search results.
    
    Args:
        ctx: The context for the agent including the HTTP client and optional Brave API key/SearXNG base url
        query: The query for the web search
        
    Returns:
        A summary of the web search.
        For Brave, this is a single paragraph.
        For SearXNG, this is a list of the top search results including the most relevant snippet from the page.
    """
    print("Calling web_search tool")
    return await web_search_tool(query, ctx.deps.http_client, ctx.deps.brave_api_key, ctx.deps.searxng_base_url)    

@agent.tool
async def retrieve_relevant_documents(ctx: RunContext[AgentDeps], user_query: str) -> str:
    """
    Retrieve relevant document chunks based on the query with RAG.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The user's question or query
        
    Returns:
        A formatted string containing the top 4 most relevant documents chunks
    """
    print("Calling retrieve_relevant_documents tool")
    return await retrieve_relevant_documents_tool(ctx.deps.supabase, ctx.deps.embedding_client, user_query)

@agent.tool
async def list_documents(ctx: RunContext[AgentDeps]) -> List[str]:
    """
    Retrieve a list of all available documents.
    
    Returns:
        List[str]: List of documents including their metadata (URL/path, schema if applicable, etc.)
    """
    print("Calling list_documents tool")
    return await list_documents_tool(ctx.deps.supabase)

@agent.tool
async def get_document_content(ctx: RunContext[AgentDeps], document_id: str) -> str:
    """
    Retrieve the full content of a specific document by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        document_id: The ID (or file path) of the document to retrieve
        
    Returns:
        str: The full content of the document with all chunks combined in order
    """
    print("Calling get_document_content tool")
    return await get_document_content_tool(ctx.deps.supabase, document_id)

@agent.tool
async def execute_sql_query(ctx: RunContext[AgentDeps], sql_query: str) -> str:
    """
    Run a SQL query - use this to query from the document_rows table once you know the file ID you are querying. 
    dataset_id is the file_id and you are always using the row_data for filtering, which is a jsonb field that has 
    all the keys from the file schema given in the document_metadata table.

    Never use a placeholder file ID. Always use the list_documents tool first to get the file ID.

    Example query:

    SELECT AVG((row_data->>'revenue')::numeric)
    FROM document_rows
    WHERE dataset_id = '123';

    Example query 2:

    SELECT 
        row_data->>'category' as category,
        SUM((row_data->>'sales')::numeric) as total_sales
    FROM document_rows
    WHERE dataset_id = '123'
    GROUP BY row_data->>'category';
    
    Args:
        ctx: The context including the Supabase client
        sql_query: The SQL query to execute (must be read-only)
        
    Returns:
        str: The results of the SQL query in JSON format
    """
    print(f"Calling execute_sql_query tool with SQL: {sql_query }")
    return await execute_sql_query_tool(ctx.deps.supabase, sql_query)    

@agent.tool
async def image_analysis(ctx: RunContext[AgentDeps], document_id: str, query: str) -> str:
    """
    Analyzes an image based on the document ID of the image provided.
    This function pulls the binary of the image from the knowledge base
    and passes that into a subagent with a vision LLM
    Before calling this tool, call list_documents to see the images available
    and to get the exact document ID for the image.
    
    Args:
        ctx: The context including the Supabase client
        document_id: The ID (or file path) of the image to analyze
        query: What to extract from the image analysis
        
    Returns:
        str: An analysis of the image based on the query
    """
    print("Calling image_analysis tool")
    return await image_analysis_tool(ctx.deps.supabase, document_id, query)    

# Using the MCP server instead for code execution, but you can use this simple version
# if you don't want to use MCP for whatever reason! Just uncomment the line below:
@agent.tool
async def execute_code(ctx: RunContext[AgentDeps], code: str) -> str:
    """
    Executes a given Python code string in a protected environment.
    Use print to output anything that you need as a result of executing the code.
    
    Args:
        code: Python code to execute
        
    Returns:
        str: Anything printed out to standard output with the print command
    """    
    print(f"executing code: {code}")
    print(f"Result is: {execute_safe_code_tool(code)}")
    return execute_safe_code_tool(code)

@agent.tool
async def semantic_search(ctx: RunContext[AgentDeps], user_query: str, match_count: int = 6, similarity_threshold: float = 0.7) -> str:
    """
    Advanced semantic search for conceptual queries and business insights.
    Best for exploring themes, patterns, and strategic questions.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The search query
        match_count: Number of results to return (default 6)
        similarity_threshold: Minimum similarity score (default 0.7)
        
    Returns:
        Formatted search results with similarity scores and metadata
    """
    print("Calling semantic_search tool")
    return await semantic_search_tool(ctx.deps.supabase, ctx.deps.embedding_client, user_query, match_count, similarity_threshold)

@agent.tool
async def hybrid_search(ctx: RunContext[AgentDeps], user_query: str, match_count: int = 8) -> str:
    """
    Hybrid search combining semantic similarity with keyword matching.
    Best for specific technical details, names, dates, and exact matches.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The search query
        match_count: Number of results to return (default 8)
        
    Returns:
        Formatted hybrid search results with both semantic and keyword matches
    """
    print("Calling hybrid_search tool")
    return await hybrid_search_tool(ctx.deps.supabase, ctx.deps.embedding_client, user_query, match_count)

@agent.tool
async def get_recent_documents(ctx: RunContext[AgentDeps], days_back: int = 7, match_count: int = 10) -> str:
    """
    Retrieve recent documents for timeline-based queries and status updates.
    Perfect for "last meeting", "recent updates", and time-sensitive queries.
    
    Args:
        ctx: The context including the Supabase client
        days_back: Number of days to look back (default 7)
        match_count: Maximum number of documents to return (default 10)
        
    Returns:
        Formatted list of recent documents with metadata and dates
    """
    print("Calling get_recent_documents tool")
    return await get_recent_documents_tool(ctx.deps.supabase, days_back, None, match_count)

@agent.tool
async def generate_meeting_insights(ctx: RunContext[AgentDeps], document_id: str, force_reprocess: bool = False) -> str:
    """
    Extract and store AI-generated insights from a meeting transcript.
    Use this tool to analyze meeting content and extract actionable insights like action items,
    decisions, risks, blockers, and opportunities. Perfect for processing new meeting transcripts.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        document_id: ID of the document to process for insights
        force_reprocess: Whether to reprocess even if insights already exist (default False)
        
    Returns:
        Summary of extracted insights with priorities and assignments
    """
    print("Calling generate_meeting_insights tool")
    return await generate_meeting_insights_tool(ctx.deps.supabase, ctx.deps.embedding_client, document_id, force_reprocess)

@agent.tool
async def get_project_insights(
    ctx: RunContext[AgentDeps], 
    project_name: str = None,
    insight_types: List[str] = None,
    priorities: List[str] = None,
    status_filter: List[str] = None,
    days_back: int = 30,
    limit: int = 20
) -> str:
    """
    Retrieve and display project insights with comprehensive filtering options.
    Perfect for getting status updates, tracking action items, and monitoring project health.
    
    Args:
        ctx: The context including the Supabase client
        project_name: Filter by project name (partial match, optional)
        insight_types: Filter by types like 'action_item', 'decision', 'risk', 'blocker' (optional)
        priorities: Filter by 'critical', 'high', 'medium', 'low' (optional)
        status_filter: Filter by 'open', 'in_progress', 'completed', 'cancelled' (optional)
        days_back: Number of days to look back (default 30)
        limit: Maximum number of insights to return (default 20)
        
    Returns:
        Formatted list of insights matching the specified criteria
    """
    print("Calling get_project_insights tool")
    return await get_project_insights_tool(
        ctx.deps.supabase,
        project_name,
        insight_types,
        priorities,
        status_filter,
        days_back,
        limit
    )

@agent.tool
async def get_insights_summary(ctx: RunContext[AgentDeps], days_back: int = 30) -> str:
    """
    Generate a comprehensive summary of project insights over a specified period.
    Provides statistics, trending issues, active projects, and key decisions.
    Perfect for executive reports and project health overviews.
    
    Args:
        ctx: The context including the Supabase client
        days_back: Number of days to include in summary (default 30)
        
    Returns:
        Comprehensive insights summary with statistics and key findings
    """
    print("Calling get_insights_summary tool")
    return await get_insights_summary_tool(ctx.deps.supabase, days_back)

@agent.tool
async def search_insights(
    ctx: RunContext[AgentDeps],
    search_query: str,
    insight_types: List[str] = None,
    priorities: List[str] = None,
    limit: int = 15
) -> str:
    """
    Search project insights using full-text search with optional filters.
    Great for finding specific topics, issues, or themes across all meeting insights.
    
    Args:
        ctx: The context including the Supabase client
        search_query: Text to search in insight titles and descriptions
        insight_types: Filter by insight types (optional)
        priorities: Filter by priority levels (optional)
        limit: Maximum number of results (default 15)
        
    Returns:
        Ranked search results with relevance scores
    """
    print("Calling search_insights tool")
    return await search_insights_tool(
        ctx.deps.supabase,
        search_query,
        insight_types,
        priorities,
        limit
    )


@agent.tool
async def strategic_business_analysis(
    ctx: RunContext[AgentDeps],
    analysis_query: str,
    focus_areas: List[str] = None
) -> str:
    """
    **EXECUTIVE INTELLIGENCE TOOL** - Use this for strategic business questions that require
    comprehensive analysis across multiple data sources. This tool automatically performs
    4-5 different searches and synthesizes the results for executive-level insights.
    
    Perfect for questions like:
    - "What are the biggest risks facing the company?"
    - "What challenges are we seeing across projects?"
    - "What patterns indicate potential problems?"
    - "What strategic issues need leadership attention?"
    
    Args:
        ctx: The context including Supabase and OpenAI clients
        analysis_query: The strategic question requiring comprehensive analysis
        focus_areas: Optional focus areas like ['risks', 'timeline', 'budget', 'personnel']
        
    Returns:
        Comprehensive strategic analysis with multi-source evidence
    """
    print("Calling strategic_business_analysis tool - EXECUTIVE INTELLIGENCE MODE")
    return await strategic_business_analysis_tool(
        ctx.deps.supabase,
        ctx.deps.embedding_client,
        analysis_query,
        focus_areas
    )