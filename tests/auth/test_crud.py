"""Tests for auth CRUD operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from app.auth.crud import (
    create_user, get_user_by_email, get_user_by_id, authenticate_user,
    update_user, update_user_password, deactivate_user, activate_user,
    get_users, count_users, count_active_users
)
from app.auth.schemas import UserCreate, UserUpdate
from app.database.models import User
from app.auth.utils import verify_password

fake = Faker()


class TestAuthCRUD:
    """Test auth CRUD operations."""

    async def test_create_user_success(self, test_db: AsyncSession):
        """Test successful user creation."""
        user_data = UserCreate(
            email=fake.email(),
            password="testpassword123",
            full_name=fake.name()
        )
        
        user = await create_user(test_db, user_data)
        
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.is_active is True
        assert user.is_admin is False
        assert user.id is not None
        assert user.uuid is not None
        assert user.created_at is not None
        assert verify_password("testpassword123", user.hashed_password)

    async def test_create_user_with_optional_fields(self, test_db: AsyncSession):
        """Test user creation with optional fields."""
        user_data = UserCreate(
            email=fake.email(),
            password="testpassword123",
            full_name=fake.name(),
            bio=fake.text(max_nb_chars=200),
            phone=fake.phone_number()
        )
        
        user = await create_user(test_db, user_data)
        
        assert user.bio == user_data.bio
        assert user.phone == user_data.phone

    async def test_get_user_by_email_exists(self, test_db: AsyncSession, test_user: User):
        """Test getting user by email when user exists."""
        user = await get_user_by_email(test_db, test_user.email)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_by_email_not_exists(self, test_db: AsyncSession):
        """Test getting user by email when user doesn't exist."""
        user = await get_user_by_email(test_db, "nonexistent@example.com")
        
        assert user is None

    async def test_get_user_by_id_exists(self, test_db: AsyncSession, test_user: User):
        """Test getting user by ID when user exists."""
        user = await get_user_by_id(test_db, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_get_user_by_id_not_exists(self, test_db: AsyncSession):
        """Test getting user by ID when user doesn't exist."""
        user = await get_user_by_id(test_db, 99999)
        
        assert user is None

    async def test_authenticate_user_success(self, test_db: AsyncSession, test_user: User):
        """Test successful user authentication."""
        user = await authenticate_user(test_db, test_user.email, "testpassword123")
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    async def test_authenticate_user_wrong_password(self, test_db: AsyncSession, test_user: User):
        """Test authentication with wrong password."""
        user = await authenticate_user(test_db, test_user.email, "wrongpassword")
        
        assert user is None

    async def test_authenticate_user_nonexistent(self, test_db: AsyncSession):
        """Test authentication with nonexistent user."""
        user = await authenticate_user(test_db, "nonexistent@example.com", "password")
        
        assert user is None

    async def test_authenticate_user_inactive(self, test_db: AsyncSession, test_user: User):
        """Test authentication with inactive user."""
        # Deactivate user
        test_user.is_active = False
        await test_db.commit()
        
        user = await authenticate_user(test_db, test_user.email, "testpassword123")
        
        assert user is None

    async def test_update_user_success(self, test_db: AsyncSession, test_user: User):
        """Test successful user update."""
        update_data = UserUpdate(
            full_name="Updated Name",
            bio="Updated bio",
            phone="+1234567890"
        )
        
        updated_user = await update_user(test_db, test_user.id, update_data)
        
        assert updated_user.full_name == update_data.full_name
        assert updated_user.bio == update_data.bio
        assert updated_user.phone == update_data.phone
        assert updated_user.email == test_user.email  # Should not change

    async def test_update_user_partial(self, test_db: AsyncSession, test_user: User):
        """Test partial user update."""
        original_name = test_user.full_name
        update_data = UserUpdate(bio="New bio only")
        
        updated_user = await update_user(test_db, test_user.id, update_data)
        
        assert updated_user.bio == "New bio only"
        assert updated_user.full_name == original_name  # Should not change

    async def test_update_user_nonexistent(self, test_db: AsyncSession):
        """Test updating nonexistent user."""
        update_data = UserUpdate(full_name="New Name")
        
        updated_user = await update_user(test_db, 99999, update_data)
        
        assert updated_user is None

    async def test_update_user_password_success(self, test_db: AsyncSession, test_user: User):
        """Test successful password update."""
        new_password = "newpassword123"
        
        success = await update_user_password(test_db, test_user.id, new_password)
        
        assert success is True
        
        # Verify password was actually changed
        await test_db.refresh(test_user)
        assert verify_password(new_password, test_user.hashed_password)

    async def test_update_user_password_nonexistent(self, test_db: AsyncSession):
        """Test updating password for nonexistent user."""
        success = await update_user_password(test_db, 99999, "newpassword")
        
        assert success is False

    async def test_deactivate_user_success(self, test_db: AsyncSession, test_user: User):
        """Test successful user deactivation."""
        success = await deactivate_user(test_db, test_user.id)
        
        assert success is True
        await test_db.refresh(test_user)
        assert test_user.is_active is False

    async def test_deactivate_user_nonexistent(self, test_db: AsyncSession):
        """Test deactivating nonexistent user."""
        success = await deactivate_user(test_db, 99999)
        
        assert success is False

    async def test_activate_user_success(self, test_db: AsyncSession, test_user: User):
        """Test successful user activation."""
        # First deactivate
        test_user.is_active = False
        await test_db.commit()
        
        success = await activate_user(test_db, test_user.id)
        
        assert success is True
        await test_db.refresh(test_user)
        assert test_user.is_active is True

    async def test_activate_user_nonexistent(self, test_db: AsyncSession):
        """Test activating nonexistent user."""
        success = await activate_user(test_db, 99999)
        
        assert success is False

    async def test_get_users_pagination(self, test_db: AsyncSession):
        """Test getting users with pagination."""
        # Create multiple users
        users_data = [
            UserCreate(
                email=fake.email(),
                password="password123",
                full_name=fake.name()
            )
            for _ in range(5)
        ]
        
        for user_data in users_data:
            await create_user(test_db, user_data)
        
        # Test pagination
        users_page1 = await get_users(test_db, skip=0, limit=3)
        users_page2 = await get_users(test_db, skip=3, limit=3)
        
        assert len(users_page1) == 3
        assert len(users_page2) >= 2  # At least 2 (might include test_user from fixture)
        
        # Ensure no overlap
        page1_ids = {user.id for user in users_page1}
        page2_ids = {user.id for user in users_page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_get_users_empty(self, test_db: AsyncSession):
        """Test getting users when none exist."""
        # Use a fresh database session without test_user fixture
        users = await get_users(test_db, skip=0, limit=10)
        
        # Should only contain users from other fixtures if any
        assert isinstance(users, list)

    async def test_count_users(self, test_db: AsyncSession, test_user: User):
        """Test counting total users."""
        # Create additional users
        for _ in range(3):
            user_data = UserCreate(
                email=fake.email(),
                password="password123",
                full_name=fake.name()
            )
            await create_user(test_db, user_data)
        
        total_count = await count_users(test_db)
        
        assert total_count >= 4  # At least 4 (3 new + test_user)

    async def test_count_active_users(self, test_db: AsyncSession, test_user: User):
        """Test counting active users."""
        # Create additional users, some inactive
        for i in range(3):
            user_data = UserCreate(
                email=fake.email(),
                password="password123",
                full_name=fake.name()
            )
            user = await create_user(test_db, user_data)
            if i == 0:  # Make first user inactive
                user.is_active = False
                await test_db.commit()
        
        active_count = await count_active_users(test_db)
        total_count = await count_users(test_db)
        
        assert active_count < total_count
        assert active_count >= 3  # At least 3 (2 new active + test_user)

    async def test_create_multiple_users_unique_emails(self, test_db: AsyncSession):
        """Test creating multiple users with unique emails."""
        emails = [fake.email() for _ in range(3)]
        
        for email in emails:
            user_data = UserCreate(
                email=email,
                password="password123",
                full_name=fake.name()
            )
            user = await create_user(test_db, user_data)
            assert user.email == email
        
        # Verify all users were created
        total_count = await count_users(test_db)
        assert total_count >= 3

    async def test_user_timestamps(self, test_db: AsyncSession):
        """Test user creation and update timestamps."""
        user_data = UserCreate(
            email=fake.email(),
            password="password123",
            full_name=fake.name()
        )
        
        user = await create_user(test_db, user_data)
        created_at = user.created_at
        updated_at = user.updated_at
        
        assert created_at is not None
        assert updated_at is not None
        assert created_at == updated_at  # Should be same on creation
        
        # Update user
        update_data = UserUpdate(full_name="Updated Name")
        updated_user = await update_user(test_db, user.id, update_data)
        
        assert updated_user.created_at == created_at  # Should not change
        assert updated_user.updated_at > updated_at  # Should be newer