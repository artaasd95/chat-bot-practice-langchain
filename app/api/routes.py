from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import (
    ChatRequest, ChatResponse, WebhookRequest, WebhookResponse,
    WebhookStatusResponse, HealthResponse
)
from app.config import settings
from app.auth.dependencies import get_current_active_user, get_optional_current_user
from app.database.database import get_db
from app.database.models import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Chat Bot API is running",
        version="1.0.0"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """Direct chat endpoint - requires authentication."""
    try:
        # Import here to avoid circular imports
        from app.main import graph
        
        if graph is None:
            raise HTTPException(status_code=500, detail="Graph not initialized")
        
        # Prepare the input for the graph
        graph_input = {
            "messages": [{"role": "user", "content": request.message}],
            "user_id": str(current_user.id),
            "user_email": current_user.email
        }
        
        # Invoke the graph
        result = await graph.ainvoke(graph_input)
        
        # Extract the response
        if "messages" in result and result["messages"]:
            response_message = result["messages"][-1]["content"]
        else:
            response_message = "I'm sorry, I couldn't process your request."
        
        # TODO: Save chat session and message to database
        # This can be implemented later to store chat history
        
        return ChatResponse(
            response=response_message,
            conversation_id=request.conversation_id or f"conv_{current_user.id}_{request.message[:10]}"
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/webhook/chat", response_model=WebhookResponse)
async def webhook_chat(
    request: WebhookRequest,
    current_user: User = Depends(get_optional_current_user)
) -> WebhookResponse:
    """Webhook chat endpoint for external integrations."""
    try:
        # Validate webhook secret if configured
        if settings.WEBHOOK_SECRET and request.secret != settings.WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
        # Import here to avoid circular imports
        from app.main import graph
        
        if graph is None:
            raise HTTPException(status_code=500, detail="Graph not initialized")
        
        # Use authenticated user if available, otherwise use webhook user
        user_id = str(current_user.id) if current_user else "webhook_user"
        user_email = current_user.email if current_user else "webhook@system.com"
        
        # Prepare the input for the graph
        graph_input = {
            "messages": [{"role": "user", "content": request.message}],
            "user_id": user_id,
            "user_email": user_email,
            "webhook_id": request.webhook_id
        }
        
        # Invoke the graph
        result = await graph.ainvoke(graph_input)
        
        # Extract the response
        if "messages" in result and result["messages"]:
            response_message = result["messages"][-1]["content"]
        else:
            response_message = "I'm sorry, I couldn't process your request."
        
        return WebhookResponse(
            success=True,
            response=response_message,
            webhook_id=request.webhook_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in webhook chat endpoint: {str(e)}")
        return WebhookResponse(
            success=False,
            response=f"Error processing request: {str(e)}",
            webhook_id=request.webhook_id
        )


@router.get("/webhook/status", response_model=WebhookStatusResponse)
async def webhook_status():
    """Get webhook status."""
    return WebhookStatusResponse(
        active=True,
        message="Webhook endpoint is active"
    )