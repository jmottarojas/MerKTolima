"""User service implementation."""

from typing import Optional, List, Dict, TYPE_CHECKING
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
from src.shared.auth import get_password_hash, verify_password, create_access_token
from src.shared.service_integration import event_bus, Event, EventType
from src.shared.models import Address, UserPreferences

if TYPE_CHECKING:
    from .repository import UserRepository


class UserRegistrationData(BaseModel):
    """User registration data model."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "buyer"
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['buyer', 'seller']:
            raise ValueError('Role must be either "buyer" or "seller"')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 100:
            raise ValueError('Name cannot be longer than 100 characters')
        return v.strip()


class LoginCredentials(BaseModel):
    """Login credentials model."""
    email: EmailStr
    password: str


class UserProfileUpdates(BaseModel):
    """User profile updates model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional["Address"] = None
    preferences: Optional["UserPreferences"] = None
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Name cannot be empty')
            if len(v.strip()) > 100:
                raise ValueError('Name cannot be longer than 100 characters')
            return v.strip()
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and len(v) > 20:
            raise ValueError('Phone number cannot be longer than 20 characters')
        return v


class User(BaseModel):
    """User model."""
    id: str
    email: str
    role: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AuthToken(BaseModel):
    """Authentication token model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRegistrationError(Exception):
    """Exception raised when user registration fails."""
    pass


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""
    pass


class UserService:
    """User service for managing user operations."""
    
    def __init__(self, repository: Optional["UserRepository"] = None):
        """Initialize user service."""
        if repository is None:
            from .repository import InMemoryUserRepository
            repository = InMemoryUserRepository()
        self._repository = repository
        self._password_hashes: Dict[str, str] = {}  # user_id -> password_hash mapping
    
    async def register_user(self, user_data: UserRegistrationData) -> User:
        """Register a new user.
        
        Args:
            user_data: User registration information
            
        Returns:
            Created user object
            
        Raises:
            UserRegistrationError: If registration fails (e.g., email already exists)
        """
        # Normalize email for consistency
        normalized_email = user_data.email.lower()
        
        # Check if email already exists
        if await self._repository.email_exists(normalized_email):
            raise UserRegistrationError(f"Email {normalized_email} is already registered")
        
        # Hash the password
        password_hash = get_password_hash(user_data.password)
        
        # Create user data with hashed password for repository
        user_creation_data = type('UserCreationData', (), {
            'email': normalized_email,
            'password_hash': password_hash,
            'role': user_data.role,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name
        })()
        
        # Create the user
        user = await self._repository.create_user(user_creation_data)
        
        # Store password hash separately (in real implementation, this would be in the database)
        self._password_hashes[user.id] = password_hash
        
        # Publish user registration event
        await event_bus.publish(Event(
            type=EventType.USER_REGISTERED,
            source_service="user_service",
            data={
                "user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
        ))
        
        return user
    
    async def authenticate_user(self, credentials: LoginCredentials) -> AuthToken:
        """Authenticate user and return token.
        
        Args:
            credentials: User login credentials
            
        Returns:
            Authentication token
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Get user by email
        user = await self._repository.get_user_by_email(credentials.email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Get password hash from repository
        password_hash = None
        
        # For SQLAlchemy repository, get hash from database
        if hasattr(self._repository, 'db'):
            from ...shared.db_models import UserDB
            db_user = self._repository.db.query(UserDB).filter(UserDB.id == user.id).first()
            if db_user:
                password_hash = db_user.password_hash
        else:
            # For in-memory repository, use the stored hash
            password_hash = self._password_hashes.get(user.id)
        
        if not password_hash or not verify_password(credentials.password, password_hash):
            raise AuthenticationError("Invalid email or password")
        
        # Create access token
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role
        }
        
        expires_delta = timedelta(minutes=30)
        access_token = create_access_token(token_data, expires_delta)
        
        return AuthToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30 minutes in seconds
        )
    
    async def update_user_profile(self, user_id: str, updates: UserProfileUpdates) -> User:
        """Update user profile.
        
        Args:
            user_id: ID of the user to update
            updates: Profile updates to apply
            
        Returns:
            Updated user object
            
        Raises:
            ValueError: If user not found
        """
        updated_user = await self._repository.update_user(user_id, updates)
        
        # Publish user profile updated event
        await event_bus.publish(Event(
            type=EventType.USER_PROFILE_UPDATED,
            source_service="user_service",
            data={
                "user_id": user_id,
                "updates": updates.dict(exclude_unset=True)
            }
        ))
        
        return updated_user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return await self._repository.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: Email of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return await self._repository.get_user_by_email(email)