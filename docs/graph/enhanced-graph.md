# Enhanced Chat Graph with API Tools and History Management

The enhanced chat graph provides advanced functionality including conversation history management, REST API tool calling, and conditional routing based on LLM decisions.

## Features

### 1. Conversation History Management
- **Automatic History Loading**: Loads previous conversation history at the start of each interaction
- **Context Integration**: Adds conversation history to LLM context for better continuity
- **Persistent Storage**: Saves all interactions to the database for future reference
- **Session-based**: Maintains separate conversation threads using session IDs

### 2. REST API Tool Calling
- **Dynamic API Calls**: LLM can request API calls during conversation
- **Multiple HTTP Methods**: Supports GET, POST, PUT, DELETE, PATCH
- **Flexible Parameters**: Handles headers, query parameters, and request bodies
- **Error Handling**: Graceful handling of API failures with informative error messages
- **Response Integration**: API responses are automatically integrated into the conversation

### 3. Conditional Routing
- **Smart Routing**: Automatically routes to API execution when needed
- **Decision-based Flow**: LLM decisions determine the conversation flow
- **Parallel Processing**: Efficient handling of different conversation paths

## Graph Architecture

```
┌─────────────────┐
│  Load History   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Preprocess    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Generate LLM  │
│    Response     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Check for API  │
│      Call       │
└─────────┬───────┘
          │
          ▼
    ┌─────────┐
    │ API     │ ◄─── Yes
    │ Call?   │
    └─────────┘
          │ No
          ▼
┌─────────────────┐
│   Postprocess   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Save History   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│      END        │
└─────────────────┘
```

## Usage

### Basic Setup

```python
from app.services.llm import get_llm
from app.graph.builder import build_enhanced_graph
from app.graph.nodes import GraphState
from langchain_core.messages import HumanMessage

# Initialize the enhanced graph
llm = get_llm()
graph = await build_enhanced_graph(llm)

# Create state with session ID
state = {
    "messages": [HumanMessage(content="Hello!")],
    "session_id": "your-session-id",
    "metadata": {"request_id": "req-1"}
}

# Run the graph
result = await graph.ainvoke(state)
```

### API Call Format

The LLM can request API calls using this format:

```
API_CALL: {"url": "https://api.example.com/data", "method": "GET", "headers": {"Authorization": "Bearer token"}, "params": {"limit": 10}}
```

#### Supported Parameters

- **url** (required): The API endpoint URL
- **method** (optional): HTTP method (GET, POST, PUT, DELETE, PATCH). Default: GET
- **headers** (optional): HTTP headers as key-value pairs
- **params** (optional): Query parameters for GET requests
- **data** (optional): Request body data for POST/PUT/PATCH requests
- **timeout** (optional): Request timeout in seconds. Default: 30

### Examples

#### Simple GET Request
```
API_CALL: {"url": "https://jsonplaceholder.typicode.com/posts/1", "method": "GET"}
```

#### POST Request with Data
```
API_CALL: {
  "url": "https://api.example.com/users",
  "method": "POST",
  "headers": {"Content-Type": "application/json"},
  "data": {"name": "John Doe", "email": "john@example.com"}
}
```

#### GET Request with Parameters
```
API_CALL: {
  "url": "https://api.example.com/search",
  "method": "GET",
  "params": {"q": "python", "limit": 5}
}
```

## State Schema

The enhanced graph uses an extended state schema:

```python
class GraphState(TypedDict, total=False):
    messages: List[BaseMessage]          # Current conversation messages
    response: Optional[str]              # Generated LLM response
    metadata: Dict[str, Any]             # Request metadata
    session_id: Optional[str]            # Conversation session ID
    history: List[BaseMessage]           # Loaded conversation history
    api_request: Optional[str]           # Raw API request from LLM
    api_response: Optional[Dict[str, Any]] # API response data
    should_call_api: bool                # Whether to make an API call
```

## Configuration

### Environment Variables

No additional environment variables are required for the enhanced graph. It uses the existing LLM and database configurations.

### Database Setup

Ensure your database includes the required tables:

- `chat_sessions`: For managing conversation sessions
- `chat_messages`: For storing individual messages

## Error Handling

### API Call Errors

- **Network Errors**: Handled gracefully with informative error messages
- **HTTP Errors**: Status codes and error details are captured and reported
- **Timeout Errors**: Configurable timeout with fallback behavior
- **Parsing Errors**: Invalid API request formats are caught and reported

### History Errors

- **Database Errors**: Graceful fallback when history cannot be loaded or saved
- **Session Errors**: Automatic session creation when session ID is not found
- **Permission Errors**: Proper error handling for database access issues

## Performance Considerations

### History Loading

- **Limit Control**: History loading is limited to the 10 most recent messages by default
- **Lazy Loading**: History is only loaded when a session ID is provided
- **Caching**: Consider implementing caching for frequently accessed sessions

### API Calls

- **Timeout Management**: Default 30-second timeout prevents hanging requests
- **Connection Pooling**: Uses aiohttp for efficient HTTP connection management
- **Async Processing**: All API calls are asynchronous and non-blocking

### Memory Usage

- **State Management**: State is passed efficiently between nodes
- **Message Limits**: Consider implementing message history limits for long conversations
- **Cleanup**: Automatic cleanup of HTTP sessions

## Security Considerations

### API Security

- **URL Validation**: All URLs are validated before making requests
- **Header Sanitization**: Headers are validated to prevent injection attacks
- **Timeout Protection**: Prevents resource exhaustion from long-running requests
- **Error Information**: Sensitive information is not exposed in error messages

### Data Privacy

- **History Encryption**: Consider encrypting sensitive conversation data
- **Session Isolation**: Each session is isolated from others
- **Access Control**: Implement proper access controls for conversation history

## Testing

Run the test suite to verify functionality:

```bash
python test_enhanced_graph.py
```

The test suite includes:

- Basic conversation flow
- History loading and saving
- API call execution
- Error handling scenarios
- LLM-generated API calls

## Troubleshooting

### Common Issues

1. **History Not Loading**
   - Check database connection
   - Verify session ID format
   - Check table permissions

2. **API Calls Failing**
   - Verify network connectivity
   - Check API endpoint availability
   - Validate request format

3. **Graph Execution Errors**
   - Check LLM configuration
   - Verify all dependencies are installed
   - Review error logs for details

### Debug Mode

Enable debug logging to get detailed information:

```python
import logging
logging.getLogger('app').setLevel(logging.DEBUG)
```

## Future Enhancements

- **API Authentication**: Built-in support for various authentication methods
- **Rate Limiting**: Automatic rate limiting for API calls
- **Caching**: Response caching for frequently called APIs
- **Webhooks**: Support for webhook-based API interactions
- **Batch Operations**: Support for multiple API calls in a single request