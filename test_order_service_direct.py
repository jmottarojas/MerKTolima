#!/usr/bin/env python3
"""
Test script to test order service directly.
"""

import asyncio
from decimal import Decimal
from datetime import datetime
from src.services.orders.service import OrderService
from src.services.orders.repository import InMemoryOrderRepository
from src.services.products.service import ProductService, Product
from src.services.payments.service import PaymentService, PaymentMethod, PaymentMethodType
from src.services.payments.repository import InMemoryPaymentRepository
from src.shared.models import Address

async def test_order_service_direct():
    """Test order service directly."""
    
    print("🧪 TESTING ORDER SERVICE DIRECTLY")
    print("="*60)
    
    # Create services
    order_repo = InMemoryOrderRepository()
    payment_repo = InMemoryPaymentRepository()
    product_service = ProductService()
    payment_service = PaymentService(payment_repo)
    order_service = OrderService(order_repo, product_service, payment_service)
    
    # Create a test product
    print("1. Creating test product...")
    
    product = Product(
        id="test-product-123",
        seller_id="seller-123",
        name="Test Product",
        description="Test product for order",
        price=Decimal("100000"),
        currency="COP",
        category="Electrónicos",
        images=["https://via.placeholder.com/400x300"],
        inventory_quantity=10,
        low_stock_threshold=2,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Add product to product service (simulate creation)
    product_service._products[product.id] = product
    print(f"   ✅ Product created: {product.id}")
    
    # Create a cart and add item
    print("\n2. Adding item to cart...")
    user_id = "buyer-123"
    cart = await order_service.add_to_cart(user_id, product.id, 2)
    print(f"   ✅ Cart created: {cart.id}")
    print(f"   ✅ Cart total: {cart.total_amount}")
    
    # Create shipping address
    print("\n3. Creating shipping address...")
    shipping_address = Address(
        street="Calle 123 #45-67",
        city="Bogotá",
        state="Cundinamarca",
        postal_code="110111",
        country="Colombia"
    )
    print(f"   ✅ Shipping address created")
    
    # Create payment method
    print("\n4. Creating payment method...")
    payment_method = PaymentMethod(
        type=PaymentMethodType.CARD,
        details={
            "card_number": "4000000000000002",
            "expiry_month": 12,
            "expiry_year": 2027,
            "cvv": "123",
            "cardholder_name": "Test User"
        }
    )
    print(f"   ✅ Payment method created")
    
    # Test payment method validation
    print("\n5. Testing payment method validation...")
    is_valid = await payment_service.validate_payment_method(payment_method)
    print(f"   Validation result: {is_valid}")
    
    if not is_valid:
        print("   ❌ Payment method validation failed - stopping test")
        return
    
    # Create order
    print("\n6. Creating order...")
    try:
        order = await order_service.create_order(
            user_id=user_id,
            cart_id=cart.id,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        
        print(f"   ✅ Order created successfully!")
        print(f"   ✅ Order ID: {order.id}")
        print(f"   ✅ Order status: {order.status}")
        print(f"   ✅ Total amount: {order.total_amount}")
        print(f"   ✅ Payment status: {order.payment_info.payment_status}")
        
    except Exception as e:
        print(f"   ❌ Order creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_order_service_direct())