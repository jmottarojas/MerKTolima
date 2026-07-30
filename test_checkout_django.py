#!/usr/bin/env python3
"""
Test script to test checkout through Django interface.
"""

import requests
import json

def test_django_checkout():
    """Test checkout through Django."""
    
    print("🧪 TESTING DJANGO CHECKOUT")
    print("="*60)
    
    # Test data
    django_url = "http://localhost:8001"
    
    # Create session
    session = requests.Session()
    
    # 1. Login to Django
    print("1. Logging in to Django...")
    
    # Get login page to get CSRF token
    login_page = session.get(f"{django_url}/login/")
    print(f"   Login page status: {login_page.status_code}")
    
    # Extract CSRF token
    csrf_token = None
    for line in login_page.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    if not csrf_token:
        print("   ❌ Could not find CSRF token")
        return
    
    print(f"   ✅ CSRF token: {csrf_token[:20]}...")
    
    # Login
    login_data = {
        'email': 'buyer@test.com',
        'password': 'Password123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(f"{django_url}/login/", data=login_data)
    print(f"   Login response status: {login_response.status_code}")
    
    if login_response.status_code != 200 or 'Bienvenido' not in login_response.text:
        print(f"   ❌ Login failed")
        return
    
    print(f"   ✅ Login successful")
    
    # 2. Add product to cart (we need a product first)
    print("\n2. Adding product to cart...")
    
    # Get home page to find products
    home_page = session.get(f"{django_url}/")
    print(f"   Home page status: {home_page.status_code}")
    
    # Try to find a product ID in the page
    product_id = None
    for line in home_page.text.split('\n'):
        if '/products/' in line and '/detail/' in line:
            # Extract product ID from URL like /products/abc123/detail/
            parts = line.split('/products/')[1].split('/detail/')[0]
            if parts:
                product_id = parts
                break
    
    if not product_id:
        print("   ❌ No products found on home page")
        print("   Trying to create a test product first...")
        
        # Try to access seller dashboard to create a product
        seller_login_data = {
            'email': 'seller@test.com',
            'password': 'Password123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        # Logout first
        session.get(f"{django_url}/logout/")
        
        # Login as seller
        login_page = session.get(f"{django_url}/login/")
        csrf_token = None
        for line in login_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        seller_login_data['csrfmiddlewaretoken'] = csrf_token
        session.post(f"{django_url}/login/", data=seller_login_data)
        
        # Try to create a simple product via API
        print("   Creating test product via API...")
        
        # Login to API as seller
        api_login = requests.post("http://localhost:8000/api/v1/users/login", json={
            "email": "seller@test.com",
            "password": "Password123"
        })
        
        if api_login.status_code == 200:
            token = api_login.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            product_data = {
                "name": "Test Product for Checkout",
                "description": "Test product for checkout testing",
                "price": 50000,
                "currency": "COP",
                "category": "Electrónicos",
                "images": ["https://via.placeholder.com/400x300"],
                "inventory_quantity": 10,
                "low_stock_threshold": 2
            }
            
            product_response = requests.post("http://localhost:8000/api/v1/products/", 
                                           json=product_data, headers=headers)
            
            if product_response.status_code == 200:
                product = product_response.json()
                product_id = product.get('id')
                print(f"   ✅ Created test product: {product_id}")
            else:
                print(f"   ❌ Failed to create product: {product_response.text}")
                return
        else:
            print(f"   ❌ Failed to login to API as seller")
            return
        
        # Login back as buyer
        session.get(f"{django_url}/logout/")
        login_page = session.get(f"{django_url}/login/")
        csrf_token = None
        for line in login_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        buyer_login_data = {
            'email': 'buyer@test.com',
            'password': 'Password123',
            'csrfmiddlewaretoken': csrf_token
        }
        session.post(f"{django_url}/login/", data=buyer_login_data)
    
    print(f"   ✅ Using product ID: {product_id}")
    
    # Get product detail page to get CSRF token
    product_page = session.get(f"{django_url}/producto/{product_id}/")
    print(f"   Product page status: {product_page.status_code}")
    
    # Extract CSRF token from product page
    csrf_token = None
    for line in product_page.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    if not csrf_token:
        print("   ❌ Could not find CSRF token on product page")
        return
    
    # Add to cart
    add_to_cart_data = {
        'quantity': 1,
        'csrfmiddlewaretoken': csrf_token
    }
    
    add_response = session.post(f"{django_url}/carrito/agregar/{product_id}/", data=add_to_cart_data)
    print(f"   Add to cart status: {add_response.status_code}")
    
    if add_response.status_code != 200:
        print(f"   ❌ Failed to add to cart")
        return
    
    print(f"   ✅ Product added to cart")
    
    # 3. Go to checkout
    print("\n3. Testing checkout...")
    
    checkout_page = session.get(f"{django_url}/checkout/")
    print(f"   Checkout page status: {checkout_page.status_code}")
    
    if checkout_page.status_code != 200:
        print(f"   ❌ Checkout page failed: {checkout_page.text[:500]}")
        return
    
    print(f"   ✅ Checkout page loaded")
    
    # Extract CSRF token from checkout page
    csrf_token = None
    for line in checkout_page.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    if not csrf_token:
        print("   ❌ Could not find CSRF token on checkout page")
        return
    
    # Submit checkout form
    checkout_data = {
        'street': 'Calle 123 #45-67',
        'city': 'Bogotá',
        'state': 'Cundinamarca',
        'postal_code': '110111',
        'country': 'Colombia',
        'phone': '3001234567',
        'payment_method': 'credit_card',
        'card_number': '4111111111111111',
        'card_holder': 'Test User',
        'expiry_date': '12/27',
        'cvv': '123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    print(f"   Submitting checkout form...")
    checkout_response = session.post(f"{django_url}/checkout/", data=checkout_data)
    print(f"   Checkout response status: {checkout_response.status_code}")
    print(f"   Checkout response URL: {checkout_response.url}")
    
    if 'error' in checkout_response.text.lower() or 'Error' in checkout_response.text:
        print(f"   ❌ Checkout failed - found error in response")
        # Look for specific error messages
        for line in checkout_response.text.split('\n'):
            if 'alert' in line.lower() or 'error' in line.lower():
                print(f"      Error line: {line.strip()}")
    else:
        print(f"   ✅ Checkout completed successfully")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_django_checkout()