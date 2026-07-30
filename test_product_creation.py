#!/usr/bin/env python3
"""
Test script to verify product creation functionality.
"""
import requests
import json

def test_product_creation():
    """Test the complete product creation flow."""
    
    # Step 1: Login to get session
    session = requests.Session()
    
    # Get CSRF token first
    login_page = session.get('http://localhost:8001/login/')
    print(f"Login page status: {login_page.status_code}")
    
    # Extract CSRF token from the page
    csrf_token = None
    for line in login_page.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            start = line.find('value=') + 6
            end = line.find('>', start)
            csrf_token = line[start:end].strip('"')
            break
    
    if not csrf_token:
        print("Could not find CSRF token")
        return False
    
    print(f"CSRF token: {csrf_token[:20]}...")
    
    # Step 2: Login with seller credentials
    login_data = {
        'email': 'vendedor@merktolima.com',
        'password': 'Vendedor123!',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post('http://localhost:8001/login/', data=login_data)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login redirected to: {login_response.url}")
    
    # Step 3: Access seller dashboard
    dashboard_response = session.get('http://localhost:8001/vendedor/')
    print(f"Dashboard status: {dashboard_response.status_code}")
    
    # Step 4: Access create product page
    create_page = session.get('http://localhost:8001/vendedor/producto/nuevo/')
    print(f"Create product page status: {create_page.status_code}")
    
    if create_page.status_code == 200:
        print("✅ Successfully accessed create product page")
        
        # Extract new CSRF token for product creation
        csrf_token = None
        for line in create_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                start = line.find('value=') + 6
                end = line.find('>', start)
                csrf_token = line[start:end].strip('"')
                break
        
        # Step 5: Create a test product
        product_data = {
            'name': 'Producto de Prueba',
            'description': 'Este es un producto de prueba creado desde el script',
            'price': '75000',
            'category': 'Electrónicos',
            'quantity': '20',
            'low_stock_threshold': '5',
            'image_option': 'url',
            'image_url': 'https://via.placeholder.com/300x300.png?text=Producto+Prueba',
            'csrfmiddlewaretoken': csrf_token
        }
        
        create_response = session.post('http://localhost:8001/vendedor/producto/nuevo/', data=product_data)
        print(f"Product creation status: {create_response.status_code}")
        print(f"Product creation redirected to: {create_response.url}")
        
        if create_response.status_code == 200:
            if 'Error al crear producto' in create_response.text:
                print("❌ Product creation failed - error in response")
                # Look for error messages
                lines = create_response.text.split('\n')
                for line in lines:
                    if 'alert-danger' in line or 'Error al crear producto' in line:
                        print(f"Error: {line.strip()}")
                return False
            else:
                print("✅ Product creation form submitted successfully")
                return True
        else:
            print("❌ Product creation failed")
            return False
    else:
        print("❌ Could not access create product page")
        return False

if __name__ == "__main__":
    success = test_product_creation()
    if success:
        print("\n🎉 Product creation test completed successfully!")
    else:
        print("\n💥 Product creation test failed!")