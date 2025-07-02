"""CRUD operations for chat sessions and messages."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.database.models import ChatSession, ChatMessage, User


# Chat Session CRUD Operations

async def create_chat_session(db: AsyncSession, session_data: Dict[str, Any]) -> ChatSession:
    """Create a new chat session."""
    db_session = ChatSession(**session_data)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session


async def get_chat_session_by_id(db: AsyncSession, session_id: int) -> Optional[ChatSession]:
    """Get chat session by ID."""
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    return result.scalar_one_or_none()


async def get_chat_session_by_uuid(db: AsyncSession, session_uuid: str) -> Optional[ChatSession]:
    """Get chat session by UUID."""
    result = await db.execute(select(ChatSession).where(ChatSession.uuid == session_uuid))
    return result.scalar_one_or_none()


async def get_user_chat_sessions(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatSession]:
    """Get all chat sessions for a user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(desc(ChatSession.updated_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_active_user_sessions(db: AsyncSession, user_id: int) -> List[ChatSession]:
    """Get active chat sessions for a user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id, ChatSession.is_active == True)
        .order_by(desc(ChatSession.updated_at))
    )
    return result.scalars().all()


async def update_chat_session(db: AsyncSession, session_id: int, update_data: Dict[str, Any]) -> Optional[ChatSession]:
    """Update chat session."""
    session = await get_chat_session_by_id(db, session_id)
    if not session:
        return None
    
    if update_data:
        await db.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await db.commit()
        await db.refresh(session)
    
    return session


async def delete_chat_session(db: AsyncSession, session_id: int) -> bool:
    """Delete chat session."""
    result = await db.execute(
        delete(ChatSession).where(ChatSession.id == session_id)
    )
    await db.commit()
    return result.rowcount > 0


async def deactivate_chat_session(db: AsyncSession, session_id: int) -> bool:
    """Deactivate chat session."""
    result = await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def activate_chat_session(db: AsyncSession, session_id: int) -> bool:
    """Activate chat session."""
    result = await db.execute(
        update(ChatSession)
        .where(ChatSession.id == session_id)
        .values(is_active=True, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def archive_old_sessions(db: AsyncSession, user_id: int, days_old: int = 30) -> int:
    """Archive old sessions by deactivating them."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    result = await db.execute(
        update(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.updated_at < cutoff_date,
            ChatSession.is_active == True
        )
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount


# Chat Message CRUD Operations

async def create_chat_message(db: AsyncSession, message_data: Dict[str, Any]) -> ChatMessage:
    """Create a new chat message."""
    db_message = ChatMessage(**message_data)
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message


async def get_chat_message_by_id(db: AsyncSession, message_id: int) -> Optional[ChatMessage]:
    """Get chat message by ID."""
    result = await db.execute(select(ChatMessage).where(ChatMessage.id == message_id))
    return result.scalar_one_or_none()


async def get_chat_message_by_uuid(db: AsyncSession, message_uuid: str) -> Optional[ChatMessage]:
    """Get chat message by UUID."""
    result = await db.execute(select(ChatMessage).where(ChatMessage.uuid == message_uuid))
    return result.scalar_one_or_none()


async def get_session_messages(db: AsyncSession, session_id: int, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
    """Get all messages for a session."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_session_messages_by_type(db: AsyncSession, session_id: int, message_type: str) -> List[ChatMessage]:
    """Get session messages filtered by type."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id, ChatMessage.message_type == message_type)
        .order_by(ChatMessage.created_at)
    )
    return result.scalars().all()


async def update_chat_message(db: AsyncSession, message_id: int, update_data: Dict[str, Any]) -> Optional[ChatMessage]:
    """Update chat message."""
    message = await get_chat_message_by_id(db, message_id)
    if not message:
        return None
    
    if update_data:
        await db.execute(
            update(ChatMessage)
            .where(ChatMessage.id == message_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(message)
    
    return message


async def delete_chat_message(db: AsyncSession, message_id: int) -> bool:
    """Delete chat message."""
    result = await db.execute(
        delete(ChatMessage).where(ChatMessage.id == message_id)
    )
    await db.commit()
    return result.rowcount > 0


# Statistics and Analytics

async def get_user_message_count(db: AsyncSession, user_id: int) -> int:
    """Get total message count for a user."""
    result = await db.execute(
        select(func.count(ChatMessage.id))
        .join(ChatSession)
        .where(ChatSession.user_id == user_id)
    )
    return result.scalar() or 0


async def get_session_message_count(db: AsyncSession, session_id: int) -> int:
    """Get message count for a specific session."""
    result = await db.execute(
        select(func.count(ChatMessage.id))
        .where(ChatMessage.session_id == session_id)
    )
    return result.scalar() or 0


async def get_recent_messages(db: AsyncSession, user_id: int, limit: int = 10) -> List[ChatMessage]:
    """Get recent messages for a user."""
    result = await db.execute(
        select(ChatMessage)
        .join(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    return result.scalars().all()


async def get_session_with_messages(db: AsyncSession, session_id: int) -> Optional[ChatSession]:
    """Get session with all its messages."""
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    return result.scalar_one_or_none()