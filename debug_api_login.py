#!/usr/bin/env python3
"""Script para debuggear el endpoint de login de la API."""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_api_health():
    """Probar que la API esté funcionando."""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health check - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_api_login():
    """Probar el endpoint de login de la API con debugging."""
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
        
        # Primero verificar que la API esté funcionando
        if not test_api_health():
            print("❌ API no está funcionando")
            return
        
        response = requests.post(url, json=login_data, headers=headers, timeout=10)
        
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
                
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API. ¿Está el servidor ejecutándose?")
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

if __name__ == "__main__":
    test_api_login()