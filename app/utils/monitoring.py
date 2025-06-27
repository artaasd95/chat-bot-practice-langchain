from typing import Dict, Any, Optional, List
import time
from functools import wraps
from loguru import logger

from app.config import settings

# Try to import prometheus client if metrics are enabled
if settings.METRICS_ENABLED:
    try:
        import prometheus_client
        from prometheus_client import Counter, Histogram, Gauge
        PROMETHEUS_AVAILABLE = True
    except ImportError:
        logger.warning("prometheus_client not installed. Metrics collection disabled.")
        PROMETHEUS_AVAILABLE = False
else:
    PROMETHEUS_AVAILABLE = False

# Try to import langsmith if tracing is enabled
if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
    try:
        from langsmith import Client
        LANGSMITH_AVAILABLE = True
    except ImportError:
        logger.warning("langsmith not installed. LangSmith tracing disabled.")
        LANGSMITH_AVAILABLE = False
else:
    LANGSMITH_AVAILABLE = False


# Define Prometheus metrics if available
if PROMETHEUS_AVAILABLE:
    # LLM metrics
    LLM_REQUEST_COUNT = Counter(
        'llm_requests_total', 
        'Total number of LLM requests',
        ['model', 'status']
    )
    LLM_REQUEST_LATENCY = Histogram(
        'llm_request_latency_seconds', 
        'LLM request latency in seconds',
        ['model']
    )
    LLM_TOKEN_USAGE = Counter(
        'llm_token_usage_total', 
        'Total number of tokens used',
        ['model', 'type']  # type can be 'prompt' or 'completion'
    )
    
    # API metrics
    API_REQUEST_COUNT = Counter(
        'api_requests_total', 
        'Total number of API requests',
        ['endpoint', 'method', 'status']
    )
    API_REQUEST_LATENCY = Histogram(
        'api_request_latency_seconds', 
        'API request latency in seconds',
        ['endpoint', 'method']
    )
    
    # Graph metrics
    GRAPH_NODE_EXECUTION_COUNT = Counter(
        'graph_node_executions_total', 
        'Total number of graph node executions',
        ['node_name', 'status']
    )
    GRAPH_NODE_EXECUTION_LATENCY = Histogram(
        'graph_node_execution_latency_seconds', 
        'Graph node execution latency in seconds',
        ['node_name']
    )
    
    # System metrics
    ACTIVE_USERS = Gauge(
        'active_users', 
        'Number of active users'
    )
    ACTIVE_CONVERSATIONS = Gauge(
        'active_conversations', 
        'Number of active conversations'
    )


def track_llm_usage(func):
    """Decorator to track LLM usage metrics.
    
    This decorator will track:
    - Request count
    - Latency
    - Token usage
    
    It will also send the data to LangSmith if configured, enabling:
    - Detailed tracing of LLM calls and completions
    - Token usage and cost tracking
    - Performance monitoring
    - Debugging of LLM interactions
    
    Args:
        func: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        model = kwargs.get('model', 'unknown')
        start_time = time.time()
        success = False
        token_usage = {}
        
        try:
            # Call the original function
            result = await func(*args, **kwargs)
            success = True
            
            # Extract token usage if available
            if hasattr(result, 'usage') and result.usage:
                token_usage = {
                    'prompt_tokens': getattr(result.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(result.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(result.usage, 'total_tokens', 0)
                }
            
            return result
        
        except Exception as e:
            logger.exception(f"Error in LLM request: {str(e)}")
            raise
        
        finally:
            # Record metrics
            duration = time.time() - start_time
            
            # Log the metrics
            status = 'success' if success else 'failure'
            logger.info(f"LLM request: model={model}, status={status}, duration={duration:.2f}s, tokens={token_usage}")
            
            # Record Prometheus metrics if available
            if PROMETHEUS_AVAILABLE:
                LLM_REQUEST_COUNT.labels(model=model, status=status).inc()
                LLM_REQUEST_LATENCY.labels(model=model).observe(duration)
                
                if token_usage:
                    LLM_TOKEN_USAGE.labels(model=model, type='prompt').inc(token_usage.get('prompt_tokens', 0))
                    LLM_TOKEN_USAGE.labels(model=model, type='completion').inc(token_usage.get('completion_tokens', 0))
            
            # Record LangSmith run if available
            if LANGSMITH_AVAILABLE and settings.LANGCHAIN_TRACING_V2:
                try:
                    from langsmith import Client
                    
                    # Create a LangSmith client
                    client = Client(
                        api_key=settings.LANGCHAIN_API_KEY,
                        api_url=settings.LANGCHAIN_ENDPOINT
                    )
                    
                    # Extract inputs and outputs
                    inputs = {}
                    outputs = {}
                    
                    # Get the prompt from args/kwargs
                    if 'prompt' in kwargs:
                        inputs['prompt'] = kwargs['prompt']
                    elif 'messages' in kwargs:
                        inputs['messages'] = kwargs['messages']
                    
                    # Get the completion from result
                    if result:
                        if hasattr(result, 'choices') and result.choices:
                            outputs['completion'] = result.choices[0].message.content
                        elif hasattr(result, 'content'):
                            outputs['completion'] = result.content
                    
                    # Add token usage if available
                    if token_usage:
                        outputs['token_usage'] = token_usage
                    
                    # Create a run in LangSmith
                    client.create_run(
                        name=f"llm_call_{model}",
                        run_type="llm",
                        inputs=inputs,
                        outputs=outputs if success else {},
                        error=str(e) if not success else None,
                        execution_time=duration,
                        project_name=settings.LANGCHAIN_PROJECT,
                        tags=["llm", model]
                    )
                    
                    logger.debug(f"Recorded LangSmith run for LLM call to {model}")
                except Exception as ls_error:
                    logger.warning(f"Failed to record LangSmith run: {ls_error}")
                    pass
    
    return wrapper


def track_api_request(func):
    """Decorator to track API request metrics.
    
    Args:
        func: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract endpoint and method from the request object
        request = kwargs.get('request', None)
        if request:
            endpoint = request.url.path
            method = request.method
        else:
            endpoint = 'unknown'
            method = 'unknown'
        
        start_time = time.time()
        status_code = 500  # Default to error
        
        try:
            # Call the original function
            response = await func(*args, **kwargs)
            status_code = response.status_code
            return response
        
        except Exception as e:
            logger.exception(f"Error in API request: {str(e)}")
            raise
        
        finally:
            # Record metrics
            duration = time.time() - start_time
            
            # Log the metrics
            logger.info(f"API request: endpoint={endpoint}, method={method}, status={status_code}, duration={duration:.2f}s")
            
            # Record Prometheus metrics if available
            if PROMETHEUS_AVAILABLE:
                API_REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=status_code).inc()
                API_REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(duration)
    
    return wrapper


def track_graph_node(func):
    """Decorator to track graph node execution metrics.
    
    Args:
        func: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get the node name from the function name
        node_name = func.__name__
        
        start_time = time.time()
        success = False
        
        try:
            # Call the original function
            result = await func(*args, **kwargs)
            success = True
            return result
        
        except Exception as e:
            logger.exception(f"Error in graph node {node_name}: {str(e)}")
            raise
        
        finally:
            # Record metrics
            duration = time.time() - start_time
            
            # Log the metrics
            status = 'success' if success else 'failure'
            logger.debug(f"Graph node execution: node={node_name}, status={status}, duration={duration:.2f}s")
            
            # Record Prometheus metrics if available
            if PROMETHEUS_AVAILABLE:
                GRAPH_NODE_EXECUTION_COUNT.labels(node_name=node_name, status=status).inc()
                GRAPH_NODE_EXECUTION_LATENCY.labels(node_name=node_name).observe(duration)
                
                # If this is a LangSmith run and tracing is enabled, record the run
                if LANGSMITH_AVAILABLE and settings.LANGCHAIN_TRACING_V2:
                    try:
                        from langsmith import Client
                        
                        # Create a LangSmith client
                        client = Client(
                            api_key=settings.LANGCHAIN_API_KEY,
                            api_url=settings.LANGCHAIN_ENDPOINT
                        )
                        
                        # Extract inputs and outputs for the run
                        inputs = {}
                        outputs = {}
                        
                        # If the first argument is a dictionary (likely the state), use it as input
                        if args and isinstance(args[0], dict):
                            inputs = args[0]
                        
                        # If the result is a dictionary, use it as output
                        if isinstance(result, dict):
                            outputs = result
                        
                        # Create a run in LangSmith
                        client.create_run(
                            name=node_name,
                            run_type="chain",
                            inputs=inputs,
                            outputs=outputs if success else {},
                            error=str(e) if not success else None,
                            execution_time=duration,
                            project_name=settings.LANGCHAIN_PROJECT,
                            tags=["graph_node", node_name]
                        )
                        
                        logger.debug(f"Recorded LangSmith run for node {node_name}")
                    except Exception as ls_error:
                        logger.warning(f"Failed to record LangSmith run: {ls_error}")
                        pass
    
    return wrapper


def setup_monitoring():
    """Set up monitoring and metrics collection.
    
    This function initializes the monitoring system based on configuration.
    """
    if settings.METRICS_ENABLED and PROMETHEUS_AVAILABLE:
        # Start Prometheus HTTP server
        prometheus_client.start_http_server(settings.METRICS_PORT)
        logger.info(f"Prometheus metrics server started on port {settings.METRICS_PORT}")
    
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


def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics.
    
    Returns:
        A dictionary of system metrics.
    """
    metrics = {
        "active_users": 0,
        "active_conversations": 0,
        "llm_requests": {},
        "api_requests": {},
        "graph_executions": {}
    }
    
    # In a real implementation, these would be populated from the actual metrics
    if PROMETHEUS_AVAILABLE:
        # This is just a placeholder - in a real implementation, you would
        # query the Prometheus metrics
        pass
    
    return metrics