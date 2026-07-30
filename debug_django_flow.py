#!/usr/bin/env python3
"""
Debug script to simulate the exact Django flow.
"""
import requests
import json

def debug_django_flow():
    """Debug the exact Django authentication flow."""
    
    print("=== DEBUGGING DJANGO AUTHENTICATION FLOW ===\n")
    
    # Simulate Django session
    django_session = {}
    
    # Step 1: Simulate Django login
    print("1. Simulating Django login process...")
    
    # Login to API
    login_data = {'email': 'vendedor@merktolima.com', 'password': 'Vendedor123!'}
    login_response = requests.post('http://localhost:8000/api/v1/users/login', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ API login failed: {login_response.status_code}")
        return
    
    token_data = login_response.json()
    access_token = token_data.get('access_token')
    print(f"✅ API login successful, token: {access_token[:50]}...")
    
    # Simulate API client setup
    api_session = requests.Session()
    api_session.headers.update({'Authorization': f'Bearer {access_token}'})
    
    # Get profile
    profile_response = api_session.get('http://localhost:8000/api/v1/users/profile',
                                     headers={'Content-Type': 'application/json'})
    
    if profile_response.status_code != 200:
        print(f"❌ Profile request failed: {profile_response.status_code}")
        return
    
    profile_data = profile_response.json()
    
    # Simulate Django session storage
    django_session['user_token'] = access_token
    django_session['user_id'] = profile_data.get('id')
    django_session['user_email'] = profile_data.get('email')
    django_session['user_role'] = profile_data.get('role')
    django_session['user_first_name'] = profile_data.get('first_name')
    
    print(f"✅ Django session created:")
    print(f"   User ID: {django_session['user_id']}")
    print(f"   Email: {django_session['user_email']}")
    print(f"   Role: {django_session['user_role']}")
    
    # Step 2: Simulate product creation request
    print("\n2. Simulating product creation...")
    
    # Get token from session (like Django does)
    user_token = django_session.get('user_token')
    user_id = django_session.get('user_id')
    
    print(f"   Retrieved token from session: {user_token[:50] if user_token else 'None'}...")
    print(f"   User ID: {user_id}")
    
    # Create new session for product creation (simulating Django API client)
    product_session = requests.Session()
    
    # Set token (like api_client.set_auth_token does)
    if user_token:
        product_session.headers.update({'Authorization': f'Bearer {user_token}'})
        print(f"   Token set in session headers: {dict(product_session.headers)}")
    else:
        print("   ❌ No token to set!")
        return
    
    # Product data
    product_data = {
        'name': 'Django Flow Test Product',
        'description': 'Testing Django authentication flow',
        'price': 35000,
        'currency': 'COP',
        'category': 'Electrónicos',
        'inventory_quantity': 8,
        'low_stock_threshold': 3
    }
    
    # Make request (like api_client.create_product does)
    create_response = product_session.post('http://localhost:8000/api/v1/products/',
                                         json=product_data,
                                         headers={'Content-Type': 'application/json'})
    
    print(f"   Product creation response: {create_response.status_code}")
    
    if create_response.status_code == 200:
        print("✅ Product creation successful!")
        product = create_response.json()
        print(f"   Product ID: {product.get('id')}")
        print(f"   Product name: {product.get('name')}")
    else:
        print(f"❌ Product creation failed!")
        print(f"   Response text: {create_response.text}")
        print(f"   Request headers: {dict(create_response.request.headers)}")
    
    # Step 3: Test if token is still valid
    print("\n3. Testing token validity...")
    test_response = product_session.get('http://localhost:8000/api/v1/users/profile',
                                      headers={'Content-Type': 'application/json'})
    
    if test_response.status_code == 200:
        print("✅ Token is still valid")
    else:
        print(f"❌ Token validation failed: {test_response.status_code}")
        print(f"   Response: {test_response.text}")

if __name__ == "__main__":
    debug_django_flow()