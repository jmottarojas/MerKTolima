"""Notification repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, and_

from ...shared.models import Notification, NotificationType
from ...shared.db_models import NotificationDB, NotificationPreferencesDB


class NotificationRepository(ABC):
    """Abstract notification repository interface."""
    
    @abstractmethod
    async def save_notification(self, notification) -> None:
        """Save notification."""
        pass
    
    @abstractmethod
    async def get_notification_by_id(self, notification_id: str):
        """Get notification by ID."""
        pass
    
    @abstractmethod
    async def get_notifications_by_user(self, user_id: str, limit: int = 50):
        """Get notifications by user ID."""
        pass
    
    @abstractmethod
    async def mark_notification_as_read(self, notification_id: str) -> None:
        """Mark notification as read."""
        pass
    
    @abstractmethod
    async def save_user_preferences(self, user_id: str, preferences) -> None:
        """Save user notification preferences."""
        pass
    
    @abstractmethod
    async def get_user_preferences(self, user_id: str):
        """Get user notification preferences."""
        pass
    
    @abstractmethod
    async def delete_old_notifications(self, days: int) -> int:
        """Delete notifications older than specified days."""
        pass


class SQLAlchemyNotificationRepository(NotificationRepository):
    """SQLAlchemy implementation of notification repository."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session
    
    def _db_to_pydantic(self, db_notification: NotificationDB) -> Notification:
        """Convert SQLAlchemy model to Pydantic model."""
        return Notification(
            id=db_notification.id,
            user_id=db_notification.user_id,
            title=db_notification.title,
            message=db_notification.message,
            notification_type=db_notification.notification_type,
            is_read=db_notification.is_read,
            metadata=db_notification.notification_metadata or {},
            created_at=db_notification.created_at,
            read_at=db_notification.read_at
        )
    
    async def save_notification(self, notification: Notification) -> None:
        """Save notification."""
        db_notification = NotificationDB(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            notification_type=notification.notification_type,
            is_read=notification.is_read,
            notification_metadata=notification.metadata,
            created_at=notification.created_at,
            read_at=notification.read_at
        )
        
        try:
            self.db.add(db_notification)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        db_notification = self.db.query(NotificationDB).filter(NotificationDB.id == notification_id).first()
        if db_notification:
            return self._db_to_pydantic(db_notification)
        return None
    
    async def get_notifications_by_user(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Get notifications by user ID."""
        db_notifications = (
            self.db.query(NotificationDB)
            .filter(NotificationDB.user_id == user_id)
            .order_by(desc(NotificationDB.created_at))
            .limit(limit)
            .all()
        )
        return [self._db_to_pydantic(db_notification) for db_notification in db_notifications]
    
    async def mark_notification_as_read(self, notification_id: str) -> None:
        """Mark notification as read."""
        db_notification = self.db.query(NotificationDB).filter(NotificationDB.id == notification_id).first()
        if db_notification:
            db_notification.is_read = True
            db_notification.read_at = datetime.utcnow()
            
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
    
    async def save_user_preferences(self, user_id: str, preferences: Dict) -> None:
        """Save user notification preferences."""
        # Check if preferences already exist
        existing_prefs = self.db.query(NotificationPreferencesDB).filter(NotificationPreferencesDB.user_id == user_id).first()
        
        if existing_prefs:
            # Update existing preferences
            existing_prefs.preferences = preferences
            existing_prefs.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            db_preferences = NotificationPreferencesDB(
                id=str(uuid.uuid4()),
                user_id=user_id,
                preferences=preferences,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(db_preferences)
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user notification preferences."""
        db_preferences = self.db.query(NotificationPreferencesDB).filter(NotificationPreferencesDB.user_id == user_id).first()
        if db_preferences:
            return db_preferences.preferences
        return None
    
    async def delete_old_notifications(self, days: int) -> int:
        """Delete notifications older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count notifications to be deleted
        count = self.db.query(NotificationDB).filter(NotificationDB.created_at < cutoff_date).count()
        
        # Delete old notifications
        self.db.query(NotificationDB).filter(NotificationDB.created_at < cutoff_date).delete()
        
        try:
            self.db.commit()
            return count
        except Exception:
            self.db.rollback()
            raise


class InMemoryNotificationRepository(NotificationRepository):
    """In-memory implementation of notification repository for testing."""
    
    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
        self.user_notifications: Dict[str, List[str]] = {}
        self.user_preferences: Dict[str, Dict] = {}
    
    async def save_notification(self, notification: Notification) -> None:
        """Save notification."""
        self.notifications[notification.id] = notification
        if notification.user_id not in self.user_notifications:
            self.user_notifications[notification.user_id] = []
        self.user_notifications[notification.user_id].append(notification.id)
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        return self.notifications.get(notification_id)
    
    async def get_notifications_by_user(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Get notifications by user ID."""
        notification_ids = self.user_notifications.get(user_id, [])
        notifications = [self.notifications[nid] for nid in notification_ids if nid in self.notifications]
        # Sort by created_at descending and limit
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        return notifications[:limit]
    
    async def mark_notification_as_read(self, notification_id: str) -> None:
        """Mark notification as read."""
        if notification_id in self.notifications:
            notification = self.notifications[notification_id]
            updated_notification = notification.copy(update={
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            self.notifications[notification_id] = updated_notification
    
    async def save_user_preferences(self, user_id: str, preferences: Dict) -> None:
        """Save user notification preferences."""
        self.user_preferences[user_id] = preferences
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user notification preferences."""
        return self.user_preferences.get(user_id)
    
    async def delete_old_notifications(self, days: int) -> int:
        """Delete notifications older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0
        
        # Find notifications to delete
        to_delete = []
        for notification_id, notification in self.notifications.items():
            if notification.created_at < cutoff_date:
                to_delete.append(notification_id)
        
        # Delete notifications
        for notification_id in to_delete:
            notification = self.notifications[notification_id]
            del self.notifications[notification_id]
            
            # Remove from user notifications list
            if notification.user_id in self.user_notifications:
                if notification_id in self.user_notifications[notification.user_id]:
                    self.user_notifications[notification.user_id].remove(notification_id)
            
            deleted_count += 1
        
        return deleted_count