"""Integration tests for complete business flows."""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime

from src.shared.service_factory import initialize_services
from src.shared.service_integration import event_bus, Event, EventType, service_registry
from src.shared.models import Address, OrderStatus
from src.services.users.service import UserRegistrationData
from src.services.products.service import ProductCreationData


class TestCompleteBusinessFlows:
    """Test complete end-to-end business flows."""
    
    @pytest.fixture(autouse=True)
    async def setup_services(self):
        """Setup services for each test."""
        # Clear any existing services and events
        service_registry._services.clear()
        service_registry._dependencies.clear()
        event_bus._handlers.clear()
        event_bus._event_history.clear()
        
        # Initialize services
        self.services = initialize_services(use_database=False)
        
        # Get service references
        self.user_service = self.services["user_service"]
        self.product_service = self.services["product_service"]
        self.order_service = self.services["order_service"]
        self.payment_service = self.services["payment_service"]
        self.notification_service = self.services["notification_service"]
        self.search_service = self.services["search_service"]
    
    @pytest.mark.asyncio
    async def test_complete_order_flow(self):
        """Test complete order flow from user registration to order delivery."""
        # 1. Register buyer and seller
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
        
        buyer = await self.user_service.register_user(buyer_data)
        seller = await self.user_service.register_user(seller_data)
        
        assert buyer.email == "buyer@example.com"
        assert seller.email == "seller@example.com"
        
        # 2. Create product
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
        
        product = await self.product_service.create_product(product_data)
        assert product.name == "Test Product"
        assert product.inventory_quantity == 100
        
        # 3. Add product to cart
        cart = await self.order_service.add_to_cart(buyer.id, product.id, 2)
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 2
        assert cart.total_amount == Decimal("59.98")
        
        # 4. Create order with payment
        shipping_address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        order = await self.order_service.create_order(
            buyer.id,
            cart.id,
            shipping_address,
            "credit_card"
        )
        
        assert order.buyer_id == buyer.id
        assert order.seller_id == seller.id
        assert order.total_amount == Decimal("59.98")
        assert order.status == OrderStatus.CONFIRMED  # Should be confirmed after successful payment
        
        # 5. Verify inventory was reduced
        updated_product = await self.product_service.get_product_by_id(product.id)
        assert updated_product.inventory_quantity == 98  # 100 - 2
        
        # 6. Update order status through fulfillment process
        order = await self.order_service.update_order_status(order.id, OrderStatus.PROCESSING)
        assert order.status == OrderStatus.PROCESSING
        
        order = await self.order_service.update_order_status(order.id, OrderStatus.SHIPPED)
        assert order.status == OrderStatus.SHIPPED
        
        order = await self.order_service.update_order_status(order.id, OrderStatus.DELIVERED)
        assert order.status == OrderStatus.DELIVERED
        
        # 7. Verify cart was cleared
        buyer_cart = await self.order_service.get_cart(buyer.id)
        assert len(buyer_cart.items) == 0
        assert buyer_cart.total_amount == Decimal("0.00")
    
    @pytest.mark.asyncio
    async def test_event_driven_notifications(self):
        """Test that events trigger appropriate notifications."""
        # Register a buyer
        buyer_data = UserRegistrationData(
            email="buyer@example.com",
            password="SecurePass123",
            first_name="John",
            last_name="Buyer",
            role="buyer"
        )
        
        buyer = await self.user_service.register_user(buyer_data)
        
        # Check that user registration event was published
        events = event_bus.get_event_history(EventType.USER_REGISTERED)
        assert len(events) == 1
        assert events[0].data["user_id"] == buyer.id
        assert events[0].data["email"] == "buyer@example.com"
    
    @pytest.mark.asyncio
    async def test_inventory_management_flow(self):
        """Test inventory management and low stock alerts."""
        # Register seller
        seller_data = UserRegistrationData(
            email="seller@example.com",
            password="SecurePass123",
            first_name="Jane",
            last_name="Seller",
            role="seller"
        )
        
        seller = await self.user_service.register_user(seller_data)
        
        # Create product with low initial inventory
        product_data = ProductCreationData(
            seller_id=seller.id,
            name="Low Stock Product",
            description="A product with low stock",
            price=Decimal("19.99"),
            currency="USD",
            category="Books",
            inventory_quantity=5,
            low_stock_threshold=10
        )
        
        product = await self.product_service.create_product(product_data)
        
        # Update inventory to trigger low stock alert
        updated_product = await self.product_service.update_inventory(product.id, 3)
        assert updated_product.inventory_quantity == 3
        
        # Check that low inventory event was published
        events = event_bus.get_event_history(EventType.PRODUCT_INVENTORY_LOW)
        assert len(events) == 1
        assert events[0].data["product_id"] == product.id
        assert events[0].data["current_quantity"] == 3
        
        # Update inventory to zero to trigger out of stock
        updated_product = await self.product_service.update_inventory(product.id, 0)
        assert updated_product.inventory_quantity == 0
        assert updated_product.status == "out_of_stock"
        
        # Check that out of stock event was published
        events = event_bus.get_event_history(EventType.PRODUCT_OUT_OF_STOCK)
        assert len(events) == 1
        assert events[0].data["product_id"] == product.id
        assert events[0].data["new_quantity"] == 0
    
    @pytest.mark.asyncio
    async def test_payment_failure_flow(self):
        """Test order flow when payment fails."""
        # Register buyer and seller
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
        
        buyer = await self.user_service.register_user(buyer_data)
        seller = await self.user_service.register_user(seller_data)
        
        # Create product
        product_data = ProductCreationData(
            seller_id=seller.id,
            name="Test Product",
            description="A test product",
            price=Decimal("29.99"),
            currency="USD",
            category="Electronics",
            inventory_quantity=100,
            low_stock_threshold=10
        )
        
        product = await self.product_service.create_product(product_data)
        
        # Add to cart
        cart = await self.order_service.add_to_cart(buyer.id, product.id, 2)
        
        # Try to create order with invalid payment method (should fail)
        shipping_address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        # Mock payment failure by using invalid payment method
        from src.services.payments.service import PaymentMethod, PaymentMethodType
        
        invalid_payment_method = PaymentMethod(
            type=PaymentMethodType.CARD,
            details={
                "card_number": "0000000000000000",  # Invalid card
                "expiry_month": "12",
                "expiry_year": "2025",
                "cvv": "000",
                "cardholder_name": "Invalid User"
            }
        )
        
        # This should raise an exception due to payment failure
        with pytest.raises(ValueError, match="Payment failed"):
            await self.order_service.create_order(
                buyer.id,
                cart.id,
                shipping_address,
                invalid_payment_method
            )
        
        # Verify inventory was not reduced
        updated_product = await self.product_service.get_product_by_id(product.id)
        assert updated_product.inventory_quantity == 100  # Should remain unchanged
        
        # Verify cart was not cleared
        buyer_cart = await self.order_service.get_cart_by_user(buyer.id)
        assert len(buyer_cart.items) == 1  # Should still have items
    
    @pytest.mark.asyncio
    async def test_multi_item_cart_flow(self):
        """Test cart and order flow with multiple items."""
        # Register buyer and seller
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
        
        buyer = await self.user_service.register_user(buyer_data)
        seller = await self.user_service.register_user(seller_data)
        
        # Create multiple products
        product1_data = ProductCreationData(
            seller_id=seller.id,
            name="Product 1",
            description="First product",
            price=Decimal("19.99"),
            currency="USD",
            category="Electronics",
            inventory_quantity=50,
            low_stock_threshold=5
        )
        
        product2_data = ProductCreationData(
            seller_id=seller.id,
            name="Product 2",
            description="Second product",
            price=Decimal("39.99"),
            currency="USD",
            category="Electronics",
            inventory_quantity=30,
            low_stock_threshold=5
        )
        
        product1 = await self.product_service.create_product(product1_data)
        product2 = await self.product_service.create_product(product2_data)
        
        # Add both products to cart
        cart = await self.order_service.add_to_cart(buyer.id, product1.id, 2)
        cart = await self.order_service.add_to_cart(buyer.id, product2.id, 1)
        
        assert len(cart.items) == 2
        expected_total = (Decimal("19.99") * 2) + (Decimal("39.99") * 1)
        assert cart.total_amount == expected_total
        
        # Create order
        shipping_address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        order = await self.order_service.create_order(
            buyer.id,
            cart.id,
            shipping_address,
            "credit_card"
        )
        
        assert len(order.items) == 2
        assert order.total_amount == expected_total
        
        # Verify inventory was reduced for both products
        updated_product1 = await self.product_service.get_product_by_id(product1.id)
        updated_product2 = await self.product_service.get_product_by_id(product2.id)
        
        assert updated_product1.inventory_quantity == 48  # 50 - 2
        assert updated_product2.inventory_quantity == 29  # 30 - 1
    
    @pytest.mark.asyncio
    async def test_service_registry_functionality(self):
        """Test that service registry works correctly."""
        # Verify all services are registered
        services = service_registry.list_services()
        expected_services = [
            "user_service", "product_service", "order_service",
            "payment_service", "notification_service", "search_service"
        ]
        
        for service_name in expected_services:
            assert service_name in services
        
        # Verify service dependencies
        order_deps = service_registry.get_dependencies("order_service")
        assert "product_service" in order_deps
        assert "payment_service" in order_deps
        
        search_deps = service_registry.get_dependencies("search_service")
        assert "product_service" in search_deps
        
        # Verify services can be retrieved
        user_service = service_registry.get_service("user_service")
        assert user_service is not None
        assert user_service == self.user_service
    
    @pytest.mark.asyncio
    async def test_event_history_tracking(self):
        """Test that event history is properly tracked."""
        # Clear event history
        event_bus._event_history.clear()
        
        # Register a user to generate events
        buyer_data = UserRegistrationData(
            email="buyer@example.com",
            password="SecurePass123",
            first_name="John",
            last_name="Buyer",
            role="buyer"
        )
        
        await self.user_service.register_user(buyer_data)
        
        # Check event history
        all_events = event_bus.get_event_history()
        assert len(all_events) == 1
        
        user_events = event_bus.get_event_history(EventType.USER_REGISTERED)
        assert len(user_events) == 1
        assert user_events[0].type == EventType.USER_REGISTERED
        
        # Check that non-existent event types return empty list
        payment_events = event_bus.get_event_history(EventType.PAYMENT_COMPLETED)
        assert len(payment_events) == 0


class TestServiceIntegration:
    """Test service integration and communication."""
    
    @pytest.fixture(autouse=True)
    async def setup_services(self):
        """Setup services for each test."""
        # Clear any existing services and events
        service_registry._services.clear()
        service_registry._dependencies.clear()
        event_bus._handlers.clear()
        event_bus._event_history.clear()
        
        # Initialize services
        self.services = initialize_services(use_database=False)
    
    @pytest.mark.asyncio
    async def test_cross_service_data_consistency(self):
        """Test that data remains consistent across services."""
        user_service = self.services["user_service"]
        product_service = self.services["product_service"]
        order_service = self.services["order_service"]
        
        # Create seller
        seller_data = UserRegistrationData(
            email="seller@example.com",
            password="SecurePass123",
            first_name="Jane",
            last_name="Seller",
            role="seller"
        )
        
        seller = await user_service.register_user(seller_data)
        
        # Create product
        product_data = ProductCreationData(
            seller_id=seller.id,
            name="Consistency Test Product",
            description="Testing data consistency",
            price=Decimal("25.00"),
            currency="USD",
            category="Test",
            inventory_quantity=10,
            low_stock_threshold=2
        )
        
        product = await product_service.create_product(product_data)
        
        # Verify product references correct seller
        assert product.seller_id == seller.id
        
        # Get products by seller
        seller_products = await product_service.get_products_by_seller(seller.id)
        assert len(seller_products) == 1
        assert seller_products[0].id == product.id
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test that concurrent operations work correctly."""
        user_service = self.services["user_service"]
        product_service = self.services["product_service"]
        
        # Create multiple users concurrently
        user_tasks = []
        for i in range(5):
            user_data = UserRegistrationData(
                email=f"user{i}@example.com",
                password="SecurePass123",
                first_name=f"User{i}",
                last_name="Test",
                role="buyer"
            )
            user_tasks.append(user_service.register_user(user_data))
        
        users = await asyncio.gather(*user_tasks)
        assert len(users) == 5
        
        # Verify all users have unique IDs and emails
        user_ids = [user.id for user in users]
        user_emails = [user.email for user in users]
        
        assert len(set(user_ids)) == 5  # All unique IDs
        assert len(set(user_emails)) == 5  # All unique emails
    
    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test that errors propagate correctly between services."""
        order_service = self.services["order_service"]
        
        # Try to add non-existent product to cart
        with pytest.raises(ValueError, match="not found"):
            await order_service.add_to_cart("user123", "nonexistent_product", 1)
        
        # Try to create order with non-existent cart
        shipping_address = Address(
            street="123 Main St",
            city="Anytown",
            state="CA",
            postal_code="12345",
            country="USA"
        )
        
        with pytest.raises(ValueError, match="Cart.*not found"):
            await order_service.create_order(
                "user123",
                "nonexistent_cart",
                shipping_address,
                "credit_card"
            )


class TestCompleteSystemIntegration:
    """Test complete system integration with all services working together."""
    
    @pytest.fixture(autouse=True)
    async def setup_services(self):
        """Setup services for integration tests."""
        # Clear any existing services and events
        service_registry._services.clear()
        service_registry._dependencies.clear()
        event_bus._handlers.clear()
        event_bus._event_history.clear()
        
        # Initialize all services
        self.services = initialize_services(use_database=False)
        
        yield
        
        # Cleanup after tests
        event_bus._event_history.clear()
    
    @pytest.mark.asyncio
    async def test_complete_marketplace_flow(self):
        """Test complete marketplace flow with multiple vendors and buyers."""
        # Get services
        user_service = self.services["user_service"]
        product_service = self.services["product_service"]
        order_service = self.services["order_service"]
        search_service = self.services["search_service"]
        notification_service = self.services["notification_service"]
        
        # 1. Register multiple users
        buyers = []
        sellers = []
        
        for i in range(2):
            buyer_data = UserRegistrationData(
                email=f"buyer{i}@marketplace.com",
                password="SecurePass123",
                first_name=f"Buyer{i}",
                last_name="Test",
                role="buyer"
            )
            buyer = await user_service.register_user(buyer_data)
            buyers.append(buyer)
        
        for i in range(3):
            seller_data = UserRegistrationData(
                email=f"seller{i}@marketplace.com",
                password="SecurePass123",
                first_name=f"Seller{i}",
                last_name="Test",
                role="seller"
            )
            seller = await user_service.register_user(seller_data)
            sellers.append(seller)
        
        assert len(buyers) == 2
        assert len(sellers) == 3
        
        # 2. Create products from different sellers
        products = []
        categories = ["Electronics", "Books", "Clothing"]
        
        for i, seller in enumerate(sellers):
            for j in range(2):
                product_data = ProductCreationData(
                    seller_id=seller.id,
                    name=f"Product {i}-{j}",
                    description=f"Product {j} from seller {i}",
                    price=Decimal(f"{10 + i * 5 + j}.99"),
                    currency="USD",
                    category=categories[i],
                    inventory_quantity=50,
                    low_stock_threshold=5
                )
                product = await product_service.create_product(product_data)
                products.append(product)
        
        assert len(products) == 6  # 3 sellers * 2 products each
        
        # 3. Test search functionality
        all_results = await search_service.search_products("")
        assert len(all_results.products) == 6
        
        electronics_results = await search_service.search_products("", {"category": "Electronics"})
        assert len(electronics_results.products) == 2
        
        # 4. Create orders from multiple buyers
        orders = []
        
        for buyer_idx, buyer in enumerate(buyers):
            # Each buyer orders from different sellers
            for product_idx in range(2):
                product = products[buyer_idx * 2 + product_idx]
                
                # Add to cart
                cart = await order_service.add_to_cart(buyer.id, product.id, 1)
                
                # Create order
                shipping_address = Address(
                    street=f"{100 + buyer_idx} Buyer St",
                    city="Marketplace City",
                    state="MC",
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
        
        assert len(orders) == 4  # 2 buyers * 2 orders each
        
        # 5. Verify inventory was reduced
        for i, product in enumerate(products[:4]):  # First 4 products were ordered
            updated_product = await product_service.get_product_by_id(product.id)
            assert updated_product.inventory.quantity == 49  # 50 - 1
        
        # 6. Process orders through fulfillment
        for order in orders:
            await order_service.update_order_status(order.id, "processing")
            await order_service.update_order_status(order.id, "shipped")
            await order_service.update_order_status(order.id, "delivered")
        
        # 7. Verify events were published
        events = event_bus.get_event_history()
        event_types = [e.type for e in events]
        
        assert EventType.USER_REGISTERED in event_types
        assert EventType.PRODUCT_CREATED in event_types
        assert EventType.ORDER_CREATED in event_types
        assert EventType.PAYMENT_COMPLETED in event_types
        assert EventType.ORDER_SHIPPED in event_types
        assert EventType.ORDER_DELIVERED in event_types
        
        # Count specific events
        user_events = event_bus.get_event_history(EventType.USER_REGISTERED)
        product_events = event_bus.get_event_history(EventType.PRODUCT_CREATED)
        order_events = event_bus.get_event_history(EventType.ORDER_CREATED)
        
        assert len(user_events) == 5  # 2 buyers + 3 sellers
        assert len(product_events) == 6  # 6 products
        assert len(order_events) == 4  # 4 orders
        
        # 8. Verify notifications were sent
        for buyer in buyers:
            notifications = await notification_service.get_user_notifications(buyer.id)
            assert len(notifications) >= 2  # Welcome + order notifications
        
        for seller in sellers:
            notifications = await notification_service.get_user_notifications(seller.id)
            assert len(notifications) >= 1  # Welcome notification at minimum
    
    @pytest.mark.asyncio
    async def test_inventory_management_integration(self):
        """Test comprehensive inventory management across services."""
        # Get services
        user_service = self.services["user_service"]
        product_service = self.services["product_service"]
        order_service = self.services["order_service"]
        notification_service = self.services["notification_service"]
        
        # Create seller and buyer
        seller_data = UserRegistrationData(
            email="inventory_seller@test.com",
            password="SecurePass123",
            first_name="Inventory",
            last_name="Seller",
            role="seller"
        )
        seller = await user_service.register_user(seller_data)
        
        buyer_data = UserRegistrationData(
            email="inventory_buyer@test.com",
            password="SecurePass123",
            first_name="Inventory",
            last_name="Buyer",
            role="buyer"
        )
        buyer = await user_service.register_user(buyer_data)
        
        # Create product with specific inventory levels
        product_data = ProductCreationData(
            seller_id=seller.id,
            name="Inventory Test Product",
            description="Product for inventory testing",
            price=Decimal("15.00"),
            currency="USD",
            category="Test",
            inventory_quantity=10,
            low_stock_threshold=3
        )
        product = await product_service.create_product(product_data)
        
        # Test 1: Normal order - should reduce inventory
        cart1 = await order_service.add_to_cart(buyer.id, product.id, 5)
        
        shipping_address = Address(
            street="123 Inventory St",
            city="Test City",
            state="TC",
            postal_code="12345",
            country="USA"
        )
        
        order1 = await order_service.create_order(
            buyer.id,
            cart1.id,
            shipping_address,
            "credit_card"
        )
        
        # Verify inventory reduced
        updated_product = await product_service.get_product_by_id(product.id)
        assert updated_product.inventory.quantity == 5  # 10 - 5
        
        # Test 2: Order that triggers low stock alert
        cart2 = await order_service.add_to_cart(buyer.id, product.id, 3)
        order2 = await order_service.create_order(
            buyer.id,
            cart2.id,
            shipping_address,
            "credit_card"
        )
        
        # Verify low stock triggered
        updated_product = await product_service.get_product_by_id(product.id)
        assert updated_product.inventory.quantity == 2  # 5 - 3 (below threshold of 3)
        
        # Check for low inventory event
        low_stock_events = event_bus.get_event_history(EventType.PRODUCT_INVENTORY_LOW)
        assert len(low_stock_events) >= 1
        
        # Verify seller received low stock notification
        seller_notifications = await notification_service.get_user_notifications(seller.id)
        low_stock_notifications = [n for n in seller_notifications if "Low Inventory" in n.subject]
        assert len(low_stock_notifications) >= 1
        
        # Test 3: Try to order more than available (should be limited)
        cart3 = await order_service.add_to_cart(buyer.id, product.id, 5)  # Only 2 available
        
        # Cart should limit to available quantity
        assert cart3.items[0].quantity == 2  # Should be limited to available stock
        
        # Test 4: Order remaining inventory to trigger out of stock
        order3 = await order_service.create_order(
            buyer.id,
            cart3.id,
            shipping_address,
            "credit_card"
        )
        
        # Verify out of stock
        updated_product = await product_service.get_product_by_id(product.id)
        assert updated_product.inventory.quantity == 0
        assert updated_product.status == "out_of_stock"
        
        # Check for out of stock event
        out_of_stock_events = event_bus.get_event_history(EventType.PRODUCT_OUT_OF_STOCK)
        assert len(out_of_stock_events) >= 1
    
    @pytest.mark.asyncio
    async def test_payment_integration_scenarios(self):
        """Test payment integration with different scenarios."""
        # Get services
        user_service = self.services["user_service"]
        product_service = self.services["product_service"]
        order_service = self.services["order_service"]
        payment_service = self.services["payment_service"]
        
        # Create users and product
        seller_data = UserRegistrationData(
            email="payment_seller@test.com",
            password="SecurePass123",
            first_name="Payment",
            last_name="Seller",
            role="seller"
        )
        seller = await user_service.register_user(seller_data)
        
        buyer_data = UserRegistrationData(
            email="payment_buyer@test.com",
            password="SecurePass123",
            first_name="Payment",
            last_name="Buyer",
            role="buyer"
        )
        buyer = await user_service.register_user(buyer_data)
        
        product_data = ProductCreationData(
            seller_id=seller.id,
            name="Payment Test Product",
            description="Product for payment testing",
            price=Decimal("50.00"),
            currency="USD",
            category="Test",
            inventory_quantity=20,
            low_stock_threshold=2
        )
        product = await product_service.create_product(product_data)
        
        # Test 1: Successful payment flow
        cart = await order_service.add_to_cart(buyer.id, product.id, 2)
        
        shipping_address = Address(
            street="123 Payment St",
            city="Payment City",
            state="PC",
            postal_code="12345",
            country="USA"
        )
        
        # Create order with valid payment
        order = await order_service.create_order(
            buyer.id,
            cart.id,
            shipping_address,
            "credit_card"
        )
        
        assert order.status == "confirmed"
        assert order.total_amount == Decimal("100.00")  # 2 * 50.00
        
        # Verify payment completed event
        payment_events = event_bus.get_event_history(EventType.PAYMENT_COMPLETED)
        assert len(payment_events) >= 1
        
        # Test 2: Payment failure scenario
        from src.services.payments.service import PaymentData, PaymentMethod
        
        # Create invalid payment data
        invalid_payment_data = PaymentData(
            order_id="test_order_fail",
            amount=Decimal("100.00"),
            currency="USD",
            payment_method=PaymentMethod(
                type="credit_card",
                card_number="0000000000000000",  # Invalid card
                expiry_month=12,
                expiry_year=2025,
                cvv="000"
            ),
            billing_address=shipping_address
        )
        
        # Process payment - should fail
        result = await payment_service.process_payment(invalid_payment_data)
        assert not result.success
        assert result.error_message is not None
        
        # Verify payment failed event
        payment_failed_events = event_bus.get_event_history(EventType.PAYMENT_FAILED)
        assert len(payment_failed_events) >= 1
    
    @pytest.mark.asyncio
    async def test_business_flow_scenarios(self):
        """Test the business flow scenarios from service factory."""
        from src.shared.service_factory import create_business_flow_test_scenario
        
        run_complete_flow, run_multi_vendor = create_business_flow_test_scenario()
        
        # Test complete order flow scenario
        result1 = await run_complete_flow()
        assert result1["buyer"] is not None
        assert result1["seller"] is not None
        assert result1["product"] is not None
        assert result1["order"] is not None
        assert result1["buyer_notifications"] >= 0
        assert result1["seller_notifications"] >= 0
        
        # Test multi-vendor scenario
        result2 = await run_multi_vendor()
        assert len(result2["sellers"]) == 3
        assert len(result2["products"]) == 6
        assert len(result2["orders"]) == 3
        assert result2["buyer"] is not None
        
        # Verify cross-vendor orders have different sellers
        seller_ids = {order.seller_id for order in result2["orders"]}
        assert len(seller_ids) == 3  # All different sellers
    
    @pytest.mark.asyncio
    async def test_service_communication_reliability(self):
        """Test that service communication is reliable under various conditions."""
        # Get services
        user_service = self.services["user_service"]
        product_service = self.services["product_service"]
        order_service = self.services["order_service"]
        
        # Test concurrent user registrations
        user_tasks = []
        for i in range(10):
            user_data = UserRegistrationData(
                email=f"concurrent_user{i}@test.com",
                password="SecurePass123",
                first_name=f"User{i}",
                last_name="Concurrent",
                role="buyer" if i % 2 == 0 else "seller"
            )
            user_tasks.append(user_service.register_user(user_data))
        
        users = await asyncio.gather(*user_tasks)
        assert len(users) == 10
        
        # Verify all users have unique IDs
        user_ids = [user.id for user in users]
        assert len(set(user_ids)) == 10
        
        # Test concurrent product creation
        sellers = [user for user in users if user.role == "seller"]
        product_tasks = []
        
        for i, seller in enumerate(sellers):
            product_data = ProductCreationData(
                seller_id=seller.id,
                name=f"Concurrent Product {i}",
                description=f"Product {i} created concurrently",
                price=Decimal(f"{20 + i}.99"),
                currency="USD",
                category="Test",
                inventory_quantity=25,
                low_stock_threshold=3
            )
            product_tasks.append(product_service.create_product(product_data))
        
        products = await asyncio.gather(*product_tasks)
        assert len(products) == len(sellers)
        
        # Verify all products have unique IDs
        product_ids = [product.id for product in products]
        assert len(set(product_ids)) == len(products)
        
        # Test that events were properly published for all operations
        user_events = event_bus.get_event_history(EventType.USER_REGISTERED)
        product_events = event_bus.get_event_history(EventType.PRODUCT_CREATED)
        
        assert len(user_events) >= 10
        assert len(product_events) >= len(sellers)