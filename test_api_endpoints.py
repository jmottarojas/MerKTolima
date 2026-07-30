#!/usr/bin/env python3
"""Script para probar varios endpoints de la API."""

import requests
import json

def test_endpoints():
    """Probar varios endpoints de la API."""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/health", 
        "/api/v1",
        "/api/v1/users/register",
        "/api/v1/users/login"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            if endpoint == "/api/v1/users/register":
                # POST request for register
                data = {
                    "email": "test_new@example.com",
                    "password": "Test123!",
                    "first_name": "Test",
                    "last_name": "User",
                    "role": "buyer"
                }
                response = requests.post(url, json=data, timeout=5)
            elif endpoint == "/api/v1/users/login":
                # POST request for login
                data = {
                    "email": "test@merktolima.com",
                    "password": "Test123!"
                }
                response = requests.post(url, json=data, timeout=5)
            else:
                # GET request
                response = requests.get(url, timeout=5)
            
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code < 400:
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text[:100]}")
            else:
                try:
                    print(f"   Error: {response.json()}")
                except:
                    print(f"   Error: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_endpoints()