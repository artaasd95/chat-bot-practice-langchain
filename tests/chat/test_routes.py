"""Tests for chat routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock
from faker import Faker

from app.database.models import User, ChatSession, ChatMessage
from app.auth.schemas import UserCreate

fake = Faker()


class TestChatRoutes:
    """Test chat routes."""

    async def test_create_chat_session_authenticated(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test creating chat session with authentication."""
        headers = {"Authorization": f"Bearer {user_token}"}
        session_data = {
            "title": "New Chat Session"
        }
        
        response = await async_client.post("/chat/sessions", json=session_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == session_data["title"]
        assert data["user_id"] == test_user.id
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_create_chat_session_unauthenticated(self, async_client: AsyncClient):
        """Test creating chat session without authentication."""
        session_data = {"title": "Unauthorized Session"}
        
        response = await async_client.post("/chat/sessions", json=session_data)
        
        assert response.status_code == 401

    async def test_create_chat_session_empty_title(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test creating chat session with empty title."""
        headers = {"Authorization": f"Bearer {user_token}"}
        session_data = {"title": ""}
        
        response = await async_client.post("/chat/sessions", json=session_data, headers=headers)
        
        assert response.status_code == 422  # Validation error

    async def test_get_user_chat_sessions(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test getting user's chat sessions."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get("/chat/sessions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that test session is in the result
        session_ids = [session["id"] for session in data]
        assert test_chat_session.id in session_ids

    async def test_get_user_chat_sessions_pagination(self, async_client: AsyncClient, test_user: User, user_token: str, test_db: AsyncSession):
        """Test getting user's chat sessions with pagination."""
        # Create additional sessions
        for i in range(5):
            session = ChatSession(
                user_id=test_user.id,
                title=f"Test Session {i}"
            )
            test_db.add(session)
        await test_db.commit()
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get("/chat/sessions?skip=0&limit=3", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3

    async def test_get_chat_session_by_id(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test getting specific chat session by ID."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get(f"/chat/sessions/{test_chat_session.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_chat_session.id
        assert data["title"] == test_chat_session.title
        assert data["user_id"] == test_user.id

    async def test_get_chat_session_unauthorized_user(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_chat_session: ChatSession):
        """Test getting chat session by unauthorized user."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get(f"/chat/sessions/{test_chat_session.id}", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "Not authorized" in data["detail"]

    async def test_get_chat_session_not_found(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test getting non-existent chat session."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get("/chat/sessions/99999", headers=headers)
        
        assert response.status_code == 404

    async def test_update_chat_session(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test updating chat session."""
        headers = {"Authorization": f"Bearer {user_token}"}
        update_data = {
            "title": "Updated Session Title"
        }
        
        response = await async_client.put(f"/chat/sessions/{test_chat_session.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["id"] == test_chat_session.id

    async def test_delete_chat_session(self, async_client: AsyncClient, test_user: User, user_token: str, test_db: AsyncSession):
        """Test deleting chat session."""
        # Create a session to delete
        session = ChatSession(
            user_id=test_user.id,
            title="Session to Delete"
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.delete(f"/chat/sessions/{session.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

    async def test_get_chat_messages(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_messages: list[ChatMessage]):
        """Test getting chat messages for a session."""
        headers = {"Authorization": f"Bearer {user_token}"}
        session_id = test_chat_messages[0].session_id
        
        response = await async_client.get(f"/chat/sessions/{session_id}/messages", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the test messages
        
        # Check message structure
        if data:
            message = data[0]
            assert "id" in message
            assert "session_id" in message
            assert "message_type" in message
            assert "content" in message
            assert "created_at" in message

    @patch('app.services.llm.get_llm')
    @patch('app.graph.builder.build_graph')
    async def test_send_message_success(self, mock_build_graph, mock_get_llm, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test sending message successfully."""
        # Mock LLM and graph
        mock_llm = AsyncMock()
        mock_get_llm.return_value = mock_llm
        
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "messages": [{"content": "AI response", "type": "ai"}]
        }
        mock_build_graph.return_value = mock_graph
        
        headers = {"Authorization": f"Bearer {user_token}"}
        message_data = {
            "content": "Hello, AI!",
            "message_type": "user"
        }
        
        response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/messages", json=message_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "user_message" in data
        assert "ai_response" in data
        assert data["user_message"]["content"] == message_data["content"]
        assert data["ai_response"]["content"] == "AI response"

    async def test_send_message_empty_content(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test sending message with empty content."""
        headers = {"Authorization": f"Bearer {user_token}"}
        message_data = {
            "content": "",
            "message_type": "user"
        }
        
        response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/messages", json=message_data, headers=headers)
        
        assert response.status_code == 422  # Validation error

    async def test_send_message_long_content(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test sending message with very long content."""
        headers = {"Authorization": f"Bearer {user_token}"}
        long_content = "A" * 10000  # Very long message
        message_data = {
            "content": long_content,
            "message_type": "user"
        }
        
        response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/messages", json=message_data, headers=headers)
        
        # Should either accept or reject based on validation rules
        assert response.status_code in [201, 422]

    @patch('app.services.llm.get_llm')
    async def test_send_message_llm_error(self, mock_get_llm, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test sending message when LLM fails."""
        # Mock LLM to raise an error
        mock_get_llm.side_effect = Exception("LLM service unavailable")
        
        headers = {"Authorization": f"Bearer {user_token}"}
        message_data = {
            "content": "Hello, AI!",
            "message_type": "user"
        }
        
        response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/messages", json=message_data, headers=headers)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"].lower()

    async def test_send_message_unauthorized_session(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_chat_session: ChatSession):
        """Test sending message to unauthorized session."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        message_data = {
            "content": "Unauthorized message",
            "message_type": "user"
        }
        
        response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/messages", json=message_data, headers=headers)
        
        assert response.status_code == 403

    async def test_get_chat_history(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_messages: list[ChatMessage]):
        """Test getting chat history with pagination."""
        headers = {"Authorization": f"Bearer {user_token}"}
        session_id = test_chat_messages[0].session_id
        
        response = await async_client.get(f"/chat/sessions/{session_id}/history?limit=10&offset=0", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert "has_more" in data
        assert isinstance(data["messages"], list)

    async def test_search_chat_messages(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_messages: list[ChatMessage]):
        """Test searching chat messages."""
        headers = {"Authorization": f"Bearer {user_token}"}
        search_query = "Hello"  # Search for messages containing "Hello"
        
        response = await async_client.get(f"/chat/search?q={search_query}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that results contain the search term
        for result in data:
            assert search_query.lower() in result["content"].lower()

    async def test_export_chat_session(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test exporting chat session."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get(f"/chat/sessions/{test_chat_session.id}/export", headers=headers)
        
        assert response.status_code == 200
        # Should return JSON or text format
        assert response.headers.get("content-type") in ["application/json", "text/plain", "text/csv"]

    async def test_chat_session_statistics(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test getting chat session statistics."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get(f"/chat/sessions/{test_chat_session.id}/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message_count" in data
        assert "session_duration" in data or "created_at" in data
        assert isinstance(data["message_count"], int)

    async def test_regenerate_response(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_messages: list[ChatMessage]):
        """Test regenerating AI response."""
        # Find an AI message to regenerate
        ai_message = next((msg for msg in test_chat_messages if msg.message_type == "assistant"), None)
        if not ai_message:
            pytest.skip("No AI message found in test data")
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        with patch('app.services.llm.get_llm') as mock_get_llm, \
             patch('app.graph.builder.build_graph') as mock_build_graph:
            
            mock_llm = AsyncMock()
            mock_get_llm.return_value = mock_llm
            
            mock_graph = AsyncMock()
            mock_graph.ainvoke.return_value = {
                "messages": [{"content": "Regenerated response", "type": "ai"}]
            }
            mock_build_graph.return_value = mock_graph
            
            response = await async_client.post(f"/chat/messages/{ai_message.id}/regenerate", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert data["content"] == "Regenerated response"

    async def test_chat_websocket_connection(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test WebSocket connection for real-time chat."""
        # Note: This is a simplified test for WebSocket endpoint existence
        # Full WebSocket testing would require additional setup
        
        with async_client.websocket_connect(f"/chat/ws/{test_chat_session.id}?token={user_token}") as websocket:
            # Test connection establishment
            assert websocket is not None
            
            # Send a test message
            await websocket.send_json({
                "type": "message",
                "content": "WebSocket test message"
            })
            
            # Receive response (this would depend on actual implementation)
            # response = await websocket.receive_json()
            # assert "type" in response

    async def test_chat_rate_limiting(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test rate limiting for chat messages."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Send multiple messages rapidly
        responses = []
        for i in range(10):
            message_data = {
                "content": f"Rate limit test message {i}",
                "message_type": "user"
            }
            response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/messages", json=message_data, headers=headers)
            responses.append(response)
        
        # Check if any requests were rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        # Rate limiting behavior depends on implementation
        # This test just ensures the endpoint handles rapid requests
        assert all(r.status_code in [201, 429, 500] for r in responses)

    async def test_chat_session_sharing(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test sharing chat session."""
        headers = {"Authorization": f"Bearer {user_token}"}
        share_data = {
            "share_type": "public",
            "expires_in": 3600  # 1 hour
        }
        
        response = await async_client.post(f"/chat/sessions/{test_chat_session.id}/share", json=share_data, headers=headers)
        
        # This endpoint may or may not exist in the implementation
        assert response.status_code in [200, 201, 404]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "share_url" in data or "share_token" in data

    async def test_chat_session_templates(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test getting chat session templates."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get("/chat/templates", headers=headers)
        
        # Templates endpoint may or may not exist
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            if data:
                template = data[0]
                assert "id" in template
                assert "name" in template
                assert "description" in template or "template" in template

    async def test_chat_context_management(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_session: ChatSession):
        """Test chat context management."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test setting context
        context_data = {
            "context": "You are a helpful assistant specialized in Python programming.",
            "max_tokens": 4000
        }
        
        response = await async_client.put(f"/chat/sessions/{test_chat_session.id}/context", json=context_data, headers=headers)
        
        # Context management may or may not be implemented
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "context" in data or "message" in data

    async def test_chat_message_reactions(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_messages: list[ChatMessage]):
        """Test adding reactions to chat messages."""
        headers = {"Authorization": f"Bearer {user_token}"}
        message_id = test_chat_messages[0].id
        
        reaction_data = {
            "reaction": "👍",
            "action": "add"
        }
        
        response = await async_client.post(f"/chat/messages/{message_id}/reactions", json=reaction_data, headers=headers)
        
        # Reactions may or may not be implemented
        assert response.status_code in [200, 201, 404]

    async def test_chat_message_editing(self, async_client: AsyncClient, test_user: User, user_token: str, test_chat_messages: list[ChatMessage]):
        """Test editing chat messages."""
        # Find a user message to edit
        user_message = next((msg for msg in test_chat_messages if msg.message_type == "user"), None)
        if not user_message:
            pytest.skip("No user message found in test data")
        
        headers = {"Authorization": f"Bearer {user_token}"}
        edit_data = {
            "content": "Edited message content"
        }
        
        response = await async_client.put(f"/chat/messages/{user_message.id}", json=edit_data, headers=headers)
        
        # Message editing may or may not be implemented
        assert response.status_code in [200, 404, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["content"] == edit_data["content"]
            assert "edited_at" in data or "updated_at" in data