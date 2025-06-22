import sys
import os
from loguru import logger
from app.config import settings


def setup_logging():
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Configure console logger
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # Configure file logger
    logger.add(
        settings.LOG_FILE,
        rotation="10 MB",
        retention="1 week",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Log startup message
    logger.info(f"Logging initialized at level {settings.LOG_LEVEL}")
    
    return logger