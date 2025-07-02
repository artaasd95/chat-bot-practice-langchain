from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import logging
import os

from app.config import settings
from app.database.base import Base

logger = logging.getLogger(__name__)

# Global variables for engine and session
engine = None
AsyncSessionLocal = None


def get_db_engine():
    """Get or create database engine."""
    global engine
    if engine is None:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300
        )
    return engine


def get_session_factory():
    """Get or create session factory."""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        engine = get_db_engine()
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return AsyncSessionLocal


async def get_db() -> AsyncSession:
    """Get database session."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and create default admin user (auth service only)."""
    service_name = os.getenv('SERVICE_NAME', 'main')
    
    # Only initialize tables and admin user in auth service
    if service_name != 'auth':
        logger.info(f"Skipping database initialization in {service_name} service")
        return
    
    # Import all models before creating tables
    from app.database.models import User, ChatSession, ChatMessage
    from app.auth.utils import get_password_hash
    
    engine = get_db_engine()
    session_factory = get_session_factory()
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    
    # Create default admin user if not exists
    async with session_factory() as session:
        try:
            # Check if admin user exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == settings.ADMIN_EMAIL)
            )
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                # Create admin user
                hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
                admin_user = User(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hashed_password,
                    full_name="System Administrator",
                    is_active=True,
                    is_admin=True
                )
                session.add(admin_user)
                await session.commit()
                logger.info(f"Default admin user created: {settings.ADMIN_EMAIL}")
            else:
                logger.info("Admin user already exists")
                
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            await session.rollback()
            raise