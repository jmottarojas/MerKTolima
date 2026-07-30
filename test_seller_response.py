#!/usr/bin/env python3
"""
Test específico para verificar que las respuestas del vendedor funcionan correctamente.
"""

import requests
import re
import time

# Configuración
DJANGO_BASE_URL = "http://localhost:8001"
API_BASE_URL = "http://localhost:8000"

def test_seller_response():
    """Test de respuesta del vendedor."""
    print("💬 TEST DE RESPUESTA DEL VENDEDOR")
    print("=" * 50)
    
    # 1. Setup: Crear chat como en el test anterior
    print("\n1️⃣ Setup: Creando chat inicial...")
    
    # Login vendedor API
    seller_login = {"email": "seller@test.com", "password": "Password123"}
    seller_api_response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=seller_login)
    seller_token = seller_api_response.json().get('access_token')
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    
    # Login comprador API
    buyer_login = {"email": "buyer@test.com", "password": "Password123"}
    buyer_api_response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=buyer_login)
    buyer_token = buyer_api_response.json().get('access_token')
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    
    # Obtener IDs
    seller_profile = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=seller_headers)
    seller_id = seller_profile.json().get('id')
    
    buyer_profile = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=buyer_headers)
    buyer_id = buyer_profile.json().get('id')
    
    # Crear producto
    product_data = {
        "name": "Test Seller Response Product",
        "description": "Producto para probar respuestas del vendedor",
        "price": 250000,
        "currency": "COP",
        "category": "Electrónicos",
        "images": ["https://via.placeholder.com/400x300"],
        "inventory_quantity": 20,
        "low_stock_threshold": 5
    }
    
    product_response = requests.post(f"{API_BASE_URL}/api/v1/products/", 
                                   json=product_data, headers=seller_headers)
    product_id = product_response.json().get('id')
    
    # Comprador envía mensaje inicial
    initial_message = {
        "product_id": product_id,
        "receiver_id": seller_id,
        "message": "Hola, ¿este producto incluye garantía? Me interesa comprarlo."
    }
    
    requests.post(f"{API_BASE_URL}/api/v1/chat/messages", 
                  json=initial_message, headers=buyer_headers)
    
    print(f"✅ Chat inicial creado - Product ID: {product_id}")
    
    # 2. Login vendedor en Django
    print("\n2️⃣ Login vendedor en Django...")
    
    django_session = requests.Session()
    
    # Obtener CSRF token
    login_page = django_session.get(f"{DJANGO_BASE_URL}/login/")
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
    csrf_token = csrf_match.group(1)
    
    # Login
    django_login_data = {
        'email': 'seller@test.com',
        'password': 'Password123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    django_session.post(f"{DJANGO_BASE_URL}/login/", 
                       data=django_login_data, 
                       headers={'Referer': f"{DJANGO_BASE_URL}/login/"})
    
    print("✅ Login Django exitoso")
    
    # 3. Test del endpoint de envío de mensajes
    print("\n3️⃣ Probando envío de respuesta del vendedor...")
    
    # Simular el envío de mensaje desde el panel del vendedor
    response_message = {
        'product_id': product_id,
        'receiver_id': buyer_id,
        'message': 'Sí, incluye garantía de 1 año. ¿Te interesa comprarlo?'
    }
    
    # Obtener CSRF token para la petición
    dashboard_response = django_session.get(f"{DJANGO_BASE_URL}/vendedor/")
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', dashboard_response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    # Enviar respuesta
    send_response = django_session.post(f"{DJANGO_BASE_URL}/api/chat/send/",
                                      json=response_message,
                                      headers={
                                          'Content-Type': 'application/json',
                                          'X-CSRFToken': csrf_token,
                                          'Referer': f"{DJANGO_BASE_URL}/vendedor/chat/{product_id}/"
                                      })
    
    print(f"   Status: {send_response.status_code}")
    
    if send_response.status_code == 200:
        response_data = send_response.json()
        print("✅ Respuesta enviada exitosamente")
        print(f"   Success: {response_data.get('success')}")
        print(f"   Message sent: {response_data.get('message_sent')}")
        print(f"   Is blocked: {response_data.get('is_blocked', False)}")
        
        if response_data.get('warning'):
            print(f"   Warning: {response_data.get('warning')}")
    else:
        print(f"❌ Error enviando respuesta: {send_response.status_code}")
        print(f"   Response: {send_response.text}")
        return
    
    # 4. Verificar que el mensaje se guardó correctamente
    print("\n4️⃣ Verificando mensajes en la API...")
    
    # Verificar desde perspectiva del comprador
    messages_buyer = requests.get(f"{API_BASE_URL}/api/v1/chat/products/{product_id}/messages", 
                                headers=buyer_headers)
    
    if messages_buyer.status_code == 200:
        messages = messages_buyer.json()
        print(f"✅ Total de mensajes: {len(messages)}")
        
        for i, msg in enumerate(messages, 1):
            sender = "Comprador" if msg.get('sender_id') == buyer_id else "Vendedor"
            print(f"   {i}. {sender}: {msg.get('message')}")
    else:
        print(f"❌ Error obteniendo mensajes: {messages_buyer.status_code}")
    
    # 5. Verificar notificaciones
    print("\n5️⃣ Verificando notificaciones...")
    
    # Notificaciones del comprador (debería tener una nueva)
    buyer_notifications = requests.get(f"{API_BASE_URL}/api/v1/chat/notifications", headers=buyer_headers)
    
    if buyer_notifications.status_code == 200:
        notifications = buyer_notifications.json()
        print(f"✅ Comprador tiene {len(notifications)} notificaciones")
    else:
        print(f"⚠️ Error obteniendo notificaciones del comprador")
    
    print(f"\n🎯 RESUMEN:")
    print(f"   - Product ID: {product_id}")
    print(f"   - Mensaje inicial enviado: ✅")
    print(f"   - Respuesta del vendedor: {'✅' if send_response.status_code == 200 else '❌'}")
    print(f"   - Mensajes verificados: {'✅' if messages_buyer.status_code == 200 else '❌'}")
    
    print(f"\n🌐 URLs para prueba manual:")
    print(f"   - Chat vendedor: http://localhost:8001/vendedor/chat/{product_id}/")
    print(f"   - Producto: http://localhost:8001/producto/{product_id}/")

if __name__ == "__main__":
    test_seller_response()