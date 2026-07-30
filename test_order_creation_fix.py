#!/usr/bin/env python3
"""
Test script to verify order creation fix.
"""

import requests
import json

def test_order_creation():
    """Test the order creation flow."""
    
    print("🧪 TESTING ORDER CREATION FIX")
    print("="*60)
    
    # Test data
    base_url = "http://localhost:8000"
    
    # 1. Login as seller to create a product
    print("1. Logging in as seller to create test product...")
    login_data = {
        "email": "seller@test.com",
        "password": "Password123"
    }
    
    login_response = requests.post(f"{base_url}/api/v1/users/login", json=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Seller login failed: {login_response.text}")
        return
    
    seller_token = login_response.json().get("access_token")
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    
    # Create a test product
    print("   Creating test product...")
    product_data = {
        "name": "Test Product for Order",
        "description": "Test product for order creation",
        "price": 100000,
        "currency": "COP",
        "category": "Electrónicos",
        "images": ["https://via.placeholder.com/400x300"],
        "inventory_quantity": 10,
        "low_stock_threshold": 2
    }
    
    product_response = requests.post(f"{base_url}/api/v1/products/", 
                                   json=product_data, headers=seller_headers)
    print(f"   Product creation status: {product_response.status_code}")
    
    if product_response.status_code != 200:
        print(f"   ❌ Product creation failed: {product_response.text}")
        return
    
    product = product_response.json()
    product_id = product.get('id')
    print(f"   ✅ Test product created: {product_id}")
    
    # 2. Login as buyer to get token
    print("\n2. Logging in as buyer...")
    buyer_login_data = {
        "email": "buyer@test.com",
        "password": "Password123"
    }
    
    buyer_login_response = requests.post(f"{base_url}/api/v1/users/login", json=buyer_login_data)
    print(f"   Login status: {buyer_login_response.status_code}")
    
    if buyer_login_response.status_code != 200:
        print(f"   ❌ Buyer login failed: {buyer_login_response.text}")
        return
    
    token = buyer_login_response.json().get("access_token")
    print(f"   ✅ Token obtained: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Add product to cart
    print("\n3. Adding product to cart...")
    add_to_cart_data = {
        "product_id": product_id,
        "quantity": 2
    }
    
    add_response = requests.post(f"{base_url}/api/v1/orders/cart/items", 
                               json=add_to_cart_data, headers=headers)
    print(f"   Add to cart status: {add_response.status_code}")
    print(f"   Add to cart response: {add_response.text}")
    
    if add_response.status_code != 200:
        print(f"   ❌ Failed to add product to cart")
        return
    
    cart_data = add_response.json()
    print(f"   ✅ Cart ID: {cart_data.get('id')}")
    print(f"   ✅ Cart items: {len(cart_data.get('items', []))}")
    print(f"   ✅ Cart total: {cart_data.get('total_amount', 0)}")
    
    # 4. Create order
    print("\n4. Creating order...")
    order_data = {
        "cart_id": cart_data.get('id'),
        "shipping_address": {
            "street": "Calle 123 #45-67",
            "city": "Bogotá",
            "state": "Cundinamarca",
            "postal_code": "110111",
            "country": "Colombia"
        },
        "payment_method": "credit_card"
    }
    
    print(f"   Order data: {json.dumps(order_data, indent=2)}")
    
    order_response = requests.post(f"{base_url}/api/v1/orders/", json=order_data, headers=headers)
    print(f"   Order status: {order_response.status_code}")
    print(f"   Order response: {order_response.text}")
    
    if order_response.status_code == 200:
        order = order_response.json()
        print(f"   ✅ Order created successfully!")
        print(f"   ✅ Order ID: {order.get('id')}")
        print(f"   ✅ Order status: {order.get('status')}")
        print(f"   ✅ Total amount: {order.get('total_amount')}")
        print(f"   ✅ Payment status: {order.get('payment_info', {}).get('payment_status')}")
    else:
        print(f"   ❌ Order creation failed")
        try:
            error_detail = order_response.json()
            print(f"   ❌ Error detail: {error_detail}")
        except:
            print(f"   ❌ Raw error: {order_response.text}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_order_creation()