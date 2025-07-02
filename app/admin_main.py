from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Set service name for database initialization
os.environ['SERVICE_NAME'] = 'admin'

from app.config import settings
from app.admin.routes import router as admin_router
from app.database.database import get_db_engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Admin Service...")
    
    # Initialize database connection (no table creation)
    try:
        engine = get_db_engine()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Admin Service...")


# Create FastAPI app
app = FastAPI(
    title="Admin Service",
    version=settings.VERSION,
    description="Administrative panel and user management service",
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

# Include admin routes
app.include_router(admin_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Admin Service",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "admin",
        "status": "healthy",
        "version": settings.VERSION
    }


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint for Prometheus."""
    return {
        "service": "admin",
        "status": "running",
        "version": settings.VERSION,
        "uptime": "running"
    }