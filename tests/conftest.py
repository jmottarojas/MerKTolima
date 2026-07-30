"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.shared.database import Base, get_db
from src.api.main import app
from tests.test_config import TestDataFactory

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return TestDataFactory.create_user_data()


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return TestDataFactory.create_product_data()


@pytest.fixture
def sample_cart_item_data():
    """Sample cart item data for testing."""
    return TestDataFactory.create_cart_item_data()


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing."""
    return TestDataFactory.create_payment_data()


@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing."""
    return TestDataFactory.create_notification_data()