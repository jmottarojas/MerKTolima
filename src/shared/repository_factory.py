"""Repository factory for managing database connections and repository instances."""

from typing import Optional
from sqlalchemy.orm import Session
from contextlib import contextmanager

from .database import get_db_session
from ..services.users.repository import UserRepository, SQLAlchemyUserRepository, InMemoryUserRepository
from ..services.products.repository import ProductRepository, SQLAlchemyProductRepository, InMemoryProductRepository
from ..services.orders.repository import OrderRepository, SQLAlchemyOrderRepository, InMemoryOrderRepository
from ..services.payments.repository import PaymentRepository, SQLAlchemyPaymentRepository, InMemoryPaymentRepository
from ..services.notifications.repository import NotificationRepository, SQLAlchemyNotificationRepository, InMemoryNotificationRepository


class RepositoryFactory:
    """Factory for creating repository instances with proper database sessions."""
    
    def __init__(self, use_in_memory: bool = False):
        """Initialize repository factory.
        
        Args:
            use_in_memory: If True, use in-memory repositories for testing
        """
        self.use_in_memory = use_in_memory
        self._db_session: Optional[Session] = None
    
    @contextmanager
    def get_session(self):
        """Get a database session context manager."""
        if self.use_in_memory:
            yield None  # In-memory repositories don't need sessions
        else:
            session = get_db_session()
            try:
                yield session
            finally:
                session.close()
    
    def create_user_repository(self, db_session: Optional[Session] = None) -> UserRepository:
        """Create a user repository instance."""
        if self.use_in_memory:
            return InMemoryUserRepository()
        else:
            if db_session is None:
                raise ValueError("Database session required for SQLAlchemy repositories")
            return SQLAlchemyUserRepository(db_session)
    
    def create_product_repository(self, db_session: Optional[Session] = None) -> ProductRepository:
        """Create a product repository instance."""
        if self.use_in_memory:
            return InMemoryProductRepository()
        else:
            if db_session is None:
                raise ValueError("Database session required for SQLAlchemy repositories")
            return SQLAlchemyProductRepository(db_session)
    
    def create_order_repository(self, db_session: Optional[Session] = None) -> OrderRepository:
        """Create an order repository instance."""
        if self.use_in_memory:
            return InMemoryOrderRepository()
        else:
            if db_session is None:
                raise ValueError("Database session required for SQLAlchemy repositories")
            return SQLAlchemyOrderRepository(db_session)
    
    def create_payment_repository(self, db_session: Optional[Session] = None) -> PaymentRepository:
        """Create a payment repository instance."""
        if self.use_in_memory:
            return InMemoryPaymentRepository()
        else:
            if db_session is None:
                raise ValueError("Database session required for SQLAlchemy repositories")
            return SQLAlchemyPaymentRepository(db_session)
    
    def create_notification_repository(self, db_session: Optional[Session] = None) -> NotificationRepository:
        """Create a notification repository instance."""
        if self.use_in_memory:
            return InMemoryNotificationRepository()
        else:
            if db_session is None:
                raise ValueError("Database session required for SQLAlchemy repositories")
            return SQLAlchemyNotificationRepository(db_session)


# Global factory instances
repository_factory = RepositoryFactory(use_in_memory=False)
test_repository_factory = RepositoryFactory(use_in_memory=True)


def get_repository_factory(use_in_memory: bool = False) -> RepositoryFactory:
    """Get a repository factory instance.
    
    Args:
        use_in_memory: If True, return factory for in-memory repositories
        
    Returns:
        RepositoryFactory instance
    """
    if use_in_memory:
        return test_repository_factory
    else:
        return repository_factory