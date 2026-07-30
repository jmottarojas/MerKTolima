#!/usr/bin/env python3
"""
Test completo del flujo: crear chat y verificar en panel Django.
"""

import requests
import re
import time

# Configuración
DJANGO_BASE_URL = "http://localhost:8001"
API_BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test completo del flujo de chat."""
    print("🔄 TEST COMPLETO DEL FLUJO DE CHAT")
    print("=" * 60)
    
    # 1. Login como vendedor en FastAPI
    print("\n1️⃣ Login vendedor en FastAPI...")
    seller_login = {
        "email": "seller@test.com",
        "password": "Password123"
    }
    
    seller_api_response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=seller_login)
    if seller_api_response.status_code != 200:
        print(f"❌ Error login vendedor: {seller_api_response.text}")
        return
    
    seller_token = seller_api_response.json().get('access_token')
    seller_headers = {"Authorization": f"Bearer {seller_token}"}
    
    # Obtener seller_id
    seller_profile = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=seller_headers)
    seller_id = seller_profile.json().get('id')
    print(f"✅ Seller ID: {seller_id}")
    
    # 2. Login como comprador en FastAPI
    print("\n2️⃣ Login comprador en FastAPI...")
    buyer_login = {
        "email": "buyer@test.com",
        "password": "Password123"
    }
    
    buyer_api_response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=buyer_login)
    if buyer_api_response.status_code != 200:
        print(f"❌ Error login comprador: {buyer_api_response.text}")
        return
    
    buyer_token = buyer_api_response.json().get('access_token')
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    
    # Obtener buyer_id
    buyer_profile = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=buyer_headers)
    buyer_id = buyer_profile.json().get('id')
    print(f"✅ Buyer ID: {buyer_id}")
    
    # 3. Crear producto
    print("\n3️⃣ Creando producto...")
    product_data = {
        "name": "Test Complete Flow Product",
        "description": "Producto para test completo",
        "price": 200000,
        "currency": "COP",
        "category": "Electrónicos",
        "images": ["https://via.placeholder.com/400x300"],
        "inventory_quantity": 15,
        "low_stock_threshold": 5
    }
    
    product_response = requests.post(f"{API_BASE_URL}/api/v1/products/", 
                                   json=product_data, headers=seller_headers)
    
    if product_response.status_code != 200:
        print(f"❌ Error creando producto: {product_response.text}")
        return
    
    product_id = product_response.json().get('id')
    print(f"✅ Producto creado: {product_id}")
    
    # 4. Enviar mensaje de chat
    print("\n4️⃣ Enviando mensaje de chat...")
    chat_data = {
        "product_id": product_id,
        "receiver_id": seller_id,
        "message": "¡Hola! Me interesa mucho este producto. ¿Podrías darme más información sobre las especificaciones técnicas?"
    }
    
    chat_response = requests.post(f"{API_BASE_URL}/api/v1/chat/messages", 
                                json=chat_data, headers=buyer_headers)
    
    if chat_response.status_code != 200:
        print(f"❌ Error enviando mensaje: {chat_response.text}")
        return
    
    print("✅ Mensaje enviado exitosamente")
    
    # 5. Verificar chats en API
    print("\n5️⃣ Verificando chats en API...")
    chats_api_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=seller_headers)
    
    if chats_api_response.status_code == 200:
        chats = chats_api_response.json()
        print(f"✅ API devuelve {len(chats)} chats")
        
        if chats:
            chat = chats[0]
            print(f"   Chat ID: {chat.get('id')}")
            print(f"   Product ID: {chat.get('product_id')}")
            print(f"   Mensajes: {chat.get('message_count', 0)}")
    else:
        print(f"❌ Error obteniendo chats de API: {chats_api_response.text}")
        return
    
    # 6. Login en Django con las MISMAS credenciales
    print("\n6️⃣ Login en Django...")
    django_session = requests.Session()
    
    # Obtener CSRF token
    login_page = django_session.get(f"{DJANGO_BASE_URL}/login/")
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if not csrf_token:
        print("❌ No se pudo obtener CSRF token")
        return
    
    # Login
    django_login_data = {
        'email': 'seller@test.com',
        'password': 'Password123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    django_login_response = django_session.post(f"{DJANGO_BASE_URL}/login/", 
                                              data=django_login_data, 
                                              headers={'Referer': f"{DJANGO_BASE_URL}/login/"})
    
    print(f"   Django login status: {django_login_response.status_code}")
    
    if django_login_response.status_code != 200:
        print("❌ Error en login Django")
        return
    
    print("✅ Login Django exitoso")
    
    # 7. Acceder al panel de chats INMEDIATAMENTE
    print("\n7️⃣ Accediendo al panel de chats...")
    
    # Pequeña pausa para asegurar que la sesión esté establecida
    time.sleep(1)
    
    chats_panel_response = django_session.get(f"{DJANGO_BASE_URL}/vendedor/chats/")
    
    if chats_panel_response.status_code == 200:
        print("✅ Panel de chats accesible")
        
        chats_html = chats_panel_response.text
        
        # Analizar contenido
        if "No tienes chats aún" in chats_html:
            print("❌ Panel muestra 'No tienes chats aún'")
            print("   PROBLEMA: Django no está obteniendo los chats de la API")
        else:
            print("✅ Panel muestra chats!")
            
            # Contar chats
            chat_count = chats_html.count('class="card"')
            print(f"   Chats encontrados en HTML: {chat_count}")
        
        # Buscar mensajes de error
        if "Error al cargar chats" in chats_html:
            print("❌ Error específico al cargar chats")
        
        # Guardar HTML para análisis
        with open('debug_complete_flow.html', 'w', encoding='utf-8') as f:
            f.write(chats_html)
        print("   HTML guardado en debug_complete_flow.html")
        
    else:
        print(f"❌ Error accediendo al panel: {chats_panel_response.status_code}")
    
    # 8. Verificar token en Django (si es posible)
    print("\n8️⃣ Información de debug...")
    print(f"   Seller ID (API): {seller_id}")
    print(f"   Buyer ID (API): {buyer_id}")
    print(f"   Product ID: {product_id}")
    print(f"   Token vendedor: {seller_token[:30]}...")
    
    # 9. Test directo del endpoint de chats desde Django
    print("\n9️⃣ Test adicional - verificar si Django puede hacer llamadas a API...")
    
    # Intentar acceder a un endpoint simple desde Django
    dashboard_response = django_session.get(f"{DJANGO_BASE_URL}/vendedor/")
    
    if dashboard_response.status_code == 200:
        print("✅ Dashboard accesible desde Django")
        
        # Buscar información del usuario en el dashboard
        if "seller@test.com" in dashboard_response.text:
            print("✅ Email del usuario visible en dashboard")
        else:
            print("⚠️ Email del usuario NO visible en dashboard")
    
    print(f"\n🎯 CONCLUSIÓN:")
    print(f"   - Chat creado en API: ✅")
    print(f"   - Login Django: ✅")
    print(f"   - Panel accesible: ✅")
    print(f"   - Chats visibles en panel: {'❌' if 'No tienes chats aún' in chats_html else '✅'}")

if __name__ == "__main__":
    test_complete_flow()