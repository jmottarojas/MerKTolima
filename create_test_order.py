#!/usr/bin/env python3
"""
Script para crear un pedido de prueba completo
"""

import requests
import re
import json
import time

def create_test_order():
    """Crear un pedido de prueba completo."""
    
    print("🛒 CREANDO PEDIDO DE PRUEBA COMPLETO")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # 1. Login como comprador
        print("📤 1. Login como comprador...")
        
        login_page = session.get("http://localhost:8001/login/")
        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
        
        if csrf_match:
            csrf_token = csrf_match.group(1)
            
            login_data = {
                'email': 'buyer@test.com',
                'password': 'Password123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            login_response = session.post(
                "http://localhost:8001/login/",
                data=login_data,
                headers={'Referer': 'http://localhost:8001/login/'}
            )
            
            if login_response.status_code in [200, 302]:
                print("   ✅ Login como comprador exitoso")
                
                # 2. Obtener productos disponibles
                print("\n📤 2. Obteniendo productos disponibles...")
                
                products_page = session.get("http://localhost:8001/productos/")
                
                if products_page.status_code == 200:
                    # Buscar enlaces de productos
                    product_links = re.findall(r'/producto/([^/]+)/', products_page.text)
                    
                    if product_links:
                        product_id = product_links[0]
                        print(f"   ✅ Producto encontrado: {product_id}")
                        
                        # 3. Agregar producto al carrito
                        print(f"\n📤 3. Agregando producto {product_id} al carrito...")
                        
                        # Obtener página del producto para CSRF token
                        product_page = session.get(f"http://localhost:8001/producto/{product_id}/")
                        csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', product_page.text)
                        
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            
                            cart_data = {
                                'quantity': '1',
                                'csrfmiddlewaretoken': csrf_token
                            }
                            
                            cart_response = session.post(
                                f"http://localhost:8001/carrito/agregar/{product_id}/",
                                data=cart_data,
                                headers={'Referer': f'http://localhost:8001/producto/{product_id}/'}
                            )
                            
                            if cart_response.status_code in [200, 302]:
                                print("   ✅ Producto agregado al carrito")
                                
                                # 4. Ir al checkout
                                print("\n📤 4. Procesando checkout...")
                                
                                checkout_page = session.get("http://localhost:8001/checkout/")
                                
                                if checkout_page.status_code == 200:
                                    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', checkout_page.text)
                                    
                                    if csrf_match:
                                        csrf_token = csrf_match.group(1)
                                        
                                        checkout_data = {
                                            'street': 'Calle de Prueba 123',
                                            'city': 'Bogotá, Bogotá D.C., Colombia',
                                            'state': 'Cundinamarca',
                                            'country': 'Colombia',
                                            'payment_method': 'credit_card',
                                            'csrfmiddlewaretoken': csrf_token
                                        }
                                        
                                        checkout_response = session.post(
                                            "http://localhost:8001/checkout/",
                                            data=checkout_data,
                                            headers={'Referer': 'http://localhost:8001/checkout/'}
                                        )
                                        
                                        if checkout_response.status_code in [200, 302]:
                                            print("   ✅ Checkout completado")
                                            
                                            # 5. Verificar que se creó el pedido
                                            print("\n📤 5. Verificando pedido creado...")
                                            
                                            orders_page = session.get("http://localhost:8001/pedidos/")
                                            
                                            if orders_page.status_code == 200:
                                                if 'Pedido #' in orders_page.text:
                                                    print("   ✅ ¡PEDIDO CREADO EXITOSAMENTE!")
                                                    
                                                    # Extraer ID del pedido
                                                    order_match = re.search(r'Pedido #([a-f0-9-]+)', orders_page.text)
                                                    if order_match:
                                                        order_id = order_match.group(1)
                                                        print(f"   📋 ID del pedido: {order_id}")
                                                    
                                                    print("\n🎯 AHORA PUEDES PROBAR LA ACTUALIZACIÓN DE ESTADO:")
                                                    print("   1. Logout del comprador")
                                                    print("   2. Login como vendedor (seller@test.com / Password123)")
                                                    print("   3. Ir a Panel Vendedor → Pedidos Recibidos")
                                                    print("   4. Hacer clic en 'Marcar como Enviado'")
                                                    print("   5. ¡Debería funcionar sin errores!")
                                                    
                                                    return True
                                                else:
                                                    print("   ❌ No se encontró el pedido en la página de pedidos")
                                            else:
                                                print(f"   ❌ Error obteniendo página de pedidos: {orders_page.status_code}")
                                        else:
                                            print(f"   ❌ Error en checkout: {checkout_response.status_code}")
                                            print(f"   Respuesta: {checkout_response.text[:300]}")
                                    else:
                                        print("   ❌ No se pudo obtener CSRF token para checkout")
                                else:
                                    print(f"   ❌ Error obteniendo página de checkout: {checkout_page.status_code}")
                            else:
                                print(f"   ❌ Error agregando al carrito: {cart_response.status_code}")
                        else:
                            print("   ❌ No se pudo obtener CSRF token para carrito")
                    else:
                        print("   ❌ No se encontraron productos")
                        print("   Ejecuta primero: python crear_producto_prueba.py")
                else:
                    print(f"   ❌ Error obteniendo productos: {products_page.status_code}")
            else:
                print(f"   ❌ Error en login: {login_response.status_code}")
        else:
            print("   ❌ No se pudo obtener CSRF token para login")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    return False

if __name__ == "__main__":
    success = create_test_order()
    if success:
        print("\n🎉 ¡PEDIDO DE PRUEBA CREADO EXITOSAMENTE!")
        print("Ahora puedes probar la funcionalidad de actualización de estado.")
    else:
        print("\n❌ No se pudo crear el pedido de prueba.")
        print("Verifica que los servidores estén corriendo y que haya productos disponibles.")