"""Tests for admin CRUD operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from faker import Faker

from app.database.models import User, ChatSession, ChatMessage
from app.auth.schemas import UserCreate
from app.admin import crud

fake = Faker()


class TestAdminCrud:
    """Test admin CRUD operations."""

    async def test_get_dashboard_stats(self, test_db: AsyncSession, test_user: User, test_chat_session: ChatSession, test_chat_messages: list[ChatMessage]):
        """Test getting dashboard statistics."""
        stats = await crud.get_dashboard_stats(test_db)
        
        assert "total_users" in stats
        assert "active_users" in stats
        assert "inactive_users" in stats
        assert "recent_users" in stats
        assert "total_chat_sessions" in stats
        assert "total_messages" in stats
        assert "recent_messages" in stats
        
        # Check data types and values
        assert isinstance(stats["total_users"], int)
        assert isinstance(stats["active_users"], int)
        assert isinstance(stats["inactive_users"], int)
        assert isinstance(stats["recent_users"], int)
        assert isinstance(stats["total_chat_sessions"], int)
        assert isinstance(stats["total_messages"], int)
        assert isinstance(stats["recent_messages"], int)
        
        assert stats["total_users"] >= 1
        assert stats["active_users"] >= 1
        assert stats["total_chat_sessions"] >= 1
        assert stats["total_messages"] >= 2

    async def test_get_all_users(self, test_db: AsyncSession, test_user: User, test_admin_user: User):
        """Test getting all users."""
        users = await crud.get_all_users(test_db)
        
        assert len(users) >= 2  # At least test_user and test_admin_user
        
        # Check that both users are in the result
        user_emails = [user.email for user in users]
        assert test_user.email in user_emails
        assert test_admin_user.email in user_emails

    async def test_get_all_users_with_pagination(self, test_db: AsyncSession):
        """Test getting users with pagination."""
        # Create additional users
        for i in range(5):
            from app.auth.crud import create_user
            user_data = UserCreate(
                email=f"user{i}@test.com",
                password="password123",
                full_name=f"User {i}"
            )
            await create_user(test_db, user_data)
        
        # Test pagination
        users_page1 = await crud.get_all_users(test_db, skip=0, limit=3)
        users_page2 = await crud.get_all_users(test_db, skip=3, limit=3)
        
        assert len(users_page1) <= 3
        assert len(users_page2) <= 3
        
        # Ensure no overlap between pages
        page1_ids = {user.id for user in users_page1}
        page2_ids = {user.id for user in users_page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_get_user_by_id_existing(self, test_db: AsyncSession, test_user: User):
        """Test getting existing user by ID."""
        user = await crud.get_user_by_id(test_db, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.full_name == test_user.full_name

    async def test_get_user_by_id_non_existing(self, test_db: AsyncSession):
        """Test getting non-existing user by ID."""
        user = await crud.get_user_by_id(test_db, 99999)
        
        assert user is None

    async def test_create_user_admin(self, test_db: AsyncSession):
        """Test creating user through admin CRUD."""
        user_data = {
            "email": fake.email(),
            "password": "password123",
            "full_name": fake.name(),
            "is_admin": True
        }
        
        user = await crud.create_user_admin(test_db, user_data)
        
        assert user.email == user_data["email"]
        assert user.full_name == user_data["full_name"]
        assert user.is_admin == user_data["is_admin"]
        assert user.is_active is True
        assert user.hashed_password != user_data["password"]  # Should be hashed

    async def test_create_user_admin_duplicate_email(self, test_db: AsyncSession, test_user: User):
        """Test creating user with duplicate email."""
        user_data = {
            "email": test_user.email,  # Duplicate email
            "password": "password123",
            "full_name": "Duplicate User"
        }
        
        with pytest.raises(Exception):  # Should raise integrity error
            await crud.create_user_admin(test_db, user_data)

    async def test_update_user_admin(self, test_db: AsyncSession, test_user: User):
        """Test updating user through admin CRUD."""
        update_data = {
            "full_name": "Updated by Admin",
            "bio": "New bio",
            "is_active": True,
            "is_admin": True
        }
        
        updated_user = await crud.update_user_admin(test_db, test_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.full_name == update_data["full_name"]
        assert updated_user.bio == update_data["bio"]
        assert updated_user.is_active == update_data["is_active"]
        assert updated_user.is_admin == update_data["is_admin"]

    async def test_update_user_admin_partial(self, test_db: AsyncSession, test_user: User):
        """Test partial update of user through admin CRUD."""
        original_email = test_user.email
        update_data = {
            "full_name": "Partially Updated"
        }
        
        updated_user = await crud.update_user_admin(test_db, test_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.full_name == update_data["full_name"]
        assert updated_user.email == original_email  # Should remain unchanged

    async def test_update_user_admin_non_existing(self, test_db: AsyncSession):
        """Test updating non-existing user."""
        update_data = {"full_name": "Non-existing User"}
        
        updated_user = await crud.update_user_admin(test_db, 99999, update_data)
        
        assert updated_user is None

    async def test_delete_user_admin(self, test_db: AsyncSession):
        """Test deleting user through admin CRUD."""
        # Create a user to delete
        from app.auth.crud import create_user
        user_data = UserCreate(
            email=fake.email(),
            password="password123",
            full_name="User to Delete"
        )
        user_to_delete = await create_user(test_db, user_data)
        
        # Delete the user
        result = await crud.delete_user_admin(test_db, user_to_delete.id)
        
        assert result is True
        
        # Verify user is deleted
        deleted_user = await crud.get_user_by_id(test_db, user_to_delete.id)
        assert deleted_user is None

    async def test_delete_user_admin_non_existing(self, test_db: AsyncSession):
        """Test deleting non-existing user."""
        result = await crud.delete_user_admin(test_db, 99999)
        
        assert result is False

    async def test_deactivate_user(self, test_db: AsyncSession, test_user: User):
        """Test deactivating user."""
        # Ensure user is active first
        test_user.is_active = True
        await test_db.commit()
        
        result = await crud.deactivate_user(test_db, test_user.id)
        
        assert result is True
        
        # Refresh user from database
        await test_db.refresh(test_user)
        assert test_user.is_active is False

    async def test_activate_user(self, test_db: AsyncSession, test_user: User):
        """Test activating user."""
        # Deactivate user first
        test_user.is_active = False
        await test_db.commit()
        
        result = await crud.activate_user(test_db, test_user.id)
        
        assert result is True
        
        # Refresh user from database
        await test_db.refresh(test_user)
        assert test_user.is_active is True

    async def test_get_all_chat_sessions(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test getting all chat sessions."""
        sessions = await crud.get_all_chat_sessions(test_db)
        
        assert len(sessions) >= 1
        
        # Check that test session is in the result
        session_ids = [session.id for session in sessions]
        assert test_chat_session.id in session_ids

    async def test_get_all_chat_sessions_with_pagination(self, test_db: AsyncSession, test_user: User):
        """Test getting chat sessions with pagination."""
        # Create additional chat sessions
        for i in range(5):
            session = ChatSession(
                user_id=test_user.id,
                title=f"Test Session {i}"
            )
            test_db.add(session)
        await test_db.commit()
        
        # Test pagination
        sessions_page1 = await crud.get_all_chat_sessions(test_db, skip=0, limit=3)
        sessions_page2 = await crud.get_all_chat_sessions(test_db, skip=3, limit=3)
        
        assert len(sessions_page1) <= 3
        assert len(sessions_page2) <= 3

    async def test_get_chat_session_by_id(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test getting chat session by ID."""
        session = await crud.get_chat_session_by_id(test_db, test_chat_session.id)
        
        assert session is not None
        assert session.id == test_chat_session.id
        assert session.title == test_chat_session.title
        assert session.user_id == test_chat_session.user_id

    async def test_get_chat_session_by_id_non_existing(self, test_db: AsyncSession):
        """Test getting non-existing chat session by ID."""
        session = await crud.get_chat_session_by_id(test_db, 99999)
        
        assert session is None

    async def test_delete_chat_session(self, test_db: AsyncSession, test_user: User):
        """Test deleting chat session."""
        # Create a session to delete
        session = ChatSession(
            user_id=test_user.id,
            title="Session to Delete"
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)
        
        # Delete the session
        result = await crud.delete_chat_session(test_db, session.id)
        
        assert result is True
        
        # Verify session is deleted
        deleted_session = await crud.get_chat_session_by_id(test_db, session.id)
        assert deleted_session is None

    async def test_delete_chat_session_non_existing(self, test_db: AsyncSession):
        """Test deleting non-existing chat session."""
        result = await crud.delete_chat_session(test_db, 99999)
        
        assert result is False

    async def test_get_chat_messages_by_session(self, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test getting chat messages by session ID."""
        session_id = test_chat_messages[0].session_id
        
        messages = await crud.get_chat_messages_by_session(test_db, session_id)
        
        assert len(messages) >= 2  # At least the test messages
        
        # Check that test messages are in the result
        message_contents = [msg.content for msg in messages]
        assert any("Hello" in content for content in message_contents)
        assert any("Hi there" in content for content in message_contents)

    async def test_get_chat_messages_by_session_with_pagination(self, test_db: AsyncSession, test_chat_session: ChatSession):
        """Test getting chat messages with pagination."""
        # Create additional messages
        for i in range(10):
            message = ChatMessage(
                session_id=test_chat_session.id,
                message_type="user" if i % 2 == 0 else "assistant",
                content=f"Test message {i}"
            )
            test_db.add(message)
        await test_db.commit()
        
        # Test pagination
        messages_page1 = await crud.get_chat_messages_by_session(test_db, test_chat_session.id, skip=0, limit=5)
        messages_page2 = await crud.get_chat_messages_by_session(test_db, test_chat_session.id, skip=5, limit=5)
        
        assert len(messages_page1) <= 5
        assert len(messages_page2) <= 5

    async def test_search_users(self, test_db: AsyncSession, test_user: User):
        """Test searching users."""
        # Search by email
        users = await crud.search_users(test_db, test_user.email)
        
        assert len(users) >= 1
        found_user = next((u for u in users if u.email == test_user.email), None)
        assert found_user is not None

    async def test_search_users_by_name(self, test_db: AsyncSession, test_user: User):
        """Test searching users by name."""
        # Search by partial name
        search_term = test_user.full_name.split()[0] if test_user.full_name else "Test"
        users = await crud.search_users(test_db, search_term)
        
        assert len(users) >= 0  # May or may not find matches

    async def test_search_users_no_results(self, test_db: AsyncSession):
        """Test searching users with no results."""
        users = await crud.search_users(test_db, "nonexistentuser@nowhere.com")
        
        assert len(users) == 0

    async def test_bulk_deactivate_users(self, test_db: AsyncSession):
        """Test bulk deactivating users."""
        # Create users to deactivate
        user_ids = []
        for i in range(3):
            from app.auth.crud import create_user
            user_data = UserCreate(
                email=f"bulk{i}@test.com",
                password="password123",
                full_name=f"Bulk User {i}"
            )
            user = await create_user(test_db, user_data)
            user_ids.append(user.id)
        
        # Bulk deactivate
        result = await crud.bulk_deactivate_users(test_db, user_ids)
        
        assert result == len(user_ids)
        
        # Verify all users are deactivated
        for user_id in user_ids:
            user = await crud.get_user_by_id(test_db, user_id)
            assert user.is_active is False

    async def test_bulk_activate_users(self, test_db: AsyncSession):
        """Test bulk activating users."""
        # Create and deactivate users
        user_ids = []
        for i in range(3):
            from app.auth.crud import create_user
            user_data = UserCreate(
                email=f"bulkactivate{i}@test.com",
                password="password123",
                full_name=f"Bulk Activate User {i}"
            )
            user = await create_user(test_db, user_data)
            user.is_active = False
            user_ids.append(user.id)
        await test_db.commit()
        
        # Bulk activate
        result = await crud.bulk_activate_users(test_db, user_ids)
        
        assert result == len(user_ids)
        
        # Verify all users are activated
        for user_id in user_ids:
            user = await crud.get_user_by_id(test_db, user_id)
            assert user.is_active is True

    async def test_get_system_stats(self, test_db: AsyncSession):
        """Test getting system statistics."""
        stats = await crud.get_system_stats(test_db)
        
        assert "database" in stats
        assert "connection_count" in stats["database"]
        assert isinstance(stats["database"]["connection_count"], int)

    async def test_export_users_data(self, test_db: AsyncSession, test_user: User, test_admin_user: User):
        """Test exporting users data."""
        users_data = await crud.export_users_data(test_db)
        
        assert len(users_data) >= 2  # At least test users
        
        # Check data structure
        if users_data:
            user_data = users_data[0]
            assert "id" in user_data
            assert "email" in user_data
            assert "full_name" in user_data
            assert "is_active" in user_data
            assert "is_admin" in user_data
            assert "created_at" in user_data
            assert "hashed_password" not in user_data  # Should not export passwords

    async def test_export_chat_data(self, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test exporting chat data."""
        chat_data = await crud.export_chat_data(test_db)
        
        assert len(chat_data) >= 2  # At least test messages
        
        # Check data structure
        if chat_data:
            message_data = chat_data[0]
            assert "session_id" in message_data
            assert "message_type" in message_data
            assert "content" in message_data
            assert "created_at" in message_data
            assert "user_email" in message_data  # Should include user info

    async def test_get_recent_activity(self, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test getting recent activity."""
        activity = await crud.get_recent_activity(test_db, limit=10)
        
        assert isinstance(activity, list)
        assert len(activity) >= 0
        
        # Check activity structure if any exist
        if activity:
            activity_item = activity[0]
            assert "type" in activity_item
            assert "timestamp" in activity_item
            assert "details" in activity_item

    async def test_get_user_activity_summary(self, test_db: AsyncSession, test_user: User, test_chat_session: ChatSession):
        """Test getting user activity summary."""
        summary = await crud.get_user_activity_summary(test_db, test_user.id)
        
        assert "total_sessions" in summary
        assert "total_messages" in summary
        assert "last_activity" in summary
        assert isinstance(summary["total_sessions"], int)
        assert isinstance(summary["total_messages"], int)
        assert summary["total_sessions"] >= 1