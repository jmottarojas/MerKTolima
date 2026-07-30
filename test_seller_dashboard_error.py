#!/usr/bin/env python3
"""
Test script to debug seller dashboard AttributeError.
"""

import requests
import json

def test_seller_dashboard():
    """Test seller dashboard access."""
    
    print("🧪 TESTING SELLER DASHBOARD ACCESS")
    print("="*60)
    
    # Test data
    django_url = "http://localhost:8001"
    
    # Create session
    session = requests.Session()
    
    # 1. Get login page to get CSRF token
    print("1. Getting login page...")
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
    
    # 2. Login as seller
    print("\n2. Logging in as seller...")
    login_data = {
        'email': 'vendedor@merkatolima.com',
        'password': 'Vendedor123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(f"{django_url}/login/", data=login_data)
    print(f"   Login response status: {login_response.status_code}")
    print(f"   Login response URL: {login_response.url}")
    
    # Check if login was successful
    if 'Bienvenido' in login_response.text or login_response.url.endswith('/vendedor/'):
        print(f"   ✅ Login successful")
    else:
        print(f"   ❌ Login failed")
        # Look for error messages
        if 'alert' in login_response.text.lower():
            for line in login_response.text.split('\n'):
                if 'alert' in line.lower() and ('error' in line.lower() or 'danger' in line.lower()):
                    print(f"      Error: {line.strip()}")
        return
    
    # 3. Access seller dashboard
    print("\n3. Accessing seller dashboard...")
    dashboard_response = session.get(f"{django_url}/vendedor/")
    print(f"   Dashboard response status: {dashboard_response.status_code}")
    print(f"   Dashboard response URL: {dashboard_response.url}")
    
    if dashboard_response.status_code == 200:
        print(f"   ✅ Dashboard loaded successfully")
        
        # Check for specific content
        if 'Panel del Vendedor' in dashboard_response.text or 'Productos' in dashboard_response.text:
            print(f"   ✅ Dashboard content looks correct")
        else:
            print(f"   ⚠️ Dashboard content might be incomplete")
            
    elif dashboard_response.status_code == 500:
        print(f"   ❌ Server error (500) - AttributeError likely occurred")
        
        # Look for error details in response
        if 'AttributeError' in dashboard_response.text:
            print(f"   🔍 AttributeError found in response")
            # Try to extract error details
            lines = dashboard_response.text.split('\n')
            for i, line in enumerate(lines):
                if 'AttributeError' in line:
                    print(f"      Error line {i}: {line.strip()}")
                    # Print surrounding lines for context
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        if j != i:
                            print(f"      Context {j}: {lines[j].strip()}")
                    break
        else:
            print(f"   🔍 No AttributeError found in response text")
            
    else:
        print(f"   ❌ Unexpected status code: {dashboard_response.status_code}")
    
    # 4. Test API endpoints directly
    print("\n4. Testing API endpoints...")
    
    # Test FastAPI login
    print("   Testing FastAPI login...")
    api_login_response = requests.post("http://localhost:8000/api/v1/users/login", json={
        "email": "vendedor@merkatolima.com",
        "password": "Vendedor123"
    })
    
    print(f"   API login status: {api_login_response.status_code}")
    
    if api_login_response.status_code == 200:
        token = api_login_response.json().get("access_token")
        print(f"   ✅ API login successful, token: {token[:20]}...")
        
        # Test get products by seller
        print("   Testing get products by seller...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user profile to get user ID
        profile_response = requests.get("http://localhost:8000/api/v1/users/profile", headers=headers)
        if profile_response.status_code == 200:
            user_id = profile_response.json().get("id")
            print(f"   User ID: {user_id}")
            
            # Test get products by seller
            products_response = requests.get(f"http://localhost:8000/api/v1/products/?seller_id={user_id}", headers=headers)
            print(f"   Get products status: {products_response.status_code}")
            
            if products_response.status_code == 200:
                products = products_response.json().get("products", [])
                print(f"   ✅ Products retrieved: {len(products)} products")
            else:
                print(f"   ❌ Failed to get products: {products_response.text}")
            
            # Test get orders by seller
            orders_response = requests.get(f"http://localhost:8000/api/v1/orders/", headers=headers)
            print(f"   Get orders status: {orders_response.status_code}")
            
            if orders_response.status_code == 200:
                orders = orders_response.json()
                print(f"   ✅ Orders retrieved: {len(orders) if isinstance(orders, list) else 'N/A'} orders")
            else:
                print(f"   ❌ Failed to get orders: {orders_response.text}")
        else:
            print(f"   ❌ Failed to get user profile: {profile_response.text}")
    else:
        print(f"   ❌ API login failed: {api_login_response.text}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_seller_dashboard()