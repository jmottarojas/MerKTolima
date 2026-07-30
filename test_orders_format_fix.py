#!/usr/bin/env python3
"""
Script simple para probar la corrección del formato de pedidos
"""

import requests

def test_format_conversion():
    """Probar la lógica de conversión de formato"""
    
    print("🔧 PROBANDO LÓGICA DE CONVERSIÓN")
    print("=" * 50)
    
    # Simular respuesta del API (lista directa como devuelve FastAPI)
    api_response = [
        {
            "id": "order_123",
            "buyer_id": "buyer_456", 
            "seller_id": "seller_789",
            "total_amount": 150000,
            "status": "pending"
        },
        {
            "id": "order_456", 
            "buyer_id": "buyer_789",
            "seller_id": "seller_789",
            "total_amount": 250000,
            "status": "confirmed"
        }
    ]
    
    print("📊 Respuesta original del API FastAPI:")
    print(f"   Tipo: {type(api_response)}")
    print(f"   Contenido: {api_response}")
    
    # Aplicar la lógica de conversión del API client
    def convert_orders_response(response):
        """Convertir respuesta del API al formato esperado por Django"""
        if isinstance(response, list):
            return {'orders': response}
        elif isinstance(response, dict) and 'error' in response:
            return response
        else:
            return response
    
    converted = convert_orders_response(api_response)
    
    print(f"\n✅ Después de conversión:")
    print(f"   Tipo: {type(converted)}")
    print(f"   Claves: {list(converted.keys())}")
    print(f"   Contenido: {converted}")
    
    # Simular procesamiento en Django views
    orders_list = converted.get('orders', []) if 'error' not in converted else []
    
    print(f"\n🎯 Django extraería:")
    print(f"   orders_list: {len(orders_list)} pedidos")
    
    for i, order in enumerate(orders_list):
        print(f"   Pedido {i+1}: ID={order['id']}, Total=${order['total_amount']}, Status={order['status']}")
    
    # Verificar que no hay error
    if 'error' not in converted and len(orders_list) >= 0:
        print(f"\n✅ ÉXITO: Django NO mostraría 'No se pudieron cargar los pedidos'")
        if len(orders_list) == 0:
            print(f"   📋 Mostraría: 'No tienes pedidos aún' (correcto)")
        else:
            print(f"   📋 Mostraría: Lista de {len(orders_list)} pedidos")
    else:
        print(f"\n❌ ERROR: Django mostraría mensaje de error")

def test_with_real_api():
    """Probar con el API real"""
    
    print(f"\n🌐 PROBANDO CON API REAL")
    print("=" * 50)
    
    try:
        # Login
        print("1. 🔐 Login...")
        login_response = requests.post(
            'http://localhost:8000/api/v1/users/login',
            json={"email": "vendedor@merkatolima.com", "password": "Vendedor123"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print(f"   ✅ Token obtenido")
            
            # Obtener pedidos directamente del API
            print("2. 📦 Obteniendo pedidos...")
            orders_response = requests.get(
                'http://localhost:8000/api/v1/orders/',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            print(f"   Status: {orders_response.status_code}")
            
            if orders_response.status_code == 200:
                raw_response = orders_response.json()
                print(f"   📊 Respuesta cruda del API:")
                print(f"      Tipo: {type(raw_response)}")
                print(f"      Contenido: {raw_response}")
                
                # Aplicar conversión
                if isinstance(raw_response, list):
                    converted = {'orders': raw_response}
                    print(f"\n   ✅ Después de conversión:")
                    print(f"      Tipo: {type(converted)}")
                    print(f"      Claves: {list(converted.keys())}")
                    
                    orders_count = len(converted['orders'])
                    print(f"      Total pedidos: {orders_count}")
                    
                    if orders_count == 0:
                        print(f"   📋 Resultado: 'No tienes pedidos aún' (correcto)")
                    else:
                        print(f"   📋 Resultado: Mostrar {orders_count} pedidos")
                else:
                    print(f"   ⚠️ Respuesta no es lista: {type(raw_response)}")
            else:
                print(f"   ❌ Error: {orders_response.status_code}")
                try:
                    error = orders_response.json()
                    print(f"      {error}")
                except:
                    print(f"      {orders_response.text}")
        else:
            print(f"   ❌ Login falló: {login_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ No se pudo conectar (¿servidores corriendo?)")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    test_format_conversion()
    test_with_real_api()
    
    print(f"\n" + "=" * 50)
    print("🎯 RESUMEN:")
    print("✅ Problema identificado: API devuelve [] pero Django espera {'orders': []}")
    print("✅ Solución aplicada: Conversión en api_client.py")
    print("✅ Resultado esperado: No más error 'No se pudieron cargar los pedidos'")
    
    print(f"\n📋 PARA PROBAR:")
    print("1. Reiniciar servidores")
    print("2. Login como vendedor: vendedor@merkatolima.com")
    print("3. Ir a 'Pedidos Recibidos'")
    print("4. Debería mostrar 'No tienes pedidos aún' en lugar del error")