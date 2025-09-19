"""
Insights API for RAG Pipeline

Provides API endpoints for insights processing, including manual triggers and webhooks.
Integrates with the existing RAG pipeline infrastructure.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from pathlib import Path

# Set up path for imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common'))

from common.db_handler import supabase, insights_processor
from insights.insights_triggers import InsightsTriggerManager, InsightsTriggerRequest, WebhookInsightsRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Pipeline Insights API",
    description="API for insights processing and management within the RAG pipeline",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize insights trigger manager
insights_trigger_manager = None
if insights_processor:
    insights_trigger_manager = InsightsTriggerManager(app, supabase)


# Request/Response Models
class ManualInsightsRequest(BaseModel):
    """Request model for manual insights processing."""
    document_ids: Optional[List[str]] = None
    user_id: Optional[str] = None
    force_reprocess: bool = False


class InsightsStatusResponse(BaseModel):
    """Response model for insights status."""
    service_available: bool
    insights_today: int
    documents_pending: int
    total_insights: int
    timestamp: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "RAG Pipeline Insights API",
        "version": "1.0.0",
        "insights_available": insights_processor is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "insights_processor": insights_processor is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/insights/trigger")
async def trigger_insights_manual(
    request: ManualInsightsRequest,
    background_tasks: BackgroundTasks
):
    """
    Manually trigger insights processing for specific documents or all pending documents.
    """
    if not insights_processor:
        raise HTTPException(status_code=503, detail="Insights service not available")
    
    logger.info(f"Manual insights trigger requested: {request.dict()}")
    
    # Add background task for processing
    background_tasks.add_task(
        _process_manual_insights,
        request.document_ids,
        request.user_id,
        request.force_reprocess
    )
    
    return {
        "message": "Insights processing started",
        "document_ids": request.document_ids,
        "user_id": request.user_id,
        "force_reprocess": request.force_reprocess,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/insights/webhook")
async def webhook_insights_trigger(
    request: WebhookInsightsRequest,
    fastapi_request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint for external systems to trigger insights processing.
    """
    if not insights_processor:
        raise HTTPException(status_code=503, detail="Insights service not available")
    
    logger.info(f"Webhook insights trigger: {request.trigger_type}")
    
    # Add background task for webhook processing
    background_tasks.add_task(
        _process_webhook_insights,
        request.trigger_type,
        request.document_id,
        request.user_id,
        request.metadata or {}
    )
    
    return {
        "message": "Webhook insights processing started",
        "trigger_type": request.trigger_type,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/insights/status", response_model=InsightsStatusResponse)
async def get_insights_status():
    """
    Get current insights processing status and statistics.
    """
    try:
        # Get insights count for today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        insights_today_result = supabase.table('ai_insights')\
            .select('id', count='exact')\
            .gte('created_at', today.isoformat())\
            .execute()
        
        insights_today = insights_today_result.count if insights_today_result.count else 0
        
        # Get total insights count
        total_insights_result = supabase.table('ai_insights')\
            .select('id', count='exact')\
            .execute()
        
        total_insights = total_insights_result.count if total_insights_result.count else 0
        
        # Get documents pending insights processing
        all_docs_result = supabase.table('documents')\
            .select('id')\
            .execute()
        
        processed_docs_result = supabase.table('ai_insights')\
            .select('document_id')\
            .execute()
        
        processed_doc_ids = set()
        if processed_docs_result.data:
            processed_doc_ids = {doc['document_id'] for doc in processed_docs_result.data if doc['document_id']}
        
        total_docs = len(all_docs_result.data) if all_docs_result.data else 0
        documents_pending = total_docs - len(processed_doc_ids)
        
        return InsightsStatusResponse(
            service_available=insights_processor is not None,
            insights_today=insights_today,
            documents_pending=documents_pending,
            total_insights=total_insights,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get insights status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights status")


@app.get("/insights/recent")
async def get_recent_insights(
    limit: int = 10,
    user_id: Optional[str] = None
):
    """
    Get recent insights with optional user filtering.
    """
    try:
        query = supabase.table('ai_insights')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)
        
        if user_id:
            query = query.eq('user_id', user_id)
        
        result = query.execute()
        
        return {
            "insights": result.data or [],
            "count": len(result.data) if result.data else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent insights")


@app.post("/insights/process-pending")
async def process_pending_insights(
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None
):
    """
    Process all documents in the insights processing queue.
    """
    if not insights_processor:
        raise HTTPException(status_code=503, detail="Insights service not available")
    
    logger.info(f"Processing pending insights queue for user: {user_id}")
    
    # Add background task
    background_tasks.add_task(
        _process_pending_queue,
        user_id
    )
    
    return {
        "message": "Processing pending insights queue",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }


# Background Tasks
async def _process_manual_insights(
    document_ids: Optional[List[str]],
    user_id: Optional[str],
    force_reprocess: bool
):
    """Background task for manual insights processing."""
    try:
        logger.info(f"Starting manual insights processing: {document_ids}")
        
        if document_ids:
            # Process specific documents
            for doc_id in document_ids:
                if force_reprocess:
                    # Mark for reprocessing
                    supabase.table('documents')\
                        .update({'insights_needs_reprocessing': True})\
                        .eq('id', doc_id)\
                        .execute()
                
                result = await insights_processor.trigger_insights_for_document(
                    document_id=doc_id,
                    user_id=user_id
                )
                logger.info(f"Processed insights for document {doc_id}: {result}")
        else:
            # Process all pending
            result = await insights_processor.process_pending_insights_queue(user_id)
            logger.info(f"Processed pending insights queue: {result}")
            
    except Exception as e:
        logger.error(f"Manual insights processing failed: {e}")


async def _process_webhook_insights(
    trigger_type: str,
    document_id: Optional[str],
    user_id: Optional[str],
    metadata: Dict[str, Any]
):
    """Background task for webhook insights processing."""
    try:
        logger.info(f"Processing webhook insights: {trigger_type}")
        
        if trigger_type == "document_processed" and document_id:
            result = await insights_processor.trigger_insights_for_document(
                document_id=document_id,
                user_id=user_id
            )
            logger.info(f"Webhook processed insights for document {document_id}: {result}")
            
        elif trigger_type == "batch_process":
            result = await insights_processor.process_pending_insights_queue(user_id)
            logger.info(f"Webhook processed pending insights: {result}")
            
        else:
            logger.warning(f"Unknown webhook trigger type: {trigger_type}")
            
    except Exception as e:
        logger.error(f"Webhook insights processing failed: {e}")


async def _process_pending_queue(user_id: Optional[str]):
    """Background task for processing pending insights queue."""
    try:
        logger.info(f"Processing pending insights queue for user: {user_id}")
        result = await insights_processor.process_pending_insights_queue(user_id)
        logger.info(f"Pending queue processing result: {result}")
        
    except Exception as e:
        logger.error(f"Pending queue processing failed: {e}")


# Development server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("INSIGHTS_API_PORT", "8002"))
    uvicorn.run(
        "insights_api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )