#!/usr/bin/env python3
"""
Script simple para crear datos de prueba
"""

import requests
import re
import json

def create_test_data():
    """Crear datos de prueba simples."""
    
    print("🔧 CREANDO DATOS DE PRUEBA SIMPLES")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # 1. Crear producto como vendedor
        print("📤 1. Creando producto como vendedor...")
        
        # Login como vendedor
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
                print("   ✅ Login como vendedor exitoso")
                
                # Ir a crear producto
                create_page = session.get("http://localhost:8001/vendedor/producto/nuevo/")
                
                if create_page.status_code == 200:
                    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', create_page.text)
                    
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                        
                        # Datos del producto
                        product_data = {
                            'name': 'Producto de Prueba para Pedidos',
                            'description': 'Este es un producto de prueba para probar la funcionalidad de actualización de estado de pedidos.',
                            'price': '50000',
                            'category': 'Electrónicos',
                            'quantity': '10',
                            'low_stock_threshold': '2',
                            'condition': 'nuevo',
                            'image_url_1': 'https://via.placeholder.com/400x300/007bff/ffffff?text=Producto+Prueba',
                            'csrfmiddlewaretoken': csrf_token
                        }
                        
                        product_response = session.post(
                            "http://localhost:8001/vendedor/producto/nuevo/",
                            data=product_data,
                            headers={'Referer': 'http://localhost:8001/vendedor/producto/nuevo/'}
                        )
                        
                        if product_response.status_code in [200, 302]:
                            print("   ✅ Producto creado exitosamente")
                            
                            # Logout del vendedor
                            session.get("http://localhost:8001/logout/")
                            
                            # 2. Crear pedido como comprador
                            print("\n📤 2. Creando pedido como comprador...")
                            
                            # Login como comprador
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
                                    
                                    # Obtener productos
                                    products_page = session.get("http://localhost:8001/productos/")
                                    
                                    if products_page.status_code == 200:
                                        # Buscar el producto que acabamos de crear
                                        product_links = re.findall(r'/producto/([^/]+)/', products_page.text)
                                        
                                        if product_links:
                                            product_id = product_links[0]
                                            print(f"   ✅ Producto encontrado: {product_id}")
                                            
                                            # Agregar al carrito
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
                                                    
                                                    # Hacer checkout
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
                                                                
                                                                print("\n🎉 ¡DATOS DE PRUEBA CREADOS EXITOSAMENTE!")
                                                                print("\n📋 INSTRUCCIONES:")
                                                                print("1. Logout del comprador")
                                                                print("2. Login como vendedor: seller@test.com / Password123")
                                                                print("3. Ir a: Panel Vendedor → Pedidos Recibidos")
                                                                print("4. Hacer clic en 'Marcar como Enviado'")
                                                                print("5. Abrir Developer Tools (F12) → Console para ver logs detallados")
                                                                print("6. ¡Debería funcionar sin errores!")
                                                                
                                                                return True
                                                            else:
                                                                print(f"   ❌ Error en checkout: {checkout_response.status_code}")
                                                        else:
                                                            print("   ❌ No se pudo obtener CSRF token para checkout")
                                                    else:
                                                        print(f"   ❌ Error obteniendo checkout: {checkout_page.status_code}")
                                                else:
                                                    print(f"   ❌ Error agregando al carrito: {cart_response.status_code}")
                                            else:
                                                print("   ❌ No se pudo obtener CSRF token para carrito")
                                        else:
                                            print("   ❌ No se encontraron productos")
                                    else:
                                        print(f"   ❌ Error obteniendo productos: {products_page.status_code}")
                                else:
                                    print(f"   ❌ Error login comprador: {login_response.status_code}")
                            else:
                                print("   ❌ No se pudo obtener CSRF token para login comprador")
                        else:
                            print(f"   ❌ Error creando producto: {product_response.status_code}")
                            print(f"   Respuesta: {product_response.text[:300]}")
                    else:
                        print("   ❌ No se pudo obtener CSRF token para crear producto")
                else:
                    print(f"   ❌ Error obteniendo página crear producto: {create_page.status_code}")
            else:
                print(f"   ❌ Error login vendedor: {login_response.status_code}")
        else:
            print("   ❌ No se pudo obtener CSRF token para login vendedor")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    return False

if __name__ == "__main__":
    success = create_test_data()
    if not success:
        print("\n❌ No se pudieron crear los datos de prueba.")
        print("Verifica que ambos servidores estén corriendo:")
        print("- Django: http://localhost:8001/")
        print("- FastAPI: http://localhost:8000/")