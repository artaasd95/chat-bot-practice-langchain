# LangGraph Chat System

A scalable asynchronous chat system built with LangGraph and FastAPI, featuring both direct and webhook response capabilities.

## Features

### Core Features
- **Multiple LLM Providers**: Support for OpenAI and DeepSeek APIs with automatic provider detection
- **Enhanced Graph Architecture**: Advanced conversation flow with history management and API tool calling
- **REST API Tools**: LLM can make external API calls during conversations with conditional routing
- **Conversation History**: Automatic loading and saving of conversation context across sessions
- **Asynchronous Processing**: Fully async implementation for high throughput
- **Dual Response Modes**:
  - Direct API responses for immediate results
  - Webhook callbacks for long-running processes

### Advanced Features
- **API Tool Integration**: Automatic detection and execution of REST API calls within conversations
- **Session Management**: Persistent conversation sessions with automatic context loading
- **Conditional Graph Routing**: Smart routing based on content analysis and API requirements
- **Database Integration**: PostgreSQL support for conversation history and session management
- **Enhanced State Management**: Rich state tracking with metadata and API call details
- **LangSmith Integration**: Comprehensive tracing, monitoring, debugging, and evaluation of LLM applications

### Architecture Features
- **Scalable Architecture**:
  - Modular design with clear separation of concerns
  - Extensible graph structure for easy addition of new nodes
  - Configurable via environment variables
- **Comprehensive Logging**: Detailed logging with rotation and retention policies
- **Request Tracking**: Built-in tracking system for webhook requests
- **Service-Oriented Design**: Dedicated services for API tools, history management, and LLM operations

## Project Structure

```
.
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration management
│   ├── api/               # API endpoints and models
│   │   ├── __init__.py
│   │   ├── models.py      # Pydantic models for requests/responses
│   │   └── routes.py      # API route definitions
│   ├── database/          # Database models and operations
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy database models
│   │   └── session.py     # Database session management
│   ├── graph/             # LangGraph implementation
│   │   ├── __init__.py
│   │   ├── builder.py     # Graph construction (basic, advanced, enhanced)
│   │   └── nodes.py       # Graph node implementations
│   ├── services/          # Core services
│   │   ├── __init__.py
│   │   ├── api_tools.py   # API tools service for external calls
│   │   ├── history.py     # Conversation history service
│   │   ├── llm.py         # LLM service
│   │   └── webhook.py     # Webhook service
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── logging.py     # Logging configuration
│       ├── monitoring.py  # Monitoring and LangSmith integration
│       └── tracking.py    # Request tracking utilities
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   │   └── chat-api.md   # Chat API endpoints and models
│   ├── ai/               # AI/LangGraph documentation
│   │   ├── langgraph-architecture.md  # Graph architecture guide
│   │   ├── langsmith-integration.md   # LangSmith integration guide
│   │   └── deepseek-integration.md    # DeepSeek integration guide
│   ├── backend/          # Backend documentation
│   │   ├── architecture.md  # System architecture
│   │   └── services.md   # Services documentation
│   └── database/         # Database documentation
│       └── schema.md     # Database schema and models
├── tests/                # Test files
│   └── test_enhanced_graph.py  # Enhanced graph tests
└── requirements.txt      # Project dependencies
```

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key OR DeepSeek API key (or other LLM provider)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chat-bot-practice-langchain.git
   cd chat-bot-practice-langchain
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your configuration:
   ```
   # API Settings
   API_HOST=0.0.0.0
   API_PORT=8000
   API_WORKERS=4
   
   # CORS Settings
   CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:8080
   
   # LLM Settings - Choose your provider
   LLM_PROVIDER=openai  # or "deepseek" for DeepSeek API
   LLM_MODEL=gpt-3.5-turbo  # or "deepseek-chat" for DeepSeek
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=1000
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key
   
   # DeepSeek Configuration (alternative to OpenAI)
   DEEPSEEK_API_KEY=your_deepseek_api_key
   
   # Logging Settings
   LOG_LEVEL=INFO
   LOG_RETENTION=7 days
   LOG_ROTATION=100 MB
   
   # Webhook Settings
   WEBHOOK_MAX_RETRIES=3
   WEBHOOK_RETRY_DELAY=2
   ```

### Running the Application

#### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000
```

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Enhanced Chat (Recommended)

The enhanced chat endpoint provides full conversation history and API tool calling capabilities:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "conversation_id": "optional-session-id"
  }'
```

Response includes enhanced metadata:
```json
{
  "response": "Hello! I'm doing well, thank you for asking.",
  "request_id": "req_123456",
  "conversation_id": "conv_789",
  "metadata": {
    "api_calls_made": 0,
    "history_loaded": true,
    "messages_in_context": 5,
    "api_call_details": null
  }
}
```

### Direct Chat (Legacy)

```bash
curl -X POST http://localhost:8000/api/chat/direct \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello, how are you?"}]}'
```

### Webhook Chat

```bash
curl -X POST http://localhost:8000/api/chat/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me about LangGraph"}],
    "callback_url": "https://your-callback-url.com/webhook"
  }'
```

### Check Webhook Status

```bash
curl http://localhost:8000/api/chat/webhook/status/{track_id}
```

## Enhanced Graph Features

### API Tool Calling

The enhanced graph can automatically detect when the LLM wants to make external API calls and execute them:

```python
# Example conversation that triggers API call
user_message = "Get the current weather in New York"
# LLM response: "API_CALL: GET https://api.weather.com/v1/current?location=New+York"
# System automatically makes the API call and incorporates the response
```

### Conversation History

Conversations are automatically saved and loaded:

- **Automatic Loading**: Previous messages are loaded when a `conversation_id` is provided
- **Context Management**: The system maintains conversation context across sessions
- **Persistent Storage**: All conversations are stored in PostgreSQL database

### Graph Types

1. **Basic Graph**: Simple linear flow for standard conversations
2. **Advanced Graph**: Extensible graph with custom nodes
3. **Conditional Graph**: Smart routing based on message content
4. **Enhanced Graph**: Full-featured graph with API tools and history management

## Extending the Graph

The system is designed to be easily extensible. To add new nodes to the graph:

1. Define new node functions in `app/graph/nodes.py`
2. Update the graph builder in `app/graph/builder.py` to include your new nodes
3. Modify the API routes as needed to support new functionality

Example of adding a new node:

```python
# In app/graph/nodes.py
async def my_new_node(state: GraphState) -> GraphState:
    # Process state
    return updated_state

# In app/graph/builder.py
async def build_custom_graph(llm: BaseLLM) -> StateGraph:
    # ... existing code ...
    graph.add_node("my_new_node", my_new_node)
    graph.add_edge("generate", "my_new_node")
    graph.add_edge("my_new_node", "postprocess")
    # ... rest of the code ...
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **API Documentation**: Complete API reference with examples
- **Architecture Guide**: Detailed system architecture and design patterns
- **Services Documentation**: In-depth service descriptions and implementations
- **Database Schema**: Database models and relationships
- **LangGraph Architecture**: Graph design patterns and node implementations
- **LangSmith Integration**: Comprehensive guide for tracing, monitoring, debugging, and evaluating LLM applications
- **DeepSeek Integration**: Guide for using DeepSeek models as an alternative LLM provider

## License

MIT