#!/usr/bin/env python3
"""
Simulación exacta de lo que hace el navegador
"""

import requests
import re
import json

def simulate_browser_flow():
    """Simular exactamente lo que hace el navegador."""
    
    print("🌐 SIMULACIÓN EXACTA DEL NAVEGADOR")
    print("=" * 60)
    
    session = requests.Session()
    
    # Simular headers de navegador
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        # 1. Obtener página de login para conseguir CSRF token
        print("📤 1. Obteniendo página de login...")
        
        login_page = session.get("http://localhost:8001/login/")
        print(f"   Status: {login_page.status_code}")
        
        if login_page.status_code == 200:
            # Extraer CSRF token del formulario de login
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF token obtenido: {csrf_token[:20]}...")
                
                # 2. Hacer login con CSRF token
                print("\n📤 2. Haciendo login...")
                
                login_data = {
                    'email': 'seller@test.com',
                    'password': 'Password123',
                    'csrfmiddlewaretoken': csrf_token
                }
                
                login_response = session.post(
                    "http://localhost:8001/login/",
                    data=login_data,
                    headers={'Referer': 'http://localhost:8001/login/'}
                )
                
                print(f"   Status: {login_response.status_code}")
                print(f"   Cookies después del login: {dict(session.cookies)}")
                
                if login_response.status_code in [200, 302]:
                    print("   ✅ Login exitoso")
                    
                    # 3. Ir a página de pedidos
                    print("\n📤 3. Obteniendo página de pedidos...")
                    
                    orders_page = session.get("http://localhost:8001/vendedor/pedidos/")
                    print(f"   Status: {orders_page.status_code}")
                    
                    if orders_page.status_code == 200:
                        print("   ✅ Página de pedidos obtenida")
                        
                        # Extraer nuevo CSRF token de la página de pedidos
                        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', orders_page.text)
                        meta_csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', orders_page.text)
                        
                        new_csrf_token = None
                        
                        if csrf_match:
                            new_csrf_token = csrf_match.group(1)
                            print(f"   ✅ Nuevo CSRF token (input): {new_csrf_token[:20]}...")
                        elif meta_csrf_match:
                            new_csrf_token = meta_csrf_match.group(1)
                            print(f"   ✅ Nuevo CSRF token (meta): {new_csrf_token[:20]}...")
                        elif 'csrftoken' in session.cookies:
                            new_csrf_token = session.cookies['csrftoken']
                            print(f"   ✅ CSRF token de cookie: {new_csrf_token[:20]}...")
                        
                        # 4. Probar actualización de estado
                        if new_csrf_token:
                            print("\n📤 4. Probando actualización de estado...")
                            
                            # Simular exactamente lo que hace el JavaScript
                            headers = {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': new_csrf_token,
                                'Referer': 'http://localhost:8001/vendedor/pedidos/',
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                            
                            # Usar un ID de pedido que podría existir
                            test_data = {
                                'order_id': 'test-order-12345',
                                'status': 'shipped'
                            }
                            
                            print(f"   Headers: {headers}")
                            print(f"   Data: {test_data}")
                            print(f"   URL: http://localhost:8001/vendedor/pedidos/actualizar-estado/")
                            
                            update_response = session.post(
                                "http://localhost:8001/vendedor/pedidos/actualizar-estado/",
                                json=test_data,
                                headers=headers
                            )
                            
                            print(f"\n📥 RESPUESTA:")
                            print(f"   Status: {update_response.status_code}")
                            print(f"   Headers: {dict(update_response.headers)}")
                            
                            # Analizar respuesta
                            content_type = update_response.headers.get('content-type', '')
                            
                            if 'application/json' in content_type:
                                try:
                                    json_data = update_response.json()
                                    print(f"   JSON: {json_data}")
                                    
                                    if json_data.get('success'):
                                        print("   ✅ Actualización exitosa")
                                    else:
                                        print(f"   ❌ Error: {json_data.get('error', 'Error desconocido')}")
                                        
                                except json.JSONDecodeError:
                                    print("   ❌ Error: Respuesta no es JSON válido")
                                    print(f"   Texto: {update_response.text[:200]}")
                            else:
                                print(f"   ❌ Respuesta no es JSON (Content-Type: {content_type})")
                                print(f"   Texto: {update_response.text[:300]}")
                                
                                # Buscar errores específicos en HTML
                                text = update_response.text.lower()
                                if 'csrf' in text:
                                    print("   🔍 Posible error CSRF detectado")
                                if 'forbidden' in text:
                                    print("   🔍 Error 403 Forbidden detectado")
                                if 'bad request' in text:
                                    print("   🔍 Error 400 Bad Request detectado")
                        else:
                            print("   ❌ No se pudo obtener CSRF token de la página de pedidos")
                    else:
                        print(f"   ❌ Error obteniendo página de pedidos: {orders_page.status_code}")
                else:
                    print(f"   ❌ Error en login: {login_response.status_code}")
                    print(f"   Respuesta: {login_response.text[:200]}")
            else:
                print("   ❌ No se pudo obtener CSRF token de la página de login")
        else:
            print(f"   ❌ Error obteniendo página de login: {login_page.status_code}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    simulate_browser_flow()