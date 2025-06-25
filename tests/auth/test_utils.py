"""Tests for auth utilities."""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from unittest.mock import patch

from app.auth.utils import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token, decode_token
)
from app.config import settings


class TestAuthUtils:
    """Test auth utility functions."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        
        # Hash password
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("wrongpassword", hashed) is False

    def test_password_hashing_different_results(self):
        """Test that same password produces different hashes."""
        password = "testpassword123"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        data = {"sub": "test@example.com"}
        
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload
        
        # Check expiry is approximately correct (within 1 minute)
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        actual_exp = datetime.fromtimestamp(payload["exp"])
        assert abs((expected_exp - actual_exp).total_seconds()) < 60

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=2)
        
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check expiry is approximately 2 hours from now
        expected_exp = datetime.utcnow() + expires_delta
        actual_exp = datetime.fromtimestamp(payload["exp"])
        assert abs((expected_exp - actual_exp).total_seconds()) < 60

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        data = {"sub": "test@example.com"}
        
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "refresh"
        assert "exp" in payload
        
        # Check expiry is approximately correct for refresh token
        expected_exp = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        actual_exp = datetime.fromtimestamp(payload["exp"])
        assert abs((expected_exp - actual_exp).total_seconds()) < 3600  # Within 1 hour

    def test_verify_token_valid_access_token(self):
        """Test verifying valid access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"

    def test_verify_token_valid_refresh_token(self):
        """Test verifying valid refresh token."""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        payload = verify_token(token, token_type="refresh")
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["type"] == "refresh"

    def test_verify_token_invalid_token(self):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        
        assert payload is None

    def test_verify_token_expired_token(self):
        """Test verifying expired token."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        
        assert payload is None

    def test_verify_token_wrong_type(self):
        """Test verifying token with wrong type."""
        data = {"sub": "test@example.com"}
        access_token = create_access_token(data)
        
        # Try to verify access token as refresh token
        payload = verify_token(access_token, token_type="refresh")
        
        assert payload is None

    def test_decode_token_valid(self):
        """Test decoding valid token."""
        data = {"sub": "test@example.com", "custom": "value"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["custom"] == "value"
        assert "exp" in payload

    def test_decode_token_invalid(self):
        """Test decoding invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = decode_token(invalid_token)
        
        assert payload is None

    def test_decode_token_malformed(self):
        """Test decoding malformed token."""
        malformed_token = "not.a.jwt"
        
        payload = decode_token(malformed_token)
        
        assert payload is None

    def test_token_with_additional_claims(self):
        """Test creating and verifying token with additional claims."""
        data = {
            "sub": "test@example.com",
            "user_id": 123,
            "is_admin": True,
            "permissions": ["read", "write"]
        }
        
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 123
        assert payload["is_admin"] is True
        assert payload["permissions"] == ["read", "write"]

    def test_token_security_different_secret(self):
        """Test that token created with different secret fails verification."""
        data = {"sub": "test@example.com"}
        
        # Create token with current secret
        token = create_access_token(data)
        
        # Try to decode with different secret
        with patch.object(settings, 'SECRET_KEY', 'different-secret'):
            payload = verify_token(token)
            assert payload is None

    def test_token_security_different_algorithm(self):
        """Test that token verification fails with different algorithm."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Try to decode with different algorithm
        with pytest.raises(Exception):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])

    def test_empty_password_hashing(self):
        """Test hashing empty password."""
        empty_password = ""
        
        hashed = get_password_hash(empty_password)
        
        assert hashed != empty_password
        assert verify_password(empty_password, hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_unicode_password_hashing(self):
        """Test hashing password with unicode characters."""
        unicode_password = "пароль123🔒"
        
        hashed = get_password_hash(unicode_password)
        
        assert verify_password(unicode_password, hashed) is True
        assert verify_password("password123", hashed) is False

    def test_very_long_password_hashing(self):
        """Test hashing very long password."""
        long_password = "a" * 1000
        
        hashed = get_password_hash(long_password)
        
        assert verify_password(long_password, hashed) is True
        assert verify_password("a" * 999, hashed) is False

    def test_token_payload_types(self):
        """Test token creation with various payload types."""
        data = {
            "sub": "test@example.com",
            "string": "value",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload["string"] == "value"
        assert payload["integer"] == 42
        assert payload["float"] == 3.14
        assert payload["boolean"] is True
        assert payload["list"] == [1, 2, 3]
        assert payload["dict"] == {"nested": "value"}