from pydantic import BaseSettings
from typing import Optional, Dict, Any, List


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat Bot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A chat bot API using LangChain and LangGraph"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"
    
    # Authentication Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Admin Settings
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: Optional[int] = None
    LLM_PROVIDER: str = "openai"  # openai, deepseek, anthropic
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Webhook Settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    
    # LangSmith Settings
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "chatbot-microservices"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    
    # Monitoring Settings
    METRICS_ENABLED: bool = False
    METRICS_PORT: int = 9090
    METRICS_PATH: str = "/metrics"
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_PATH: str = "/health"
    HEALTH_CHECK_INTERVAL: int = 30
    TRACING_ENABLED: bool = False
    TRACING_ENDPOINT: Optional[str] = None
    TRACING_SERVICE_NAME: str = "chat-bot-api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()