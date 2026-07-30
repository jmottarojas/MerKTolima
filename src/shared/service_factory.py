"""Service factory for initializing and connecting all services."""

from typing import Dict, Any
import logging

from .service_integration import service_registry, orchestrator
from ..services.users.service import UserService
from ..services.users.repository import InMemoryUserRepository, SQLAlchemyUserRepository
from ..services.products.service import ProductService
from ..services.products.repository import InMemoryProductRepository, SQLAlchemyProductRepository
from ..services.orders.service import OrderService
from ..services.orders.repository import InMemoryOrderRepository, SQLAlchemyOrderRepository
from ..services.payments.service import PaymentService
from ..services.payments.repository import InMemoryPaymentRepository, SQLAlchemyPaymentRepository
from ..services.notifications.service import NotificationService
from ..services.notifications.repository import InMemoryNotificationRepository, SQLAlchemyNotificationRepository
from ..services.search.service import SearchService
from ..services.search.repository import SearchRepository

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Factory for creating and configuring services."""
    
    def __init__(self, use_database: bool = False, db_session=None):
        """Initialize service factory.
        
        Args:
            use_database: Whether to use database repositories or in-memory ones
            db_session: Database session for SQLAlchemy repositories
        """
        self.use_database = use_database
        self.db_session = db_session
        self._services: Dict[str, Any] = {}
    
    def create_all_services(self) -> Dict[str, Any]:
        """Create and configure all services with proper dependencies."""
        logger.info("Creating all services...")
        
        # Create repositories
        if self.use_database and self.db_session:
            user_repository = SQLAlchemyUserRepository(self.db_session)
            product_repository = SQLAlchemyProductRepository(self.db_session)
            order_repository = SQLAlchemyOrderRepository(self.db_session)
            payment_repository = SQLAlchemyPaymentRepository(self.db_session)
            notification_repository = SQLAlchemyNotificationRepository(self.db_session)
            search_repository = SearchRepository()  # Search service uses in-memory for now
        else:
            user_repository = InMemoryUserRepository()
            product_repository = InMemoryProductRepository()
            order_repository = InMemoryOrderRepository()
            payment_repository = InMemoryPaymentRepository()
            notification_repository = InMemoryNotificationRepository()
            search_repository = SearchRepository()
        
        # Create services
        user_service = UserService(user_repository)
        product_service = ProductService()  # ProductService doesn't take repository
        payment_service = PaymentService(payment_repository)
        notification_service = NotificationService(notification_repository)
        search_service = SearchService(product_service)  # SearchService takes product_service
        
        # Create order service with dependencies
        order_service = OrderService(order_repository, product_service, payment_service)
        
        # Store services
        self._services = {
            "user_service": user_service,
            "product_service": product_service,
            "order_service": order_service,
            "payment_service": payment_service,
            "notification_service": notification_service,
            "search_service": search_service
        }
        
        # Register services in the service registry
        service_registry.register_service("user_service", user_service, [])
        service_registry.register_service("product_service", product_service, [])
        service_registry.register_service("payment_service", payment_service, [])
        service_registry.register_service("notification_service", notification_service, [])
        service_registry.register_service("search_service", search_service, ["product_service"])
        service_registry.register_service("order_service", order_service, ["product_service", "payment_service"])
        
        # Configure event-driven communication between services
        self._setup_service_event_integration()
        
        logger.info(f"Created and registered {len(self._services)} services")
        return self._services
    
    def _setup_service_event_integration(self):
        """Setup event-driven communication between services."""
        from .service_integration import event_bus, EventType, Event
        
        # Get services
        user_service = self._services["user_service"]
        product_service = self._services["product_service"]
        order_service = self._services["order_service"]
        payment_service = self._services["payment_service"]
        notification_service = self._services["notification_service"]
        search_service = self._services["search_service"]
        
        # Configure user service to publish events
        original_register = user_service.register_user
        async def register_with_event(user_data):
            user = await original_register(user_data)
            await event_bus.publish(Event(
                type=EventType.USER_REGISTERED,
                source_service="user_service",
                data={
                    "user_id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "role": user.role
                }
            ))
            return user
        user_service.register_user = register_with_event
        
        # Configure product service to publish events
        original_create_product = product_service.create_product
        async def create_product_with_event(product_data):
            product = await original_create_product(product_data)
            await event_bus.publish(Event(
                type=EventType.PRODUCT_CREATED,
                source_service="product_service",
                data={
                    "product_id": product.id,
                    "seller_id": product.seller_id,
                    "name": product.name,
                    "price": float(product.price)
                }
            ))
            return product
        product_service.create_product = create_product_with_event
        
        original_update_inventory = product_service.update_inventory
        async def update_inventory_with_event(product_id, quantity_change):
            product = await original_update_inventory(product_id, quantity_change)
            if product.inventory.quantity == 0:
                await event_bus.publish(Event(
                    type=EventType.PRODUCT_OUT_OF_STOCK,
                    source_service="product_service",
                    data={
                        "product_id": product.id,
                        "seller_id": product.seller_id,
                        "name": product.name
                    }
                ))
            elif product.inventory.quantity <= product.inventory.low_stock_threshold:
                await event_bus.publish(Event(
                    type=EventType.PRODUCT_INVENTORY_LOW,
                    source_service="product_service",
                    data={
                        "product_id": product.id,
                        "seller_id": product.seller_id,
                        "current_quantity": product.inventory.quantity,
                        "threshold": product.inventory.low_stock_threshold
                    }
                ))
            return product
        product_service.update_inventory = update_inventory_with_event
        
        # Configure order service to publish events
        original_create_order = order_service.create_order
        async def create_order_with_event(buyer_id, cart_id, shipping_address, payment_method):
            order = await original_create_order(buyer_id, cart_id, shipping_address, payment_method)
            await event_bus.publish(Event(
                type=EventType.ORDER_CREATED,
                source_service="order_service",
                data={
                    "id": order.id,
                    "buyer_id": order.buyer_id,
                    "seller_id": order.seller_id,
                    "total_amount": float(order.total_amount),
                    "status": order.status
                }
            ))
            return order
        order_service.create_order = create_order_with_event
        
        original_update_status = order_service.update_order_status
        async def update_status_with_event(order_id, status):
            order = await original_update_status(order_id, status)
            if status == "shipped":
                await event_bus.publish(Event(
                    type=EventType.ORDER_SHIPPED,
                    source_service="order_service",
                    data={
                        "order_id": order.id,
                        "buyer_id": order.buyer_id,
                        "tracking_number": order.tracking_number
                    }
                ))
            elif status == "delivered":
                await event_bus.publish(Event(
                    type=EventType.ORDER_DELIVERED,
                    source_service="order_service",
                    data={
                        "order_id": order.id,
                        "buyer_id": order.buyer_id
                    }
                ))
            return order
        order_service.update_order_status = update_status_with_event
        
        # Configure payment service to publish events
        original_process_payment = payment_service.process_payment
        async def process_payment_with_event(payment_data):
            result = await original_process_payment(payment_data)
            if result.success:
                await event_bus.publish(Event(
                    type=EventType.PAYMENT_COMPLETED,
                    source_service="payment_service",
                    data={
                        "payment_id": result.payment_id,
                        "order_id": payment_data.order_id,
                        "amount": float(payment_data.amount)
                    }
                ))
            else:
                await event_bus.publish(Event(
                    type=EventType.PAYMENT_FAILED,
                    source_service="payment_service",
                    data={
                        "order_id": payment_data.order_id,
                        "amount": float(payment_data.amount),
                        "error": result.error_message
                    }
                ))
            return result
        payment_service.process_payment = process_payment_with_event
        
        logger.info("Service event integration configured successfully")
    
    def get_service(self, service_name: str) -> Any:
        """Get a service by name."""
        return self._services.get(service_name)
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all created services."""
        return self._services.copy()


def initialize_services(use_database: bool = False, db_session=None) -> Dict[str, Any]:
    """Initialize all services and return them.
    
    Args:
        use_database: Whether to use database repositories
        db_session: Database session for SQLAlchemy repositories
        
    Returns:
        Dictionary of initialized services
    """
    factory = ServiceFactory(use_database, db_session)
    services = factory.create_all_services()
    
    logger.info("Service initialization complete")
    logger.info(f"Available services: {list(services.keys())}")
    
    return services


def create_business_flow_test_scenario():
    """Create a test scenario to demonstrate complete business flows."""
    
    async def run_complete_order_flow():
        """Demonstrate a complete order flow from registration to delivery."""
        logger.info("Starting complete order flow demonstration...")
        
        try:
            # Get services
            user_service = service_registry.get_service("user_service")
            product_service = service_registry.get_service("product_service")
            order_service = service_registry.get_service("order_service")
            search_service = service_registry.get_service("search_service")
            notification_service = service_registry.get_service("notification_service")
            
            # 1. Register users (buyer and seller)
            from ..services.users.service import UserRegistrationData
            
            buyer_data = UserRegistrationData(
                email="buyer@example.com",
                password="SecurePass123",
                first_name="John",
                last_name="Buyer",
                role="buyer"
            )
            
            seller_data = UserRegistrationData(
                email="seller@example.com",
                password="SecurePass123",
                first_name="Jane",
                last_name="Seller",
                role="seller"
            )
            
            buyer = await user_service.register_user(buyer_data)
            seller = await user_service.register_user(seller_data)
            
            logger.info(f"Registered buyer: {buyer.id} and seller: {seller.id}")
            
            # 2. Create products
            from ..services.products.service import ProductCreationData
            from decimal import Decimal
            
            product_data = ProductCreationData(
                seller_id=seller.id,
                name="Test Product",
                description="A great test product",
                price=Decimal("29.99"),
                currency="USD",
                category="Electronics",
                inventory_quantity=100,
                low_stock_threshold=10
            )
            
            product = await product_service.create_product(product_data)
            logger.info(f"Created product: {product.id}")
            
            # 3. Test search functionality
            search_results = await search_service.search_products("Test Product")
            logger.info(f"Search found {len(search_results.products)} products")
            
            # 4. Add to cart
            cart = await order_service.add_to_cart(buyer.id, product.id, 2)
            logger.info(f"Added to cart: {cart.id}")
            
            # 5. Create order
            from ..shared.models import Address
            
            shipping_address = Address(
                street="123 Main St",
                city="Anytown",
                state="CA",
                postal_code="12345",
                country="USA"
            )
            
            order = await order_service.create_order(
                buyer.id, 
                cart.id, 
                shipping_address, 
                "credit_card"
            )
            logger.info(f"Created order: {order.id}")
            
            # 6. Update order status to simulate fulfillment
            await order_service.update_order_status(order.id, "processing")
            await order_service.update_order_status(order.id, "shipped")
            await order_service.update_order_status(order.id, "delivered")
            
            # 7. Verify notifications were sent
            buyer_notifications = await notification_service.get_user_notifications(buyer.id)
            seller_notifications = await notification_service.get_user_notifications(seller.id)
            
            logger.info(f"Buyer received {len(buyer_notifications)} notifications")
            logger.info(f"Seller received {len(seller_notifications)} notifications")
            
            # 8. Test low inventory scenario
            # Reduce inventory to trigger low stock notification
            await product_service.update_inventory(product.id, -95)  # Should trigger low stock
            
            logger.info("Complete order flow demonstration completed successfully!")
            
            return {
                "buyer": buyer,
                "seller": seller,
                "product": product,
                "order": order,
                "buyer_notifications": len(buyer_notifications),
                "seller_notifications": len(seller_notifications)
            }
            
        except Exception as e:
            logger.error(f"Error in order flow demonstration: {e}")
            raise
    
    async def run_multi_vendor_scenario():
        """Demonstrate multi-vendor marketplace scenario."""
        logger.info("Starting multi-vendor scenario...")
        
        try:
            # Get services
            user_service = service_registry.get_service("user_service")
            product_service = service_registry.get_service("product_service")
            order_service = service_registry.get_service("order_service")
            search_service = service_registry.get_service("search_service")
            
            # Register multiple sellers and one buyer
            from ..services.users.service import UserRegistrationData
            from ..services.products.service import ProductCreationData
            from decimal import Decimal
            
            # Create buyer
            buyer_data = UserRegistrationData(
                email="multibuyer@example.com",
                password="SecurePass123",
                first_name="Multi",
                last_name="Buyer",
                role="buyer"
            )
            buyer = await user_service.register_user(buyer_data)
            
            # Create multiple sellers
            sellers = []
            products = []
            
            for i in range(3):
                seller_data = UserRegistrationData(
                    email=f"seller{i}@example.com",
                    password="SecurePass123",
                    first_name=f"Seller{i}",
                    last_name="Multi",
                    role="seller"
                )
                seller = await user_service.register_user(seller_data)
                sellers.append(seller)
                
                # Each seller creates products
                for j in range(2):
                    product_data = ProductCreationData(
                        seller_id=seller.id,
                        name=f"Product {i}-{j}",
                        description=f"Product from seller {i}",
                        price=Decimal(f"{10 + i * 5 + j}.99"),
                        currency="USD",
                        category="Electronics" if i % 2 == 0 else "Books",
                        inventory_quantity=50,
                        low_stock_threshold=5
                    )
                    product = await product_service.create_product(product_data)
                    products.append(product)
            
            # Test category-based search
            electronics_results = await search_service.search_products("", {"category": "Electronics"})
            books_results = await search_service.search_products("", {"category": "Books"})
            
            logger.info(f"Found {len(electronics_results.products)} electronics products")
            logger.info(f"Found {len(books_results.products)} books products")
            
            # Create orders from multiple vendors
            orders = []
            for i, product in enumerate(products[:3]):  # Order from first 3 products
                cart = await order_service.add_to_cart(buyer.id, product.id, 1)
                
                from ..shared.models import Address
                shipping_address = Address(
                    street=f"{100 + i} Main St",
                    city="Anytown",
                    state="CA",
                    postal_code="12345",
                    country="USA"
                )
                
                order = await order_service.create_order(
                    buyer.id,
                    cart.id,
                    shipping_address,
                    "credit_card"
                )
                orders.append(order)
            
            logger.info(f"Created {len(orders)} orders from multiple vendors")
            logger.info("Multi-vendor scenario completed successfully!")
            
            return {
                "buyer": buyer,
                "sellers": sellers,
                "products": products,
                "orders": orders
            }
            
        except Exception as e:
            logger.error(f"Error in multi-vendor scenario: {e}")
            raise
    
    return run_complete_order_flow, run_multi_vendor_scenario