"""API integration tests."""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"


def test_api_info_endpoint(client: TestClient):
    """Test API info endpoint."""
    response = client.get("/api/v1")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data


class TestUserEndpoints:
    """Test user-related endpoints."""
    
    def test_user_registration_flow(self, client: TestClient):
        """Test complete user registration flow."""
        # Register a new user
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "buyer"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 200
        
        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["role"] == user_data["role"]
        assert user["first_name"] == user_data["first_name"]
        assert user["last_name"] == user_data["last_name"]
        assert "id" in user
        
        return user
    
    def test_user_login_flow(self, client: TestClient):
        """Test user login flow."""
        # First register a user
        user_data = {
            "email": "login@example.com",
            "password": "TestPass123",
            "first_name": "Login",
            "last_name": "User",
            "role": "seller"
        }
        
        register_response = client.post("/api/v1/users/register", json=user_data)
        assert register_response.status_code == 200
        
        # Then login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/v1/users/login", json=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert "expires_in" in token_data
        
        return token_data["access_token"]
    
    def test_user_profile_operations(self, client: TestClient):
        """Test user profile get and update operations."""
        # Register and login
        user_data = {
            "email": "profile@example.com",
            "password": "TestPass123",
            "first_name": "Profile",
            "last_name": "User",
            "role": "buyer"
        }
        
        client.post("/api/v1/users/register", json=user_data)
        
        login_response = client.post("/api/v1/users/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get profile
        profile_response = client.get("/api/v1/users/profile", headers=headers)
        assert profile_response.status_code == 200
        
        profile = profile_response.json()
        assert profile["email"] == user_data["email"]
        assert profile["first_name"] == user_data["first_name"]
        
        # Update profile
        update_data = {
            "first_name": "Updated",
            "phone": "+1234567890"
        }
        
        update_response = client.put("/api/v1/users/profile", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        updated_profile = update_response.json()
        assert updated_profile["first_name"] == "Updated"
        assert updated_profile["phone"] == "+1234567890"
    
    def test_authentication_required(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        # Try to access profile without token
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 401
        
        # Try with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/profile", headers=headers)
        assert response.status_code == 401


class TestProductEndpoints:
    """Test product-related endpoints."""
    
    def setup_seller_auth(self, client: TestClient):
        """Helper to create seller and get auth token."""
        user_data = {
            "email": "seller@example.com",
            "password": "TestPass123",
            "first_name": "Seller",
            "last_name": "User",
            "role": "seller"
        }
        
        client.post("/api/v1/users/register", json=user_data)
        
        login_response = client.post("/api/v1/users/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_product_crud_flow(self, client: TestClient):
        """Test complete product CRUD flow."""
        headers = self.setup_seller_auth(client)
        
        # Create product
        product_data = {
            "name": "Test Product",
            "description": "A test product for integration testing",
            "price": "29.99",
            "category": "Electronics",
            "inventory_quantity": 100,
            "low_stock_threshold": 10
        }
        
        create_response = client.post("/api/v1/products/", json=product_data, headers=headers)
        assert create_response.status_code == 200
        
        product = create_response.json()
        assert product["name"] == product_data["name"]
        assert product["price"] == product_data["price"]
        assert product["status"] == "active"
        product_id = product["id"]
        
        # Get product
        get_response = client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 200
        
        retrieved_product = get_response.json()
        assert retrieved_product["id"] == product_id
        assert retrieved_product["name"] == product_data["name"]
        
        # Update product
        update_data = {
            "name": "Updated Product",
            "price": "39.99"
        }
        
        update_response = client.put(f"/api/v1/products/{product_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        updated_product = update_response.json()
        assert updated_product["name"] == "Updated Product"
        assert updated_product["price"] == "39.99"
        
        # Delete product
        delete_response = client.delete(f"/api/v1/products/{product_id}", headers=headers)
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted_response = client.get(f"/api/v1/products/{product_id}")
        assert get_deleted_response.status_code == 404
    
    def test_product_search(self, client: TestClient):
        """Test product search functionality."""
        headers = self.setup_seller_auth(client)
        
        # Create multiple products
        products = [
            {
                "name": "iPhone 15",
                "description": "Latest Apple smartphone",
                "price": "999.99",
                "category": "Electronics",
                "inventory_quantity": 50
            },
            {
                "name": "Samsung Galaxy",
                "description": "Android smartphone",
                "price": "799.99",
                "category": "Electronics",
                "inventory_quantity": 30
            },
            {
                "name": "Coffee Mug",
                "description": "Ceramic coffee mug",
                "price": "15.99",
                "category": "Home",
                "inventory_quantity": 100
            }
        ]
        
        for product_data in products:
            client.post("/api/v1/products/", json=product_data, headers=headers)
        
        # Search by term
        search_response = client.get("/api/v1/products/search?term=phone")
        assert search_response.status_code == 200
        
        search_results = search_response.json()
        assert search_results["total_count"] >= 2
        assert len(search_results["products"]) >= 2
        
        # Search by category
        category_response = client.get("/api/v1/products/search?category=Electronics")
        assert category_response.status_code == 200
        
        category_results = category_response.json()
        assert category_results["total_count"] >= 2
        
        # Search with price filter
        price_response = client.get("/api/v1/products/search?min_price=500&max_price=1000")
        assert price_response.status_code == 200
        
        price_results = price_response.json()
        for product in price_results["products"]:
            price = float(product["price"])
            assert 500 <= price <= 1000


class TestOrderEndpoints:
    """Test order and cart-related endpoints."""
    
    def setup_buyer_and_seller(self, client: TestClient):
        """Helper to create buyer, seller, and product."""
        # Create seller
        seller_data = {
            "email": "seller@orders.com",
            "password": "TestPass123",
            "first_name": "Seller",
            "last_name": "User",
            "role": "seller"
        }
        client.post("/api/v1/users/register", json=seller_data)
        
        seller_login = client.post("/api/v1/users/login", json={
            "email": seller_data["email"],
            "password": seller_data["password"]
        })
        seller_token = seller_login.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # Create buyer
        buyer_data = {
            "email": "buyer@orders.com",
            "password": "TestPass123",
            "first_name": "Buyer",
            "last_name": "User",
            "role": "buyer"
        }
        client.post("/api/v1/users/register", json=buyer_data)
        
        buyer_login = client.post("/api/v1/users/login", json={
            "email": buyer_data["email"],
            "password": buyer_data["password"]
        })
        buyer_token = buyer_login.json()["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
        
        # Create product
        product_data = {
            "name": "Order Test Product",
            "description": "Product for order testing",
            "price": "49.99",
            "category": "Test",
            "inventory_quantity": 10
        }
        
        product_response = client.post("/api/v1/products/", json=product_data, headers=seller_headers)
        product = product_response.json()
        
        return buyer_headers, seller_headers, product["id"]
    
    def test_cart_operations(self, client: TestClient):
        """Test cart operations."""
        buyer_headers, seller_headers, product_id = self.setup_buyer_and_seller(client)
        
        # Add to cart
        add_to_cart_data = {
            "product_id": product_id,
            "quantity": 2
        }
        
        add_response = client.post("/api/v1/orders/cart/items", json=add_to_cart_data, headers=buyer_headers)
        assert add_response.status_code == 200
        
        cart = add_response.json()
        assert len(cart["items"]) == 1
        assert cart["items"][0]["product_id"] == product_id
        assert cart["items"][0]["quantity"] == 2
        
        # Get cart
        get_cart_response = client.get("/api/v1/orders/cart", headers=buyer_headers)
        assert get_cart_response.status_code == 200
        
        retrieved_cart = get_cart_response.json()
        assert retrieved_cart["id"] == cart["id"]
        
        # Update cart item
        update_data = {"quantity": 3}
        update_response = client.put(f"/api/v1/orders/cart/items/{product_id}", json=update_data, headers=buyer_headers)
        assert update_response.status_code == 200
        
        updated_cart = update_response.json()
        assert updated_cart["items"][0]["quantity"] == 3
        
        # Remove from cart
        remove_response = client.delete(f"/api/v1/orders/cart/items/{product_id}", headers=buyer_headers)
        assert remove_response.status_code == 200
        
        empty_cart = remove_response.json()
        assert len(empty_cart["items"]) == 0
    
    def test_order_creation_flow(self, client: TestClient):
        """Test order creation flow."""
        buyer_headers, seller_headers, product_id = self.setup_buyer_and_seller(client)
        
        # Add item to cart
        add_to_cart_data = {
            "product_id": product_id,
            "quantity": 1
        }
        
        cart_response = client.post("/api/v1/orders/cart/items", json=add_to_cart_data, headers=buyer_headers)
        cart = cart_response.json()
        
        # Create order
        order_data = {
            "cart_id": cart["id"],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "Test State",
                "postal_code": "12345",
                "country": "Test Country"
            },
            "payment_method": "credit_card"
        }
        
        order_response = client.post("/api/v1/orders/", json=order_data, headers=buyer_headers)
        assert order_response.status_code == 200
        
        order = order_response.json()
        assert order["buyer_id"] is not None
        assert order["seller_id"] is not None
        assert len(order["items"]) == 1
        assert order["items"][0]["product_id"] == product_id
        assert order["status"] in ["pending", "confirmed"]
        assert "tracking_number" in order
        
        return order["id"]


class TestPaymentEndpoints:
    """Test payment-related endpoints."""
    
    def test_payment_method_validation(self, client: TestClient):
        """Test payment method validation."""
        # Create user and login
        user_data = {
            "email": "payment@example.com",
            "password": "TestPass123",
            "first_name": "Payment",
            "last_name": "User",
            "role": "buyer"
        }
        
        client.post("/api/v1/users/register", json=user_data)
        
        login_response = client.post("/api/v1/users/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test valid card
        valid_card = {
            "type": "card",
            "details": {
                "card_number": "4111111111111111",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
                "cardholder_name": "Test User"
            }
        }
        
        validation_response = client.post("/api/v1/payments/validate-method", json=valid_card, headers=headers)
        assert validation_response.status_code == 200
        
        validation_result = validation_response.json()
        assert validation_result["success"] is True
        
        # Test invalid card
        invalid_card = {
            "type": "card",
            "details": {
                "card_number": "invalid",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123",
                "cardholder_name": "Test User"
            }
        }
        
        invalid_response = client.post("/api/v1/payments/validate-method", json=invalid_card, headers=headers)
        assert invalid_response.status_code == 200
        
        invalid_result = invalid_response.json()
        assert invalid_result["success"] is False


class TestNotificationEndpoints:
    """Test notification-related endpoints."""
    
    def setup_user_auth(self, client: TestClient):
        """Helper to create user and get auth token."""
        user_data = {
            "email": "notifications@example.com",
            "password": "TestPass123",
            "first_name": "Notification",
            "last_name": "User",
            "role": "buyer"
        }
        
        client.post("/api/v1/users/register", json=user_data)
        
        login_response = client.post("/api/v1/users/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_notification_preferences(self, client: TestClient):
        """Test notification preferences management."""
        headers = self.setup_user_auth(client)
        
        # Get default preferences
        get_response = client.get("/api/v1/notifications/preferences", headers=headers)
        assert get_response.status_code == 200
        
        preferences = get_response.json()
        assert "email_enabled" in preferences
        assert "in_app_enabled" in preferences
        assert "channels" in preferences
        
        # Update preferences
        update_data = {
            "email_enabled": False,
            "in_app_enabled": True,
            "sms_enabled": False,
            "channels": {
                "order_updates": True,
                "price_alerts": False,
                "inventory_alerts": True,
                "marketing": False
            }
        }
        
        update_response = client.put("/api/v1/notifications/preferences", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        # Verify update
        verify_response = client.get("/api/v1/notifications/preferences", headers=headers)
        updated_preferences = verify_response.json()
        assert updated_preferences["email_enabled"] is False
        assert updated_preferences["channels"]["price_alerts"] is False
    
    def test_notification_history(self, client: TestClient):
        """Test notification history retrieval."""
        headers = self.setup_user_auth(client)
        
        # Send a notification
        notification_data = {
            "type": "in_app",
            "channel": "order_updates",
            "subject": "Test Notification",
            "content": "This is a test notification for integration testing"
        }
        
        send_response = client.post("/api/v1/notifications/send", json=notification_data, headers=headers)
        assert send_response.status_code == 200
        
        # Get notification history
        history_response = client.get("/api/v1/notifications/", headers=headers)
        assert history_response.status_code == 200
        
        notifications = history_response.json()
        assert isinstance(notifications, list)
        
        if len(notifications) > 0:
            notification = notifications[0]
            assert "id" in notification
            assert "subject" in notification
            assert "content" in notification
            assert "read" in notification


class TestEndToEndFlow:
    """Test complete end-to-end user flows."""
    
    def test_complete_marketplace_flow(self, client: TestClient):
        """Test complete marketplace flow from registration to order completion."""
        # 1. Register seller
        seller_data = {
            "email": "e2e_seller@example.com",
            "password": "TestPass123",
            "first_name": "E2E",
            "last_name": "Seller",
            "role": "seller"
        }
        
        seller_reg_response = client.post("/api/v1/users/register", json=seller_data)
        assert seller_reg_response.status_code == 200
        
        # 2. Login seller
        seller_login_response = client.post("/api/v1/users/login", json={
            "email": seller_data["email"],
            "password": seller_data["password"]
        })
        seller_token = seller_login_response.json()["access_token"]
        seller_headers = {"Authorization": f"Bearer {seller_token}"}
        
        # 3. Create product
        product_data = {
            "name": "E2E Test Product",
            "description": "End-to-end test product",
            "price": "99.99",
            "category": "Test",
            "inventory_quantity": 5
        }
        
        product_response = client.post("/api/v1/products/", json=product_data, headers=seller_headers)
        assert product_response.status_code == 200
        product = product_response.json()
        product_id = product["id"]
        
        # 4. Register buyer
        buyer_data = {
            "email": "e2e_buyer@example.com",
            "password": "TestPass123",
            "first_name": "E2E",
            "last_name": "Buyer",
            "role": "buyer"
        }
        
        buyer_reg_response = client.post("/api/v1/users/register", json=buyer_data)
        assert buyer_reg_response.status_code == 200
        
        # 5. Login buyer
        buyer_login_response = client.post("/api/v1/users/login", json={
            "email": buyer_data["email"],
            "password": buyer_data["password"]
        })
        buyer_token = buyer_login_response.json()["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
        
        # 6. Search for product
        search_response = client.get(f"/api/v1/products/search?term=E2E")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert search_results["total_count"] >= 1
        
        # 7. Add to cart
        add_to_cart_data = {
            "product_id": product_id,
            "quantity": 2
        }
        
        cart_response = client.post("/api/v1/orders/cart/items", json=add_to_cart_data, headers=buyer_headers)
        assert cart_response.status_code == 200
        cart = cart_response.json()
        
        # 8. Create order
        order_data = {
            "cart_id": cart["id"],
            "shipping_address": {
                "street": "123 E2E St",
                "city": "Test City",
                "state": "Test State",
                "postal_code": "12345",
                "country": "Test Country"
            },
            "payment_method": "credit_card"
        }
        
        order_response = client.post("/api/v1/orders/", json=order_data, headers=buyer_headers)
        assert order_response.status_code == 200
        order = order_response.json()
        
        # 9. Verify order details
        assert order["buyer_id"] is not None
        assert order["seller_id"] is not None
        assert len(order["items"]) == 1
        assert order["items"][0]["product_id"] == product_id
        assert order["items"][0]["quantity"] == 2
        assert "tracking_number" in order
        
        # 10. Get orders for buyer
        buyer_orders_response = client.get("/api/v1/orders/", headers=buyer_headers)
        assert buyer_orders_response.status_code == 200
        buyer_orders = buyer_orders_response.json()
        assert len(buyer_orders) >= 1
        
        # 11. Get orders for seller
        seller_orders_response = client.get("/api/v1/orders/", headers=seller_headers)
        assert seller_orders_response.status_code == 200
        seller_orders = seller_orders_response.json()
        assert len(seller_orders) >= 1