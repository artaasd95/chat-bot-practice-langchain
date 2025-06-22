import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.api.routes import router as api_router
from app.config import settings
from app.graph.builder import build_graph
from app.services.llm import get_llm
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    # Setup
    setup_logging()
    logger.info("Starting LangGraph Chat API")
    
    # Initialize the LLM
    llm = get_llm()
    
    # Build the graph
    app.state.graph = await build_graph(llm)
    
    logger.info("LangGraph Chat API started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down LangGraph Chat API")


app = FastAPI(
    title="LangGraph Chat API",
    description="A scalable chat system built with LangGraph and FastAPI",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to LangGraph Chat API",
        "docs": "/docs",
        "version": app.version,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )