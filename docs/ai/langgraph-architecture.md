# LangGraph Architecture Documentation

This document provides comprehensive documentation for the LangGraph-based AI architecture used in the Chat Bot System.

## Table of Contents

1. [Overview](#overview)
2. [Graph Architecture](#graph-architecture)
3. [Graph State](#graph-state)
4. [Graph Nodes](#graph-nodes)
5. [Graph Builders](#graph-builders)
6. [LLM Integration](#llm-integration)
7. [Message Flow](#message-flow)
8. [Advanced Features](#advanced-features)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

## Overview

The Chat Bot System uses LangGraph to create a sophisticated conversation flow that processes user messages through a series of interconnected nodes. LangGraph provides a framework for building stateful, multi-step applications with language models.

### Key Components

- **StateGraph**: The main graph structure that defines the conversation flow
- **GraphState**: The state object that carries data between nodes
- **Nodes**: Individual processing units that handle specific tasks
- **Edges**: Connections between nodes that define the flow
- **LLM Integration**: Language model integration for generating responses

### Architecture Benefits

- **Modularity**: Each processing step is isolated in its own node
- **Flexibility**: Easy to add, remove, or modify processing steps
- **Observability**: Clear visibility into the conversation flow
- **Scalability**: Can handle complex multi-step conversations
- **Maintainability**: Clean separation of concerns

## Graph Architecture

### Graph Structure

The system implements four main graph types:

1. **Basic Graph**: Simple linear flow for standard conversations
2. **Advanced Graph**: Extensible graph with additional custom nodes
3. **Conditional Graph**: Smart routing based on message content
4. **Enhanced Graph**: Advanced graph with API tool calling and conversation history

### Enhanced Graph Flow Diagram

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ Entry Point │───▶│ Load History │───▶│ Preprocess   │───▶│ Generate    │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
                                                            ┌──────────────┐
                                                            │ Check API    │
                                                            │ Call         │
                                                            └──────────────┘
                                                                    │
                                                            ┌───────┴───────┐
                                                            │               │
                                                            ▼               ▼
                                                    ┌──────────────┐ ┌──────────────┐
                                                    │ Make API     │ │ Postprocess  │
                                                    │ Call         │ │              │
                                                    └──────────────┘ └──────────────┘
                                                            │               │
                                                            ▼               │
                                                    ┌──────────────┐        │
                                                    │ Postprocess  │        │
                                                    │              │        │
                                                    └──────────────┘        │
                                                            │               │
                                                            ▼               ▼
                                                    ┌──────────────┐ ┌──────────────┐
                                                    │ Save to      │ │ Save to      │
                                                    │ History      │ │ History      │
                                                    └──────────────┘ └──────────────┘
                                                            │               │
                                                            ▼               ▼
                                                            ┌───────────────┐
                                                            │      END      │
                                                            └───────────────┘
```

### Conditional Graph Flow

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Entry Point │───▶│ Preprocess   │───▶│   Router    │
└─────────────┘    └──────────────┘    └─────────────┘
                                               │
                                               ├─────────────┐
                                               │             │
                                               ▼             ▼
                                        ┌─────────────┐ ┌──────────┐
                                        │ Generate    │ │ Help     │
                                        └─────────────┘ │ Flow     │
                                               │        └──────────┘
                                               │             │
                                               ▼             │
                                        ┌──────────────┐     │
                                        │ Postprocess  │◀────┘
                                        └──────────────┘
                                               │
                                               ▼
                                          ┌─────────┐
                                          │   END   │
                                          └─────────┘
```

## Graph State

### GraphState Definition

The `GraphState` is a TypedDict that carries information between nodes:

```python
class GraphState(TypedDict, total=False):
    """Type definition for the graph state."""
    messages: List[BaseMessage]     # Conversation history
    response: Optional[str]         # Generated response
    metadata: Dict[str, Any]        # Additional metadata
    session_id: Optional[str]       # Conversation session ID
    history: List[Dict[str, Any]]   # Loaded conversation history
    api_request: Optional[APIRequest]   # API request to be made
    api_response: Optional[APIResponse] # API response received
    should_call_api: bool           # Whether to make an API call
```

### State Components

#### Messages
- **Type**: `List[BaseMessage]`
- **Purpose**: Stores the conversation history
- **Content**: Contains both user messages (`HumanMessage`) and AI responses (`AIMessage`)
- **Usage**: Passed to the LLM for context and response generation

#### Response
- **Type**: `Optional[str]`
- **Purpose**: Stores the generated response text
- **Content**: The final response that will be sent to the user
- **Usage**: Set by the generate node and potentially modified by postprocess

#### Metadata
- **Type**: `Dict[str, Any]`
- **Purpose**: Stores additional information about the request
- **Content**: Request ID, timestamps, processing flags, etc.
- **Usage**: Used for tracking, logging, and conditional processing

### State Flow

1. **Initial State**: Created with user message and metadata
2. **Preprocessing**: State is validated and potentially modified
3. **Generation**: LLM response is added to the state
4. **Postprocessing**: Final modifications are applied
5. **Final State**: Contains complete conversation and response

## Graph Nodes

### Preprocess Node

**Purpose**: Validates and prepares input messages for processing

**Key Functions**:
- Message length validation and truncation
- Content moderation (if implemented)
- Input sanitization
- Metadata enrichment

**Implementation Details**:
```python
async def preprocess_input(state: GraphState) -> GraphState:
    messages = state.get("messages", [])
    metadata = state.get("metadata", {})
    
    # Truncate long messages
    MAX_MESSAGE_LENGTH = 4000
    processed_messages = []
    
    for message in messages:
        if len(message.content) > MAX_MESSAGE_LENGTH:
            truncated_content = message.content[:MAX_MESSAGE_LENGTH] + "... [truncated]"
            processed_message = message.copy()
            processed_message.content = truncated_content
            processed_messages.append(processed_message)
        else:
            processed_messages.append(message)
    
    return {**state, "messages": processed_messages}
```

**Error Handling**:
- Logs warnings for truncated messages
- Handles empty message lists gracefully
- Preserves original state structure

### Generate Node

**Purpose**: Generates AI responses using the configured language model

**Key Functions**:
- LLM invocation with conversation context
- Response extraction and formatting
- Error handling and retry logic
- Metadata collection

**Implementation Details**:
```python
async def generate_response(state: GraphState, llm: BaseLLM) -> GraphState:
    messages = state.get("messages", [])
    metadata = state.get("metadata", {})
    
    # Generate response using LLM service
    result = await generate_llm_response(llm, messages)
    response_text = result["response"]
    
    # Add response to conversation
    updated_messages = messages + [AIMessage(content=response_text)]
    
    return {
        **state,
        "messages": updated_messages,
        "response": response_text,
        "metadata": {**metadata, **result.get("metadata", {})}
    }
```

**Error Handling**:
- Comprehensive exception logging
- Graceful degradation for LLM failures
- Request tracking for debugging

### Postprocess Node

**Purpose**: Applies final modifications to the generated response

**Key Functions**:
- Response formatting and cleanup
- Content filtering (if required)
- Disclaimer addition
- Final validation

**Implementation Details**:
```python
async def postprocess_output(state: GraphState) -> GraphState:
    response = state.get("response", "")
    
    if response:
        processed_response = response.strip()
        
        # Add AI disclaimer
        disclaimer = "\n\nThis response was generated by an AI assistant."
        if not processed_response.endswith(disclaimer):
            processed_response += disclaimer
        
        return {**state, "response": processed_response}
    
    return state
```

**Customization Options**:
- Configurable disclaimers
- Content filtering rules
- Response formatting templates

### Enhanced Graph Nodes

#### Load History Node
```python
def load_history_node(state: GraphState) -> GraphState:
    """Load conversation history from database."""
    if state.get("session_id"):
        history_service = HistoryService()
        history = history_service.get_conversation_history(state["session_id"])
        state["history"] = history
        state["metadata"]["history_loaded"] = True
        state["metadata"]["messages_in_context"] = len(history)
    return state
```

#### Check API Call Node
```python
def check_api_call_node(state: GraphState) -> GraphState:
    """Determine if an API call should be made."""
    response = state.get("response", "")
    
    # Check if response contains API call indicators
    api_indicators = ["API_CALL:", "FETCH:", "GET:", "POST:"]
    should_call_api = any(indicator in response for indicator in api_indicators)
    
    if should_call_api:
        # Extract API request details
        api_request = extract_api_request(response)
        state["api_request"] = api_request
        state["should_call_api"] = True
    else:
        state["should_call_api"] = False
    
    return state
```

#### Make API Call Node
```python
def make_api_call_node(state: GraphState) -> GraphState:
    """Execute the API call."""
    api_request = state.get("api_request")
    
    if api_request:
        api_service = APIToolsService()
        api_response = api_service.make_request(api_request)
        state["api_response"] = api_response
        
        # Update metadata
        state["metadata"]["api_calls_made"] = 1
        state["metadata"]["api_call_details"] = {
            "url": api_request.url,
            "method": api_request.method,
            "status_code": api_response.status_code,
            "success": api_response.success
        }
    
    return state
```

#### Save History Node
```python
def save_history_node(state: GraphState) -> GraphState:
    """Save the conversation to database."""
    session_id = state.get("session_id")
    messages = state.get("messages", [])
    response = state.get("response", "")
    
    if session_id:
        history_service = HistoryService()
        
        # Save user message
        if messages:
            last_message = messages[-1]
            history_service.save_message(
                session_id=session_id,
                message_type="user",
                content=last_message.content
            )
        
        # Save assistant response
        history_service.save_message(
            session_id=session_id,
            message_type="assistant",
            content=response
        )
    
    return state
```

### Help Flow Node (Conditional Graph)

**Purpose**: Handles help and support requests with specialized responses

**Key Functions**:
- Detects help-related keywords
- Provides structured assistance
- Routes to appropriate support resources

**Implementation Details**:
```python
async def help_flow(state: GraphState) -> GraphState:
    help_response = "I'm here to help! Please let me know what you need assistance with."
    
    return {
        **state,
        "response": help_response,
        "messages": state.get("messages", []) + [AIMessage(content=help_response)]
    }
```

## Graph Builders

### Basic Graph Builder

**Purpose**: Creates a simple linear conversation flow

**Usage**: Standard chat interactions without complex routing

**Configuration**:
```python
async def build_graph(llm: BaseLLM) -> StateGraph:
    graph = StateGraph(GraphState)
    
    # Add nodes
    graph.add_node("preprocess", preprocess_input)
    graph.add_node("generate", generate_with_llm)
    graph.add_node("postprocess", postprocess_output)
    
    # Define edges
    graph.add_edge("preprocess", "generate")
    graph.add_edge("generate", "postprocess")
    graph.add_edge("postprocess", END)
    
    # Set entry point
    graph.set_entry_point("preprocess")
    
    return await graph.compile()
```

### Advanced Graph Builder

**Purpose**: Creates an extensible graph with custom nodes

**Usage**: Complex workflows requiring additional processing steps

**Features**:
- Dynamic node addition
- Flexible edge configuration
- Custom processing logic

**Configuration**:
```python
async def build_advanced_graph(
    llm: BaseLLM, 
    additional_nodes: Dict[str, Callable] = None
) -> StateGraph:
    graph = StateGraph(GraphState)
    
    # Add core nodes
    graph.add_node("preprocess", preprocess_input)
    graph.add_node("generate", generate_with_llm)
    graph.add_node("postprocess", postprocess_output)
    
    # Add custom nodes
    if additional_nodes:
        for name, node_func in additional_nodes.items():
            graph.add_node(name, node_func)
    
    # Configure edges (customizable)
    graph.add_edge("preprocess", "generate")
    graph.add_edge("generate", "postprocess")
    graph.add_edge("postprocess", END)
    
    return await graph.compile()
```

### Conditional Graph Builder

**Purpose**: Creates a graph with intelligent routing based on content

**Usage**: Applications requiring different processing paths

**Features**:
- Content-based routing
- Specialized response flows
- Dynamic path selection

**Router Logic**:
```python
def router(state: GraphState) -> str:
    messages = state.get("messages", [])
    if not messages:
        return "generate"
    
    last_message = messages[-1]
    content = last_message.content.lower()
    
    # Route based on content
    if "help" in content or "support" in content:
        return "help_flow"
    else:
        return "generate"
```

### Enhanced Graph Builder

**Purpose**: Creates an advanced graph with API tool calling and conversation history management

**Usage**: Full-featured chat applications with external API integration and persistent conversations

**Features**:
- Automatic conversation history loading and saving
- Dynamic API call detection and execution
- Conditional routing based on API requirements
- Enhanced state management with session tracking

**Configuration**:
```python
async def build_enhanced_graph(
    llm: BaseLLM,
    history_service: HistoryService,
    api_service: APIToolsService
) -> StateGraph:
    graph = StateGraph(GraphState)
    
    # Add enhanced nodes
    graph.add_node("load_history", load_history_node)
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("generate", generate_node)
    graph.add_node("check_api_call", check_api_call_node)
    graph.add_node("make_api_call", make_api_call_node)
    graph.add_node("postprocess", postprocess_node)
    graph.add_node("save_history", save_history_node)
    
    # Define enhanced routing
    graph.add_edge("load_history", "preprocess")
    graph.add_edge("preprocess", "generate")
    graph.add_edge("generate", "check_api_call")
    
    # Conditional routing for API calls
    graph.add_conditional_edges(
        "check_api_call",
        route_api_decision,
        {
            "make_api_call": "make_api_call",
            "postprocess": "postprocess"
        }
    )
    
    graph.add_edge("make_api_call", "postprocess")
    graph.add_edge("postprocess", "save_history")
    graph.add_edge("save_history", END)
    
    # Set entry point
    graph.set_entry_point("load_history")
    
    return await graph.compile()
```

**Enhanced Router Logic**:
```python
def route_api_decision(state: GraphState) -> str:
    """Route based on API call requirement."""
    should_call_api = state.get("should_call_api", False)
    
    if should_call_api:
        return "make_api_call"
    else:
        return "postprocess"

def route_with_error_handling(state: GraphState) -> str:
    """Enhanced routing with error handling."""
    try:
        # Check for errors in previous nodes
        if state.get("error"):
            return "error_handler"
        
        # Normal routing logic
        return route_api_decision(state)
    except Exception as e:
        logger.error(f"Routing error: {e}")
        return "error_handler"
```

## LLM Integration

### LLM Configuration

The system uses OpenAI's GPT models through LangChain integration:

```python
def get_llm() -> BaseLLM:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )
```

### Configuration Parameters

- **Model**: Configurable model selection (GPT-3.5-turbo, GPT-4, etc.)
- **Temperature**: Controls response creativity (0.0 - 2.0)
- **API Key**: Secure authentication with OpenAI

### Response Generation

**Retry Logic**: Implements exponential backoff for reliability

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_llm_response(
    llm: BaseLLM,
    messages: List[BaseMessage],
    **kwargs
) -> Dict[str, Any]:
    response = await llm.agenerate([messages], **kwargs)
    response_text = response.generations[0][0].text
    
    return {
        "response": response_text,
        "metadata": response.llm_output or {},
    }
```

**Error Handling**:
- Automatic retry on transient failures
- Comprehensive error logging
- Graceful degradation strategies

## Message Flow

### Request Processing Flow

1. **Request Initiation**
   - User sends message through API
   - Request ID generated for tracking
   - Initial state created with message and metadata

2. **Graph Execution**
   - Graph processes state through defined nodes
   - Each node transforms the state
   - Errors are caught and logged at each step

3. **Response Generation**
   - LLM generates response based on conversation context
   - Response is added to conversation history
   - Metadata is enriched with generation details

4. **Response Delivery**
   - Final response is extracted from state
   - Response is sent back to user
   - Request tracking is updated

### State Transitions

```
Initial State:
{
  "messages": [HumanMessage("Hello")],
  "metadata": {"request_id": "123"}
}

After Preprocessing:
{
  "messages": [HumanMessage("Hello")],  # Validated
  "metadata": {"request_id": "123"}
}

After Generation:
{
  "messages": [
    HumanMessage("Hello"),
    AIMessage("Hi there! How can I help you?")
  ],
  "response": "Hi there! How can I help you?",
  "metadata": {"request_id": "123", "tokens_used": 15}
}

After Postprocessing:
{
  "messages": [
    HumanMessage("Hello"),
    AIMessage("Hi there! How can I help you?\n\nThis response was generated by an AI assistant.")
  ],
  "response": "Hi there! How can I help you?\n\nThis response was generated by an AI assistant.",
  "metadata": {"request_id": "123", "tokens_used": 15}
}
```

## Advanced Features

### Custom Node Development

Developers can create custom nodes for specialized processing:

```python
async def custom_sentiment_analysis(state: GraphState) -> GraphState:
    """Analyze sentiment of user messages."""
    messages = state.get("messages", [])
    metadata = state.get("metadata", {})
    
    if messages:
        last_message = messages[-1]
        # Implement sentiment analysis logic
        sentiment = analyze_sentiment(last_message.content)
        metadata["sentiment"] = sentiment
    
    return {**state, "metadata": metadata}
```

### Dynamic Graph Configuration

Graphs can be configured at runtime based on requirements:

```python
# Example: Add sentiment analysis for customer service
additional_nodes = {
    "sentiment_analysis": custom_sentiment_analysis
}

graph = await build_advanced_graph(llm, additional_nodes)
```

### Conditional Routing Strategies

1. **Content-Based Routing**: Route based on message content
2. **User-Based Routing**: Route based on user profile or history
3. **Context-Based Routing**: Route based on conversation context
4. **Time-Based Routing**: Route based on time of day or business hours

### Integration Points

- **Database Integration**: Store conversation history
- **Cache Integration**: Cache frequent responses
- **Analytics Integration**: Track conversation metrics
- **Webhook Integration**: Send notifications or updates

## Performance Considerations

### Optimization Strategies

1. **Async Processing**: All nodes use async/await for non-blocking execution
2. **Connection Pooling**: Reuse LLM connections where possible
3. **Caching**: Cache frequent responses to reduce LLM calls
4. **Batching**: Process multiple requests efficiently

### Monitoring Metrics

- **Response Time**: Track end-to-end processing time
- **Token Usage**: Monitor LLM token consumption
- **Error Rates**: Track failures at each node
- **Throughput**: Measure requests per second

### Scaling Considerations

- **Horizontal Scaling**: Deploy multiple graph instances
- **Load Balancing**: Distribute requests across instances
- **Resource Management**: Monitor memory and CPU usage
- **Rate Limiting**: Prevent API quota exhaustion

## Troubleshooting

### Common Issues

#### Graph Compilation Errors

**Symptoms**: Graph fails to compile
**Causes**: 
- Invalid node definitions
- Circular dependencies
- Missing edge definitions

**Solutions**:
- Validate node signatures
- Check edge connectivity
- Review graph structure

#### LLM Generation Failures

**Symptoms**: Empty or error responses
**Causes**:
- API key issues
- Rate limiting
- Model availability
- Invalid message format

**Solutions**:
- Verify API credentials
- Implement retry logic
- Check model status
- Validate message structure

#### State Corruption

**Symptoms**: Unexpected state values
**Causes**:
- Node implementation errors
- Type mismatches
- Concurrent modifications

**Solutions**:
- Add state validation
- Use proper typing
- Implement state locking

### Debugging Tools

1. **Logging**: Comprehensive logging at each node
2. **State Inspection**: Log state at each transition
3. **Performance Profiling**: Track execution times
4. **Error Tracking**: Capture and analyze exceptions

### Best Practices

1. **Error Handling**: Implement comprehensive error handling
2. **State Validation**: Validate state at each node
3. **Logging**: Add detailed logging for debugging
4. **Testing**: Write unit tests for each node
5. **Documentation**: Document custom nodes and flows
6. **Monitoring**: Implement health checks and metrics

This documentation provides a comprehensive guide to understanding and working with the LangGraph architecture in the Chat Bot System. For additional support or questions, refer to the development team or the LangGraph official documentation.