from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.database.models import User, ChatSession, ChatMessage
from app.auth.schemas import UserCreate, UserUpdate
from app.auth.utils import get_password_hash, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_uuid(db: AsyncSession, user_uuid: str) -> Optional[User]:
    """Get user by UUID."""
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination."""
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        avatar_url=user.avatar_url,
        bio=user.bio,
        phone=user.phone
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    # Get the user first
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    if update_data:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await db.commit()
        await db.refresh(user)
    
    return user


async def update_user_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
    """Update user password."""
    hashed_password = get_password_hash(new_password)
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(hashed_password=hashed_password, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def update_last_login(db: AsyncSession, user_id: int) -> None:
    """Update user's last login timestamp."""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(last_login=datetime.utcnow())
    )
    await db.commit()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """Deactivate a user."""
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def activate_user(db: AsyncSession, user_id: int) -> bool:
    """Activate a user."""
    result = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=True, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def get_user_with_sessions(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user with their chat sessions."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.chat_sessions))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def count_users(db: AsyncSession) -> int:
    """Count total number of users."""
    result = await db.execute(select(User.id))
    return len(result.scalars().all())


async def count_active_users(db: AsyncSession) -> int:
    """Count active users."""
    result = await db.execute(select(User.id).where(User.is_active == True))
    return len(result.scalars().all())