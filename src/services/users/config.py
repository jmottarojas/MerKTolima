"""User service configuration."""

from typing import Optional


class UserServiceConfig:
    """User service configuration settings."""
    
    def __init__(self):
        # JWT Configuration
        self.secret_key: str = "your-secret-key-here"
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        
        # Password Configuration
        self.password_min_length: int = 8
        self.password_require_uppercase: bool = True
        self.password_require_lowercase: bool = True
        self.password_require_numbers: bool = True
        
        # Email Configuration
        self.email_verification_required: bool = True
        self.email_verification_expire_hours: int = 24


# Global configuration instance
user_config = UserServiceConfig()