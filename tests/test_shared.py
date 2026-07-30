"""Tests for shared utilities."""

import pytest
from hypothesis import given, strategies as st
from src.shared.auth import get_password_hash, verify_password, create_access_token, verify_token


class TestAuth:
    """Test authentication utilities."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    @given(st.text(min_size=1, max_size=100))
    def test_password_hashing_property(self, password: str):
        """Property test: any password should hash and verify correctly."""
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert hashed != password  # Hash should be different from original
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification."""
        data = {"sub": "test@example.com", "role": "buyer"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "buyer"
    
    def test_invalid_token_verification(self):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        decoded = verify_token(invalid_token)
        assert decoded is None