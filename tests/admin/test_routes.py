"""Tests for admin routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from faker import Faker

from app.database.models import User, ChatSession, ChatMessage
from app.auth.schemas import UserCreate

fake = Faker()


class TestAdminRoutes:
    """Test admin routes."""

    async def test_dashboard_stats_admin_access(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test dashboard stats with admin access."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert "recent_users" in data
        assert "total_chat_sessions" in data
        assert "total_messages" in data
        assert "recent_messages" in data
        
        # Check data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["active_users"], int)
        assert isinstance(data["inactive_users"], int)
        assert data["total_users"] >= 0
        assert data["active_users"] >= 0
        assert data["inactive_users"] >= 0

    async def test_dashboard_stats_non_admin_access(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test dashboard stats with non-admin access."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = await async_client.get("/admin/dashboard", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "Not enough permissions" in data["detail"]

    async def test_dashboard_stats_unauthenticated(self, async_client: AsyncClient):
        """Test dashboard stats without authentication."""
        response = await async_client.get("/admin/dashboard")
        
        assert response.status_code == 401

    async def test_get_users_list_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_db: AsyncSession):
        """Test getting users list as admin."""
        # Create additional test users
        for i in range(5):
            from app.auth.crud import create_user
            user_data = UserCreate(
                email=fake.email(),
                password="password123",
                full_name=fake.name()
            )
            await create_user(test_db, user_data)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5  # At least the created users
        
        # Check user data structure
        if data:
            user = data[0]
            assert "id" in user
            assert "email" in user
            assert "full_name" in user
            assert "is_active" in user
            assert "is_admin" in user
            assert "created_at" in user
            assert "hashed_password" not in user  # Should not expose password

    async def test_get_users_list_pagination(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_db: AsyncSession):
        """Test users list pagination."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test with pagination parameters
        response = await async_client.get("/admin/users?skip=0&limit=2", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    async def test_get_user_by_id_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_user: User):
        """Test getting specific user by ID as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get(f"/admin/users/{test_user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "hashed_password" not in data

    async def test_get_user_by_id_not_found(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test getting non-existent user by ID."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/users/99999", headers=headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    async def test_create_user_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test creating user as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "email": fake.email(),
            "password": "newpassword123",
            "full_name": fake.name(),
            "is_admin": False
        }
        
        response = await async_client.post("/admin/users", json=user_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_admin"] == user_data["is_admin"]
        assert "hashed_password" not in data

    async def test_create_admin_user(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test creating admin user."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "email": fake.email(),
            "password": "adminpassword123",
            "full_name": "New Admin",
            "is_admin": True
        }
        
        response = await async_client.post("/admin/users", json=user_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_admin"] is True

    async def test_update_user_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_user: User):
        """Test updating user as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {
            "full_name": "Updated by Admin",
            "bio": "Updated bio",
            "is_active": True
        }
        
        response = await async_client.put(f"/admin/users/{test_user.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]
        assert data["is_active"] == update_data["is_active"]

    async def test_deactivate_user_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_user: User):
        """Test deactivating user as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.post(f"/admin/users/{test_user.id}/deactivate", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "User deactivated successfully" in data["message"]

    async def test_activate_user_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_user: User, test_db: AsyncSession):
        """Test activating user as admin."""
        # First deactivate the user
        test_user.is_active = False
        await test_db.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.post(f"/admin/users/{test_user.id}/activate", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "User activated successfully" in data["message"]

    async def test_delete_user_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_db: AsyncSession):
        """Test deleting user as admin."""
        # Create a user to delete
        from app.auth.crud import create_user
        user_data = UserCreate(
            email=fake.email(),
            password="password123",
            full_name="User to Delete"
        )
        user_to_delete = await create_user(test_db, user_data)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.delete(f"/admin/users/{user_to_delete.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "User deleted successfully" in data["message"]

    async def test_get_chat_sessions_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_chat_session: ChatSession):
        """Test getting chat sessions as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/chat-sessions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            session = data[0]
            assert "id" in session
            assert "user_id" in session
            assert "title" in session
            assert "created_at" in session
            assert "is_active" in session

    async def test_get_chat_session_by_id_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_chat_session: ChatSession):
        """Test getting specific chat session by ID as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get(f"/admin/chat-sessions/{test_chat_session.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_chat_session.id
        assert data["user_id"] == test_chat_session.user_id
        assert data["title"] == test_chat_session.title

    async def test_get_chat_messages_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_chat_messages: list[ChatMessage]):
        """Test getting chat messages as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        session_id = test_chat_messages[0].session_id
        
        response = await async_client.get(f"/admin/chat-sessions/{session_id}/messages", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the test messages
        
        if data:
            message = data[0]
            assert "id" in message
            assert "session_id" in message
            assert "message_type" in message
            assert "content" in message
            assert "created_at" in message

    async def test_delete_chat_session_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_chat_session: ChatSession):
        """Test deleting chat session as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.delete(f"/admin/chat-sessions/{test_chat_session.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "Chat session deleted successfully" in data["message"]

    async def test_get_system_stats_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test getting system statistics as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/system/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for system stats
        assert "database" in data
        assert "memory" in data or "disk" in data or "uptime" in data

    async def test_export_users_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test exporting users data as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/export/users", headers=headers)
        
        assert response.status_code == 200
        # Should return CSV or JSON data
        assert response.headers.get("content-type") in ["text/csv", "application/json"]

    async def test_export_chat_data_admin(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test exporting chat data as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/export/chat-data", headers=headers)
        
        assert response.status_code == 200
        # Should return CSV or JSON data
        assert response.headers.get("content-type") in ["text/csv", "application/json"]

    async def test_admin_search_users(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_user: User):
        """Test searching users as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Search by email
        response = await async_client.get(f"/admin/users/search?q={test_user.email}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should find the test user
        found_user = next((u for u in data if u["email"] == test_user.email), None)
        assert found_user is not None

    async def test_admin_bulk_operations(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_db: AsyncSession):
        """Test bulk operations as admin."""
        # Create multiple users for bulk operations
        user_ids = []
        for _ in range(3):
            from app.auth.crud import create_user
            user_data = UserCreate(
                email=fake.email(),
                password="password123",
                full_name=fake.name()
            )
            user = await create_user(test_db, user_data)
            user_ids.append(user.id)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Bulk deactivate
        bulk_data = {"user_ids": user_ids, "action": "deactivate"}
        response = await async_client.post("/admin/users/bulk", json=bulk_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "processed" in data
        assert data["processed"] == len(user_ids)

    async def test_admin_audit_log(self, async_client: AsyncClient, test_admin_user: User, admin_token: str):
        """Test getting audit log as admin."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/audit-log", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check audit log entry structure if any exist
        if data:
            entry = data[0]
            assert "id" in entry
            assert "action" in entry
            assert "user_id" in entry
            assert "timestamp" in entry

    async def test_non_admin_access_denied(self, async_client: AsyncClient, test_user: User, user_token: str):
        """Test that non-admin users are denied access to admin endpoints."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        admin_endpoints = [
            "/admin/dashboard",
            "/admin/users",
            "/admin/chat-sessions",
            "/admin/system/stats",
            "/admin/export/users",
            "/admin/audit-log"
        ]
        
        for endpoint in admin_endpoints:
            response = await async_client.get(endpoint, headers=headers)
            assert response.status_code == 403
            data = response.json()
            assert "Not enough permissions" in data["detail"]

    async def test_admin_dashboard_with_data(self, async_client: AsyncClient, test_admin_user: User, admin_token: str, test_db: AsyncSession, test_chat_messages: list[ChatMessage]):
        """Test dashboard stats with actual data."""
        # Create additional test data
        for _ in range(3):
            from app.auth.crud import create_user
            user_data = UserCreate(
                email=fake.email(),
                password="password123",
                full_name=fake.name()
            )
            await create_user(test_db, user_data)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await async_client.get("/admin/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have meaningful data now
        assert data["total_users"] >= 3
        assert data["total_messages"] >= 2  # From test_chat_messages fixture
        assert data["total_chat_sessions"] >= 1