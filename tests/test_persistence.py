"""Tests for database persistence layer."""

import pytest
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.shared.db_models import Base
from src.shared.models import (
    UserRole, ProductStatus, OrderStatus, PaymentStatus, NotificationType,
    Address, UserPreferences, InventoryInfo
)
from src.services.users.repository import SQLAlchemyUserRepository
from src.services.products.repository import SQLAlchemyProductRepository
from src.services.orders.repository import SQLAlchemyOrderRepository
from src.services.payments.repository import SQLAlchemyPaymentRepository
from src.services.notifications.repository import SQLAlchemyNotificationRepository
from src.shared.models import Cart, Order, CartItem, OrderItem, PaymentInfo, Notification


# Test data models that match the repository interfaces
class UserRegistrationData:
    """Test user registration data."""
    def __init__(self, email, password_hash, role, first_name, last_name):
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.first_name = first_name
        self.last_name = last_name


class UserProfileUpdates:
    """Test user profile updates."""
    def __init__(self, first_name=None, last_name=None, phone=None, address=None, preferences=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.address = address
        self.preferences = preferences


class ProductCreationData:
    """Test product creation data."""
    def __init__(self, seller_id, name, description, price, currency, category, images, inventory):
        self.seller_id = seller_id
        self.name = name
        self.description = description
        self.price = price
        self.currency = currency
        self.category = category
        self.images = images
        self.inventory = inventory


class ProductUpdates:
    """Test product updates."""
    def __init__(self, name=None, description=None, price=None, category=None, images=None, inventory=None):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.images = images
        self.inventory = inventory


class SearchQuery:
    """Test search query."""
    def __init__(self, search_term=None, category=None, min_price=None, max_price=None, 
                 seller_id=None, sort_by=None, page=1, page_size=10):
        self.search_term = search_term
        self.category = category
        self.min_price = min_price
        self.max_price = max_price
        self.seller_id = seller_id
        self.sort_by = sort_by
        self.page = page
        self.page_size = page_size


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()


class TestUserRepository:
    """Test SQLAlchemy user repository."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user."""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Create user data
        user_data = type('UserData', (), {
            'email': "test@example.com",
            'password_hash': "hashed_password_123",
            'role': UserRole.BUYER,
            'first_name': "John",
            'last_name': "Doe"
        })()
        
        user = await repo.create_user(user_data)
        
        assert user.email == "test@example.com"
        assert user.role == UserRole.BUYER
        assert user.profile.first_name == "John"
        assert user.profile.last_name == "Doe"
        assert user.is_active is True
        assert user.email_verified is False
    
    @pytest.mark.asyncio
    async def test_create_duplicate_email_fails(self, db_session):
        """Test that creating a user with duplicate email fails."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user_data = UserRegistrationData(
            email="test@example.com",
            password_hash="hashed_password_123",
            role=UserRole.BUYER,
            first_name="John",
            last_name="Doe"
        )
        
        # Create first user
        await repo.create_user(user_data)
        
        # Try to create second user with same email
        with pytest.raises(ValueError, match="already exists"):
            await repo.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_session):
        """Test getting user by ID."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user_data = UserRegistrationData(
            email="test@example.com",
            password_hash="hashed_password_123",
            role=UserRole.SELLER,
            first_name="Jane",
            last_name="Smith"
        )
        
        created_user = await repo.create_user(user_data)
        retrieved_user = await repo.get_user_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.role == UserRole.SELLER
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session):
        """Test getting user by email."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user_data = UserRegistrationData(
            email="test@example.com",
            password_hash="hashed_password_123",
            role=UserRole.BUYER,
            first_name="John",
            last_name="Doe"
        )
        
        created_user = await repo.create_user(user_data)
        retrieved_user = await repo.get_user_by_email("test@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user(self, db_session):
        """Test updating user profile."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user_data = UserRegistrationData(
            email="test@example.com",
            password_hash="hashed_password_123",
            role=UserRole.BUYER,
            first_name="John",
            last_name="Doe"
        )
        
        created_user = await repo.create_user(user_data)
        
        # Update user
        address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        preferences = UserPreferences(
            email_notifications=False,
            in_app_notifications=True,
            marketing_emails=False
        )
        
        updates = UserProfileUpdates(
            first_name="Jane",
            phone="555-1234",
            address=address,
            preferences=preferences
        )
        
        updated_user = await repo.update_user(created_user.id, updates)
        
        assert updated_user.profile.first_name == "Jane"
        assert updated_user.profile.phone == "555-1234"
        assert updated_user.profile.address.street == "123 Main St"
        assert updated_user.profile.preferences.email_notifications is False
    
    @pytest.mark.asyncio
    async def test_email_exists(self, db_session):
        """Test checking if email exists."""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Email doesn't exist initially
        assert await repo.email_exists("test@example.com") is False
        
        # Create user
        user_data = UserRegistrationData(
            email="test@example.com",
            password_hash="hashed_password_123",
            role=UserRole.BUYER,
            first_name="John",
            last_name="Doe"
        )
        
        await repo.create_user(user_data)
        
        # Email exists now
        assert await repo.email_exists("test@example.com") is True
        assert await repo.email_exists("TEST@EXAMPLE.COM") is True  # Case insensitive


class TestProductRepository:
    """Test SQLAlchemy product repository."""
    
    @pytest.mark.asyncio
    async def test_create_product(self, db_session):
        """Test creating a product."""
        repo = SQLAlchemyProductRepository(db_session)
        
        inventory = InventoryInfo(
            quantity=100,
            low_stock_threshold=10,
            track_inventory=True
        )
        
        product_data = ProductCreationData(
            seller_id="seller123",
            name="Test Product",
            description="A test product",
            price=Decimal("29.99"),
            currency="USD",
            category="Electronics",
            images=["image1.jpg", "image2.jpg"],
            inventory=inventory
        )
        
        product = await repo.create_product(product_data)
        
        assert product.name == "Test Product"
        assert product.price == Decimal("29.99")
        assert product.inventory.quantity == 100
        assert product.status == ProductStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_create_product_out_of_stock(self, db_session):
        """Test creating a product with zero inventory."""
        repo = SQLAlchemyProductRepository(db_session)
        
        inventory = InventoryInfo(
            quantity=0,
            low_stock_threshold=10,
            track_inventory=True
        )
        
        product_data = ProductCreationData(
            seller_id="seller123",
            name="Out of Stock Product",
            description="A product with no inventory",
            price=Decimal("19.99"),
            currency="USD",
            category="Books",
            images=[],
            inventory=inventory
        )
        
        product = await repo.create_product(product_data)
        
        assert product.status == ProductStatus.OUT_OF_STOCK
    
    @pytest.mark.asyncio
    async def test_update_inventory(self, db_session):
        """Test updating product inventory."""
        repo = SQLAlchemyProductRepository(db_session)
        
        # Create product
        inventory = InventoryInfo(quantity=100, low_stock_threshold=10, track_inventory=True)
        product_data = ProductCreationData(
            seller_id="seller123",
            name="Test Product",
            description="A test product",
            price=Decimal("29.99"),
            currency="USD",
            category="Electronics",
            images=[],
            inventory=inventory
        )
        
        product = await repo.create_product(product_data)
        
        # Update inventory to zero
        updated_product = await repo.update_inventory(product.id, 0)
        assert updated_product.inventory.quantity == 0
        assert updated_product.status == ProductStatus.OUT_OF_STOCK
        
        # Update inventory back to positive
        updated_product = await repo.update_inventory(product.id, 50)
        assert updated_product.inventory.quantity == 50
        assert updated_product.status == ProductStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_search_products(self, db_session):
        """Test searching products."""
        repo = SQLAlchemyProductRepository(db_session)
        
        # Create test products
        inventory = InventoryInfo(quantity=100, low_stock_threshold=10, track_inventory=True)
        
        products_data = [
            ProductCreationData(
                seller_id="seller1",
                name="iPhone 15",
                description="Latest iPhone model",
                price=Decimal("999.99"),
                currency="USD",
                category="Electronics",
                images=[],
                inventory=inventory
            ),
            ProductCreationData(
                seller_id="seller2",
                name="Samsung Galaxy",
                description="Android smartphone",
                price=Decimal("799.99"),
                currency="USD",
                category="Electronics",
                images=[],
                inventory=inventory
            ),
            ProductCreationData(
                seller_id="seller1",
                name="MacBook Pro",
                description="Professional laptop",
                price=Decimal("1999.99"),
                currency="USD",
                category="Computers",
                images=[],
                inventory=inventory
            )
        ]
        
        for product_data in products_data:
            await repo.create_product(product_data)
        
        # Search by term
        query = SearchQuery(search_term="iPhone", page=1, page_size=10)
        results = await repo.search_products(query)
        
        assert results.total_count == 1
        assert len(results.products) == 1
        assert results.products[0].name == "iPhone 15"
        
        # Search by category
        query = SearchQuery(category="Electronics", page=1, page_size=10)
        results = await repo.search_products(query)
        
        assert results.total_count == 2
        assert len(results.products) == 2
        
        # Search with price range
        query = SearchQuery(min_price=Decimal("800"), max_price=Decimal("1000"), page=1, page_size=10)
        results = await repo.search_products(query)
        
        assert results.total_count == 1  # Only iPhone (Samsung is 799.99, below min_price of 800)


class TestOrderRepository:
    """Test SQLAlchemy order repository."""
    
    @pytest.mark.asyncio
    async def test_create_and_get_cart(self, db_session):
        """Test creating and retrieving a cart."""
        repo = SQLAlchemyOrderRepository(db_session)
        
        cart = await repo.create_cart("user123")
        
        assert cart.user_id == "user123"
        assert cart.total_amount == Decimal("0.00")
        assert len(cart.items) == 0
        
        # Retrieve cart
        retrieved_cart = await repo.get_cart_by_user("user123")
        assert retrieved_cart is not None
        assert retrieved_cart.id == cart.id
    
    @pytest.mark.asyncio
    async def test_update_cart(self, db_session):
        """Test updating a cart."""
        repo = SQLAlchemyOrderRepository(db_session)
        
        cart = await repo.create_cart("user123")
        
        # Add items to cart
        item = CartItem(
            product_id="product123",
            quantity=2,
            unit_price=Decimal("29.99"),
            total_price=Decimal("59.98")
        )
        
        cart.items = [item]
        cart.total_amount = Decimal("59.98")
        
        updated_cart = await repo.update_cart(cart)
        
        assert len(updated_cart.items) == 1
        assert updated_cart.total_amount == Decimal("59.98")
        assert updated_cart.items[0].product_id == "product123"
    
    @pytest.mark.asyncio
    async def test_create_order(self, db_session):
        """Test creating an order."""
        repo = SQLAlchemyOrderRepository(db_session)
        
        # Create order items
        items = [
            OrderItem(
                product_id="product123",
                quantity=2,
                unit_price=Decimal("29.99"),
                total_price=Decimal("59.98")
            )
        ]
        
        # Create address
        address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        # Create payment info
        payment_info = PaymentInfo(
            payment_method="credit_card",
            payment_status=PaymentStatus.PENDING,
            amount=Decimal("59.98"),
            currency="USD"
        )
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            buyer_id="buyer123",
            seller_id="seller123",
            items=items,
            total_amount=Decimal("59.98"),
            currency="USD",
            status=OrderStatus.PENDING,
            shipping_address=address,
            payment_info=payment_info,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_order = await repo.create_order(order)
        
        assert created_order.id == order.id
        assert created_order.buyer_id == "buyer123"
        assert len(created_order.items) == 1
        assert created_order.total_amount == Decimal("59.98")
    
    @pytest.mark.asyncio
    async def test_update_order_status(self, db_session):
        """Test updating order status."""
        repo = SQLAlchemyOrderRepository(db_session)
        
        # Create order first
        items = [OrderItem(
            product_id="product123",
            quantity=1,
            unit_price=Decimal("29.99"),
            total_price=Decimal("29.99")
        )]
        
        address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        payment_info = PaymentInfo(
            payment_method="credit_card",
            payment_status=PaymentStatus.COMPLETED,
            amount=Decimal("29.99"),
            currency="USD"
        )
        
        order = Order(
            id=str(uuid.uuid4()),
            buyer_id="buyer123",
            seller_id="seller123",
            items=items,
            total_amount=Decimal("29.99"),
            currency="USD",
            status=OrderStatus.PENDING,
            shipping_address=address,
            payment_info=payment_info,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_order = await repo.create_order(order)
        
        # Update status
        updated_order = await repo.update_order_status(created_order.id, OrderStatus.CONFIRMED)
        
        assert updated_order.status == OrderStatus.CONFIRMED
    
    @pytest.mark.asyncio
    async def test_generate_tracking_number(self, db_session):
        """Test generating tracking number."""
        repo = SQLAlchemyOrderRepository(db_session)
        
        tracking_number = await repo.generate_tracking_number()
        
        assert tracking_number.startswith("TRK")
        assert len(tracking_number) == 15  # TRK + 12 characters


class TestPaymentRepository:
    """Test SQLAlchemy payment repository."""
    
    @pytest.mark.asyncio
    async def test_save_and_get_payment_result(self, db_session):
        """Test saving and retrieving payment result."""
        repo = SQLAlchemyPaymentRepository(db_session)
        
        from src.services.payments.service import PaymentResult, PaymentStatus
        
        payment_result = PaymentResult(
            payment_id=str(uuid.uuid4()),
            status=PaymentStatus.COMPLETED,
            transaction_id="txn_123456",
            message="Payment processed successfully",
            gateway_response={
                "order_id": "order123",
                "amount": "99.99",
                "currency": "USD",
                "payment_method": "credit_card",
                "status": "approved", 
                "code": "00"
            }
        )
        
        await repo.save_payment_result(payment_result)
        
        # Retrieve payment
        retrieved_payment = await repo.get_payment_by_id(payment_result.payment_id)
        
        assert retrieved_payment is not None
        assert retrieved_payment.payment_id == payment_result.payment_id
        assert retrieved_payment.status == PaymentStatus.COMPLETED
        assert retrieved_payment.transaction_id == "txn_123456"
    
    @pytest.mark.asyncio
    async def test_save_and_get_receipt(self, db_session):
        """Test saving and retrieving receipt."""
        repo = SQLAlchemyPaymentRepository(db_session)
        
        from src.services.payments.service import Receipt
        
        receipt = Receipt(
            id=str(uuid.uuid4()),
            payment_id="payment123",
            order_id="order123",
            amount=Decimal("99.99"),
            currency="USD",
            payment_method_type="credit_card",
            issued_at=datetime.utcnow(),
            receipt_number="RCP-001",
            merchant_info={
                'name': 'Marketplace Platform',
                'address': '123 Commerce St, Business City, BC 12345',
                'tax_id': 'TAX123456789',
                'contact': 'support@marketplace.com'
            }
        )
        
        await repo.save_receipt(receipt)
        
        # Retrieve receipt
        retrieved_receipt = await repo.get_receipt_by_payment("payment123")
        
        assert retrieved_receipt is not None
        assert retrieved_receipt.receipt_number == "RCP-001"
        assert retrieved_receipt.amount == Decimal("99.99")
        assert retrieved_receipt.currency == "USD"


class TestNotificationRepository:
    """Test SQLAlchemy notification repository."""
    
    @pytest.mark.asyncio
    async def test_save_and_get_notification(self, db_session):
        """Test saving and retrieving notification."""
        repo = SQLAlchemyNotificationRepository(db_session)
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id="user123",
            title="Test Notification",
            message="This is a test notification",
            notification_type=NotificationType.EMAIL,
            is_read=False,
            metadata={"order_id": "order123"},
            created_at=datetime.utcnow()
        )
        
        await repo.save_notification(notification)
        
        # Retrieve notification
        retrieved_notification = await repo.get_notification_by_id(notification.id)
        
        assert retrieved_notification is not None
        assert retrieved_notification.title == "Test Notification"
        assert retrieved_notification.user_id == "user123"
        assert retrieved_notification.metadata["order_id"] == "order123"
    
    @pytest.mark.asyncio
    async def test_get_notifications_by_user(self, db_session):
        """Test getting notifications by user."""
        repo = SQLAlchemyNotificationRepository(db_session)
        
        # Create multiple notifications
        notifications = []
        for i in range(3):
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id="user123",
                title=f"Notification {i+1}",
                message=f"Message {i+1}",
                notification_type=NotificationType.IN_APP,
                is_read=False,
                metadata={},
                created_at=datetime.utcnow()
            )
            notifications.append(notification)
            await repo.save_notification(notification)
        
        # Retrieve notifications
        user_notifications = await repo.get_notifications_by_user("user123")
        
        assert len(user_notifications) == 3
        # Should be ordered by created_at descending
        assert user_notifications[0].title == "Notification 3"
    
    @pytest.mark.asyncio
    async def test_mark_notification_as_read(self, db_session):
        """Test marking notification as read."""
        repo = SQLAlchemyNotificationRepository(db_session)
        
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id="user123",
            title="Test Notification",
            message="This is a test notification",
            notification_type=NotificationType.IN_APP,
            is_read=False,
            metadata={},
            created_at=datetime.utcnow()
        )
        
        await repo.save_notification(notification)
        
        # Mark as read
        await repo.mark_notification_as_read(notification.id)
        
        # Retrieve and verify
        updated_notification = await repo.get_notification_by_id(notification.id)
        
        assert updated_notification.is_read is True
        assert updated_notification.read_at is not None
    
    @pytest.mark.asyncio
    async def test_save_and_get_user_preferences(self, db_session):
        """Test saving and retrieving user preferences."""
        repo = SQLAlchemyNotificationRepository(db_session)
        
        preferences = {
            "email_notifications": True,
            "in_app_notifications": False,
            "marketing_emails": True
        }
        
        await repo.save_user_preferences("user123", preferences)
        
        # Retrieve preferences
        retrieved_preferences = await repo.get_user_preferences("user123")
        
        assert retrieved_preferences is not None
        assert retrieved_preferences["email_notifications"] is True
        assert retrieved_preferences["in_app_notifications"] is False


class TestDatabaseIntegrity:
    """Test database referential integrity."""
    
    @pytest.mark.asyncio
    async def test_user_product_relationship(self, db_session):
        """Test relationship between users and products."""
        user_repo = SQLAlchemyUserRepository(db_session)
        product_repo = SQLAlchemyProductRepository(db_session)
        
        # Create user
        user_data = UserRegistrationData(
            email="seller@example.com",
            password_hash="hashed_password",
            role=UserRole.SELLER,
            first_name="John",
            last_name="Seller"
        )
        user = await user_repo.create_user(user_data)
        
        # Create product for user
        inventory = InventoryInfo(quantity=50, low_stock_threshold=5, track_inventory=True)
        product_data = ProductCreationData(
            seller_id=user.id,
            name="User's Product",
            description="A product by the user",
            price=Decimal("49.99"),
            currency="USD",
            category="Test",
            images=[],
            inventory=inventory
        )
        product = await product_repo.create_product(product_data)
        
        assert product.seller_id == user.id
        
        # Get products by seller
        seller_products = await product_repo.get_products_by_seller(user.id)
        assert len(seller_products) == 1
        assert seller_products[0].id == product.id
    
    @pytest.mark.asyncio
    async def test_order_user_relationship(self, db_session):
        """Test relationship between orders and users."""
        user_repo = SQLAlchemyUserRepository(db_session)
        order_repo = SQLAlchemyOrderRepository(db_session)
        
        # Create buyer and seller
        buyer_data = UserRegistrationData(
            email="buyer@example.com",
            password_hash="hashed_password",
            role=UserRole.BUYER,
            first_name="Jane",
            last_name="Buyer"
        )
        buyer = await user_repo.create_user(buyer_data)
        
        seller_data = UserRegistrationData(
            email="seller@example.com",
            password_hash="hashed_password",
            role=UserRole.SELLER,
            first_name="John",
            last_name="Seller"
        )
        seller = await user_repo.create_user(seller_data)
        
        # Create order
        items = [OrderItem(
            product_id="product123",
            quantity=1,
            unit_price=Decimal("29.99"),
            total_price=Decimal("29.99")
        )]
        
        address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        payment_info = PaymentInfo(
            payment_method="credit_card",
            payment_status=PaymentStatus.COMPLETED,
            amount=Decimal("29.99"),
            currency="USD"
        )
        
        order = Order(
            id=str(uuid.uuid4()),
            buyer_id=buyer.id,
            seller_id=seller.id,
            items=items,
            total_amount=Decimal("29.99"),
            currency="USD",
            status=OrderStatus.PENDING,
            shipping_address=address,
            payment_info=payment_info,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_order = await order_repo.create_order(order)
        
        # Test relationships
        buyer_orders = await order_repo.get_orders_by_buyer(buyer.id)
        seller_orders = await order_repo.get_orders_by_seller(seller.id)
        
        assert len(buyer_orders) == 1
        assert len(seller_orders) == 1
        assert buyer_orders[0].id == created_order.id
        assert seller_orders[0].id == created_order.id