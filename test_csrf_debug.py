#!/usr/bin/env python3
"""
Test para debuggear el problema de CSRF token
"""

import requests
import re

def test_csrf_token():
    """Probar obtención y uso del CSRF token."""
    
    print("🧪 DEBUGGEANDO CSRF TOKEN")
    print("=" * 60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Obtener la página de pedidos para conseguir el CSRF token
    print("📤 1. Obteniendo página de pedidos...")
    
    try:
        response = session.get("http://localhost:8001/vendedor/pedidos/")
        
        print(f"   Status: {response.status_code}")
        print(f"   Cookies: {dict(response.cookies)}")
        
        if response.status_code == 200:
            # Buscar CSRF token en el HTML
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            meta_csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
            
            csrf_token = None
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF token encontrado en input: {csrf_token[:20]}...")
            elif meta_csrf_match:
                csrf_token = meta_csrf_match.group(1)
                print(f"   ✅ CSRF token encontrado en meta: {csrf_token[:20]}...")
            else:
                print("   ❌ CSRF token NO encontrado en HTML")
            
            # Verificar cookie CSRF
            csrf_cookie = response.cookies.get('csrftoken')
            if csrf_cookie:
                print(f"   ✅ CSRF cookie encontrada: {csrf_cookie[:20]}...")
            else:
                print("   ❌ CSRF cookie NO encontrada")
            
            # 2. Probar actualización de estado con el token
            if csrf_token or csrf_cookie:
                print("\n📤 2. Probando actualización de estado...")
                
                token_to_use = csrf_token or csrf_cookie
                
                headers = {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token_to_use,
                    'Referer': 'http://localhost:8001/vendedor/pedidos/'
                }
                
                data = {
                    'order_id': 'test-order-123',
                    'status': 'shipped'
                }
                
                print(f"   Token usado: {token_to_use[:20]}...")
                print(f"   Headers: {headers}")
                print(f"   Data: {data}")
                
                update_response = session.post(
                    "http://localhost:8001/vendedor/pedidos/actualizar-estado/",
                    json=data,
                    headers=headers
                )
                
                print(f"   Status: {update_response.status_code}")
                print(f"   Response: {update_response.text[:200]}")
                
                if update_response.status_code == 200:
                    try:
                        json_response = update_response.json()
                        print(f"   JSON: {json_response}")
                    except:
                        print("   ❌ Respuesta no es JSON válido")
                else:
                    print(f"   ❌ Error HTTP: {update_response.status_code}")
            
        else:
            print(f"   ❌ Error al obtener página: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_csrf_token()