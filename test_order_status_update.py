#!/usr/bin/env python3
"""
Test para verificar la actualización de estado de pedidos
"""

import requests
import json

def test_order_status_update():
    """Probar la actualización de estado de pedidos."""
    
    print("🧪 PROBANDO ACTUALIZACIÓN DE ESTADO DE PEDIDOS")
    print("=" * 60)
    
    # URL del endpoint
    url = "http://localhost:8001/vendedor/pedidos/actualizar-estado/"
    
    # Datos de prueba
    test_data = {
        "order_id": "test-order-123",
        "status": "shipped"
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'test-token'  # En producción esto vendría de la cookie
    }
    
    print(f"📤 Enviando petición a: {url}")
    print(f"📦 Datos: {test_data}")
    print(f"📋 Headers: {headers}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\n📥 Respuesta:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"   JSON: {response_data}")
        else:
            print(f"   Text: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_order_status_update()