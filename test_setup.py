#!/usr/bin/env python3
"""Test script to verify project setup and dependencies."""

import sys
import traceback


def test_imports():
    """Test that all services can be imported."""
    print("Testing service imports...")
    
    try:
        from src.services.users import UserService, user_config
        print("✓ User service imported successfully")
        
        from src.services.products import ProductService, product_config
        print("✓ Product service imported successfully")
        
        from src.services.orders import OrderService, order_config
        print("✓ Order service imported successfully")
        
        from src.services.payments import PaymentService, payment_config
        print("✓ Payment service imported successfully")
        
        from src.services.notifications import NotificationService, notification_config
        print("✓ Notification service imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_service_initialization():
    """Test that all services can be initialized."""
    print("\nTesting service initialization...")
    
    try:
        from src.services.users import UserService
        user_service = UserService()
        print("✓ User service initialized successfully")
        
        from src.services.products import ProductService
        product_service = ProductService()
        print("✓ Product service initialized successfully")
        
        from src.services.orders import OrderService
        order_service = OrderService()
        print("✓ Order service initialized successfully")
        
        from src.services.payments import PaymentService
        payment_service = PaymentService()
        print("✓ Payment service initialized successfully")
        
        from src.services.notifications import NotificationService
        notification_service = NotificationService()
        print("✓ Notification service initialized successfully")
        
        return True
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        traceback.print_exc()
        return False


def test_model_creation():
    """Test that models can be created with valid data."""
    print("\nTesting model creation...")
    
    try:
        from src.services.users import UserRegistrationData
        user_data = UserRegistrationData(
            email="test@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
            role="buyer"
        )
        print("✓ User model created successfully")
        
        from src.services.products import ProductCreationData
        from decimal import Decimal
        product_data = ProductCreationData(
            name="Test Product",
            description="A comprehensive test product description",
            price=Decimal("99.99"),
            currency="USD",
            category="electronics",
            inventory_quantity=10
        )
        print("✓ Product model created successfully")
        
        from src.services.orders import CartItem
        cart_item = CartItem(
            product_id="test-product-id",
            quantity=2,
            unit_price=Decimal("99.99"),
            total_price=Decimal("199.98")
        )
        print("✓ Order model created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        traceback.print_exc()
        return False


def test_testing_framework():
    """Test that testing framework is properly configured."""
    print("\nTesting framework setup...")
    
    try:
        import pytest
        print("✓ Pytest imported successfully")
        
        import hypothesis
        print("✓ Hypothesis imported successfully")
        
        from tests.test_config import TestDataFactory, PropertyTestUtils
        print("✓ Test configuration imported successfully")
        
        # Test data factory
        user_data = TestDataFactory.create_user_data()
        assert user_data["email"] == "test@example.com"
        print("✓ Test data factory working")
        
        return True
    except Exception as e:
        print(f"✗ Testing framework setup failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all setup tests."""
    print("=" * 60)
    print("MARKETPLACE PLATFORM - PROJECT SETUP VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_service_initialization,
        test_model_creation,
        test_testing_framework,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ Project setup completed successfully!")
        print("✓ All microservices structure configured")
        print("✓ All dependencies properly installed")
        print("✓ Testing framework ready for property-based testing")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())