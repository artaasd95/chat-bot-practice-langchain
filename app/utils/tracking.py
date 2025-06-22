from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
import asyncio
from loguru import logger

from app.api.models import WebhookStatusResponse


class RequestTracker:
    """Utility class for tracking webhook requests.
    
    This is a simple in-memory implementation. In a production environment,
    this would be replaced with a persistent store like Redis or a database.
    """
    
    def __init__(self):
        self._requests: Dict[str, WebhookStatusResponse] = {}
        self._lock = asyncio.Lock()
    
    async def add_request(self, track_id: UUID, status: str = "processing") -> None:
        """Add a new request to the tracker.
        
        Args:
            track_id: The tracking ID for the request.
            status: The initial status of the request.
        """
        async with self._lock:
            self._requests[str(track_id)] = WebhookStatusResponse(
                track_id=track_id,
                status=status,
                timestamp=datetime.utcnow()
            )
            logger.debug(f"Added request with track_id: {track_id}")
    
    async def update_request(self, track_id: UUID, **kwargs) -> None:
        """Update an existing request.
        
        Args:
            track_id: The tracking ID for the request.
            **kwargs: The fields to update.
        """
        track_id_str = str(track_id)
        async with self._lock:
            if track_id_str not in self._requests:
                logger.warning(f"Attempted to update non-existent request: {track_id}")
                return
            
            current = self._requests[track_id_str].dict()
            current.update(kwargs)
            current["timestamp"] = datetime.utcnow()  # Always update timestamp
            
            self._requests[track_id_str] = WebhookStatusResponse(**current)
            logger.debug(f"Updated request with track_id: {track_id}")
    
    async def get_request(self, track_id: UUID) -> Optional[WebhookStatusResponse]:
        """Get a request by its tracking ID.
        
        Args:
            track_id: The tracking ID for the request.
            
        Returns:
            The request status, or None if not found.
        """
        async with self._lock:
            return self._requests.get(str(track_id))
    
    async def cleanup_old_requests(self, max_age_hours: int = 24) -> int:
        """Clean up old requests.
        
        Args:
            max_age_hours: The maximum age of requests to keep, in hours.
            
        Returns:
            The number of requests removed.
        """
        cutoff = datetime.utcnow() - datetime.timedelta(hours=max_age_hours)
        to_remove = []
        
        async with self._lock:
            for track_id, request in self._requests.items():
                if request.timestamp < cutoff:
                    to_remove.append(track_id)
            
            for track_id in to_remove:
                del self._requests[track_id]
            
            logger.info(f"Cleaned up {len(to_remove)} old requests")
            return len(to_remove)


# Create a singleton instance
request_tracker = RequestTracker()