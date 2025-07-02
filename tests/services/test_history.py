"""Tests for history service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from faker import Faker

from app.services.history import HistoryService
from app.models.chat import ChatMessage, ChatSession
from app.models.auth import User

fake = Faker()


class TestHistoryService:
    """Test HistoryService functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def history_service(self, mock_db_session):
        """Create a HistoryService instance with mocked session."""
        return HistoryService(mock_db_session)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return User(
            id=1,
            email=fake.email(),
            username=fake.user_name(),
            hashed_password=fake.password(),
            is_active=True,
            is_admin=False
        )

    @pytest.fixture
    def sample_session(self, sample_user):
        """Create a sample chat session."""
        return ChatSession(
            id=1,
            title=fake.sentence(),
            user_id=sample_user.id,
            user=sample_user,
            is_active=True
        )

    @pytest.fixture
    def sample_messages(self, sample_session):
        """Create sample chat messages."""
        return [
            ChatMessage(
                id=1,
                content="Hello, AI!",
                message_type="human",
                session_id=sample_session.id,
                session=sample_session,
                message_metadata={}
            ),
            ChatMessage(
                id=2,
                content="Hello! How can I help you today?",
                message_type="ai",
                session_id=sample_session.id,
                session=sample_session,
                message_metadata={}
            ),
            ChatMessage(
                id=3,
                content="What's the weather like?",
                message_type="human",
                session_id=sample_session.id,
                session=sample_session,
                message_metadata={}
            )
        ]

    async def test_load_conversation_history_success(self, history_service, mock_db_session, sample_messages):
        """Test successful loading of conversation history."""
        session_id = 1
        
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_messages
        mock_db_session.execute.return_value = mock_result
        
        # Load conversation history
        result = await history_service.load_conversation_history(session_id)
        
        assert result is not None
        assert len(result) == 3
        
        # Check message types and content
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == "Hello, AI!"
        
        assert isinstance(result[1], AIMessage)
        assert result[1].content == "Hello! How can I help you today?"
        
        assert isinstance(result[2], HumanMessage)
        assert result[2].content == "What's the weather like?"
        
        # Verify database was queried
        mock_db_session.execute.assert_called_once()

    async def test_load_conversation_history_empty_session(self, history_service, mock_db_session):
        """Test loading conversation history for empty session."""
        session_id = 999
        
        # Mock empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    async def test_load_conversation_history_with_system_messages(self, history_service, mock_db_session, sample_session):
        """Test loading conversation history with system messages."""
        session_id = 1
        
        # Create messages including system message
        messages_with_system = [
            ChatMessage(
                id=1,
                content="You are a helpful assistant.",
                message_type="system",
                session_id=session_id,
                session=sample_session,
                message_metadata={}
            ),
            ChatMessage(
                id=2,
                content="Hello!",
                message_type="human",
                session_id=session_id,
                session=sample_session,
                message_metadata={}
            ),
            ChatMessage(
                id=3,
                content="Hi there!",
                message_type="ai",
                session_id=session_id,
                session=sample_session,
                message_metadata={}
            )
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages_with_system
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 3
        assert isinstance(result[0], SystemMessage)
        assert result[0].content == "You are a helpful assistant."
        assert isinstance(result[1], HumanMessage)
        assert isinstance(result[2], AIMessage)

    async def test_load_conversation_history_with_metadata(self, history_service, mock_db_session, sample_session):
        """Test loading conversation history with message metadata."""
        session_id = 1
        
        # Create message with metadata
        message_with_metadata = ChatMessage(
            id=1,
            content="Message with metadata",
            message_type="human",
            session_id=session_id,
            session=sample_session,
            message_metadata={
                "timestamp": "2024-01-01T00:00:00Z",
                "user_agent": "ChatBot/1.0",
                "ip_address": "192.168.1.1"
            }
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [message_with_metadata]
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == "Message with metadata"
        
        # Check if metadata is preserved (depends on implementation)
        # This might be stored in additional_kwargs or other attributes
        if hasattr(result[0], 'additional_kwargs'):
            assert 'metadata' in result[0].additional_kwargs

    async def test_load_conversation_history_ordering(self, history_service, mock_db_session, sample_session):
        """Test that conversation history is loaded in correct order."""
        session_id = 1
        
        # Create messages with specific timestamps
        messages = [
            ChatMessage(
                id=3,
                content="Third message",
                message_type="human",
                session_id=session_id,
                session=sample_session,
                message_metadata={},
                created_at=fake.date_time()
            ),
            ChatMessage(
                id=1,
                content="First message",
                message_type="human",
                session_id=session_id,
                session=sample_session,
                message_metadata={},
                created_at=fake.date_time()
            ),
            ChatMessage(
                id=2,
                content="Second message",
                message_type="ai",
                session_id=session_id,
                session=sample_session,
                message_metadata={},
                created_at=fake.date_time()
            )
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 3
        # The order should be preserved as returned by the database query
        # (which should be ordered by created_at in the actual implementation)
        assert result[0].content == "Third message"
        assert result[1].content == "First message"
        assert result[2].content == "Second message"

    async def test_load_conversation_history_large_conversation(self, history_service, mock_db_session, sample_session):
        """Test loading large conversation history."""
        session_id = 1
        
        # Create large number of messages
        large_messages = []
        for i in range(100):
            message_type = "human" if i % 2 == 0 else "ai"
            large_messages.append(
                ChatMessage(
                    id=i + 1,
                    content=f"Message {i + 1}",
                    message_type=message_type,
                    session_id=session_id,
                    session=sample_session,
                    message_metadata={}
                )
            )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = large_messages
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 100
        
        # Check alternating message types
        for i, message in enumerate(result):
            if i % 2 == 0:
                assert isinstance(message, HumanMessage)
            else:
                assert isinstance(message, AIMessage)
            assert message.content == f"Message {i + 1}"

    async def test_load_conversation_history_database_error(self, history_service, mock_db_session):
        """Test handling of database errors."""
        session_id = 1
        
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception) as exc_info:
            await history_service.load_conversation_history(session_id)
        
        assert "Database connection error" in str(exc_info.value)

    async def test_load_conversation_history_invalid_session_id(self, history_service, mock_db_session):
        """Test loading conversation history with invalid session ID."""
        # Test with None session_id
        with pytest.raises((TypeError, ValueError)):
            await history_service.load_conversation_history(None)
        
        # Test with negative session_id
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(-1)
        assert result == []

    async def test_load_conversation_history_unknown_message_type(self, history_service, mock_db_session, sample_session):
        """Test handling of unknown message types."""
        session_id = 1
        
        # Create message with unknown type
        unknown_message = ChatMessage(
            id=1,
            content="Unknown type message",
            message_type="unknown",
            session_id=session_id,
            session=sample_session,
            message_metadata={}
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [unknown_message]
        mock_db_session.execute.return_value = mock_result
        
        # Should handle unknown message types gracefully
        # This depends on implementation - might skip, convert to HumanMessage, or raise error
        try:
            result = await history_service.load_conversation_history(session_id)
            # If it doesn't raise an error, check the result
            assert isinstance(result, list)
        except ValueError:
            # If it raises an error for unknown types, that's also acceptable
            pass

    async def test_load_conversation_history_empty_content(self, history_service, mock_db_session, sample_session):
        """Test loading conversation history with empty message content."""
        session_id = 1
        
        # Create message with empty content
        empty_message = ChatMessage(
            id=1,
            content="",
            message_type="human",
            session_id=session_id,
            session=sample_session,
            message_metadata={}
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [empty_message]
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)
        assert result[0].content == ""

    async def test_load_conversation_history_special_characters(self, history_service, mock_db_session, sample_session):
        """Test loading conversation history with special characters."""
        session_id = 1
        
        # Create message with special characters
        special_message = ChatMessage(
            id=1,
            content="Message with émojis 😊🤖 and symbols ∑∆ and quotes \"test\"",
            message_type="human",
            session_id=session_id,
            session=sample_session,
            message_metadata={}
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [special_message]
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)
        assert "émojis 😊🤖" in result[0].content
        assert "symbols ∑∆" in result[0].content
        assert '"test"' in result[0].content

    async def test_load_conversation_history_concurrent_access(self, history_service, mock_db_session, sample_messages):
        """Test concurrent access to conversation history."""
        import asyncio
        
        session_id = 1
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_messages
        mock_db_session.execute.return_value = mock_result
        
        # Create multiple concurrent requests
        tasks = []
        for _ in range(5):
            task = history_service.load_conversation_history(session_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All results should be identical
        assert len(results) == 5
        for result in results:
            assert len(result) == 3
            assert result[0].content == "Hello, AI!"
            assert result[1].content == "Hello! How can I help you today?"
            assert result[2].content == "What's the weather like?"

    async def test_load_conversation_history_performance(self, history_service, mock_db_session, sample_session):
        """Test performance with large conversation history."""
        import time
        
        session_id = 1
        
        # Create very large conversation
        large_messages = []
        for i in range(1000):
            message_type = "human" if i % 2 == 0 else "ai"
            large_messages.append(
                ChatMessage(
                    id=i + 1,
                    content=f"Performance test message {i + 1}" * 10,  # Longer content
                    message_type=message_type,
                    session_id=session_id,
                    session=sample_session,
                    message_metadata={"index": i}
                )
            )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = large_messages
        mock_db_session.execute.return_value = mock_result
        
        start_time = time.time()
        result = await history_service.load_conversation_history(session_id)
        execution_time = time.time() - start_time
        
        assert len(result) == 1000
        assert execution_time < 5.0  # Should complete within reasonable time

    async def test_load_conversation_history_message_conversion_accuracy(self, history_service, mock_db_session, sample_session):
        """Test accuracy of ChatMessage to BaseMessage conversion."""
        session_id = 1
        
        # Test all message types
        test_messages = [
            ChatMessage(
                id=1,
                content="System instruction",
                message_type="system",
                session_id=session_id,
                session=sample_session,
                message_metadata={"role": "system"}
            ),
            ChatMessage(
                id=2,
                content="Human question",
                message_type="human",
                session_id=session_id,
                session=sample_session,
                message_metadata={"role": "user"}
            ),
            ChatMessage(
                id=3,
                content="AI response",
                message_type="ai",
                session_id=session_id,
                session=sample_session,
                message_metadata={"role": "assistant"}
            )
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = test_messages
        mock_db_session.execute.return_value = mock_result
        
        result = await history_service.load_conversation_history(session_id)
        
        assert len(result) == 3
        
        # Verify correct message type conversion
        assert isinstance(result[0], SystemMessage)
        assert result[0].content == "System instruction"
        
        assert isinstance(result[1], HumanMessage)
        assert result[1].content == "Human question"
        
        assert isinstance(result[2], AIMessage)
        assert result[2].content == "AI response"

    async def test_history_service_initialization(self, mock_db_session):
        """Test HistoryService initialization."""
        service = HistoryService(mock_db_session)
        
        assert service.db == mock_db_session
        assert hasattr(service, 'load_conversation_history')

    async def test_history_service_with_real_session_mock(self):
        """Test HistoryService with more realistic session mock."""
        # Create a more realistic mock that behaves like AsyncSession
        mock_session = AsyncMock(spec=AsyncSession)
        
        # Mock the query execution chain
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        service = HistoryService(mock_session)
        result = await service.load_conversation_history(1)
        
        assert result == []
        mock_session.execute.assert_called_once()
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()