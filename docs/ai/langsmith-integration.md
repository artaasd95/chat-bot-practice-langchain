# LangSmith Integration Guide

This document provides comprehensive information about integrating and using LangSmith with the LangGraph Chat Bot System.

## Overview

LangSmith is a powerful platform for debugging, testing, evaluating, and monitoring LLM applications. It provides detailed tracing and visualization of LangChain and LangGraph components, making it easier to understand and optimize your LLM application.

## Setup

### Prerequisites

- A LangSmith account (sign up at [smith.langchain.com](https://smith.langchain.com))
- LangSmith API key (available in your LangSmith account settings)

### Configuration

1. Add the following environment variables to your `.env` file:

```bash
# LangSmith Settings
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=chatbot-microservices
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

2. Install the required packages:

```bash
pip install langsmith langchain
```

3. Restart your application to apply the changes.

## Integration Points

The Chat Bot System integrates with LangSmith at several key points:

### 1. LLM Calls

All LLM calls are automatically traced using the `track_llm_usage` decorator in `app/utils/monitoring.py`. This decorator:

- Records the prompt and completion
- Tracks token usage
- Measures latency
- Captures any errors

```python
@track_llm_usage
async def generate_llm_response(prompt, model):
    # LLM call implementation
    pass
```

### 2. Graph Node Executions

Each node in the LangGraph is traced using the `track_graph_node` decorator. This provides visibility into:

- The flow of data through the graph
- Execution time of each node
- Inputs and outputs at each step
- Any errors that occur

```python
@track_graph_node
async def process_input(state):
    # Node implementation
    pass
```

### 3. Application Startup

LangSmith is initialized during application startup in the `setup_monitoring` function:

```python
def setup_monitoring():
    # Other monitoring setup...
    
    if settings.LANGCHAIN_TRACING_V2 and LANGSMITH_AVAILABLE:
        # Initialize LangSmith client
        logger.info(f"LangSmith tracing enabled for project {settings.LANGCHAIN_PROJECT}")
        
        # Set environment variables for LangChain
        import os
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        if settings.LANGCHAIN_ENDPOINT:
            os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
```

## Using LangSmith

### Accessing Traces

1. Log in to your LangSmith account at [smith.langchain.com](https://smith.langchain.com)
2. Navigate to the project specified in your configuration (default: `chatbot-microservices`)
3. View the list of traces, which include:
   - LLM calls
   - Graph executions
   - API calls

### Analyzing Traces

#### Trace View

Click on any trace to see detailed information:

- **Inputs and Outputs**: See what went into and came out of each component
- **Execution Time**: Identify performance bottlenecks
- **Token Usage**: Monitor costs and optimize prompts
- **Errors**: Debug failures with full context

#### Graph Visualization

For LangGraph traces, you can see a visual representation of the graph execution:

- **Node Flow**: See the exact path taken through the graph
- **State at Each Step**: Inspect the state before and after each node
- **Decision Points**: Understand routing decisions in conditional graphs

### Evaluating Responses

LangSmith provides tools for evaluating LLM responses:

1. Create evaluation datasets from your traces
2. Define custom evaluation metrics
3. Compare different models and prompts
4. Track performance over time

## Advanced Usage

### Custom Tracing

You can add custom traces for specific parts of your application:

```python
from langsmith import Client

client = Client(
    api_key=settings.LANGCHAIN_API_KEY,
    api_url=settings.LANGCHAIN_ENDPOINT
)

with client.trace("custom_operation", project_name=settings.LANGCHAIN_PROJECT) as trace:
    # Your code here
    result = perform_operation()
    trace.add_input({"input_data": input_data})
    trace.add_output({"result": result})
```

### A/B Testing

Use LangSmith to compare different approaches:

1. Create multiple versions of your graph or prompts
2. Run them in parallel with the same inputs
3. Compare the results in LangSmith
4. Use the evaluation tools to quantify the differences

## Troubleshooting

### Common Issues

1. **No traces appearing in LangSmith**
   - Verify your API key is correct
   - Check that `LANGCHAIN_TRACING_V2` is set to `true`
   - Ensure the application has internet access

2. **Missing information in traces**
   - Check that decorators are applied correctly
   - Verify that the data being passed is serializable

3. **Performance impact**
   - LangSmith tracing adds minimal overhead
   - For production, consider sampling traces instead of tracing everything

## Best Practices

1. **Use meaningful names** for your traces and projects
2. **Add tags** to categorize traces
3. **Include relevant metadata** in your traces
4. **Create datasets** from your traces for continuous evaluation
5. **Share traces** with your team for collaborative debugging

## Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Documentation](https://python.langchain.com/docs/langsmith)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)