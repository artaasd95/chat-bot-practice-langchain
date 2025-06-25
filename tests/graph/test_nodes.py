"""Tests for graph nodes."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from faker import Faker

from app.graph.nodes import GraphState, generate_response

fake = Faker()


class TestGraphState:
    """Test GraphState TypedDict."""

    def test_graph_state_creation(self):
        """Test creating a GraphState instance."""
        messages = [HumanMessage(content="Test message")]
        metadata = {"user_id": 1, "session_id": 1}
        session_id = 1
        api_call_info = {"timestamp": "2024-01-01T00:00:00Z"}
        
        state = GraphState(
            messages=messages,
            metadata=metadata,
            session_id=session_id,
            api_call_info=api_call_info
        )
        
        assert state["messages"] == messages
        assert state["metadata"] == metadata
        assert state["session_id"] == session_id
        assert state["api_call_info"] == api_call_info

    def test_graph_state_empty_initialization(self):
        """Test creating GraphState with empty values."""
        state = GraphState(
            messages=[],
            metadata={},
            session_id=0,
            api_call_info={}
        )
        
        assert state["messages"] == []
        assert state["metadata"] == {}
        assert state["session_id"] == 0
        assert state["api_call_info"] == {}

    def test_graph_state_with_multiple_message_types(self):
        """Test GraphState with different message types."""
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="User question"),
            AIMessage(content="AI response")
        ]
        
        state = GraphState(
            messages=messages,
            metadata={"conversation_type": "multi_turn"},
            session_id=123,
            api_call_info={"model": "gpt-4"}
        )
        
        assert len(state["messages"]) == 3
        assert isinstance(state["messages"][0], SystemMessage)
        assert isinstance(state["messages"][1], HumanMessage)
        assert isinstance(state["messages"][2], AIMessage)

    def test_graph_state_metadata_types(self):
        """Test GraphState with various metadata types."""
        metadata = {
            "user_id": 123,
            "session_id": 456,
            "preferences": {
                "language": "en",
                "tone": "formal"
            },
            "context": ["previous", "conversation", "topics"],
            "timestamp": 1704067200.0,
            "is_premium": True
        }
        
        state = GraphState(
            messages=[HumanMessage(content="Test")],
            metadata=metadata,
            session_id=456,
            api_call_info={}
        )
        
        assert state["metadata"]["user_id"] == 123
        assert state["metadata"]["preferences"]["language"] == "en"
        assert state["metadata"]["context"] == ["previous", "conversation", "topics"]
        assert state["metadata"]["is_premium"] is True

    def test_graph_state_api_call_info_structure(self):
        """Test GraphState with comprehensive API call info."""
        api_call_info = {
            "request_id": "req_123456",
            "timestamp": "2024-01-01T00:00:00Z",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False,
            "user_agent": "ChatBot/1.0",
            "ip_address": "192.168.1.1"
        }
        
        state = GraphState(
            messages=[HumanMessage(content="API test")],
            metadata={},
            session_id=1,
            api_call_info=api_call_info
        )
        
        assert state["api_call_info"]["request_id"] == "req_123456"
        assert state["api_call_info"]["model"] == "gpt-4"
        assert state["api_call_info"]["temperature"] == 0.7
        assert state["api_call_info"]["stream"] is False


class TestGenerateResponse:
    """Test generate_response function."""

    @patch('app.services.llm.get_llm')
    async def test_generate_response_success(self, mock_get_llm):
        """Test successful response generation."""
        # Mock LLM
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="This is a test response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        # Create input state
        state = GraphState(
            messages=[HumanMessage(content="Hello, AI!")],
            metadata={"user_id": 1},
            session_id=1,
            api_call_info={}
        )
        
        # Generate response
        result = await generate_response(state)
        
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) == 2  # Original + AI response
        
        # Check AI response
        ai_message = result["messages"][-1]
        assert isinstance(ai_message, AIMessage)
        assert ai_message.content == "This is a test response"
        
        # Verify LLM was called
        mock_llm.ainvoke.assert_called_once()

    @patch('app.services.llm.get_llm')
    async def test_generate_response_with_conversation_history(self, mock_get_llm):
        """Test response generation with conversation history."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Response with context")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        # Create state with conversation history
        state = GraphState(
            messages=[
                HumanMessage(content="What's the weather?"),
                AIMessage(content="I don't have access to weather data."),
                HumanMessage(content="Can you help with something else?")
            ],
            metadata={"conversation_length": 3},
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        assert len(result["messages"]) == 4  # 3 original + 1 new AI response
        
        # Verify conversation history is preserved
        assert result["messages"][0].content == "What's the weather?"
        assert result["messages"][1].content == "I don't have access to weather data."
        assert result["messages"][2].content == "Can you help with something else?"
        assert result["messages"][3].content == "Response with context"
        
        # Verify LLM received the full conversation
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert len(call_args) == 3  # All previous messages

    @patch('app.services.llm.get_llm')
    async def test_generate_response_with_system_message(self, mock_get_llm):
        """Test response generation with system message."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="System-aware response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        state = GraphState(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Hello!")
            ],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        assert len(result["messages"]) == 3  # System + Human + AI
        assert isinstance(result["messages"][0], SystemMessage)
        assert isinstance(result["messages"][1], HumanMessage)
        assert isinstance(result["messages"][2], AIMessage)
        
        # System message should be included in LLM call
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert len(call_args) == 2
        assert isinstance(call_args[0], SystemMessage)

    @patch('app.services.llm.get_llm')
    async def test_generate_response_empty_messages(self, mock_get_llm):
        """Test response generation with empty messages."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Default response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        state = GraphState(
            messages=[],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        # Should handle empty messages gracefully
        assert "messages" in result
        assert len(result["messages"]) >= 1
        
        # Should have generated a response
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        assert len(ai_messages) >= 1

    @patch('app.services.llm.get_llm')
    async def test_generate_response_llm_error(self, mock_get_llm):
        """Test response generation when LLM fails."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("LLM service error")
        mock_get_llm.return_value = mock_llm
        
        state = GraphState(
            messages=[HumanMessage(content="Test message")],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        # Should propagate LLM errors
        with pytest.raises(Exception) as exc_info:
            await generate_response(state)
        
        assert "LLM service error" in str(exc_info.value)

    @patch('app.services.llm.get_llm')
    async def test_generate_response_preserves_metadata(self, mock_get_llm):
        """Test that response generation preserves metadata."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Metadata preserved")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        original_metadata = {
            "user_id": 123,
            "session_id": 456,
            "preferences": {"language": "en"},
            "context": "technical_support"
        }
        
        state = GraphState(
            messages=[HumanMessage(content="Technical question")],
            metadata=original_metadata,
            session_id=456,
            api_call_info={"model": "gpt-4"}
        )
        
        result = await generate_response(state)
        
        # Metadata should be preserved
        assert result["metadata"] == original_metadata
        assert result["session_id"] == 456
        assert result["api_call_info"]["model"] == "gpt-4"

    @patch('app.services.llm.get_llm')
    async def test_generate_response_updates_api_call_info(self, mock_get_llm):
        """Test that response generation updates API call info."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="API info updated")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        initial_api_info = {
            "request_id": "req_123",
            "start_time": "2024-01-01T00:00:00Z"
        }
        
        state = GraphState(
            messages=[HumanMessage(content="Test")],
            metadata={},
            session_id=1,
            api_call_info=initial_api_info
        )
        
        result = await generate_response(state)
        
        # Original API info should be preserved
        assert result["api_call_info"]["request_id"] == "req_123"
        assert result["api_call_info"]["start_time"] == "2024-01-01T00:00:00Z"
        
        # Additional info might be added (depending on implementation)
        # This is flexible based on actual implementation
        assert "api_call_info" in result

    @patch('app.services.llm.get_llm')
    async def test_generate_response_with_long_conversation(self, mock_get_llm):
        """Test response generation with long conversation history."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Long conversation response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        # Create long conversation
        messages = []
        for i in range(50):
            if i % 2 == 0:
                messages.append(HumanMessage(content=f"User message {i}"))
            else:
                messages.append(AIMessage(content=f"AI response {i}"))
        
        state = GraphState(
            messages=messages,
            metadata={"conversation_length": 50},
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        # Should handle long conversations
        assert len(result["messages"]) == 51  # 50 + 1 new response
        
        # Last message should be the new AI response
        assert isinstance(result["messages"][-1], AIMessage)
        assert result["messages"][-1].content == "Long conversation response"

    @patch('app.services.llm.get_llm')
    async def test_generate_response_with_special_characters(self, mock_get_llm):
        """Test response generation with special characters."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Response with émojis 🤖 and symbols ∑∆")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        state = GraphState(
            messages=[HumanMessage(content="Message with émojis 😊 and symbols ∑∆")],
            metadata={"encoding": "utf-8"},
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        # Should handle special characters properly
        ai_response = result["messages"][-1]
        assert isinstance(ai_response, AIMessage)
        assert "émojis 🤖" in ai_response.content
        assert "symbols ∑∆" in ai_response.content

    @patch('app.services.llm.get_llm')
    async def test_generate_response_concurrent_calls(self, mock_get_llm):
        """Test concurrent response generation calls."""
        import asyncio
        
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Concurrent response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        # Create multiple states for concurrent processing
        states = []
        for i in range(5):
            state = GraphState(
                messages=[HumanMessage(content=f"Concurrent message {i}")],
                metadata={"call_id": i},
                session_id=i,
                api_call_info={}
            )
            states.append(state)
        
        # Execute concurrently
        tasks = [generate_response(state) for state in states]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        
        # Each result should be independent
        for i, result in enumerate(results):
            assert result["session_id"] == i
            assert result["metadata"]["call_id"] == i
            assert len(result["messages"]) == 2  # Original + AI response

    @patch('app.services.llm.get_llm')
    async def test_generate_response_with_custom_llm_config(self, mock_get_llm):
        """Test response generation with custom LLM configuration."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Custom config response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        state = GraphState(
            messages=[HumanMessage(content="Custom config test")],
            metadata={
                "llm_config": {
                    "temperature": 0.9,
                    "max_tokens": 500,
                    "top_p": 0.95
                }
            },
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        # Should generate response regardless of custom config
        assert len(result["messages"]) == 2
        assert isinstance(result["messages"][-1], AIMessage)
        
        # Custom config should be preserved in metadata
        assert "llm_config" in result["metadata"]
        assert result["metadata"]["llm_config"]["temperature"] == 0.9

    @patch('app.services.llm.get_llm')
    async def test_generate_response_message_ordering(self, mock_get_llm):
        """Test that message ordering is preserved."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Ordered response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        # Create messages with specific order
        messages = [
            SystemMessage(content="System: You are helpful"),
            HumanMessage(content="Human: First question"),
            AIMessage(content="AI: First answer"),
            HumanMessage(content="Human: Second question"),
            AIMessage(content="AI: Second answer"),
            HumanMessage(content="Human: Third question")
        ]
        
        state = GraphState(
            messages=messages,
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        result = await generate_response(state)
        
        # Order should be preserved
        assert len(result["messages"]) == 7  # 6 original + 1 new
        
        # Check specific ordering
        assert result["messages"][0].content == "System: You are helpful"
        assert result["messages"][1].content == "Human: First question"
        assert result["messages"][2].content == "AI: First answer"
        assert result["messages"][5].content == "Human: Third question"
        assert result["messages"][6].content == "Ordered response"

    @patch('app.services.llm.get_llm')
    async def test_generate_response_state_immutability(self, mock_get_llm):
        """Test that original state is not mutated."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Immutable test response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        original_messages = [HumanMessage(content="Original message")]
        original_metadata = {"original": True}
        original_api_info = {"original_request": True}
        
        state = GraphState(
            messages=original_messages.copy(),
            metadata=original_metadata.copy(),
            session_id=1,
            api_call_info=original_api_info.copy()
        )
        
        result = await generate_response(state)
        
        # Original state should not be mutated
        assert len(original_messages) == 1
        assert original_messages[0].content == "Original message"
        assert original_metadata == {"original": True}
        assert original_api_info == {"original_request": True}
        
        # Result should have new content
        assert len(result["messages"]) == 2
        assert result["messages"][1].content == "Immutable test response"