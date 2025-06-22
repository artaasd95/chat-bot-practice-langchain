from typing import Dict, Any
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from app.config import settings


@retry(
    stop=stop_after_attempt(settings.WEBHOOK_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=settings.WEBHOOK_RETRY_DELAY, max=10)
)
async def send_webhook_response(callback_url: str, data: Dict[str, Any]) -> bool:
    """Send a webhook response to the callback URL with retry logic.
    
    Args:
        callback_url: The URL to send the response to.
        data: The data to send.
        
    Returns:
        True if the response was sent successfully, False otherwise.
    """
    try:
        logger.info(f"Sending webhook response to {callback_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                callback_url,
                json=data,
                timeout=settings.WEBHOOK_TIMEOUT
            ) as response:
                if response.status < 400:
                    response_text = await response.text()
                    logger.info(f"Webhook response sent successfully to {callback_url}")
                    logger.debug(f"Webhook response: {response_text}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send webhook response to {callback_url}: {response.status} - {error_text}")
                    return False
    except aiohttp.ClientError as e:
        logger.error(f"Client error sending webhook response to {callback_url}: {str(e)}")
        raise
    except asyncio.TimeoutError:
        logger.error(f"Timeout sending webhook response to {callback_url}")
        raise
    except Exception as e:
        logger.error(f"Error sending webhook response to {callback_url}: {str(e)}")
        raise