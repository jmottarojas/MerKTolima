#!/usr/bin/env python3
"""
Test script para verificar el panel Django del vendedor.
"""

import requests
import re

# Configuración
DJANGO_BASE_URL = "http://localhost:8001"

def test_django_seller_panel():
    """Test del panel de vendedor en Django."""
    print("🌐 TESTING PANEL DJANGO DEL VENDEDOR")
    print("=" * 60)
    
    # Crear sesión
    session = requests.Session()
    
    # 1. Obtener página de login
    print("\n1️⃣ Obteniendo página de login...")
    login_url = f"{DJANGO_BASE_URL}/login/"
    
    try:
        login_page = session.get(login_url)
        print(f"   Status: {login_page.status_code}")
        
        if login_page.status_code == 200:
            print("✅ Página de login accesible")
            
            # Extraer CSRF token usando regex
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token obtenido: {csrf_token[:20]}...")
            else:
                print("❌ No se pudo obtener CSRF token")
                return
        else:
            print(f"❌ Error accediendo a login: {login_page.status_code}")
            return
    except Exception as e:
        print(f"❌ Error conectando a Django: {e}")
        return
    
    # 2. Login como vendedor
    print("\n2️⃣ Login como vendedor...")
    login_data = {
        'email': 'seller@test.com',
        'password': 'Password123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(login_url, data=login_data, 
                                headers={'Referer': login_url})
    
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 302:  # Redirect after successful login
        print("✅ Login exitoso (redirect)")
        redirect_url = login_response.headers.get('Location', '')
        print(f"   Redirect a: {redirect_url}")
    elif login_response.status_code == 200:
        # Verificar si hay mensajes de error
        if "error" in login_response.text.lower() or "invalid" in login_response.text.lower():
            print("❌ Login falló - credenciales inválidas")
            return
        else:
            print("✅ Login exitoso (sin redirect)")
    else:
        print(f"❌ Error en login: {login_response.status_code}")
        return
    
    # 3. Acceder al dashboard del vendedor
    print("\n3️⃣ Accediendo al dashboard del vendedor...")
    dashboard_url = f"{DJANGO_BASE_URL}/vendedor/"
    
    dashboard_response = session.get(dashboard_url)
    print(f"   Status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("✅ Dashboard accesible")
        
        # Verificar contenido del dashboard
        if "Panel de Vendedor" in dashboard_response.text:
            print("✅ Dashboard cargado correctamente")
        else:
            print("⚠️ Dashboard accesible pero contenido inesperado")
    else:
        print(f"❌ Error accediendo al dashboard: {dashboard_response.status_code}")
        return
    
    # 4. Acceder al panel de chats
    print("\n4️⃣ Accediendo al panel de chats...")
    chats_url = f"{DJANGO_BASE_URL}/vendedor/chats/"
    
    chats_response = session.get(chats_url)
    print(f"   Status: {chats_response.status_code}")
    
    if chats_response.status_code == 200:
        print("✅ Panel de chats accesible")
        
        # Analizar contenido del panel de chats
        chats_html = chats_response.text
        
        if "No tienes chats aún" in chats_html:
            print("⚠️ Panel muestra 'No tienes chats aún'")
            print("   Esto indica que los chats no se están cargando desde la API")
        elif "Mis Chats" in chats_html:
            print("✅ Panel de chats cargado")
            
            # Contar elementos de chat usando regex
            chat_cards = len(re.findall(r'class=["\']card["\']', chats_html))
            print(f"   Tarjetas de chat encontradas: {chat_cards}")
            
            # Buscar mensajes de error
            if "error" in chats_html.lower():
                print("⚠️ Posibles errores en el panel")
        else:
            print("❓ Contenido del panel no reconocido")
            
        # Guardar HTML para debug
        with open('debug_chats_panel.html', 'w', encoding='utf-8') as f:
            f.write(chats_html)
        print("   HTML guardado en debug_chats_panel.html")
        
    else:
        print(f"❌ Error accediendo al panel de chats: {chats_response.status_code}")
        if chats_response.status_code == 403:
            print("   Posible problema de permisos o autenticación")
        elif chats_response.status_code == 404:
            print("   URL no encontrada - verificar configuración de URLs")
    
    # 5. Verificar URLs disponibles
    print("\n5️⃣ Verificando URLs disponibles...")
    test_urls = [
        "/",
        "/vendedor/",
        "/vendedor/productos/",
        "/vendedor/chats/",
    ]
    
    for url in test_urls:
        full_url = f"{DJANGO_BASE_URL}{url}"
        try:
            response = session.get(full_url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {url} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} - Error: {e}")

if __name__ == "__main__":
    test_django_seller_panel()