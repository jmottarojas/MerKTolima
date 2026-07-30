#!/usr/bin/env python3
"""
Test para verificar que el estado 'processing' funciona
"""

import requests
import re
import json

def test_processing_status():
    """Probar el estado processing."""
    
    print("🔄 PROBANDO ESTADO 'PROCESSING'")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # Login como vendedor
        print("📤 1. Login como vendedor...")
        
        login_page = session.get("http://localhost:8001/login/")
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
        
        if csrf_match:
            csrf_token = csrf_match.group(1)
            
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
            
            if login_response.status_code in [200, 302]:
                print("   ✅ Login exitoso")
                
                # Obtener página de pedidos
                orders_page = session.get("http://localhost:8001/vendedor/pedidos/")
                
                if orders_page.status_code == 200:
                    # Buscar pedidos
                    order_ids = re.findall(r'updateOrderStatus\(["\']([^"\']+)["\']', orders_page.text)
                    
                    if order_ids:
                        test_order_id = order_ids[0]
                        print(f"   ✅ Pedido encontrado: {test_order_id}")
                        
                        # Obtener CSRF token
                        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', orders_page.text)
                        
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            
                            # Probar cambio a processing
                            print(f"\n📤 2. Probando cambio a 'processing'...")
                            
                            headers = {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrf_token,
                                'Referer': 'http://localhost:8001/vendedor/pedidos/',
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                            
                            test_data = {
                                'order_id': test_order_id,
                                'status': 'processing'
                            }
                            
                            print(f"   Datos: {test_data}")
                            
                            update_response = session.post(
                                "http://localhost:8001/vendedor/pedidos/actualizar-estado/",
                                json=test_data,
                                headers=headers
                            )
                            
                            print(f"\n📥 RESPUESTA:")
                            print(f"   Status: {update_response.status_code}")
                            
                            if update_response.headers.get('content-type', '').startswith('application/json'):
                                try:
                                    json_data = update_response.json()
                                    print(f"   JSON: {json_data}")
                                    
                                    if json_data.get('success'):
                                        print("   ✅ ¡CAMBIO A PROCESSING EXITOSO!")
                                        
                                        # Ahora probar cambio a shipped
                                        print(f"\n📤 3. Probando cambio a 'shipped'...")
                                        
                                        test_data['status'] = 'shipped'
                                        
                                        shipped_response = session.post(
                                            "http://localhost:8001/vendedor/pedidos/actualizar-estado/",
                                            json=test_data,
                                            headers=headers
                                        )
                                        
                                        if shipped_response.headers.get('content-type', '').startswith('application/json'):
                                            shipped_data = shipped_response.json()
                                            print(f"   JSON: {shipped_data}")
                                            
                                            if shipped_data.get('success'):
                                                print("   ✅ ¡CAMBIO A SHIPPED EXITOSO!")
                                                print("\n🎉 ¡FLUJO COMPLETO FUNCIONA CORRECTAMENTE!")
                                            else:
                                                print(f"   ❌ Error en shipped: {shipped_data.get('error')}")
                                        else:
                                            print(f"   ❌ Respuesta shipped no JSON: {shipped_response.text[:200]}")
                                    else:
                                        print(f"   ❌ Error en processing: {json_data.get('error')}")
                                except:
                                    print(f"   ❌ Error parseando JSON: {update_response.text[:200]}")
                            else:
                                print(f"   ❌ Respuesta no JSON: {update_response.text[:200]}")
                        else:
                            print("   ❌ No se pudo obtener CSRF token")
                    else:
                        print("   ❌ No se encontraron pedidos")
                else:
                    print(f"   ❌ Error obteniendo pedidos: {orders_page.status_code}")
            else:
                print(f"   ❌ Error en login: {login_response.status_code}")
        else:
            print("   ❌ No se pudo obtener CSRF token para login")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_processing_status()