"""Pytest configuration and shared fixtures."""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock

from app.database.database import get_db, Base
from app.database.models import User, ChatSession, ChatMessage
from app.config import settings
from app.main import app
from app.auth.utils import create_access_token, get_password_hash


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def override_get_db(test_db: AsyncSession):
    """Override the get_db dependency."""
    async def _override_get_db():
        yield test_db
    return _override_get_db


@pytest.fixture
def client(override_get_db) -> Generator[TestClient, None, None]:
    """Create a test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    from app.auth.crud import create_user
    from app.auth.schemas import UserCreate
    
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    user = await create_user(test_db, user_data)
    return user


@pytest.fixture
async def test_admin_user(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    from app.auth.crud import create_user
    from app.auth.schemas import UserCreate
    
    user_data = UserCreate(
        email="admin@example.com",
        password="adminpassword123",
        full_name="Admin User"
    )
    user = await create_user(test_db, user_data)
    user.is_admin = True
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    """Create an access token for test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    """Create an access token for admin user."""
    return create_access_token(data={"sub": test_admin_user.email})


@pytest.fixture
async def test_chat_session(test_db: AsyncSession, test_user: User) -> ChatSession:
    """Create a test chat session."""
    session = ChatSession(
        user_id=test_user.id,
        title="Test Chat Session"
    )
    test_db.add(session)
    await test_db.commit()
    await test_db.refresh(session)
    return session


@pytest.fixture
async def test_chat_messages(test_db: AsyncSession, test_chat_session: ChatSession) -> list[ChatMessage]:
    """Create test chat messages."""
    messages = [
        ChatMessage(
            session_id=test_chat_session.id,
            message_type="user",
            content="Hello, how are you?"
        ),
        ChatMessage(
            session_id=test_chat_session.id,
            message_type="assistant",
            content="I'm doing well, thank you! How can I help you today?"
        )
    ]
    
    for message in messages:
        test_db.add(message)
    
    await test_db.commit()
    
    for message in messages:
        await test_db.refresh(message)
    
    return messages


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = AsyncMock()
    mock.ainvoke.return_value = MagicMock(
        content="This is a mocked response from the LLM."
    )
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock = AsyncMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="This is a mocked OpenAI response."
                )
            )
        ]
    )
    return mock


@pytest.fixture
def mock_deepseek_client():
    """Mock DeepSeek client for testing."""
    mock = AsyncMock()
    mock.ainvoke.return_value = MagicMock(
        content="This is a mocked DeepSeek response."
    )
    return mock