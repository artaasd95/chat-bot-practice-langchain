from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException, status
from langchain_core.messages import HumanMessage
import asyncio
from uuid import uuid4, UUID
from datetime import datetime
from loguru import logger

from app.api.models import (
    ChatRequest,
    ChatResponse,
    WebhookRequest,
    WebhookResponse,
    WebhookStatusResponse,
    HealthResponse,
)
from app.services.webhook import send_webhook_response
from app import __version__

router = APIRouter()

# In-memory store for tracking webhook requests
# In a production environment, this would be replaced with a persistent store
webhook_requests = {}


async def get_graph(request: Request):
    """Get the graph from the app state."""
    if not hasattr(request.app.state, "graph"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Graph not initialized"
        )
    return request.app.state.graph


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(version=__version__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, graph=Depends(get_graph)):
    """Direct response chat endpoint."""
    request_id = uuid4()
    logger.info(f"Received chat request: {request.message} (ID: {request_id})")
    
    # Create a human message
    message = HumanMessage(content=request.message)
    
    # Prepare the initial state
    state = {
        "messages": [message],
        "metadata": {**(request.metadata or {}), "request_id": str(request_id)}
    }
    
    try:
        # Execute the graph
        result = await graph.ainvoke(state)
        
        logger.info(f"Chat response generated for request ID: {request_id}")
        
        return ChatResponse(
            response=result["response"],
            request_id=request_id,
            metadata=result.get("metadata")
        )
    except Exception as e:
        logger.error(f"Error processing chat request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


@router.post("/webhook", response_model=WebhookResponse)
async def webhook_chat(request: WebhookRequest, background_tasks: BackgroundTasks, graph=Depends(get_graph)):
    """Webhook chat endpoint that processes the request asynchronously."""
    # Use track_id from metadata if provided, otherwise generate a new one
    metadata = request.metadata or {}
    track_id = UUID(metadata.get("track_id")) if metadata.get("track_id") else uuid4()
    logger.info(f"Received webhook request: {request.message} (Track ID: {track_id})")
    
    # Create a human message
    message = HumanMessage(content=request.message)
    
    # Prepare the initial state
    state = {
        "messages": [message],
        "metadata": {
            **metadata,
            "track_id": str(track_id),
            "callback_url": str(request.callback_url)
        }
    }
    
    # Store initial status
    webhook_requests[str(track_id)] = WebhookStatusResponse(
        track_id=track_id,
        status="processing",
        timestamp=datetime.utcnow()
    )
    
    # Add the task to background tasks
    background_tasks.add_task(
        process_webhook_request,
        state,
        graph,
        str(request.callback_url),
        track_id
    )
    
    logger.info(f"Webhook request queued with track_id: {track_id}")
    
    return WebhookResponse(track_id=track_id)


async def process_webhook_request(state, graph, callback_url, track_id):
    """Process a webhook request in the background."""
    track_id_str = str(track_id)
    logger.info(f"Processing webhook request with track_id: {track_id_str}")
    
    try:
        # Execute the graph
        result = await graph.ainvoke(state)
        
        # Update status
        webhook_requests[track_id_str] = WebhookStatusResponse(
            track_id=track_id,
            status="completed",
            timestamp=datetime.utcnow(),
            response=result["response"]
        )
        
        # Send the response to the callback URL
        await send_webhook_response(callback_url, {
            "track_id": track_id_str,
            "response": result["response"],
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": result.get("metadata")
        })
        
        logger.info(f"Webhook response sent for track_id: {track_id_str}")
    except Exception as e:
        logger.error(f"Error processing webhook request with track_id {track_id_str}: {str(e)}")
        
        # Update status
        webhook_requests[track_id_str] = WebhookStatusResponse(
            track_id=track_id,
            status="failed",
            timestamp=datetime.utcnow(),
            error=str(e)
        )
        
        # Send error response
        try:
            await send_webhook_response(callback_url, {
                "track_id": track_id_str,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as webhook_error:
            logger.error(f"Failed to send error webhook for {track_id_str}: {str(webhook_error)}")


@router.get("/webhook/{track_id}", response_model=WebhookStatusResponse)
async def get_webhook_status(track_id: UUID):
    """Get the status of a webhook request."""
    track_id_str = str(track_id)
    if track_id_str not in webhook_requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with track_id {track_id} not found"
        )
    
    return webhook_requests[track_id_str]