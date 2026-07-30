#!/usr/bin/env python3
"""
Script para diagnosticar el problema de pedidos del vendedor
"""

import requests
import json

def test_seller_orders_api():
    """Probar directamente el API de pedidos del vendedor"""
    
    print("🔍 DIAGNOSTICANDO PEDIDOS DEL VENDEDOR")
    print("=" * 60)
    
    # Primero, intentar login para obtener token
    print("\n1. 🔐 INTENTANDO LOGIN...")
    login_data = {
        "email": "vendedor@merkatolima.com",
        "password": "Vendedor123"
    }
    
    try:
        login_response = requests.post(
            'http://localhost:8000/api/v1/users/login',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"   ✅ Login exitoso")
            print(f"   🔑 Token: {token[:20]}..." if token else "   ❌ No token")
            
            if token:
                # Obtener perfil para verificar user_id
                print("\n2. 👤 OBTENIENDO PERFIL...")
                profile_response = requests.get(
                    'http://localhost:8000/api/v1/users/profile',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                print(f"   Status: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    user_id = profile.get('id')
                    user_role = profile.get('role')
                    print(f"   ✅ Perfil obtenido")
                    print(f"   👤 User ID: {user_id}")
                    print(f"   🏷️ Role: {user_role}")
                    
                    # Probar obtener pedidos del vendedor
                    print("\n3. 📦 OBTENIENDO PEDIDOS DEL VENDEDOR...")
                    orders_response = requests.get(
                        'http://localhost:8000/api/v1/orders/',
                        params={'seller_id': user_id},
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Content-Type': 'application/json'
                        }
                    )
                    
                    print(f"   Status: {orders_response.status_code}")
                    print(f"   URL: {orders_response.url}")
                    
                    if orders_response.status_code == 200:
                        orders_data = orders_response.json()
                        print(f"   ✅ Pedidos obtenidos")
                        print(f"   📊 Respuesta: {json.dumps(orders_data, indent=2, ensure_ascii=False)}")
                        
                        if isinstance(orders_data, dict) and 'orders' in orders_data:
                            orders_list = orders_data['orders']
                            print(f"   📦 Total pedidos: {len(orders_list)}")
                            
                            for i, order in enumerate(orders_list):
                                print(f"   📋 Pedido {i+1}:")
                                print(f"      ID: {order.get('id', 'N/A')}")
                                print(f"      Status: {order.get('status', 'N/A')}")
                                print(f"      Total: {order.get('total_amount', 'N/A')}")
                                print(f"      Seller ID: {order.get('seller_id', 'N/A')}")
                        else:
                            print(f"   ⚠️ Formato inesperado: {type(orders_data)}")
                    else:
                        print(f"   ❌ Error obteniendo pedidos")
                        try:
                            error_data = orders_response.json()
                            print(f"   Error: {error_data}")
                        except:
                            print(f"   Error: {orders_response.text}")
                else:
                    print(f"   ❌ Error obteniendo perfil")
                    try:
                        error_data = profile_response.json()
                        print(f"   Error: {error_data}")
                    except:
                        print(f"   Error: {profile_response.text}")
            else:
                print("   ❌ No se obtuvo token del login")
        else:
            print(f"   ❌ Login falló")
            try:
                error_data = login_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {login_response.text}")
                
    except requests.exceptions.ConnectionError:
        print("   ❌ No se pudo conectar al API (¿está corriendo en puerto 8000?)")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_all_orders():
    """Probar obtener todos los pedidos para ver si hay alguno"""
    
    print("\n4. 📋 PROBANDO OBTENER TODOS LOS PEDIDOS...")
    
    try:
        # Sin autenticación primero
        response = requests.get('http://localhost:8000/api/v1/orders/')
        print(f"   Status (sin auth): {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ API requiere autenticación (correcto)")
        elif response.status_code == 200:
            data = response.json()
            print(f"   📊 Datos: {data}")
        else:
            print(f"   ⚠️ Respuesta inesperada: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def test_django_seller_orders():
    """Probar la página de pedidos del vendedor en Django"""
    
    print("\n5. 🌐 PROBANDO PÁGINA DJANGO...")
    
    try:
        response = requests.get('http://localhost:8001/vendedor/pedidos/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Página carga correctamente")
            # Buscar mensajes de error en el HTML
            content = response.text
            if "No se pudieron cargar los pedidos" in content:
                print("   ⚠️ Mensaje de error encontrado en HTML")
            if "No tienes pedidos aún" in content:
                print("   ℹ️ Mensaje de 'sin pedidos' encontrado")
        elif response.status_code == 302:
            print("   ↪️ Redirección (probablemente a login)")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def check_order_creation():
    """Verificar si se están creando pedidos correctamente"""
    
    print("\n6. 🛒 VERIFICANDO CREACIÓN DE PEDIDOS...")
    
    # Datos de ejemplo para crear un pedido
    order_data = {
        "cart_id": "test_cart_123",
        "shipping_address": {
            "street": "Calle Test 123",
            "city": "Bogotá",
            "state": "Cundinamarca",
            "country": "Colombia"
        },
        "payment_method": "credit_card"
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/orders/',
            json=order_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Requiere autenticación (correcto)")
        elif response.status_code == 422:
            error_data = response.json()
            print(f"   ℹ️ Error de validación: {error_data}")
        else:
            print(f"   📊 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    test_seller_orders_api()
    test_all_orders()
    test_django_seller_orders()
    check_order_creation()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DEL DIAGNÓSTICO:")
    print("1. Verificar que el login funciona y devuelve token")
    print("2. Verificar que el perfil se obtiene correctamente")
    print("3. Verificar que la API de pedidos responde")
    print("4. Verificar que Django puede comunicarse con FastAPI")
    print("5. Verificar que los pedidos se están creando y guardando")
    print("\n💡 POSIBLES CAUSAS:")
    print("- Token de autenticación expirado o inválido")
    print("- API de pedidos no funciona correctamente")
    print("- Pedidos no se están guardando en la base de datos")
    print("- Problema de comunicación Django <-> FastAPI")
    print("- seller_id no coincide entre pedido y vendedor")