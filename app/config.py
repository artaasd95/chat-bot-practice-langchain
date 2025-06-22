from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    # API Settings
    API_PREFIX: str = "/api"
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(default=["*"])
    
    # LLM Settings
    OPENAI_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gpt-3.5-turbo")
    LLM_TEMPERATURE: float = Field(default=0.7)
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/langgraph_chat.log")
    
    # Webhook Settings
    WEBHOOK_TIMEOUT: int = Field(default=60)  # seconds
    WEBHOOK_RETRY_ATTEMPTS: int = Field(default=3)
    WEBHOOK_RETRY_DELAY: int = Field(default=2)  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()