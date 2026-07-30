#!/usr/bin/env python3
"""Script para probar login con el usuario recién creado."""

import requests
import json

def test_new_user_login():
    """Probar login con el usuario recién creado."""
    url = "http://localhost:8000/api/v1/users/login"
    
    # Datos de login del usuario recién creado
    login_data = {
        "email": "test_new@example.com",
        "password": "Test123!"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🔐 Probando login con usuario recién creado...")
        print(f"URL: {url}")
        print(f"Datos: {login_data}")
        
        response = requests.post(url, json=login_data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
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
    test_new_user_login()