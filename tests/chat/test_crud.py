"""Tests for chat CRUD operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from faker import Faker

from app.database.models import User, ChatSession, ChatMessage
from app.auth.schemas import UserCreate
from app.chat import crud

fake = Faker()


class TestChatCrud:
    """Test chat CRUD operations."""

    async def test_create_chat_session(self, test_db: AsyncSession, test_user: User):
        """Test creating a new chat session."""
        session_data = {
            "title": "Test Chat Session",
            "user_id": test_user.id
        }
        
        session = await crud.create_chat_session(test_db, session_data)
        
        assert session.title == session_data["title"]
        assert session.user_id == session_data["user_id"]
        assert session.is_active is True
        assert session.id is not None
        assert session.created_at is not None

    async def test_create_chat_session_with_optional_fields(self, test_db: AsyncSession, test_user: User):
        """Test creating chat session with optional fields."""
        session_data = {
            "title": "Advanced Chat Session",
            "user_id": test_user.id,
            "description": "A test session with description",
            "tags": ["test", "advanced"]
        }
        
        session = await crud.create_chat_session(test_db, session_data)
        
        assert session.title == session_data["title"]
        assert session.description == session_data["description"]
        assert session.tags == session_data["tags"]

    async def test_get_chat_session_by_id_existing(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test getting existing chat session by ID."""
        session = await crud.get_chat_session_by_id(test_db, test_chat_session.id)
        
        assert session is not None
        assert session.id == test_chat_session.id
        assert session.title == test_chat_session.title
        assert session.user_id == test_chat_session.user_id

    async def test_get_chat_session_by_id_non_existing(self, test_db: AsyncSession):
        """Test getting non-existing chat session by ID."""
        session = await crud.get_chat_session_by_id(test_db, 99999)
        
        assert session is None

    async def test_get_user_chat_sessions(self, test_db: AsyncSession, test_user: User, test_chat_session: ChatSession):
        """Test getting all chat sessions for a user."""
        sessions = await crud.get_user_chat_sessions(test_db, test_user.id)
        
        assert len(sessions) >= 1
        session_ids = [session.id for session in sessions]
        assert test_chat_session.id in session_ids
        
        # Verify all sessions belong to the user
        for session in sessions:
            assert session.user_id == test_user.id

    async def test_get_user_chat_sessions_with_pagination(self, test_db: AsyncSession, test_user: User):
        """Test getting user chat sessions with pagination."""
        # Create additional sessions
        for i in range(5):
            session_data = {
                "title": f"Pagination Test Session {i}",
                "user_id": test_user.id
            }
            await crud.create_chat_session(test_db, session_data)
        
        # Test pagination
        sessions_page1 = await crud.get_user_chat_sessions(test_db, test_user.id, skip=0, limit=3)
        sessions_page2 = await crud.get_user_chat_sessions(test_db, test_user.id, skip=3, limit=3)
        
        assert len(sessions_page1) <= 3
        assert len(sessions_page2) <= 3
        
        # Ensure no overlap between pages
        page1_ids = {session.id for session in sessions_page1}
        page2_ids = {session.id for session in sessions_page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_get_user_chat_sessions_only_active(self, test_db: AsyncSession, test_user: User):
        """Test getting only active chat sessions for a user."""
        # Create active and inactive sessions
        active_session_data = {
            "title": "Active Session",
            "user_id": test_user.id
        }
        inactive_session_data = {
            "title": "Inactive Session",
            "user_id": test_user.id
        }
        
        active_session = await crud.create_chat_session(test_db, active_session_data)
        inactive_session = await crud.create_chat_session(test_db, inactive_session_data)
        
        # Deactivate one session
        inactive_session.is_active = False
        await test_db.commit()
        
        # Get only active sessions
        active_sessions = await crud.get_user_chat_sessions(test_db, test_user.id, active_only=True)
        
        session_ids = [session.id for session in active_sessions]
        assert active_session.id in session_ids
        assert inactive_session.id not in session_ids

    async def test_update_chat_session(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test updating chat session."""
        update_data = {
            "title": "Updated Session Title",
            "description": "Updated description"
        }
        
        updated_session = await crud.update_chat_session(test_db, test_chat_session.id, update_data)
        
        assert updated_session is not None
        assert updated_session.title == update_data["title"]
        assert updated_session.description == update_data["description"]
        assert updated_session.id == test_chat_session.id

    async def test_update_chat_session_partial(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test partial update of chat session."""
        original_title = test_chat_session.title
        update_data = {
            "description": "Only updating description"
        }
        
        updated_session = await crud.update_chat_session(test_db, test_chat_session.id, update_data)
        
        assert updated_session is not None
        assert updated_session.title == original_title  # Should remain unchanged
        assert updated_session.description == update_data["description"]

    async def test_update_chat_session_non_existing(self, test_db: AsyncSession):
        """Test updating non-existing chat session."""
        update_data = {"title": "Non-existing Session"}
        
        updated_session = await crud.update_chat_session(test_db, 99999, update_data)
        
        assert updated_session is None

    async def test_delete_chat_session(self, test_db: AsyncSession, test_user: User):
        """Test deleting chat session."""
        # Create a session to delete
        session_data = {
            "title": "Session to Delete",
            "user_id": test_user.id
        }
        session_to_delete = await crud.create_chat_session(test_db, session_data)
        
        # Delete the session
        result = await crud.delete_chat_session(test_db, session_to_delete.id)
        
        assert result is True
        
        # Verify session is deleted
        deleted_session = await crud.get_chat_session_by_id(test_db, session_to_delete.id)
        assert deleted_session is None

    async def test_delete_chat_session_non_existing(self, test_db: AsyncSession):
        """Test deleting non-existing chat session."""
        result = await crud.delete_chat_session(test_db, 99999)
        
        assert result is False

    async def test_deactivate_chat_session(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test deactivating chat session."""
        # Ensure session is active first
        test_chat_session.is_active = True
        await test_db.commit()
        
        result = await crud.deactivate_chat_session(test_db, test_chat_session.id)
        
        assert result is True
        
        # Refresh session from database
        await test_db.refresh(test_chat_session)
        assert test_chat_session.is_active is False

    async def test_activate_chat_session(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test activating chat session."""
        # Deactivate session first
        test_chat_session.is_active = False
        await test_db.commit()
        
        result = await crud.activate_chat_session(test_db, test_chat_session.id)
        
        assert result is True
        
        # Refresh session from database
        await test_db.refresh(test_chat_session)
        assert test_chat_session.is_active is True

    async def test_create_chat_message(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test creating a new chat message."""
        message_data = {
            "session_id": test_chat_session.id,
            "message_type": "user",
            "content": "Test message content"
        }
        
        message = await crud.create_chat_message(test_db, message_data)
        
        assert message.session_id == message_data["session_id"]
        assert message.message_type == message_data["message_type"]
        assert message.content == message_data["content"]
        assert message.id is not None
        assert message.created_at is not None

    async def test_create_chat_message_with_metadata(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test creating chat message with metadata."""
        message_data = {
            "session_id": test_chat_session.id,
            "message_type": "assistant",
            "content": "AI response with metadata",
            "metadata": {
                "model": "gpt-4",
                "tokens_used": 150,
                "response_time": 2.5
            }
        }
        
        message = await crud.create_chat_message(test_db, message_data)
        
        assert message.metadata == message_data["metadata"]
        assert message.metadata["model"] == "gpt-4"
        assert message.metadata["tokens_used"] == 150

    async def test_get_chat_message_by_id(self, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test getting chat message by ID."""
        test_message = test_chat_messages[0]
        
        message = await crud.get_chat_message_by_id(test_db, test_message.id)
        
        assert message is not None
        assert message.id == test_message.id
        assert message.content == test_message.content
        assert message.message_type == test_message.message_type

    async def test_get_chat_message_by_id_non_existing(self, test_db: AsyncSession):
        """Test getting non-existing chat message by ID."""
        message = await crud.get_chat_message_by_id(test_db, 99999)
        
        assert message is None

    async def test_get_session_messages(self, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test getting all messages for a session."""
        session_id = test_chat_messages[0].session_id
        
        messages = await crud.get_session_messages(test_db, session_id)
        
        assert len(messages) >= 2  # At least the test messages
        
        # Verify all messages belong to the session
        for message in messages:
            assert message.session_id == session_id
        
        # Check that test messages are included
        message_contents = [msg.content for msg in messages]
        assert any("Hello" in content for content in message_contents)
        assert any("Hi there" in content for content in message_contents)

    async def test_get_session_messages_with_pagination(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test getting session messages with pagination."""
        # Create additional messages
        for i in range(10):
            message_data = {
                "session_id": test_chat_session.id,
                "message_type": "user" if i % 2 == 0 else "assistant",
                "content": f"Pagination test message {i}"
            }
            await crud.create_chat_message(test_db, message_data)
        
        # Test pagination
        messages_page1 = await crud.get_session_messages(test_db, test_chat_session.id, skip=0, limit=5)
        messages_page2 = await crud.get_session_messages(test_db, test_chat_session.id, skip=5, limit=5)
        
        assert len(messages_page1) <= 5
        assert len(messages_page2) <= 5
        
        # Ensure no overlap between pages
        page1_ids = {msg.id for msg in messages_page1}
        page2_ids = {msg.id for msg in messages_page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_get_session_messages_by_type(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test getting session messages filtered by type."""
        # Create messages of different types
        user_message_data = {
            "session_id": test_chat_session.id,
            "message_type": "user",
            "content": "User message"
        }
        assistant_message_data = {
            "session_id": test_chat_session.id,
            "message_type": "assistant",
            "content": "Assistant message"
        }
        
        await crud.create_chat_message(test_db, user_message_data)
        await crud.create_chat_message(test_db, assistant_message_data)
        
        # Get only user messages
        user_messages = await crud.get_session_messages(test_db, test_chat_session.id, message_type="user")
        
        assert len(user_messages) >= 1
        for message in user_messages:
            assert message.message_type == "user"

    async def test_update_chat_message(self, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test updating chat message."""
        test_message = test_chat_messages[0]
        update_data = {
            "content": "Updated message content",
            "metadata": {"edited": True, "edit_time": datetime.utcnow().isoformat()}
        }
        
        updated_message = await crud.update_chat_message(test_db, test_message.id, update_data)
        
        assert updated_message is not None
        assert updated_message.content == update_data["content"]
        assert updated_message.metadata["edited"] is True
        assert updated_message.id == test_message.id

    async def test_update_chat_message_non_existing(self, test_db: AsyncSession):
        """Test updating non-existing chat message."""
        update_data = {"content": "Non-existing message"}
        
        updated_message = await crud.update_chat_message(test_db, 99999, update_data)
        
        assert updated_message is None

    async def test_delete_chat_message(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test deleting chat message."""
        # Create a message to delete
        message_data = {
            "session_id": test_chat_session.id,
            "message_type": "user",
            "content": "Message to delete"
        }
        message_to_delete = await crud.create_chat_message(test_db, message_data)
        
        # Delete the message
        result = await crud.delete_chat_message(test_db, message_to_delete.id)
        
        assert result is True
        
        # Verify message is deleted
        deleted_message = await crud.get_chat_message_by_id(test_db, message_to_delete.id)
        assert deleted_message is None

    async def test_delete_chat_message_non_existing(self, test_db: AsyncSession):
        """Test deleting non-existing chat message."""
        result = await crud.delete_chat_message(test_db, 99999)
        
        assert result is False

    async def test_search_messages(self, test_db: AsyncSession, test_user: User, test_chat_session: ChatSession):
        """Test searching messages by content."""
        # Create messages with searchable content
        search_messages = [
            {"session_id": test_chat_session.id, "message_type": "user", "content": "Python programming tutorial"},
            {"session_id": test_chat_session.id, "message_type": "assistant", "content": "Here's a Python example"},
            {"session_id": test_chat_session.id, "message_type": "user", "content": "JavaScript is different"}
        ]
        
        for msg_data in search_messages:
            await crud.create_chat_message(test_db, msg_data)
        
        # Search for "Python"
        python_messages = await crud.search_messages(test_db, test_user.id, "Python")
        
        assert len(python_messages) >= 2
        for message in python_messages:
            assert "Python" in message.content or "python" in message.content.lower()

    async def test_search_messages_no_results(self, test_db: AsyncSession, test_user: User):
        """Test searching messages with no results."""
        messages = await crud.search_messages(test_db, test_user.id, "nonexistentterm12345")
        
        assert len(messages) == 0

    async def test_get_user_message_count(self, test_db: AsyncSession, test_user: User, test_chat_messages: list[ChatMessage]):
        """Test getting total message count for a user."""
        count = await crud.get_user_message_count(test_db, test_user.id)
        
        assert count >= 2  # At least the test messages
        assert isinstance(count, int)

    async def test_get_session_message_count(self, test_db: AsyncSession, test_chat_session: ChatSession, test_chat_messages: list[ChatMessage]):
        """Test getting message count for a specific session."""
        count = await crud.get_session_message_count(test_db, test_chat_session.id)
        
        assert count >= 2  # At least the test messages
        assert isinstance(count, int)

    async def test_get_recent_messages(self, test_db: AsyncSession, test_user: User, test_chat_messages: list[ChatMessage]):
        """Test getting recent messages for a user."""
        recent_messages = await crud.get_recent_messages(test_db, test_user.id, limit=10)
        
        assert len(recent_messages) >= 2
        assert len(recent_messages) <= 10
        
        # Messages should be ordered by creation time (most recent first)
        if len(recent_messages) > 1:
            for i in range(len(recent_messages) - 1):
                assert recent_messages[i].created_at >= recent_messages[i + 1].created_at

    async def test_get_chat_statistics(self, test_db: AsyncSession, test_user: User, test_chat_session: ChatSession, test_chat_messages: list[ChatMessage]):
        """Test getting chat statistics for a user."""
        stats = await crud.get_chat_statistics(test_db, test_user.id)
        
        assert "total_sessions" in stats
        assert "total_messages" in stats
        assert "active_sessions" in stats
        assert "recent_activity" in stats
        
        assert isinstance(stats["total_sessions"], int)
        assert isinstance(stats["total_messages"], int)
        assert isinstance(stats["active_sessions"], int)
        
        assert stats["total_sessions"] >= 1
        assert stats["total_messages"] >= 2

    async def test_get_session_statistics(self, test_db: AsyncSession, test_chat_session: ChatSession, test_chat_messages: list[ChatMessage]):
        """Test getting statistics for a specific session."""
        stats = await crud.get_session_statistics(test_db, test_chat_session.id)
        
        assert "message_count" in stats
        assert "user_messages" in stats
        assert "assistant_messages" in stats
        assert "session_duration" in stats or "created_at" in stats
        
        assert isinstance(stats["message_count"], int)
        assert isinstance(stats["user_messages"], int)
        assert isinstance(stats["assistant_messages"], int)
        
        assert stats["message_count"] >= 2
        assert stats["user_messages"] + stats["assistant_messages"] == stats["message_count"]

    async def test_export_session_data(self, test_db: AsyncSession, test_chat_session: ChatSession, test_chat_messages: list[ChatMessage]):
        """Test exporting session data."""
        export_data = await crud.export_session_data(test_db, test_chat_session.id)
        
        assert "session" in export_data
        assert "messages" in export_data
        
        session_data = export_data["session"]
        assert session_data["id"] == test_chat_session.id
        assert session_data["title"] == test_chat_session.title
        
        messages_data = export_data["messages"]
        assert len(messages_data) >= 2
        
        for message in messages_data:
            assert "content" in message
            assert "message_type" in message
            assert "created_at" in message

    async def test_bulk_delete_messages(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test bulk deleting messages."""
        # Create messages to delete
        message_ids = []
        for i in range(5):
            message_data = {
                "session_id": test_chat_session.id,
                "message_type": "user",
                "content": f"Bulk delete message {i}"
            }
            message = await crud.create_chat_message(test_db, message_data)
            message_ids.append(message.id)
        
        # Bulk delete
        deleted_count = await crud.bulk_delete_messages(test_db, message_ids)
        
        assert deleted_count == len(message_ids)
        
        # Verify messages are deleted
        for message_id in message_ids:
            deleted_message = await crud.get_chat_message_by_id(test_db, message_id)
            assert deleted_message is None

    async def test_get_conversation_context(self, test_db: AsyncSession, test_chat_session: ChatSession, test_chat_messages: list[ChatMessage]):
        """Test getting conversation context for AI processing."""
        context = await crud.get_conversation_context(test_db, test_chat_session.id, max_messages=10)
        
        assert isinstance(context, list)
        assert len(context) >= 2
        
        # Context should be in chronological order
        if len(context) > 1:
            for i in range(len(context) - 1):
                assert context[i]["created_at"] <= context[i + 1]["created_at"]
        
        # Each context item should have required fields
        for item in context:
            assert "content" in item
            assert "message_type" in item
            assert "created_at" in item

    async def test_archive_old_sessions(self, test_db: AsyncSession, test_user: User):
        """Test archiving old sessions."""
        # Create an old session
        old_session_data = {
            "title": "Old Session",
            "user_id": test_user.id
        }
        old_session = await crud.create_chat_session(test_db, old_session_data)
        
        # Manually set old creation date
        old_session.created_at = datetime.utcnow() - timedelta(days=365)
        await test_db.commit()
        
        # Archive sessions older than 6 months
        archived_count = await crud.archive_old_sessions(test_db, days_old=180)
        
        assert archived_count >= 1
        
        # Verify session is archived (implementation dependent)
        # This could mean setting is_active=False or moving to archive table
        await test_db.refresh(old_session)
        # The exact behavior depends on implementation
        assert old_session.is_active is False or hasattr(old_session, 'archived_at')

    async def test_get_popular_topics(self, test_db: AsyncSession, test_user: User, test_chat_session: ChatSession):
        """Test getting popular topics from chat messages."""
        # Create messages with various topics
        topics_messages = [
            {"session_id": test_chat_session.id, "message_type": "user", "content": "Tell me about Python programming"},
            {"session_id": test_chat_session.id, "message_type": "user", "content": "Python data structures"},
            {"session_id": test_chat_session.id, "message_type": "user", "content": "JavaScript frameworks"},
            {"session_id": test_chat_session.id, "message_type": "user", "content": "Machine learning with Python"}
        ]
        
        for msg_data in topics_messages:
            await crud.create_chat_message(test_db, msg_data)
        
        # Get popular topics
        topics = await crud.get_popular_topics(test_db, test_user.id, limit=5)
        
        assert isinstance(topics, list)
        # The exact format depends on implementation
        # Could be word counts, topic categories, etc.
        assert len(topics) <= 5