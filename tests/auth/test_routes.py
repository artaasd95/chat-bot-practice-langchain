"""Tests for auth routes."""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from app.database.models import User
from app.auth.schemas import UserCreate, UserUpdate
from app.auth.utils import verify_password


class TestAuthRoutes:
    """Test auth routes."""

    async def test_register_success(self, async_client: AsyncClient, test_db: AsyncSession):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, async_client: AsyncClient, test_user: User):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,
            "password": "newpassword123",
            "full_name": "Duplicate User"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422

    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password."""
        user_data = {
            "email": "test@example.com",
            "password": "123",
            "full_name": "Test User"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422

    async def test_login_success(self, async_client: AsyncClient, test_user: User):
        """Test successful login."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = await async_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, async_client: AsyncClient, test_user: User):
        """Test login with invalid credentials."""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await async_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401

    async def test_login_inactive_user(self, async_client: AsyncClient, test_user: User, test_db: AsyncSession):
        """Test login with inactive user."""
        # Deactivate user
        test_user.is_active = False
        await test_db.commit()
        
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = await async_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Inactive user" in response.json()["detail"]

    async def test_refresh_token_success(self, async_client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # First login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await async_client.post("/auth/login", data=login_data)
        tokens = login_response.json()
        
        # Use refresh token
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        
        response = await async_client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """Test refresh with invalid token."""
        refresh_data = {
            "refresh_token": "invalid_token"
        }
        
        response = await async_client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401

    async def test_get_current_user(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test getting current user info."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "hashed_password" not in data

    async def test_get_current_user_unauthorized(self, async_client: AsyncClient):
        """Test getting current user without token."""
        response = await async_client.get("/auth/me")
        
        assert response.status_code == 401

    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = await async_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401

    async def test_update_profile_success(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test successful profile update."""
        headers = {"Authorization": f"Bearer {user_token}"}
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
            "phone": "+1234567890"
        }
        
        response = await async_client.put("/auth/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]
        assert data["phone"] == update_data["phone"]

    async def test_change_password_success(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test successful password change."""
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        
        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password updated successfully"

    async def test_change_password_wrong_current(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test password change with wrong current password."""
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = await async_client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 400
        assert "Incorrect current password" in response.json()["detail"]

    async def test_logout_success(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test successful logout."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.post("/auth/logout", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    async def test_password_reset_request(self, async_client: AsyncClient, test_user: User):
        """Test password reset request."""
        reset_data = {
            "email": test_user.email
        }
        
        with patch('app.auth.routes.send_password_reset_email') as mock_send:
            response = await async_client.post("/auth/password-reset", json=reset_data)
            
            assert response.status_code == 200
            assert "Password reset email sent" in response.json()["message"]
            mock_send.assert_called_once()

    async def test_password_reset_nonexistent_email(self, async_client: AsyncClient):
        """Test password reset with nonexistent email."""
        reset_data = {
            "email": "nonexistent@example.com"
        }
        
        response = await async_client.post("/auth/password-reset", json=reset_data)
        
        # Should still return 200 for security reasons
        assert response.status_code == 200
        assert "Password reset email sent" in response.json()["message"]