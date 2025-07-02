from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Set service name for database initialization
os.environ['SERVICE_NAME'] = 'chat'

from app.config import settings
from app.api.routes import router as api_router
from app.graph.graph import build_graph
from app.database.database import get_db_engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variable to store the graph
graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Chat Service...")
    
    # Initialize database connection (no table creation)
    try:
        engine = get_db_engine()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    # Build graph
    global graph
    try:
        graph = build_graph()
        logger.info("Graph built successfully")
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Chat Service...")


# Create FastAPI app
app = FastAPI(
    title="Chat Service",
    version=settings.VERSION,
    description="Chat processing and conversation management service",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Chat Service",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "chat",
        "status": "healthy",
        "version": settings.VERSION,
        "graph_ready": graph is not None
    }


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint for Prometheus."""
    return {
        "service": "chat",
        "status": "running",
        "version": settings.VERSION,
        "graph_ready": graph is not None,
        "uptime": "running"
    }