#!/usr/bin/env python3
"""
Debug script to identify the token authentication issue.
"""
import requests
import json

def debug_token_issue():
    """Debug the token authentication issue."""
    
    print("=== DEBUGGING TOKEN AUTHENTICATION ISSUE ===\n")
    
    # Step 1: Login and get token
    print("1. Testing direct API login...")
    login_data = {'email': 'vendedor@merktolima.com', 'password': 'Vendedor123!'}
    response = requests.post('http://localhost:8000/api/v1/users/login', json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token_data = response.json()
    token = token_data.get('access_token')
    print(f"✅ Login successful, token: {token[:50]}...")
    
    # Step 2: Test token with profile endpoint
    print("\n2. Testing token with profile endpoint...")
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    profile_response = requests.get('http://localhost:8000/api/v1/users/profile', headers=headers)
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print(f"✅ Profile endpoint works, user: {profile_data.get('email')}")
        print(f"   User ID: {profile_data.get('id')}")
        print(f"   Role: {profile_data.get('role')}")
    else:
        print(f"❌ Profile endpoint failed: {profile_response.status_code}")
        print(f"   Response: {profile_response.text}")
        return
    
    # Step 3: Test token with product creation
    print("\n3. Testing token with product creation...")
    product_data = {
        'name': 'Debug Test Product',
        'description': 'Testing token authentication',
        'price': 25000,
        'currency': 'COP',
        'category': 'Electrónicos',
        'inventory_quantity': 5,
        'low_stock_threshold': 2
    }
    
    create_response = requests.post('http://localhost:8000/api/v1/products/', 
                                  json=product_data, headers=headers)
    
    if create_response.status_code == 200:
        print("✅ Product creation successful!")
        product = create_response.json()
        print(f"   Product ID: {product.get('id')}")
        print(f"   Product name: {product.get('name')}")
    else:
        print(f"❌ Product creation failed: {create_response.status_code}")
        print(f"   Response: {create_response.text}")
    
    # Step 4: Test Django API client simulation
    print("\n4. Testing Django API client simulation...")
    
    # Simulate what the Django API client does
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {token}'})
    
    # Test with session
    session_response = session.post('http://localhost:8000/api/v1/products/', 
                                  json=product_data, 
                                  headers={'Content-Type': 'application/json'})
    
    if session_response.status_code == 200:
        print("✅ Session-based request successful!")
    else:
        print(f"❌ Session-based request failed: {session_response.status_code}")
        print(f"   Response: {session_response.text}")
        print(f"   Headers sent: {dict(session.headers)}")

if __name__ == "__main__":
    debug_token_issue()