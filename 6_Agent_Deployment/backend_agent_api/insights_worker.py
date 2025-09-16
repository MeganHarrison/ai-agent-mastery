"""
Background Worker for Automated Insights Processing

This worker continuously monitors the insights_processing_queue and processes
documents to extract insights. It handles:

- Queue monitoring and processing
- Multi-project insights assignment
- Error handling and retries
- Batch processing for efficiency
- Graceful shutdown

Can be run as:
1. Standalone background process
2. Integrated with the main FastAPI app
3. Scheduled job (cron, etc.)
"""

import os
import asyncio
import logging
import signal
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from supabase import Client
from openai import AsyncOpenAI
from dotenv import load_dotenv
from pathlib import Path

from automated_insights_pipeline import AutomatedInsightsPipeline
from clients import get_agent_clients

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InsightsWorker:
    """Background worker for processing insights queue."""
    
    def __init__(self, 
                 polling_interval: int = 30,  # seconds
                 batch_size: int = 5,         # documents per batch
                 max_concurrent: int = 3):    # concurrent processing
        
        self.polling_interval = polling_interval
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        
        self.supabase: Optional[Client] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        self.pipeline: Optional[AutomatedInsightsPipeline] = None
        
        self.running = False
        self.processing_tasks = set()
        
        # Setup graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        for sig in [signal.SIGTERM, signal.SIGINT]:
            signal.signal(sig, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    async def initialize(self):
        """Initialize the worker with database and API clients."""
        try:
            logger.info("Initializing Insights Worker...")
            
            # Get clients
            self.openai_client, self.supabase = get_agent_clients()
            
            # Initialize pipeline
            self.pipeline = AutomatedInsightsPipeline()
            await self.pipeline.initialize()
            
            logger.info("Insights Worker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize worker: {e}")
            raise
    
    async def start(self):
        """Start the worker main loop."""
        if not self.pipeline:
            await self.initialize()
        
        self.running = True
        logger.info(f"Starting Insights Worker (polling every {self.polling_interval}s)")
        
        try:
            while self.running:
                try:
                    # Check queue and process documents
                    await self._process_queue_batch()
                    
                    # Clean up completed tasks
                    await self._cleanup_completed_tasks()
                    
                    # Log status
                    await self._log_status()
                    
                    # Wait before next poll
                    if self.running:  # Check if we should continue
                        await asyncio.sleep(self.polling_interval)
                        
                except asyncio.CancelledError:
                    logger.info("Worker cancelled, shutting down...")
                    break
                    
                except Exception as e:
                    logger.error(f"Error in worker main loop: {e}")
                    # Continue running despite errors
                    await asyncio.sleep(self.polling_interval)
            
        finally:
            await self._shutdown()
    
    async def _process_queue_batch(self):
        """Process a batch of documents from the queue."""
        try:
            # Get queue statistics
            stats_result = self.supabase.rpc('get_insights_queue_stats').execute()
            
            if stats_result.data and len(stats_result.data) > 0:
                stats = stats_result.data[0]
                pending_count = stats.get('pending_count', 0)
                processing_count = stats.get('processing_count', 0)
                
                if pending_count == 0:
                    return  # No work to do
                
                # Don't start too many concurrent jobs
                current_concurrent = len(self.processing_tasks) + processing_count
                if current_concurrent >= self.max_concurrent:
                    logger.debug(f"Max concurrent processing reached ({current_concurrent}/{self.max_concurrent})")
                    return
                
                # Get documents to process
                documents_to_process = []
                for _ in range(min(self.batch_size, self.max_concurrent - current_concurrent)):
                    doc_result = self.supabase.rpc('get_next_document_for_processing').execute()
                    
                    if doc_result.data and len(doc_result.data) > 0:
                        doc_info = doc_result.data[0]
                        documents_to_process.append(doc_info)
                    else:
                        break  # No more documents available
                
                # Process documents concurrently
                for doc_info in documents_to_process:
                    task = asyncio.create_task(
                        self._process_single_document(
                            doc_info['queue_id'],
                            doc_info['document_id'],
                            doc_info['document_title']
                        )
                    )
                    self.processing_tasks.add(task)
                    
                if documents_to_process:
                    logger.info(f"Started processing {len(documents_to_process)} documents")
                    
        except Exception as e:
            logger.error(f"Error processing queue batch: {e}")
    
    async def _process_single_document(self, queue_id: int, document_id: str, document_title: str):
        """Process a single document for insights."""
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing document {document_id}: {document_title}")
            
            # Process the document
            result = await self.pipeline.process_new_document(document_id)
            
            if result.get('error'):
                # Mark as failed
                await self._complete_processing(queue_id, False, result['error'])
                logger.error(f"Failed to process document {document_id}: {result['error']}")
                
            elif result.get('processed'):
                # Mark as completed successfully
                insights_count = result.get('insights_count', 0)
                await self._complete_processing(queue_id, True, insights_count=insights_count)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Successfully processed document {document_id}: {insights_count} insights in {processing_time:.1f}s")
                
            else:
                # Document was not processed (not a meeting transcript, etc.)
                await self._complete_processing(queue_id, True, "Not a meeting transcript", 0)
                logger.info(f"Document {document_id} skipped: {result.get('reason', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Exception processing document {document_id}: {e}")
            await self._complete_processing(queue_id, False, str(e))
    
    async def _complete_processing(self, queue_id: int, success: bool, error_msg: str = None, insights_count: int = 0):
        """Mark a document processing job as completed."""
        try:
            self.supabase.rpc(
                'complete_document_processing',
                {
                    'queue_id_param': queue_id,
                    'success': success,
                    'error_msg': error_msg,
                    'insights_count': insights_count
                }
            ).execute()
            
        except Exception as e:
            logger.error(f"Failed to mark processing complete for queue ID {queue_id}: {e}")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed processing tasks."""
        if not self.processing_tasks:
            return
            
        # Find completed tasks
        completed = [task for task in self.processing_tasks if task.done()]
        
        # Remove completed tasks
        for task in completed:
            self.processing_tasks.discard(task)
            
            # Check for exceptions
            try:
                await task
            except Exception as e:
                logger.error(f"Task completed with error: {e}")
    
    async def _log_status(self):
        """Log current worker status."""
        try:
            # Get queue stats
            stats_result = self.supabase.rpc('get_insights_queue_stats').execute()
            
            if stats_result.data and len(stats_result.data) > 0:
                stats = stats_result.data[0]
                
                pending = stats.get('pending_count', 0)
                processing = stats.get('processing_count', 0)
                completed = stats.get('completed_count', 0)
                failed = stats.get('failed_count', 0)
                active_tasks = len(self.processing_tasks)
                
                if pending > 0 or processing > 0 or active_tasks > 0:
                    logger.info(
                        f"Queue status: {pending} pending, {processing} processing, "
                        f"{completed} completed, {failed} failed | Active tasks: {active_tasks}"
                    )
                    
        except Exception as e:
            logger.error(f"Failed to log status: {e}")
    
    async def _shutdown(self):
        """Gracefully shutdown the worker."""
        logger.info("Shutting down Insights Worker...")
        
        # Cancel all running tasks
        if self.processing_tasks:
            logger.info(f"Cancelling {len(self.processing_tasks)} running tasks...")
            
            for task in self.processing_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        logger.info("Insights Worker shutdown complete")
    
    async def process_all_retroactively(self) -> Dict[str, Any]:
        """Process all unprocessed documents retroactively (one-time operation)."""
        if not self.pipeline:
            await self.initialize()
        
        logger.info("Starting retroactive processing of all unprocessed documents...")
        
        try:
            # First, queue any unprocessed documents
            queue_result = self.supabase.rpc('queue_unprocessed_documents').execute()
            
            if queue_result.data:
                queued_count = queue_result.data if isinstance(queue_result.data, int) else queue_result.data[0]
                logger.info(f"Queued {queued_count} unprocessed documents")
            
            # Process the entire queue
            result = await self.pipeline.process_all_unprocessed_documents()
            
            logger.info(f"Retroactive processing complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in retroactive processing: {e}")
            return {'error': str(e)}


# Standalone worker functions

async def run_worker():
    """Run the insights worker as a standalone process."""
    worker = InsightsWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise


async def run_retroactive_processing():
    """Run retroactive processing once and exit."""
    worker = InsightsWorker()
    
    try:
        result = await worker.process_all_retroactively()
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        logger.error(f"Retroactive processing error: {e}")
        return {'error': str(e)}


@asynccontextmanager
async def managed_worker(polling_interval: int = 30):
    """Context manager for running worker alongside another service."""
    worker = InsightsWorker(polling_interval=polling_interval)
    
    # Start worker task
    worker_task = asyncio.create_task(worker.start())
    
    try:
        yield worker
    finally:
        # Graceful shutdown
        worker.running = False
        
        # Wait a moment for graceful shutdown
        try:
            await asyncio.wait_for(worker_task, timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Worker shutdown timeout, cancelling...")
            worker_task.cancel()
            
            try:
                await worker_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "retroactive":
        # Run retroactive processing once
        asyncio.run(run_retroactive_processing())
    else:
        # Run continuous worker
        asyncio.run(run_worker())