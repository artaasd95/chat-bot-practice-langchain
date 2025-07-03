#!/usr/bin/env python3
"""Test script for the enhanced chat graph with API tools and history management."""

import asyncio
import uuid
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from app.services.llm import get_llm
from app.graph.builder import build_enhanced_graph
from app.graph.nodes import GraphState
from app.database.database import init_db


async def test_basic_conversation():
    """Test basic conversation without API calls."""
    print("\n=== Testing Basic Conversation ===")
    
    # Initialize database
    await init_db()
    
    # Get LLM and build graph
    llm = get_llm()
    graph = await build_enhanced_graph(llm)
    
    # Create test state
    session_id = str(uuid.uuid4())
    state: GraphState = {
        "messages": [HumanMessage(content="Hello! How are you today?")],
        "response": None,
        "metadata": {"request_id": "test-1"},
        "session_id": session_id,
        "history": [],
        "api_request": None,
        "api_response": None,
        "should_call_api": False
    }
    
    # Run the graph
    result = await graph.ainvoke(state)
    
    print(f"Session ID: {session_id}")
    print(f"User: {state['messages'][0].content}")
    print(f"Assistant: {result.get('response', 'No response')}")
    print(f"History loaded: {len(result.get('history', []))} messages")
    print(f"API called: {result.get('should_call_api', False)}")
    
    return session_id


async def test_conversation_with_history(session_id: str):
    """Test conversation that should load previous history."""
    print("\n=== Testing Conversation with History ===")
    
    # Get LLM and build graph
    llm = get_llm()
    graph = await build_enhanced_graph(llm)
    
    # Create test state with same session ID
    state: GraphState = {
        "messages": [HumanMessage(content="What did I ask you before?")],
        "response": None,
        "metadata": {"request_id": "test-2"},
        "session_id": session_id,
        "history": [],
        "api_request": None,
        "api_response": None,
        "should_call_api": False
    }
    
    # Run the graph
    result = await graph.ainvoke(state)
    
    print(f"Session ID: {session_id}")
    print(f"User: {state['messages'][0].content}")
    print(f"Assistant: {result.get('response', 'No response')}")
    print(f"History loaded: {len(result.get('history', []))} messages")
    print(f"API called: {result.get('should_call_api', False)}")


async def test_api_call_conversation():
    """Test conversation that triggers an API call."""
    print("\n=== Testing API Call Conversation ===")
    
    # Get LLM and build graph
    llm = get_llm()
    graph = await build_enhanced_graph(llm)
    
    # Create test state with API call request
    session_id = str(uuid.uuid4())
    api_message = '''Please make an API call to get some data.
    
    API_CALL: {"url": "https://jsonplaceholder.typicode.com/posts/1", "method": "GET"}'''
    
    state: GraphState = {
        "messages": [HumanMessage(content=api_message)],
        "response": None,
        "metadata": {"request_id": "test-3"},
        "session_id": session_id,
        "history": [],
        "api_request": None,
        "api_response": None,
        "should_call_api": False
    }
    
    # Run the graph
    result = await graph.ainvoke(state)
    
    print(f"Session ID: {session_id}")
    print(f"User: {state['messages'][0].content[:50]}...")
    print(f"Assistant: {result.get('response', 'No response')[:200]}...")
    print(f"History loaded: {len(result.get('history', []))} messages")
    print(f"API called: {result.get('should_call_api', False)}")
    
    if result.get('api_response'):
        api_resp = result['api_response']
        print(f"API Response Status: {api_resp.get('status_code')}")
        print(f"API Response Success: {api_resp.get('success')}")
        if api_resp.get('error'):
            print(f"API Error: {api_resp['error']}")


async def test_llm_generated_api_call():
    """Test conversation where LLM decides to make an API call."""
    print("\n=== Testing LLM-Generated API Call ===")
    
    # Get LLM and build graph
    llm = get_llm()
    graph = await build_enhanced_graph(llm)
    
    # Create test state that might trigger LLM to suggest API call
    session_id = str(uuid.uuid4())
    
    # Add instruction to LLM about API calling
    api_instruction = '''You are an AI assistant that can make API calls when needed. 
    If you need to fetch external data, you can make an API call using this format:
    
    API_CALL: {"url": "https://api.example.com/endpoint", "method": "GET", "headers": {}, "params": {}}
    
    User question: Can you get me information about a sample blog post from JSONPlaceholder API?'''
    
    state: GraphState = {
        "messages": [HumanMessage(content=api_instruction)],
        "response": None,
        "metadata": {"request_id": "test-4"},
        "session_id": session_id,
        "history": [],
        "api_request": None,
        "api_response": None,
        "should_call_api": False
    }
    
    # Run the graph
    result = await graph.ainvoke(state)
    
    print(f"Session ID: {session_id}")
    print(f"User: {state['messages'][0].content[:100]}...")
    print(f"Assistant: {result.get('response', 'No response')[:300]}...")
    print(f"History loaded: {len(result.get('history', []))} messages")
    print(f"API called: {result.get('should_call_api', False)}")
    
    if result.get('api_response'):
        api_resp = result['api_response']
        print(f"API Response Status: {api_resp.get('status_code')}")
        print(f"API Response Success: {api_resp.get('success')}")


async def main():
    """Run all tests."""
    print("Enhanced Chat Graph Test Suite")
    print("==============================")
    
    try:
        # Test basic conversation and get session ID
        session_id = await test_basic_conversation()
        
        # Test conversation with history using same session
        await test_conversation_with_history(session_id)
        
        # Test explicit API call
        await test_api_call_conversation()
        
        # Test LLM-generated API call
        await test_llm_generated_api_call()
        
        print("\n=== All Tests Completed ===")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())