from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database.models import Base
import os

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize the database."""
    # Create tables
    await create_tables()
    
    # Create default admin user if it doesn't exist
    from app.auth.crud import create_user
    from app.auth.schemas import UserCreate
    
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        from sqlalchemy import select
        from app.database.models import User
        
        result = await session.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            # Create admin user
            admin_data = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                full_name="System Administrator",
                is_admin=True
            )
            await create_user(session, admin_data)
            print(f"Admin user created: {settings.ADMIN_EMAIL}")