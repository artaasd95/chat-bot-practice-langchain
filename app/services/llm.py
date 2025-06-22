from typing import Dict, Any, List, Optional
from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from app.config import settings


def get_llm() -> BaseLLM:
    """Get the language model instance.
    
    Returns:
        BaseLLM: The language model instance.
    """
    logger.info(f"Initializing LLM with model {settings.LLM_MODEL}")
    
    # Initialize the LLM with settings
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
    )
    
    return llm


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_llm_response(
    llm: BaseLLM,
    messages: List[BaseMessage],
    **kwargs
) -> Dict[str, Any]:
    """Generate a response from the LLM with retry logic.
    
    Args:
        llm: The language model to use.
        messages: The messages to generate a response for.
        **kwargs: Additional arguments to pass to the LLM.
        
    Returns:
        Dict containing the response and any additional metadata.
    """
    logger.info(f"Generating LLM response for {len(messages)} messages")
    
    try:
        # Generate response
        response = await llm.agenerate([messages], **kwargs)
        response_text = response.generations[0][0].text
        
        # Extract any additional metadata
        metadata = {}
        if hasattr(response, "llm_output") and response.llm_output:
            metadata = response.llm_output
        
        logger.info(f"LLM response generated successfully")
        
        return {
            "response": response_text,
            "metadata": metadata,
        }
    except Exception as e:
        logger.error(f"Error generating LLM response: {str(e)}")
        raise