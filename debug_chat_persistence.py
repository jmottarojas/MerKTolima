#!/usr/bin/env python3
"""
Debug script para diagnosticar problemas de persistencia de chats.
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"

def debug_chat_persistence():
    """Debug de la persistencia de chats."""
    print("🔍 DIAGNOSTICANDO PERSISTENCIA DE CHATS")
    print("=" * 60)
    
    # 1. Login como vendedor
    print("\n1️⃣ Login como vendedor...")
    seller_login = {
        "email": "seller@test.com",
        "password": "Password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=seller_login)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.text}")
        return
    
    seller_token = response.json().get('access_token')
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    
    # Obtener seller_id
    profile_response = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=seller_headers)
    seller_profile = profile_response.json()
    seller_id = seller_profile.get('id')
    print(f"✅ Seller ID: {seller_id}")
    
    # 2. Login como comprador
    print("\n2️⃣ Login como comprador...")
    buyer_login = {
        "email": "buyer@test.com",
        "password": "Password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=buyer_login)
    if response.status_code != 200:
        print(f"❌ Error en buyer login: {response.text}")
        return
    
    buyer_token = response.json().get('access_token')
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    
    # Obtener buyer_id
    profile_response = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=buyer_headers)
    buyer_profile = profile_response.json()
    buyer_id = buyer_profile.get('id')
    print(f"✅ Buyer ID: {buyer_id}")
    
    # 3. Crear producto
    print("\n3️⃣ Creando producto...")
    product_data = {
        "name": "Test Chat Persistence Product",
        "description": "Producto para probar persistencia de chats",
        "price": 150000,
        "currency": "COP",
        "category": "Electrónicos",
        "images": ["https://via.placeholder.com/400x300"],
        "inventory_quantity": 10,
        "low_stock_threshold": 3
    }
    
    product_response = requests.post(f"{API_BASE_URL}/api/v1/products/", 
                                   json=product_data, headers=seller_headers)
    
    if product_response.status_code != 200:
        print(f"❌ Error creando producto: {product_response.text}")
        return
    
    product = product_response.json()
    product_id = product.get('id')
    print(f"✅ Producto creado: {product_id}")
    print(f"   Seller del producto: {product.get('seller_id')}")
    
    # 4. Verificar chats ANTES del mensaje
    print("\n4️⃣ Chats ANTES del mensaje:")
    
    # Chats del vendedor
    seller_chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=seller_headers)
    if seller_chats_response.status_code == 200:
        seller_chats = seller_chats_response.json()
        print(f"   Vendedor: {len(seller_chats)} chats")
    else:
        print(f"   ❌ Error obteniendo chats del vendedor: {seller_chats_response.text}")
    
    # Chats del comprador
    buyer_chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=buyer_headers)
    if buyer_chats_response.status_code == 200:
        buyer_chats = buyer_chats_response.json()
        print(f"   Comprador: {len(buyer_chats)} chats")
    else:
        print(f"   ❌ Error obteniendo chats del comprador: {buyer_chats_response.text}")
    
    # 5. Enviar mensaje
    print("\n5️⃣ Enviando mensaje...")
    chat_data = {
        "product_id": product_id,
        "receiver_id": seller_id,
        "message": "Hola, ¿este producto incluye envío gratis? Me interesa mucho comprarlo."
    }
    
    print(f"   Datos del mensaje:")
    print(f"   - Product ID: {product_id}")
    print(f"   - Sender ID (buyer): {buyer_id}")
    print(f"   - Receiver ID (seller): {seller_id}")
    print(f"   - Message: {chat_data['message']}")
    
    chat_response = requests.post(f"{API_BASE_URL}/api/v1/chat/messages", 
                                json=chat_data, headers=buyer_headers)
    
    if chat_response.status_code == 200:
        chat_result = chat_response.json()
        print("✅ Mensaje enviado exitosamente")
        print(f"   Bloqueado: {chat_result.get('is_blocked', False)}")
        
        # Mostrar detalles del mensaje creado
        message_data = chat_result.get('message', {})
        print(f"   Mensaje ID: {message_data.get('id')}")
        print(f"   Sender ID: {message_data.get('sender_id')}")
        print(f"   Receiver ID: {message_data.get('receiver_id')}")
        print(f"   Product ID: {message_data.get('product_id')}")
    else:
        print(f"❌ Error enviando mensaje: {chat_response.text}")
        return
    
    # 6. Verificar chats DESPUÉS del mensaje
    print("\n6️⃣ Chats DESPUÉS del mensaje:")
    
    # Chats del vendedor
    seller_chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=seller_headers)
    if seller_chats_response.status_code == 200:
        seller_chats = seller_chats_response.json()
        print(f"   Vendedor: {len(seller_chats)} chats")
        
        for i, chat in enumerate(seller_chats, 1):
            print(f"     Chat {i}:")
            print(f"     - ID: {chat.get('id')}")
            print(f"     - Product ID: {chat.get('product_id')}")
            print(f"     - Buyer ID: {chat.get('buyer_id')}")
            print(f"     - Seller ID: {chat.get('seller_id')}")
            print(f"     - Mensajes: {chat.get('message_count', 0)}")
    else:
        print(f"   ❌ Error obteniendo chats del vendedor: {seller_chats_response.text}")
    
    # Chats del comprador
    buyer_chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=buyer_headers)
    if buyer_chats_response.status_code == 200:
        buyer_chats = buyer_chats_response.json()
        print(f"   Comprador: {len(buyer_chats)} chats")
        
        for i, chat in enumerate(buyer_chats, 1):
            print(f"     Chat {i}:")
            print(f"     - ID: {chat.get('id')}")
            print(f"     - Product ID: {chat.get('product_id')}")
            print(f"     - Buyer ID: {chat.get('buyer_id')}")
            print(f"     - Seller ID: {chat.get('seller_id')}")
            print(f"     - Mensajes: {chat.get('message_count', 0)}")
    else:
        print(f"   ❌ Error obteniendo chats del comprador: {buyer_chats_response.text}")
    
    # 7. Verificar mensajes específicos del producto
    print("\n7️⃣ Mensajes del producto:")
    
    # Mensajes desde perspectiva del vendedor
    messages_seller_response = requests.get(f"{API_BASE_URL}/api/v1/chat/products/{product_id}/messages", 
                                          headers=seller_headers)
    if messages_seller_response.status_code == 200:
        messages_seller = messages_seller_response.json()
        print(f"   Vendedor ve: {len(messages_seller)} mensajes")
        for msg in messages_seller:
            print(f"     - {msg.get('sender_id')}: {msg.get('message')[:50]}...")
    else:
        print(f"   ❌ Error obteniendo mensajes (vendedor): {messages_seller_response.text}")
    
    # Mensajes desde perspectiva del comprador
    messages_buyer_response = requests.get(f"{API_BASE_URL}/api/v1/chat/products/{product_id}/messages", 
                                         headers=buyer_headers)
    if messages_buyer_response.status_code == 200:
        messages_buyer = messages_buyer_response.json()
        print(f"   Comprador ve: {len(messages_buyer)} mensajes")
        for msg in messages_buyer:
            print(f"     - {msg.get('sender_id')}: {msg.get('message')[:50]}...")
    else:
        print(f"   ❌ Error obteniendo mensajes (comprador): {messages_buyer_response.text}")
    
    # 8. Verificar notificaciones
    print("\n8️⃣ Notificaciones:")
    
    # Notificaciones del vendedor
    notif_seller_response = requests.get(f"{API_BASE_URL}/api/v1/chat/notifications", headers=seller_headers)
    if notif_seller_response.status_code == 200:
        notif_seller = notif_seller_response.json()
        print(f"   Vendedor: {len(notif_seller)} notificaciones")
        for notif in notif_seller:
            print(f"     - {notif.get('title')}: {notif.get('message')}")
    else:
        print(f"   ❌ Error obteniendo notificaciones del vendedor: {notif_seller_response.text}")
    
    # Notificaciones del comprador
    notif_buyer_response = requests.get(f"{API_BASE_URL}/api/v1/chat/notifications", headers=buyer_headers)
    if notif_buyer_response.status_code == 200:
        notif_buyer = notif_buyer_response.json()
        print(f"   Comprador: {len(notif_buyer)} notificaciones")
        for notif in notif_buyer:
            print(f"     - {notif.get('title')}: {notif.get('message')}")
    else:
        print(f"   ❌ Error obteniendo notificaciones del comprador: {notif_buyer_response.text}")
    
    print(f"\n🎯 RESUMEN:")
    print(f"   - Producto ID: {product_id}")
    print(f"   - Seller ID: {seller_id}")
    print(f"   - Buyer ID: {buyer_id}")
    print(f"   - Mensaje enviado: ✅")
    print(f"   - Chats del vendedor: {len(seller_chats) if 'seller_chats' in locals() else 'Error'}")
    print(f"   - Chats del comprador: {len(buyer_chats) if 'buyer_chats' in locals() else 'Error'}")
    print(f"   - Notificaciones del vendedor: {len(notif_seller) if 'notif_seller' in locals() else 'Error'}")

if __name__ == "__main__":
    debug_chat_persistence()