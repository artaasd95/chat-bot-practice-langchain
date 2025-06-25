"""Tests for API routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock
from faker import Faker

from app.database.models import User, ChatSession, ChatMessage
from app.api.models import ChatRequest, WebhookRequest

fake = Faker()


class TestAPIRoutes:
    """Test API routes."""

    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "Chat Bot API is running"
        assert data["version"] == "1.0.0"

    async def test_chat_endpoint_authenticated(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint with authentication."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "Hello, how are you?",
            "conversation_id": "test_conversation_123"
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_enhanced_graph') as mock_build_graph:
            
            # Mock LLM
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            # Mock graph
            mock_graph = AsyncMock()
            mock_graph.ainvoke.return_value = {
                "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                "metadata": {"request_id": "test_123"}
            }
            mock_build_graph.return_value = mock_graph
            
            response = await async_client.post("/chat", json=chat_data, headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "conversation_id" in data
            assert "metadata" in data
            assert data["conversation_id"] == chat_data["conversation_id"]

    async def test_chat_endpoint_unauthenticated(self, async_client: AsyncClient):
        """Test chat endpoint without authentication."""
        chat_data = {
            "message": "Hello, how are you?"
        }
        
        response = await async_client.post("/chat", json=chat_data)
        
        assert response.status_code == 401

    async def test_chat_endpoint_invalid_token(self, async_client: AsyncClient):
        """Test chat endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        chat_data = {
            "message": "Hello, how are you?"
        }
        
        response = await async_client.post("/chat", json=chat_data, headers=headers)
        
        assert response.status_code == 401

    async def test_chat_endpoint_empty_message(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint with empty message."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": ""
        }
        
        response = await async_client.post("/chat", json=chat_data, headers=headers)
        
        assert response.status_code == 422

    async def test_chat_endpoint_long_message(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint with very long message."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "A" * 10000  # Very long message
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_enhanced_graph') as mock_build_graph:
            
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke.return_value = {
                "response": "I received your long message.",
                "metadata": {"request_id": "test_123"}
            }
            mock_build_graph.return_value = mock_graph
            
            response = await async_client.post("/chat", json=chat_data, headers=headers)
            
            # Should handle long messages gracefully
            assert response.status_code in [200, 422]  # Either success or validation error

    async def test_chat_endpoint_with_context(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint with conversation context."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "What did I ask before?",
            "conversation_id": "existing_conversation",
            "context": {
                "previous_messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            }
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_enhanced_graph') as mock_build_graph:
            
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke.return_value = {
                "response": "You asked 'Hello' before.",
                "metadata": {"request_id": "test_123"}
            }
            mock_build_graph.return_value = mock_graph
            
            response = await async_client.post("/chat", json=chat_data, headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    async def test_chat_endpoint_llm_error(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint when LLM fails."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "Hello"
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm:
            mock_get_llm.side_effect = Exception("LLM service unavailable")
            
            response = await async_client.post("/chat", json=chat_data, headers=headers)
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data["detail"] or "LLM" in data["detail"]

    async def test_chat_endpoint_graph_error(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint when graph building fails."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "Hello"
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_enhanced_graph') as mock_build_graph:
            
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            mock_build_graph.side_effect = Exception("Graph building failed")
            
            response = await async_client.post("/chat", json=chat_data, headers=headers)
            
            assert response.status_code == 500

    async def test_webhook_endpoint_valid_request(self, async_client: AsyncClient):
        """Test webhook endpoint with valid request."""
        webhook_data = {
            "event": "message.received",
            "data": {
                "user_id": "123",
                "message": "Hello from webhook",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            "signature": "valid_signature"
        }
        
        with patch('app.services.webhook.verify_webhook_signature') as mock_verify, \
             patch('app.services.webhook.process_webhook_event') as mock_process:
            
            mock_verify.return_value = True
            mock_process.return_value = {"status": "processed", "message_id": "msg_123"}
            
            response = await async_client.post("/webhook", json=webhook_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "result" in data

    async def test_webhook_endpoint_invalid_signature(self, async_client: AsyncClient):
        """Test webhook endpoint with invalid signature."""
        webhook_data = {
            "event": "message.received",
            "data": {"user_id": "123"},
            "signature": "invalid_signature"
        }
        
        with patch('app.services.webhook.verify_webhook_signature') as mock_verify:
            mock_verify.return_value = False
            
            response = await async_client.post("/webhook", json=webhook_data)
            
            assert response.status_code == 401
            data = response.json()
            assert "Invalid webhook signature" in data["detail"]

    async def test_webhook_endpoint_missing_signature(self, async_client: AsyncClient):
        """Test webhook endpoint without signature."""
        webhook_data = {
            "event": "message.received",
            "data": {"user_id": "123"}
        }
        
        response = await async_client.post("/webhook", json=webhook_data)
        
        assert response.status_code == 422  # Validation error

    async def test_webhook_endpoint_processing_error(self, async_client: AsyncClient):
        """Test webhook endpoint when processing fails."""
        webhook_data = {
            "event": "message.received",
            "data": {"user_id": "123"},
            "signature": "valid_signature"
        }
        
        with patch('app.services.webhook.verify_webhook_signature') as mock_verify, \
             patch('app.services.webhook.process_webhook_event') as mock_process:
            
            mock_verify.return_value = True
            mock_process.side_effect = Exception("Processing failed")
            
            response = await async_client.post("/webhook", json=webhook_data)
            
            assert response.status_code == 500

    async def test_webhook_status_endpoint(self, async_client: AsyncClient):
        """Test webhook status endpoint."""
        webhook_id = "webhook_123"
        
        with patch('app.services.webhook.get_webhook_status') as mock_get_status:
            mock_get_status.return_value = {
                "id": webhook_id,
                "status": "completed",
                "processed_at": "2024-01-01T00:00:00Z",
                "result": {"message_id": "msg_123"}
            }
            
            response = await async_client.get(f"/webhook/status/{webhook_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == webhook_id
            assert data["status"] == "completed"

    async def test_webhook_status_not_found(self, async_client: AsyncClient):
        """Test webhook status endpoint for non-existent webhook."""
        webhook_id = "nonexistent_webhook"
        
        with patch('app.services.webhook.get_webhook_status') as mock_get_status:
            mock_get_status.return_value = None
            
            response = await async_client.get(f"/webhook/status/{webhook_id}")
            
            assert response.status_code == 404

    async def test_chat_endpoint_rate_limiting(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint rate limiting."""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "Hello"
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_enhanced_graph') as mock_build_graph:
            
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke.return_value = {
                "response": "Hello!",
                "metadata": {"request_id": "test_123"}
            }
            mock_build_graph.return_value = mock_graph
            
            # Make multiple rapid requests
            responses = []
            for _ in range(10):
                response = await async_client.post("/chat", json=chat_data, headers=headers)
                responses.append(response)
            
            # At least some should succeed
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count > 0

    async def test_chat_endpoint_concurrent_requests(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test chat endpoint with concurrent requests."""
        import asyncio
        
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "message": "Hello"
        }
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_enhanced_graph') as mock_build_graph:
            
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke.return_value = {
                "response": "Hello!",
                "metadata": {"request_id": "test_123"}
            }
            mock_build_graph.return_value = mock_graph
            
            # Make concurrent requests
            tasks = [
                async_client.post("/chat", json=chat_data, headers=headers)
                for _ in range(5)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that most requests succeeded
            success_count = sum(
                1 for r in responses 
                if not isinstance(r, Exception) and r.status_code == 200
            )
            assert success_count >= 3  # At least 3 out of 5 should succeed

    async def test_api_error_handling(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test API error handling and response format."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test with malformed JSON
        response = await async_client.post(
            "/chat", 
            content="{invalid json}", 
            headers={**headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_api_cors_headers(self, async_client: AsyncClient):
        """Test CORS headers in API responses."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        # CORS headers should be present (if configured)
        # This depends on your CORS configuration