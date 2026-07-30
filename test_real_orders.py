#!/usr/bin/env python3
"""
Test para verificar si hay pedidos reales en el sistema
"""

import requests
import re
import json

def check_real_orders():
    """Verificar si hay pedidos reales en el sistema."""
    
    print("🔍 VERIFICANDO PEDIDOS REALES EN EL SISTEMA")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # 1. Login como vendedor
        print("📤 1. Haciendo login como vendedor...")
        
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
                
                # 2. Obtener página de pedidos
                print("\n📤 2. Obteniendo página de pedidos...")
                
                orders_page = session.get("http://localhost:8001/vendedor/pedidos/")
                
                if orders_page.status_code == 200:
                    print("   ✅ Página de pedidos obtenida")
                    
                    # Buscar pedidos en el HTML
                    order_ids = re.findall(r'updateOrderStatus\(["\']([^"\']+)["\']', orders_page.text)
                    
                    if order_ids:
                        print(f"\n🎯 PEDIDOS ENCONTRADOS: {len(order_ids)}")
                        for i, order_id in enumerate(order_ids[:5]):  # Mostrar máximo 5
                            print(f"   {i+1}. {order_id}")
                        
                        # Probar con el primer pedido real
                        if order_ids:
                            test_order_id = order_ids[0]
                            print(f"\n📤 3. Probando actualización con pedido real: {test_order_id}")
                            
                            # Obtener nuevo CSRF token
                            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', orders_page.text)
                            
                            if csrf_match:
                                new_csrf_token = csrf_match.group(1)
                                
                                headers = {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': new_csrf_token,
                                    'Referer': 'http://localhost:8001/vendedor/pedidos/',
                                    'X-Requested-With': 'XMLHttpRequest'
                                }
                                
                                test_data = {
                                    'order_id': test_order_id,
                                    'status': 'shipped'
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
                                            print("   ✅ ¡ACTUALIZACIÓN EXITOSA!")
                                        else:
                                            print(f"   ❌ Error: {json_data.get('error', 'Error desconocido')}")
                                    except:
                                        print(f"   ❌ Error parseando JSON: {update_response.text[:200]}")
                                else:
                                    print(f"   ❌ Respuesta no JSON: {update_response.text[:200]}")
                    else:
                        print("\n⚠️ NO SE ENCONTRARON PEDIDOS")
                        print("   Para probar la funcionalidad:")
                        print("   1. Login como comprador (buyer@test.com / Password123)")
                        print("   2. Agregar productos al carrito")
                        print("   3. Completar checkout")
                        print("   4. Luego probar como vendedor")
                else:
                    print(f"   ❌ Error obteniendo página de pedidos: {orders_page.status_code}")
            else:
                print(f"   ❌ Error en login: {login_response.status_code}")
        else:
            print("   ❌ No se pudo obtener CSRF token")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    check_real_orders()