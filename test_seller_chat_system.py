#!/usr/bin/env python3
"""
Test script para verificar el sistema de chat de vendedores.
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"
DJANGO_BASE_URL = "http://localhost:8001"

def test_login_and_create_product():
    """Test login y creación de producto."""
    print("🔐 Probando login de vendedor...")
    
    # Login
    login_data = {
        "email": "seller@test.com",
        "password": "Password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        print(f"✅ Login exitoso, token: {access_token[:20]}...")
        
        # Crear producto
        headers = {"Authorization": f"Bearer {access_token}"}
        product_data = {
            "name": "iPhone 15 Pro Max - Chat Test",
            "description": "Producto de prueba para sistema de chat",
            "price": 4500000,
            "currency": "COP",
            "category": "Electrónicos",
            "images": [
                "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop",
                "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop"
            ],
            "inventory_quantity": 10,
            "low_stock_threshold": 3
        }
        
        print("📦 Creando producto de prueba...")
        product_response = requests.post(f"{API_BASE_URL}/api/v1/products/", 
                                       json=product_data, headers=headers)
        
        print(f"Product creation response: {product_response.status_code}")
        
        if product_response.status_code == 200:
            product = product_response.json()
            print(f"✅ Producto creado: {product.get('id')}")
            print(f"   Nombre: {product.get('name')}")
            print(f"   Vistas: {product.get('view_count', 0)}")
            return product.get('id'), access_token
        else:
            print(f"❌ Error creando producto: {product_response.text}")
            return None, access_token
    else:
        print(f"❌ Error en login: {response.text}")
        return None, None

def test_chat_system(product_id, seller_token):
    """Test del sistema de chat."""
    if not product_id:
        print("❌ No hay producto para probar chat")
        return
    
    print(f"\n💬 Probando sistema de chat para producto: {product_id}")
    
    # Login como comprador
    buyer_login = {
        "email": "buyer@test.com",
        "password": "Password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=buyer_login)
    if response.status_code == 200:
        buyer_token_data = response.json()
        buyer_token = buyer_token_data.get('access_token')
        print(f"✅ Buyer login exitoso")
        
        # Obtener información del vendedor del producto
        headers = {"Authorization": f"Bearer {buyer_token}"}
        product_response = requests.get(f"{API_BASE_URL}/api/v1/products/{product_id}", 
                                      headers=headers)
        
        if product_response.status_code == 200:
            product = product_response.json()
            seller_id = product.get('seller_id')
            print(f"✅ Producto obtenido, seller_id: {seller_id}")
            
            # Enviar mensaje de chat
            chat_data = {
                "product_id": product_id,
                "receiver_id": seller_id,
                "message": "Hola, ¿está disponible este producto? ¿Incluye garantía?"
            }
            
            chat_response = requests.post(f"{API_BASE_URL}/api/v1/chat/messages", 
                                        json=chat_data, headers=headers)
            
            print(f"Chat message response: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print(f"✅ Mensaje enviado exitosamente")
                print(f"   Bloqueado: {chat_result.get('is_blocked', False)}")
                if chat_result.get('warning'):
                    print(f"   Advertencia: {chat_result.get('warning')}")
                
                # Obtener mensajes como vendedor
                seller_headers = {"Authorization": f"Bearer {seller_token}"}
                messages_response = requests.get(f"{API_BASE_URL}/api/v1/chat/products/{product_id}/messages", 
                                               headers=seller_headers)
                
                if messages_response.status_code == 200:
                    messages = messages_response.json()
                    print(f"✅ Mensajes obtenidos: {len(messages)} mensajes")
                    for msg in messages:
                        print(f"   - {msg.get('message')[:50]}...")
                else:
                    print(f"❌ Error obteniendo mensajes: {messages_response.text}")
                
                # Obtener chats del vendedor
                chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", 
                                            headers=seller_headers)
                
                if chats_response.status_code == 200:
                    chats = chats_response.json()
                    print(f"✅ Chats del vendedor: {len(chats)} chats")
                else:
                    print(f"❌ Error obteniendo chats: {chats_response.text}")
                
            else:
                print(f"❌ Error enviando mensaje: {chat_response.text}")
        else:
            print(f"❌ Error obteniendo producto: {product_response.text}")
    else:
        print(f"❌ Error en buyer login: {response.text}")

def test_view_counter(product_id, token):
    """Test del contador de vistas."""
    if not product_id:
        print("❌ No hay producto para probar contador")
        return
    
    print(f"\n👁️ Probando contador de vistas para producto: {product_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Obtener vistas actuales
    product_response = requests.get(f"{API_BASE_URL}/api/v1/products/{product_id}", 
                                  headers=headers)
    
    if product_response.status_code == 200:
        product = product_response.json()
        initial_views = product.get('view_count', 0)
        print(f"✅ Vistas iniciales: {initial_views}")
        
        # Incrementar vista
        view_response = requests.post(f"{API_BASE_URL}/api/v1/products/{product_id}/view", 
                                    headers=headers)
        
        if view_response.status_code == 200:
            print("✅ Vista incrementada")
            
            # Verificar incremento
            product_response2 = requests.get(f"{API_BASE_URL}/api/v1/products/{product_id}", 
                                           headers=headers)
            
            if product_response2.status_code == 200:
                product2 = product_response2.json()
                final_views = product2.get('view_count', 0)
                print(f"✅ Vistas finales: {final_views}")
                print(f"   Incremento: {final_views - initial_views}")
            else:
                print(f"❌ Error verificando vistas: {product_response2.text}")
        else:
            print(f"❌ Error incrementando vista: {view_response.text}")
    else:
        print(f"❌ Error obteniendo producto: {product_response.text}")

if __name__ == "__main__":
    print("🧪 TESTING SELLER CHAT SYSTEM")
    print("=" * 50)
    
    # Test 1: Login y crear producto
    product_id, seller_token = test_login_and_create_product()
    
    # Test 2: Sistema de chat
    test_chat_system(product_id, seller_token)
    
    # Test 3: Contador de vistas
    test_view_counter(product_id, seller_token)
    
    print("\n" + "=" * 50)
    print("🎉 Tests completados!")
    
    if product_id:
        print(f"\n🌐 Puedes probar el sistema manualmente en:")
        print(f"   - Producto: http://localhost:8001/marketplace/producto/{product_id}/")
        print(f"   - Panel vendedor: http://localhost:8001/marketplace/vendedor/")
        print(f"   - Chats vendedor: http://localhost:8001/marketplace/vendedor/chats/")
        print(f"\n👥 Usuarios de prueba:")
        print(f"   - Vendedor: seller@test.com / Password123")
        print(f"   - Comprador: buyer@test.com / Password123")