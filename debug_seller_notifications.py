#!/usr/bin/env python3
"""
Debug script para diagnosticar problemas de notificaciones y panel de vendedor.
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"
DJANGO_BASE_URL = "http://localhost:8001"

def debug_seller_notifications():
    """Debug del sistema de notificaciones del vendedor."""
    print("🔍 DIAGNOSTICANDO SISTEMA DE NOTIFICACIONES")
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
    
    seller_token_data = response.json()
    seller_token = seller_token_data.get('access_token')
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    print(f"✅ Seller login exitoso")
    
    # 2. Obtener perfil del vendedor para obtener user_id
    profile_response = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=seller_headers)
    if profile_response.status_code == 200:
        seller_profile = profile_response.json()
        seller_id = seller_profile.get('id')
        print(f"✅ Seller ID obtenido: {seller_id}")
    else:
        print(f"❌ Error obteniendo perfil: {profile_response.text}")
        return
    
    # 3. Verificar chats del vendedor
    print("\n2️⃣ Verificando chats del vendedor...")
    chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=seller_headers)
    
    if chats_response.status_code == 200:
        chats = chats_response.json()
        print(f"✅ Chats encontrados: {len(chats)}")
        
        for i, chat in enumerate(chats, 1):
            print(f"\n   Chat {i}:")
            print(f"   - ID: {chat.get('id')}")
            print(f"   - Product ID: {chat.get('product_id')}")
            print(f"   - Buyer ID: {chat.get('buyer_id')}")
            print(f"   - Seller ID: {chat.get('seller_id')}")
            print(f"   - Mensajes: {chat.get('message_count', 0)}")
            print(f"   - Último mensaje: {chat.get('last_message_at')}")
            
            # Obtener mensajes de este chat
            messages_response = requests.get(f"{API_BASE_URL}/api/v1/chat/products/{chat.get('product_id')}/messages", 
                                           headers=seller_headers)
            if messages_response.status_code == 200:
                messages = messages_response.json()
                print(f"   - Mensajes detallados: {len(messages)}")
                for msg in messages:
                    print(f"     * {msg.get('sender_id')}: {msg.get('message')[:30]}...")
            else:
                print(f"   - ❌ Error obteniendo mensajes: {messages_response.text}")
    else:
        print(f"❌ Error obteniendo chats: {chats_response.text}")
    
    # 4. Verificar notificaciones
    print("\n3️⃣ Verificando notificaciones...")
    notifications_response = requests.get(f"{API_BASE_URL}/api/v1/chat/notifications", headers=seller_headers)
    
    if notifications_response.status_code == 200:
        notifications = notifications_response.json()
        print(f"✅ Notificaciones encontradas: {len(notifications)}")
        
        for i, notif in enumerate(notifications, 1):
            print(f"\n   Notificación {i}:")
            print(f"   - ID: {notif.get('id')}")
            print(f"   - Usuario: {notif.get('user_id')}")
            print(f"   - Tipo: {notif.get('type')}")
            print(f"   - Título: {notif.get('title')}")
            print(f"   - Mensaje: {notif.get('message')}")
            print(f"   - Leída: {notif.get('is_read')}")
            print(f"   - Fecha: {notif.get('created_at')}")
    else:
        print(f"❌ Error obteniendo notificaciones: {notifications_response.text}")
    
    # 5. Test del panel Django
    print("\n4️⃣ Probando panel Django...")
    
    # Simular login en Django
    django_session = requests.Session()
    
    # Obtener CSRF token
    csrf_response = django_session.get(f"{DJANGO_BASE_URL}/marketplace/login/")
    if csrf_response.status_code == 200:
        # Extraer CSRF token del HTML
        csrf_token = None
        for line in csrf_response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        if csrf_token:
            print(f"✅ CSRF token obtenido: {csrf_token[:20]}...")
            
            # Login en Django
            login_data = {
                'email': 'seller@test.com',
                'password': 'Password123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            login_response = django_session.post(f"{DJANGO_BASE_URL}/marketplace/login/", 
                                               data=login_data,
                                               headers={'Referer': f"{DJANGO_BASE_URL}/marketplace/login/"})
            
            if login_response.status_code == 200 or login_response.status_code == 302:
                print("✅ Login Django exitoso")
                
                # Probar acceso al panel de chats
                chats_panel_response = django_session.get(f"{DJANGO_BASE_URL}/marketplace/vendedor/chats/")
                
                print(f"Panel de chats response: {chats_panel_response.status_code}")
                
                if chats_panel_response.status_code == 200:
                    print("✅ Panel de chats accesible")
                    
                    # Buscar indicadores de chats en el HTML
                    html_content = chats_panel_response.text
                    if "No tienes chats aún" in html_content:
                        print("⚠️ El panel muestra 'No tienes chats aún'")
                    elif "Chat del Producto" in html_content or "mensaje" in html_content.lower():
                        print("✅ El panel muestra chats")
                    else:
                        print("❓ Estado del panel no claro")
                        
                    # Contar elementos de chat en el HTML
                    chat_cards = html_content.count('class="card"')
                    print(f"📊 Tarjetas de chat encontradas en HTML: {chat_cards}")
                    
                else:
                    print(f"❌ Error accediendo al panel: {chats_panel_response.status_code}")
                    print(f"Response: {chats_panel_response.text[:200]}...")
            else:
                print(f"❌ Error en login Django: {login_response.status_code}")
        else:
            print("❌ No se pudo obtener CSRF token")
    else:
        print(f"❌ Error obteniendo página de login: {csrf_response.status_code}")

def test_notification_creation():
    """Test específico para creación de notificaciones."""
    print("\n🔔 TESTING CREACIÓN DE NOTIFICACIONES")
    print("=" * 60)
    
    # Login como comprador
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
    
    # Login como vendedor
    seller_login = {
        "email": "seller@test.com",
        "password": "Password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=seller_login)
    if response.status_code != 200:
        print(f"❌ Error en seller login: {response.text}")
        return
    
    seller_token = response.json().get('access_token')
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    
    # Obtener seller_id
    profile_response = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=seller_headers)
    seller_id = profile_response.json().get('id')
    
    # Crear producto
    product_data = {
        "name": "Test Notification Product",
        "description": "Producto para probar notificaciones",
        "price": 100000,
        "currency": "COP",
        "category": "Electrónicos",
        "images": ["https://via.placeholder.com/400x300"],
        "inventory_quantity": 5,
        "low_stock_threshold": 2
    }
    
    product_response = requests.post(f"{API_BASE_URL}/api/v1/products/", 
                                   json=product_data, headers=seller_headers)
    
    if product_response.status_code != 200:
        print(f"❌ Error creando producto: {product_response.text}")
        return
    
    product_id = product_response.json().get('id')
    print(f"✅ Producto creado: {product_id}")
    
    # Verificar notificaciones ANTES del mensaje
    print("\n📋 Notificaciones ANTES del mensaje:")
    notif_before = requests.get(f"{API_BASE_URL}/api/v1/chat/notifications", headers=seller_headers)
    if notif_before.status_code == 200:
        notifications_before = notif_before.json()
        print(f"   Cantidad: {len(notifications_before)}")
    
    # Enviar mensaje
    chat_data = {
        "product_id": product_id,
        "receiver_id": seller_id,
        "message": "¿Este producto tiene garantía? Estoy muy interesado en comprarlo."
    }
    
    print(f"\n💬 Enviando mensaje...")
    print(f"   Product ID: {product_id}")
    print(f"   Receiver ID (seller): {seller_id}")
    print(f"   Message: {chat_data['message']}")
    
    chat_response = requests.post(f"{API_BASE_URL}/api/v1/chat/messages", 
                                json=chat_data, headers=buyer_headers)
    
    if chat_response.status_code == 200:
        print("✅ Mensaje enviado exitosamente")
        chat_result = chat_response.json()
        print(f"   Bloqueado: {chat_result.get('is_blocked', False)}")
    else:
        print(f"❌ Error enviando mensaje: {chat_response.text}")
        return
    
    # Verificar notificaciones DESPUÉS del mensaje
    print("\n📋 Notificaciones DESPUÉS del mensaje:")
    notif_after = requests.get(f"{API_BASE_URL}/api/v1/chat/notifications", headers=seller_headers)
    if notif_after.status_code == 200:
        notifications_after = notif_after.json()
        print(f"   Cantidad: {len(notifications_after)}")
        
        if len(notifications_after) > len(notifications_before):
            print("✅ Nueva notificación creada!")
            new_notif = notifications_after[0]  # Asumiendo que es la más reciente
            print(f"   - Título: {new_notif.get('title')}")
            print(f"   - Mensaje: {new_notif.get('message')}")
            print(f"   - Usuario: {new_notif.get('user_id')}")
        else:
            print("❌ No se creó nueva notificación")
    else:
        print(f"❌ Error obteniendo notificaciones: {notif_after.text}")

if __name__ == "__main__":
    debug_seller_notifications()
    test_notification_creation()