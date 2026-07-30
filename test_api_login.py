#!/usr/bin/env python3
"""Script para probar el endpoint de login de la API."""

import requests
import json

def test_api_login():
    """Probar el endpoint de login de la API."""
    url = "http://localhost:8000/api/v1/users/login"
    
    # Datos de login
    login_data = {
        "email": "test@merktolima.com",
        "password": "Test123!"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🔐 Probando endpoint de login de la API...")
        print(f"URL: {url}")
        print(f"Datos: {login_data}")
        
        response = requests.post(url, json=login_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login exitoso!")
            print(f"Token: {data.get('access_token', 'No token')[:50]}...")
            print(f"Tipo: {data.get('token_type', 'No type')}")
            print(f"Expira en: {data.get('expires_in', 'No expiry')} segundos")
        else:
            print("❌ Login falló!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

if __name__ == "__main__":
    test_api_login()