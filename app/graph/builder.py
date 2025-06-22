from typing import Dict, Any, Optional, List, Callable, Awaitable
from langchain_core.language_models import BaseLLM
from langgraph.graph import StateGraph, END
from loguru import logger

from app.graph.nodes import GraphState, generate_response, preprocess_input, postprocess_output


async def build_graph(llm: BaseLLM) -> StateGraph:
    """Build the chat graph.
    
    Args:
        llm: The language model to use.
        
    Returns:
        The compiled chat graph.
    """
    logger.info("Building chat graph")
    
    # Define the graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    # We'll use partial application to bind the LLM to the generate_response node
    async def generate_with_llm(state: GraphState) -> GraphState:
        return await generate_response(state, llm)
    
    graph.add_node("preprocess", preprocess_input)
    graph.add_node("generate", generate_with_llm)
    graph.add_node("postprocess", postprocess_output)
    
    # Define the edges
    graph.add_edge("preprocess", "generate")
    graph.add_edge("generate", "postprocess")
    graph.add_edge("postprocess", END)
    
    # Set the entry point
    graph.set_entry_point("preprocess")
    
    # Compile the graph
    compiled_graph = await graph.compile()
    logger.info("Chat graph built successfully")
    
    return compiled_graph


async def build_advanced_graph(llm: BaseLLM, additional_nodes: Dict[str, Callable[[GraphState], Awaitable[GraphState]]] = None) -> StateGraph:
    """Build an advanced chat graph with additional nodes.
    
    This is a more flexible version of the build_graph function that allows
    for additional nodes to be added to the graph.
    
    Args:
        llm: The language model to use.
        additional_nodes: Additional nodes to add to the graph.
        
    Returns:
        The compiled chat graph.
    """
    logger.info("Building advanced chat graph")
    
    # Define the graph
    graph = StateGraph(GraphState)
    
    # Add core nodes
    async def generate_with_llm(state: GraphState) -> GraphState:
        return await generate_response(state, llm)
    
    graph.add_node("preprocess", preprocess_input)
    graph.add_node("generate", generate_with_llm)
    graph.add_node("postprocess", postprocess_output)
    
    # Add additional nodes
    if additional_nodes:
        for name, node_func in additional_nodes.items():
            logger.info(f"Adding additional node: {name}")
            graph.add_node(name, node_func)
    
    # Define the core edges
    graph.add_edge("preprocess", "generate")
    graph.add_edge("generate", "postprocess")
    graph.add_edge("postprocess", END)
    
    # Set the entry point
    graph.set_entry_point("preprocess")
    
    # Compile the graph
    compiled_graph = await graph.compile()
    logger.info("Advanced chat graph built successfully")
    
    return compiled_graph


async def build_conditional_graph(llm: BaseLLM) -> StateGraph:
    """Build a chat graph with conditional routing.
    
    This is an example of a more complex graph with conditional routing
    based on the content of the messages.
    
    Args:
        llm: The language model to use.
        
    Returns:
        The compiled chat graph.
    """
    logger.info("Building conditional chat graph")
    
    # Define the graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    async def generate_with_llm(state: GraphState) -> GraphState:
        return await generate_response(state, llm)
    
    graph.add_node("preprocess", preprocess_input)
    graph.add_node("generate", generate_with_llm)
    graph.add_node("postprocess", postprocess_output)
    
    # Define a conditional router
    def router(state: GraphState) -> str:
        """Route based on message content."""
        messages = state.get("messages", [])
        if not messages:
            return "generate"
        
        last_message = messages[-1]
        content = last_message.content.lower()
        
        # Example routing logic
        if "help" in content or "support" in content:
            logger.info("Routing to help flow")
            return "help_flow"
        else:
            return "generate"
    
    # Add a help flow node
    async def help_flow(state: GraphState) -> GraphState:
        """Handle help requests."""
        logger.info("Processing help request")
        return {
            **state,
            "response": "I'm here to help! Please let me know what you need assistance with.",
            "messages": state.get("messages", []) + [AIMessage(content="I'm here to help! Please let me know what you need assistance with.")]
        }
    
    graph.add_node("help_flow", help_flow)
    
    # Define the edges with conditional routing
    graph.add_conditional_edges(
        "preprocess",
        router,
        {
            "generate": "generate",
            "help_flow": "help_flow"
        }
    )
    graph.add_edge("generate", "postprocess")
    graph.add_edge("help_flow", "postprocess")
    graph.add_edge("postprocess", END)
    
    # Set the entry point
    graph.set_entry_point("preprocess")
    
    # Compile the graph
    compiled_graph = await graph.compile()
    logger.info("Conditional chat graph built successfully")
    
    return compiled_graph