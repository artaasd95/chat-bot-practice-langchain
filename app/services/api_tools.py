"""API Tools service for making REST API calls from the chat graph."""

import json
import aiohttp
from typing import Dict, Any, Optional, List
from loguru import logger
from pydantic import BaseModel, HttpUrl, validator
from enum import Enum


class HttpMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class APIRequest(BaseModel):
    """Model for API request configuration."""
    url: HttpUrl
    method: HttpMethod = HttpMethod.GET
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    
    @validator('headers')
    def validate_headers(cls, v):
        if v is None:
            return {}
        return v


class APIResponse(BaseModel):
    """Model for API response."""
    status_code: int
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    error: Optional[str] = None
    success: bool


class APIToolsService:
    """Service for making REST API calls."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make an HTTP request.
        
        Args:
            request: The API request configuration.
            
        Returns:
            APIResponse: The response from the API.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            logger.info(f"Making {request.method} request to {request.url}")
            
            # Prepare request parameters
            kwargs = {
                'timeout': aiohttp.ClientTimeout(total=request.timeout),
                'headers': request.headers or {}
            }
            
            if request.params:
                kwargs['params'] = request.params
                
            if request.data and request.method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
                kwargs['json'] = request.data
                kwargs['headers']['Content-Type'] = 'application/json'
            
            # Make the request
            async with self.session.request(
                method=request.method.value,
                url=str(request.url),
                **kwargs
            ) as response:
                
                # Get response content
                try:
                    response_data = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    response_data = None
                    
                response_text = await response.text()
                
                # Create response object
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    text=response_text,
                    success=200 <= response.status < 300
                )
                
                if api_response.success:
                    logger.info(f"API request successful: {response.status}")
                else:
                    logger.warning(f"API request failed: {response.status}")
                    api_response.error = f"HTTP {response.status}: {response.reason}"
                
                return api_response
                
        except aiohttp.ClientError as e:
            logger.error(f"Client error during API request: {str(e)}")
            return APIResponse(
                status_code=0,
                error=f"Client error: {str(e)}",
                success=False
            )
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
            return APIResponse(
                status_code=0,
                error=f"Unexpected error: {str(e)}",
                success=False
            )
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None


def parse_api_request_from_text(text: str) -> Optional[APIRequest]:
    """Parse API request from LLM text response.
    
    Expected format:
    API_CALL: {"url": "https://api.example.com/data", "method": "GET", "headers": {...}, "params": {...}}
    
    Args:
        text: The text to parse.
        
    Returns:
        APIRequest if found and valid, None otherwise.
    """
    try:
        # Look for API_CALL: pattern
        if "API_CALL:" not in text:
            return None
            
        # Extract JSON part
        start_idx = text.find("API_CALL:") + len("API_CALL:")
        json_part = text[start_idx:].strip()
        
        # Find the JSON object
        brace_count = 0
        json_end = -1
        for i, char in enumerate(json_part):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        if json_end == -1:
            return None
            
        json_str = json_part[:json_end]
        
        # Parse JSON
        api_data = json.loads(json_str)
        
        # Create APIRequest
        return APIRequest(**api_data)
        
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse API request from text: {str(e)}")
        return None


def should_make_api_call(text: str) -> bool:
    """Check if the text contains an API call request.
    
    Args:
        text: The text to check.
        
    Returns:
        True if an API call should be made, False otherwise.
    """
    return "API_CALL:" in text


# Global service instance
_api_service: Optional[APIToolsService] = None


async def get_api_service() -> APIToolsService:
    """Get or create the global API service instance."""
    global _api_service
    if _api_service is None:
        _api_service = APIToolsService()
    return _api_service


async def cleanup_api_service():
    """Cleanup the global API service instance."""
    global _api_service
    if _api_service:
        await _api_service.close()
        _api_service = None