from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="The message to process")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the request"
    )


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="The generated response")
    request_id: UUID = Field(..., description="Unique identifier for the request")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the response"
    )


class WebhookRequest(BaseModel):
    """Webhook request model."""
    message: str = Field(..., description="The message to process")
    callback_url: HttpUrl = Field(..., description="URL to send the response to")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata for the request"
    )


class WebhookResponse(BaseModel):
    """Webhook response model."""
    track_id: UUID = Field(..., description="Tracking ID for the request")
    status: str = Field(
        default="processing",
        description="Status of the request (processing, completed, failed)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    response: Optional[str] = Field(default=None, description="The generated response")
    error: Optional[str] = Field(default=None, description="Error message if the request failed")


class WebhookStatusResponse(BaseModel):
    """Webhook status response model."""
    track_id: UUID = Field(..., description="Tracking ID for the request")
    status: str = Field(..., description="Status of the request")
    timestamp: datetime = Field(..., description="Timestamp of the status update")
    response: Optional[str] = Field(default=None, description="The generated response")
    error: Optional[str] = Field(default=None, description="Error message if the request failed")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(default="ok", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")