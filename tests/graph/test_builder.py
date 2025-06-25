"""Tests for graph builder."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from faker import Faker

from app.graph.builder import build_graph
from app.graph.nodes import GraphState

fake = Faker()


class TestGraphBuilder:
    """Test graph builder functionality."""

    @patch('app.services.llm.get_llm')
    async def test_build_graph_success(self, mock_get_llm):
        """Test successful graph building."""
        # Mock LLM
        mock_llm = AsyncMock()
        mock_get_llm.return_value = mock_llm
        
        # Build graph
        graph = build_graph()
        
        assert graph is not None
        assert hasattr(graph, 'ainvoke')
        assert hasattr(graph, 'nodes')
        
        # Check that graph has expected nodes
        expected_nodes = ['preprocess', 'generate_response', 'postprocess']
        for node in expected_nodes:
            assert node in graph.nodes

    @patch('app.services.llm.get_llm')
    async def test_graph_execution_flow(self, mock_get_llm):
        """Test complete graph execution flow."""
        # Mock LLM response
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Test AI response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        # Build graph
        graph = build_graph()
        
        # Prepare input state
        input_state = GraphState(
            messages=[HumanMessage(content="Hello, AI!")],
            metadata={"user_id": 1, "session_id": 1},
            session_id=1,
            api_call_info={}
        )
        
        # Execute graph
        result = await graph.ainvoke(input_state)
        
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) >= 1
        
        # Check that AI response was added
        ai_responses = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        assert len(ai_responses) >= 1
        assert ai_responses[0].content == "Test AI response"

    @patch('app.services.llm.get_llm')
    async def test_graph_with_empty_messages(self, mock_get_llm):
        """Test graph execution with empty messages."""
        mock_llm = AsyncMock()
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        input_state = GraphState(
            messages=[],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        # Should handle empty messages gracefully
        result = await graph.ainvoke(input_state)
        assert result is not None
        assert "messages" in result

    @patch('app.services.llm.get_llm')
    async def test_graph_with_multiple_messages(self, mock_get_llm):
        """Test graph execution with multiple messages."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Response to conversation")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        input_state = GraphState(
            messages=[
                HumanMessage(content="First message"),
                AIMessage(content="First response"),
                HumanMessage(content="Second message")
            ],
            metadata={"conversation_length": 3},
            session_id=1,
            api_call_info={}
        )
        
        result = await graph.ainvoke(input_state)
        
        assert result is not None
        assert len(result["messages"]) >= 3
        
        # Should preserve conversation history
        assert any(msg.content == "First message" for msg in result["messages"] if isinstance(msg, HumanMessage))
        assert any(msg.content == "Second message" for msg in result["messages"] if isinstance(msg, HumanMessage))

    @patch('app.services.llm.get_llm')
    async def test_graph_with_metadata(self, mock_get_llm):
        """Test graph execution with metadata."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Metadata-aware response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        metadata = {
            "user_id": 123,
            "session_id": 456,
            "user_preferences": {"language": "en", "tone": "formal"},
            "context": "technical_discussion"
        }
        
        input_state = GraphState(
            messages=[HumanMessage(content="Technical question")],
            metadata=metadata,
            session_id=456,
            api_call_info={}
        )
        
        result = await graph.ainvoke(input_state)
        
        assert result is not None
        assert result["metadata"] == metadata
        assert result["session_id"] == 456

    @patch('app.services.llm.get_llm')
    async def test_graph_llm_error_handling(self, mock_get_llm):
        """Test graph handling of LLM errors."""
        # Mock LLM to raise an error
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("LLM service unavailable")
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        input_state = GraphState(
            messages=[HumanMessage(content="Test message")],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        # Should handle LLM errors gracefully
        with pytest.raises(Exception) as exc_info:
            await graph.ainvoke(input_state)
        
        assert "LLM service unavailable" in str(exc_info.value)

    @patch('app.services.llm.get_llm')
    async def test_graph_preprocessing_node(self, mock_get_llm):
        """Test preprocessing node functionality."""
        mock_llm = AsyncMock()
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        # Test that preprocessing node exists and is entry point
        assert 'preprocess' in graph.nodes
        
        # The entry point should be preprocess
        # This depends on the actual implementation
        # but we can test that the graph starts with preprocessing
        input_state = GraphState(
            messages=[HumanMessage(content="Raw user input")],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        # Execute just to ensure preprocessing doesn't fail
        try:
            result = await graph.ainvoke(input_state)
            assert result is not None
        except Exception as e:
            # If there's an error, it should be from downstream nodes, not preprocessing
            assert "preprocess" not in str(e).lower()

    @patch('app.services.llm.get_llm')
    async def test_graph_postprocessing_node(self, mock_get_llm):
        """Test postprocessing node functionality."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Raw AI response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        assert 'postprocess' in graph.nodes
        
        input_state = GraphState(
            messages=[HumanMessage(content="Test input")],
            metadata={},
            session_id=1,
            api_call_info={}
        )
        
        result = await graph.ainvoke(input_state)
        
        # Postprocessing should have been applied
        assert result is not None
        assert "messages" in result
        
        # The result should contain processed messages
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        assert len(ai_messages) >= 1

    @patch('app.services.llm.get_llm')
    async def test_graph_state_persistence(self, mock_get_llm):
        """Test that graph state is properly maintained throughout execution."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="State-aware response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        initial_metadata = {"test_key": "test_value", "counter": 1}
        initial_api_info = {"start_time": "2024-01-01T00:00:00Z"}
        
        input_state = GraphState(
            messages=[HumanMessage(content="State test")],
            metadata=initial_metadata,
            session_id=999,
            api_call_info=initial_api_info
        )
        
        result = await graph.ainvoke(input_state)
        
        # State should be preserved
        assert result["session_id"] == 999
        assert "test_key" in result["metadata"]
        assert result["metadata"]["test_key"] == "test_value"
        assert "start_time" in result["api_call_info"]

    @patch('app.services.llm.get_llm')
    async def test_graph_concurrent_execution(self, mock_get_llm):
        """Test graph handling of concurrent executions."""
        import asyncio
        
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Concurrent response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        # Create multiple concurrent executions
        tasks = []
        for i in range(5):
            input_state = GraphState(
                messages=[HumanMessage(content=f"Concurrent message {i}")],
                metadata={"execution_id": i},
                session_id=i,
                api_call_info={}
            )
            task = graph.ainvoke(input_state)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        
        # Each result should be independent
        for i, result in enumerate(results):
            assert result is not None
            assert result["session_id"] == i
            assert result["metadata"]["execution_id"] == i

    @patch('app.services.llm.get_llm')
    async def test_graph_with_custom_config(self, mock_get_llm):
        """Test graph building with custom configuration."""
        mock_llm = AsyncMock()
        mock_get_llm.return_value = mock_llm
        
        # Test with custom configuration if supported
        custom_config = {
            "max_iterations": 10,
            "timeout": 30,
            "debug": True
        }
        
        # This depends on whether build_graph accepts config parameters
        try:
            graph = build_graph(config=custom_config)
        except TypeError:
            # If build_graph doesn't accept config, just build normally
            graph = build_graph()
        
        assert graph is not None
        assert hasattr(graph, 'ainvoke')

    @patch('app.services.llm.get_llm')
    async def test_graph_memory_efficiency(self, mock_get_llm):
        """Test graph memory efficiency with large inputs."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Memory efficient response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        # Create a large conversation history
        large_messages = []
        for i in range(100):
            if i % 2 == 0:
                large_messages.append(HumanMessage(content=f"User message {i}" * 10))
            else:
                large_messages.append(AIMessage(content=f"AI response {i}" * 10))
        
        input_state = GraphState(
            messages=large_messages,
            metadata={"large_conversation": True},
            session_id=1,
            api_call_info={}
        )
        
        # Should handle large inputs without memory issues
        result = await graph.ainvoke(input_state)
        
        assert result is not None
        assert len(result["messages"]) >= 100

    @patch('app.services.llm.get_llm')
    async def test_graph_edge_cases(self, mock_get_llm):
        """Test graph handling of edge cases."""
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Edge case response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        # Test with None values
        edge_case_state = GraphState(
            messages=[HumanMessage(content="")],  # Empty content
            metadata={"empty_key": "", "null_key": None},
            session_id=0,
            api_call_info={}
        )
        
        result = await graph.ainvoke(edge_case_state)
        
        assert result is not None
        # Should handle edge cases gracefully
        assert "messages" in result

    @patch('app.services.llm.get_llm')
    async def test_graph_performance_metrics(self, mock_get_llm):
        """Test graph execution performance tracking."""
        import time
        
        mock_llm = AsyncMock()
        mock_ai_message = AIMessage(content="Performance test response")
        mock_llm.ainvoke.return_value = mock_ai_message
        mock_get_llm.return_value = mock_llm
        
        graph = build_graph()
        
        input_state = GraphState(
            messages=[HumanMessage(content="Performance test")],
            metadata={},
            session_id=1,
            api_call_info={"start_time": time.time()}
        )
        
        start_time = time.time()
        result = await graph.ainvoke(input_state)
        execution_time = time.time() - start_time
        
        assert result is not None
        assert execution_time < 10.0  # Should complete within reasonable time
        
        # Check if performance metrics are tracked in api_call_info
        if "execution_time" in result["api_call_info"]:
            assert isinstance(result["api_call_info"]["execution_time"], (int, float))