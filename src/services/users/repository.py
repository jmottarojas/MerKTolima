"""User repository interface and implementation."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

if TYPE_CHECKING:
    from .service import User, UserRegistrationData, UserProfileUpdates

from ...shared.db_models import UserDB


class UserRepository(ABC):
    """Abstract user repository interface."""
    
    @abstractmethod
    async def create_user(self, user_data: "UserRegistrationData") -> "User":
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional["User"]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional["User"]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, updates: "UserProfileUpdates") -> "User":
        """Update user profile."""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> None:
        """Delete user."""
        pass
    
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        pass


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session
    
    def _db_to_pydantic(self, db_user: UserDB) -> "User":
        """Convert SQLAlchemy model to Pydantic model."""
        from .service import User
        
        return User(
            id=db_user.id,
            email=db_user.email,
            role=db_user.role,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            phone=db_user.phone,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def create_user(self, user_data: "UserRegistrationData") -> "User":
        """Create a new user."""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Normalize email to lowercase for consistency
        normalized_email = user_data.email.lower()
        
        # Create default preferences
        from ...shared.models import UserPreferences
        default_preferences = UserPreferences()
        
        db_user = UserDB(
            id=user_id,
            email=normalized_email,
            password_hash=user_data.password_hash,
            role=user_data.role,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=None,
            address=None,
            preferences=default_preferences.dict(),
            is_active=True,
            email_verified=False,
            created_at=now,
            updated_at=now
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return self._db_to_pydantic(db_user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {normalized_email} already exists")
    
    async def get_user_by_id(self, user_id: str) -> Optional["User"]:
        """Get user by ID."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            return self._db_to_pydantic(db_user)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional["User"]:
        """Get user by email."""
        db_user = self.db.query(UserDB).filter(UserDB.email == email.lower()).first()
        if db_user:
            return self._db_to_pydantic(db_user)
        return None
    
    async def update_user(self, user_id: str, updates: "UserProfileUpdates") -> "User":
        """Update user profile."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update fields if provided
        if updates.first_name is not None:
            db_user.first_name = updates.first_name
        if updates.last_name is not None:
            db_user.last_name = updates.last_name
        if updates.phone is not None:
            db_user.phone = updates.phone
        if updates.address is not None:
            db_user.address = updates.address.dict() if updates.address else None
        if updates.preferences is not None:
            db_user.preferences = updates.preferences.dict()
        
        db_user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return self._db_to_pydantic(db_user)
        except Exception:
            self.db.rollback()
            raise
    
    async def delete_user(self, user_id: str) -> None:
        """Delete user."""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        count = self.db.query(UserDB).filter(UserDB.email == email.lower()).count()
        return count > 0


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of user repository for testing and development."""
    
    def __init__(self):
        """Initialize the in-memory repository."""
        self._users: Dict[str, "User"] = {}
        self._email_index: Dict[str, str] = {}  # email -> user_id mapping
    
    async def create_user(self, user_data: "UserRegistrationData") -> "User":
        """Create a new user."""
        from .service import User
        from ...shared.models import UserProfile, UserPreferences
        
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Normalize email to lowercase for consistency
        normalized_email = user_data.email.lower()
        
        # Check if email already exists
        if normalized_email in self._email_index:
            raise ValueError(f"User with email {normalized_email} already exists")
        
        # Create default profile
        profile = UserProfile(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=None,
            address=None,
            preferences=UserPreferences()
        )
        
        user = User(
            id=user_id,
            email=normalized_email,
            role=user_data.role,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=None,
            created_at=now,
            updated_at=now
        )
        
        self._users[user_id] = user
        self._email_index[normalized_email] = user_id
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional["User"]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional["User"]:
        """Get user by email."""
        user_id = self._email_index.get(email.lower())
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def update_user(self, user_id: str, updates: "UserProfileUpdates") -> "User":
        """Update user profile."""
        user = self._users.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Create updated user with new fields
        update_data = {}
        if updates.first_name is not None:
            update_data['first_name'] = updates.first_name
        if updates.last_name is not None:
            update_data['last_name'] = updates.last_name
        if updates.phone is not None:
            update_data['phone'] = updates.phone
        
        # Update timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        updated_user = user.copy(update=update_data)
        
        self._users[user_id] = updated_user
        return updated_user
    
    async def delete_user(self, user_id: str) -> None:
        """Delete user."""
        user = self._users.get(user_id)
        if user:
            del self._users[user_id]
            del self._email_index[user.email.lower()]
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return email.lower() in self._email_index