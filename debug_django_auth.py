#!/usr/bin/env python3
"""
Debug script para diagnosticar problemas de autenticación en Django.
"""

import requests
import re

# Configuración
DJANGO_BASE_URL = "http://localhost:8001"

def debug_django_authentication():
    """Debug de la autenticación en Django."""
    print("🔐 DIAGNOSTICANDO AUTENTICACIÓN DJANGO")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Login
    print("\n1️⃣ Realizando login...")
    login_url = f"{DJANGO_BASE_URL}/login/"
    
    # Obtener CSRF token
    login_page = session.get(login_url)
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if not csrf_token:
        print("❌ No se pudo obtener CSRF token")
        return
    
    # Login
    login_data = {
        'email': 'seller@test.com',
        'password': 'Password123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(login_url, data=login_data, headers={'Referer': login_url})
    print(f"   Login status: {login_response.status_code}")
    
    # 2. Verificar sesión en el dashboard
    print("\n2️⃣ Verificando sesión en dashboard...")
    dashboard_url = f"{DJANGO_BASE_URL}/vendedor/"
    dashboard_response = session.get(dashboard_url)
    
    if dashboard_response.status_code == 200:
        print("✅ Dashboard accesible")
        
        # Buscar información de usuario en el HTML
        if "seller@test.com" in dashboard_response.text:
            print("✅ Email del usuario encontrado en dashboard")
        else:
            print("⚠️ Email del usuario NO encontrado en dashboard")
        
        # Buscar indicadores de autenticación
        if "Panel de Vendedor" in dashboard_response.text:
            print("✅ Contenido de vendedor visible")
        
        if "Cerrar Sesión" in dashboard_response.text or "logout" in dashboard_response.text.lower():
            print("✅ Opción de logout visible")
        else:
            print("⚠️ Opción de logout NO visible")
    else:
        print(f"❌ Error accediendo al dashboard: {dashboard_response.status_code}")
        return
    
    # 3. Test directo de API desde Django
    print("\n3️⃣ Probando llamadas a API desde Django...")
    
    # Crear un endpoint de test para verificar la comunicación con la API
    test_api_url = f"{DJANGO_BASE_URL}/api/generar-productos-prueba/"
    
    # Obtener CSRF token para POST
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', dashboard_response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if csrf_token:
        print(f"✅ CSRF token obtenido para API test")
        
        # Test API call
        api_test_response = session.post(test_api_url, 
                                       data={'csrfmiddlewaretoken': csrf_token},
                                       headers={'Referer': dashboard_url})
        
        print(f"   API test status: {api_test_response.status_code}")
        
        if api_test_response.status_code == 200:
            try:
                api_result = api_test_response.json()
                print(f"✅ API respondió correctamente")
                print(f"   Mensaje: {api_result.get('message', 'N/A')}")
            except:
                print("⚠️ API respondió pero no es JSON válido")
        else:
            print(f"❌ Error en API test: {api_test_response.text[:200]}")
    else:
        print("❌ No se pudo obtener CSRF token para API test")
    
    # 4. Test específico del endpoint de chats
    print("\n4️⃣ Probando endpoint específico de chats...")
    
    # Simular la llamada que hace la vista seller_chats
    # Esto requiere hacer una petición GET que internamente llame a la API
    chats_url = f"{DJANGO_BASE_URL}/vendedor/chats/"
    chats_response = session.get(chats_url)
    
    print(f"   Chats panel status: {chats_response.status_code}")
    
    if chats_response.status_code == 200:
        chats_html = chats_response.text
        
        # Buscar mensajes de error en el HTML
        if "Error al cargar chats" in chats_html:
            print("❌ Error específico al cargar chats encontrado en HTML")
        elif "No tienes chats aún" in chats_html:
            print("⚠️ Panel muestra 'No tienes chats aún' - chats vacíos")
        else:
            print("✅ Panel de chats cargado sin errores obvios")
        
        # Buscar indicadores de datos de chat
        chat_count = chats_html.count('class="card"')
        print(f"   Tarjetas de chat en HTML: {chat_count}")
        
        # Buscar mensajes de Django
        if "messages" in chats_html and "alert" in chats_html:
            print("⚠️ Posibles mensajes de Django en el panel")
    else:
        print(f"❌ Error accediendo al panel de chats: {chats_response.status_code}")
    
    # 5. Verificar cookies de sesión
    print("\n5️⃣ Verificando cookies de sesión...")
    
    cookies = session.cookies
    session_cookie = None
    csrf_cookie = None
    
    for cookie in cookies:
        if 'session' in cookie.name.lower():
            session_cookie = cookie
            print(f"✅ Cookie de sesión encontrada: {cookie.name}")
        elif 'csrf' in cookie.name.lower():
            csrf_cookie = cookie
            print(f"✅ Cookie CSRF encontrada: {cookie.name}")
    
    if not session_cookie:
        print("❌ No se encontró cookie de sesión")
    
    if not csrf_cookie:
        print("❌ No se encontró cookie CSRF")
    
    print(f"\n📊 Total de cookies: {len(cookies)}")
    for cookie in cookies:
        print(f"   - {cookie.name}: {cookie.value[:20]}...")

if __name__ == "__main__":
    debug_django_authentication()