from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.routes import router as api_router
from app.auth.routes import router as auth_router
from app.admin.routes import router as admin_router
from app.core.graph import build_graph
from app.database.database import init_db
from app.utils.monitoring import setup_monitoring

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
    logger.info("Starting up the application...")
    
    # Initialize monitoring
    try:
        setup_monitoring()
        logger.info("Monitoring system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")
        logger.warning("Continuing without monitoring...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
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
    logger.info("Shutting down the application...")
    # Add any cleanup code here if needed


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
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
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Chat Bot API",
        "version": settings.VERSION,
        "docs": "/docs",
        "authentication": "Required for chat endpoints"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )