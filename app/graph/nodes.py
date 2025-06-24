from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseLLM
from typing_extensions import TypedDict
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session

from app.config import settings
from app.services.api_tools import (
    get_api_service, 
    parse_api_request_from_text, 
    should_make_api_call,
    APIRequest,
    APIResponse
)
from app.services.history import get_history_service, format_history_for_llm
from app.database.database import get_db
from app.services.llm import generate_llm_response


class GraphState(TypedDict, total=False):
    """Type definition for the graph state."""
    messages: List[BaseMessage]
    response: Optional[str]
    metadata: Dict[str, Any]
    session_id: Optional[str]
    history: List[BaseMessage]
    api_request: Optional[str]
    api_response: Optional[Dict[str, Any]]
    should_call_api: bool


async def generate_response(state: GraphState, llm: BaseLLM) -> GraphState:
    """Generate a response using the LLM.
    
    Args:
        state: The current state.
        llm: The language model to use.
        
    Returns:
        The updated state with the response.
    """
    messages = state.get("messages", [])
    metadata = state.get("metadata", {})
    
    request_id = metadata.get("request_id", "unknown")
    logger.info(f"Generating response for request ID: {request_id}")
    
    # Get the last message
    if not messages:
        logger.warning(f"No messages to respond to for request ID: {request_id}")
        return {**state, "response": "No messages to respond to."}
    
    try:
        # Generate response using the LLM service
        result = await generate_llm_response(llm, messages)
        response_text = result["response"]
        
        # Add the response to the messages
        updated_messages = messages + [AIMessage(content=response_text)]
        
        logger.info(f"Generated response for request ID: {request_id}")
        logger.debug(f"Response: {response_text}")
        
        # Update the state
        return {
            **state,
            "messages": updated_messages,
            "response": response_text,
            "metadata": {**metadata, **result.get("metadata", {})}
        }
    except Exception as e:
        logger.error(f"Error generating response for request ID {request_id}: {str(e)}")
        raise


async def preprocess_input(state: GraphState) -> GraphState:
    """Preprocess the input messages.
    
    This node can be used for input validation, content moderation,
    or any other preprocessing steps.
    
    Args:
        state: The current state.
        
    Returns:
        The updated state after preprocessing.
    """
    messages = state.get("messages", [])
    metadata = state.get("metadata", {})
    
    request_id = metadata.get("request_id", "unknown")
    logger.info(f"Preprocessing input for request ID: {request_id}")
    
    # Example preprocessing: Truncate very long messages
    MAX_MESSAGE_LENGTH = 4000
    
    processed_messages = []
    for message in messages:
        if len(message.content) > MAX_MESSAGE_LENGTH:
            logger.warning(f"Truncating long message for request ID: {request_id}")
            # Create a new message with truncated content
            truncated_content = message.content[:MAX_MESSAGE_LENGTH] + "... [truncated]"
            processed_message = message.copy()
            processed_message.content = truncated_content
            processed_messages.append(processed_message)
        else:
            processed_messages.append(message)
    
    logger.info(f"Input preprocessing completed for request ID: {request_id}")
    
    return {**state, "messages": processed_messages}


async def postprocess_output(state: GraphState) -> GraphState:
    """Post-process the output.
    
    Args:
        state: The current state.
        
    Returns:
        The updated state.
    """
    logger.info("Post-processing output")
    
    # Add any post-processing logic here
    state["metadata"]["postprocessed"] = True
    
    return state


async def load_conversation_history(state: GraphState) -> GraphState:
    """Load conversation history for the session.
    
    Args:
        state: The current state.
        
    Returns:
        The updated state with conversation history.
    """
    logger.info("Loading conversation history")
    
    session_id = state.get("session_id")
    if not session_id:
        logger.warning("No session_id provided, skipping history loading")
        state["history"] = []
        return state
    
    try:
        # Get database session
        db = next(get_db())
        history_service = get_history_service(db)
        
        # Load conversation history
        history = await history_service.load_conversation_history(session_id, limit=10)
        state["history"] = history
        
        # Add history to messages for LLM context
        if history:
            # Create a system message with formatted history
            history_text = format_history_for_llm(history)
            from langchain_core.messages import SystemMessage
            history_message = SystemMessage(content=f"Context: {history_text}")
            
            # Insert at the beginning of messages
            current_messages = state.get("messages", [])
            state["messages"] = [history_message] + current_messages
        
        logger.info(f"Loaded {len(history)} messages from history")
        
    except Exception as e:
        logger.error(f"Error loading conversation history: {str(e)}")
        state["history"] = []
    
    return state


async def check_for_api_call(state: GraphState) -> GraphState:
    """Check if the LLM response contains an API call request.
    
    Args:
        state: The current state.
        
    Returns:
        The updated state with API call information.
    """
    logger.info("Checking for API call request")
    
    response = state.get("response", "")
    
    # Check if response contains API call
    if should_make_api_call(response):
        state["should_call_api"] = True
        state["api_request"] = response
        logger.info("API call detected in response")
    else:
        state["should_call_api"] = False
        logger.info("No API call detected")
    
    return state


async def make_api_call(state: GraphState) -> GraphState:
    """Make the API call requested by the LLM.
    
    Args:
        state: The current state.
        
    Returns:
        The updated state with API response.
    """
    logger.info("Making API call")
    
    api_request_text = state.get("api_request", "")
    
    try:
        # Parse the API request
        api_request = parse_api_request_from_text(api_request_text)
        
        if not api_request:
            logger.error("Failed to parse API request")
            state["api_response"] = {
                "error": "Failed to parse API request",
                "success": False
            }
            return state
        
        # Make the API call
        api_service = await get_api_service()
        response = await api_service.make_request(api_request)
        
        # Store the response
        state["api_response"] = {
            "status_code": response.status_code,
            "data": response.data,
            "text": response.text,
            "error": response.error,
            "success": response.success
        }
        
        # Update the LLM response to include API results
        if response.success:
            api_result = f"\n\nAPI Response: {response.data or response.text}"
            state["response"] = state.get("response", "") + api_result
            logger.info("API call successful")
        else:
            error_msg = f"\n\nAPI Error: {response.error}"
            state["response"] = state.get("response", "") + error_msg
            logger.error(f"API call failed: {response.error}")
        
    except Exception as e:
        logger.error(f"Error making API call: {str(e)}")
        state["api_response"] = {
            "error": str(e),
            "success": False
        }
        error_msg = f"\n\nAPI Error: {str(e)}"
        state["response"] = state.get("response", "") + error_msg
    
    return state


async def save_to_history(state: GraphState) -> GraphState:
    """Save the current interaction to conversation history.
    
    Args:
        state: The current state.
        
    Returns:
        The updated state.
    """
    logger.info("Saving interaction to history")
    
    session_id = state.get("session_id")
    if not session_id:
        logger.warning("No session_id provided, skipping history saving")
        return state
    
    try:
        # Get database session
        db = next(get_db())
        history_service = get_history_service(db)
        
        # Save human message
        messages = state.get("messages", [])
        human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
        
        if human_messages:
            latest_human_message = human_messages[-1]
            await history_service.save_human_message(
                session_id, 
                latest_human_message.content
            )
        
        # Save AI response
        response = state.get("response")
        if response:
            metadata = {
                "api_called": state.get("should_call_api", False),
                "api_response": state.get("api_response")
            }
            await history_service.save_ai_message(
                session_id, 
                response, 
                metadata
            )
        
        logger.info("Successfully saved interaction to history")
        
    except Exception as e:
        logger.error(f"Error saving to history: {str(e)}")
    
    return state