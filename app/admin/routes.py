from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.database.database import get_db
from app.database.models import User, ChatSession, ChatMessage
from app.auth.schemas import UserResponse, UserCreate, UserUpdate
from app.auth.dependencies import get_current_admin_user
from app.auth.crud import (
    get_users, get_user_by_id, create_user, update_user,
    deactivate_user, activate_user, count_users, count_active_users
)
from sqlalchemy import select, func, and_

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for admin panel."""
    # User statistics
    total_users = await count_users(db)
    active_users = await count_active_users(db)
    inactive_users = total_users - active_users
    
    # Recent users (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_users_query = select(func.count(User.id)).where(
        User.created_at >= seven_days_ago
    )
    result = await db.execute(recent_users_query)
    recent_users = result.scalar() or 0
    
    # Chat statistics
    total_sessions_query = select(func.count(ChatSession.id))
    result = await db.execute(total_sessions_query)
    total_chat_sessions = result.scalar() or 0
    
    total_messages_query = select(func.count(ChatMessage.id))
    result = await db.execute(total_messages_query)
    total_messages = result.scalar() or 0
    
    # Recent chat activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_messages_query = select(func.count(ChatMessage.id)).where(
        ChatMessage.created_at >= yesterday
    )
    result = await db.execute(recent_messages_query)
    recent_messages = result.scalar() or 0
    
    # Active sessions (last 24 hours)
    active_sessions_query = select(func.count(ChatSession.id)).where(
        ChatSession.updated_at >= yesterday
    )
    result = await db.execute(active_sessions_query)
    active_sessions = result.scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": inactive_users,
            "recent_registrations": recent_users
        },
        "chat": {
            "total_sessions": total_chat_sessions,
            "total_messages": total_messages,
            "recent_messages_24h": recent_messages,
            "active_sessions_24h": active_sessions
        },
        "system": {
            "uptime": "System running",
            "version": "1.0.0"
        }
    }


@router.get("/users", response_model=List[UserResponse])
async def get_all_users_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_admin: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with filtering and pagination."""
    query = select(User)
    
    # Apply filters
    conditions = []
    
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            (User.email.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )
    
    if is_active is not None:
        conditions.append(User.is_active == is_active)
    
    if is_admin is not None:
        conditions.append(User.is_admin == is_admin)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user details by ID."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (admin only)."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await create_user(db, user_data)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)."""
    updated_user = await update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle user active status."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_active:
        success = await deactivate_user(db, user_id)
        action = "deactivated"
    else:
        success = await activate_user(db, user_id)
        action = "activated"
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {action.replace('ed', 'e')} user"
        )
    
    return {"message": f"User {action} successfully"}


@router.post("/users/{user_id}/make-admin")
async def make_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Grant admin privileges to user."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )
    
    user_update = UserUpdate(is_admin=True)
    updated_user = await update_user(db, user_id, user_update)
    
    return {"message": "User granted admin privileges successfully"}


@router.post("/users/{user_id}/remove-admin")
async def remove_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove admin privileges from user."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    # Prevent removing admin privileges from the last admin
    admin_count_query = select(func.count(User.id)).where(User.is_admin == True)
    result = await db.execute(admin_count_query)
    admin_count = result.scalar() or 0
    
    if admin_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove admin privileges from the last admin"
        )
    
    user_update = UserUpdate(is_admin=False)
    updated_user = await update_user(db, user_id, user_update)
    
    return {"message": "Admin privileges removed successfully"}


@router.get("/users/{user_id}/chat-history")
async def get_user_chat_history(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's chat history."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get chat sessions for the user
    sessions_query = select(ChatSession).where(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(sessions_query)
    sessions = result.scalars().all()
    
    # Get messages for each session
    chat_history = []
    for session in sessions:
        messages_query = select(ChatMessage).where(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at.asc())
        
        result = await db.execute(messages_query)
        messages = result.scalars().all()
        
        chat_history.append({
            "session_id": session.id,
            "session_title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(messages),
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "role": msg.role,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        })
    
    return {
        "user_id": user_id,
        "user_email": user.email,
        "chat_history": chat_history
    }


@router.get("/system/logs")
async def get_system_logs(
    lines: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system logs (placeholder - implement based on your logging system)."""
    # This is a placeholder implementation
    # In a real system, you would read from your log files or logging system
    return {
        "message": "System logs endpoint - implement based on your logging system",
        "lines_requested": lines,
        "logs": [
            "[INFO] System started successfully",
            "[INFO] Database connection established",
            "[INFO] Authentication system initialized",
            "[INFO] API routes registered"
        ]
    }


@router.post("/system/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle maintenance mode (placeholder)."""
    # This is a placeholder implementation
    # In a real system, you would implement actual maintenance mode logic
    return {
        "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}",
        "maintenance_mode": enabled
    }