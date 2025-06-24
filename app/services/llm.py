from typing import List, Dict, Any
from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from app.config import settings

try:
    from langchain_deepseek import ChatDeepSeek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    logger.warning("langchain-deepseek not installed. DeepSeek support disabled.")


def get_llm() -> BaseLLM:
    """Get the language model instance based on available API keys and configuration.
    
    Returns:
        BaseLLM: The language model instance.
        
    Raises:
        ValueError: If no valid API key is found or provider is not supported.
    """
    logger.info(f"Initializing LLM with model {settings.LLM_MODEL}")
    
    # Determine which provider to use based on API keys and configuration
    provider = _determine_provider()
    
    if provider == "deepseek":
        if not DEEPSEEK_AVAILABLE:
            raise ValueError("DeepSeek provider requested but langchain-deepseek not installed. Run: pip install langchain-deepseek")
        
        logger.info("Using DeepSeek provider")
        llm = ChatDeepSeek(
            model=settings.LLM_MODEL if settings.LLM_MODEL.startswith("deepseek") else "deepseek-chat",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.DEEPSEEK_API_KEY,
        )
    elif provider == "openai":
        logger.info("Using OpenAI provider")
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    return llm


def _determine_provider() -> str:
    """Determine which LLM provider to use based on configuration and available API keys.
    
    Returns:
        str: The provider name ("openai", "deepseek")
        
    Raises:
        ValueError: If no valid API key is found.
    """
    # If provider is explicitly set and API key is available, use it
    if settings.LLM_PROVIDER == "deepseek" and settings.DEEPSEEK_API_KEY:
        return "deepseek"
    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return "openai"
    
    # Auto-detect based on available API keys
    if settings.DEEPSEEK_API_KEY and DEEPSEEK_AVAILABLE:
        logger.info("DeepSeek API key found, using DeepSeek provider")
        return "deepseek"
    elif settings.OPENAI_API_KEY:
        logger.info("OpenAI API key found, using OpenAI provider")
        return "openai"
    
    # Fallback error
    raise ValueError(
        "No valid API key found. Please set either OPENAI_API_KEY or DEEPSEEK_API_KEY in your environment variables."
    )


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