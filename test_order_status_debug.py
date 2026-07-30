#!/usr/bin/env python3
"""
Test específico para debuggear el error 400 en actualización de estado
"""

import requests
import json

def test_order_status_update_detailed():
    """Test detallado del endpoint de actualización de estado."""
    
    print("🧪 TEST DETALLADO - ACTUALIZACIÓN ESTADO PEDIDOS")
    print("=" * 60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Primero hacer login como vendedor
    print("📤 1. Intentando login como vendedor...")
    
    login_data = {
        'email': 'seller@test.com',
        'password': 'Password123'
    }
    
    try:
        login_response = session.post(
            "http://localhost:8001/login/",
            data=login_data,
            allow_redirects=False
        )
        
        print(f"   Login Status: {login_response.status_code}")
        print(f"   Login Cookies: {dict(login_response.cookies)}")
        
        if login_response.status_code in [200, 302]:
            print("   ✅ Login exitoso")
            
            # 2. Obtener página de pedidos para conseguir CSRF token
            print("\n📤 2. Obteniendo página de pedidos...")
            
            orders_response = session.get("http://localhost:8001/vendedor/pedidos/")
            
            print(f"   Orders Status: {orders_response.status_code}")
            print(f"   Orders Cookies: {dict(orders_response.cookies)}")
            
            if orders_response.status_code == 200:
                print("   ✅ Página de pedidos obtenida")
                
                # Buscar CSRF token
                import re
                csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', orders_response.text)
                meta_csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', orders_response.text)
                
                csrf_token = None
                
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   ✅ CSRF token encontrado en input: {csrf_token[:20]}...")
                elif meta_csrf_match:
                    csrf_token = meta_csrf_match.group(1)
                    print(f"   ✅ CSRF token encontrado en meta: {csrf_token[:20]}...")
                elif 'csrftoken' in orders_response.cookies:
                    csrf_token = orders_response.cookies['csrftoken']
                    print(f"   ✅ CSRF token encontrado en cookie: {csrf_token[:20]}...")
                else:
                    print("   ❌ CSRF token NO encontrado")
                
                # 3. Probar actualización de estado
                if csrf_token:
                    print("\n📤 3. Probando actualización de estado...")
                    
                    headers = {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token,
                        'Referer': 'http://localhost:8001/vendedor/pedidos/',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    data = {
                        'order_id': 'test-order-' + str(int(time.time())),
                        'status': 'shipped'
                    }
                    
                    print(f"   Token usado: {csrf_token[:20]}...")
                    print(f"   Headers: {headers}")
                    print(f"   Data: {data}")
                    
                    update_response = session.post(
                        "http://localhost:8001/vendedor/pedidos/actualizar-estado/",
                        json=data,
                        headers=headers
                    )
                    
                    print(f"\n📥 RESPUESTA ACTUALIZACIÓN:")
                    print(f"   Status: {update_response.status_code}")
                    print(f"   Headers: {dict(update_response.headers)}")
                    print(f"   Content-Type: {update_response.headers.get('content-type', 'No especificado')}")
                    
                    # Mostrar contenido de respuesta
                    try:
                        if update_response.headers.get('content-type', '').startswith('application/json'):
                            json_response = update_response.json()
                            print(f"   JSON Response: {json_response}")
                        else:
                            text_response = update_response.text
                            print(f"   Text Response (primeros 500 chars): {text_response[:500]}")
                            
                            # Si es HTML, buscar errores específicos
                            if '<html' in text_response.lower():
                                if 'csrf' in text_response.lower():
                                    print("   ⚠️ Posible error CSRF en respuesta HTML")
                                if 'forbidden' in text_response.lower():
                                    print("   ⚠️ Posible error 403 Forbidden")
                                if 'bad request' in text_response.lower():
                                    print("   ⚠️ Posible error 400 Bad Request")
                                    
                    except Exception as parse_error:
                        print(f"   ❌ Error parseando respuesta: {parse_error}")
                        print(f"   Raw response: {update_response.text[:200]}")
                
                else:
                    print("   ❌ No se puede probar sin CSRF token")
            else:
                print(f"   ❌ Error obteniendo página de pedidos: {orders_response.status_code}")
        else:
            print(f"   ❌ Error en login: {login_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    import time
    test_order_status_update_detailed()