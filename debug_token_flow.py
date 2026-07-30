#!/usr/bin/env python3
"""
Debug script para verificar el flujo de tokens entre Django y FastAPI.
"""

import requests
import re
import json

# Configuración
DJANGO_BASE_URL = "http://localhost:8001"
API_BASE_URL = "http://localhost:8000"

def debug_token_flow():
    """Debug del flujo de tokens."""
    print("🔑 DIAGNOSTICANDO FLUJO DE TOKENS")
    print("=" * 60)
    
    # 1. Login directo en FastAPI para obtener token
    print("\n1️⃣ Login directo en FastAPI...")
    
    login_data = {
        "email": "seller@test.com",
        "password": "Password123"
    }
    
    api_login_response = requests.post(f"{API_BASE_URL}/api/v1/users/login", json=login_data)
    
    if api_login_response.status_code == 200:
        token_data = api_login_response.json()
        direct_token = token_data.get('access_token')
        print(f"✅ Token directo obtenido: {direct_token[:30]}...")
        
        # Test directo con token
        headers = {"Authorization": f"Bearer {direct_token}"}
        
        # Obtener perfil
        profile_response = requests.get(f"{API_BASE_URL}/api/v1/users/profile", headers=headers)
        if profile_response.status_code == 200:
            profile = profile_response.json()
            seller_id = profile.get('id')
            print(f"✅ Perfil obtenido - Seller ID: {seller_id}")
            
            # Obtener chats directamente
            chats_response = requests.get(f"{API_BASE_URL}/api/v1/chat/my-chats", headers=headers)
            if chats_response.status_code == 200:
                chats = chats_response.json()
                print(f"✅ Chats obtenidos directamente: {len(chats)} chats")
                
                for i, chat in enumerate(chats, 1):
                    print(f"   Chat {i}: Product {chat.get('product_id')[:8]}... - {chat.get('message_count', 0)} mensajes")
            else:
                print(f"❌ Error obteniendo chats directamente: {chats_response.status_code}")
                print(f"   Response: {chats_response.text}")
        else:
            print(f"❌ Error obteniendo perfil: {profile_response.status_code}")
    else:
        print(f"❌ Error en login directo: {api_login_response.status_code}")
        return
    
    # 2. Login a través de Django
    print("\n2️⃣ Login a través de Django...")
    
    django_session = requests.Session()
    
    # Obtener página de login
    login_page = django_session.get(f"{DJANGO_BASE_URL}/login/")
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
    
    login_response = django_session.post(f"{DJANGO_BASE_URL}/login/", 
                                       data=login_data, 
                                       headers={'Referer': f"{DJANGO_BASE_URL}/login/"})
    
    print(f"   Django login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login Django exitoso")
        
        # 3. Verificar si Django puede acceder a la API
        print("\n3️⃣ Probando acceso a API desde Django...")
        
        # Crear un endpoint de test personalizado para verificar el token
        test_endpoint_code = '''
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .api_client import api_client

@csrf_exempt
def test_api_token(request):
    """Test endpoint para verificar token."""
    try:
        # Verificar si hay token en la sesión
        token = request.session.get('user_token')
        if not token:
            return JsonResponse({
                'error': 'No token in session',
                'session_keys': list(request.session.keys())
            })
        
        # Probar llamada a la API
        response = api_client._make_request('GET', '/api/v1/users/profile', request=request)
        
        return JsonResponse({
            'success': True,
            'token_present': bool(token),
            'token_preview': token[:30] if token else None,
            'api_response': response,
            'session_user_id': request.session.get('user_id'),
            'session_user_role': request.session.get('user_role')
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'session_keys': list(request.session.keys())
        })
'''
        
        print("   Necesitamos crear un endpoint de test en Django...")
        print("   Por ahora, vamos a probar el panel de chats directamente")
        
        # 4. Acceder al panel de chats
        print("\n4️⃣ Accediendo al panel de chats desde Django...")
        
        chats_response = django_session.get(f"{DJANGO_BASE_URL}/vendedor/chats/")
        
        if chats_response.status_code == 200:
            print("✅ Panel de chats accesible")
            
            chats_html = chats_response.text
            
            # Buscar indicadores de problemas
            if "No tienes chats aún" in chats_html:
                print("⚠️ Panel muestra 'No tienes chats aún'")
                print("   Esto sugiere que la API no está devolviendo chats")
            
            # Buscar mensajes de error de Django
            if "Error al cargar chats" in chats_html:
                print("❌ Error específico al cargar chats")
            
            # Buscar logs de debug en el HTML (si están habilitados)
            if "📤 ENVIANDO REQUEST A FASTAPI" in chats_html:
                print("✅ Logs de API client encontrados en HTML")
            elif "NO HAY TOKEN" in chats_html:
                print("❌ Logs indican que no hay token")
            
        else:
            print(f"❌ Error accediendo al panel: {chats_response.status_code}")
    
    # 5. Comparar tokens
    print("\n5️⃣ Comparando tokens...")
    
    print(f"   Token directo FastAPI: {direct_token[:30]}...")
    
    # Intentar extraer el token de Django (esto requeriría modificar el código)
    print("   Token de Django: [Necesita endpoint de debug]")
    
    # 6. Recomendaciones
    print("\n6️⃣ Recomendaciones:")
    print("   1. Verificar que el token se guarde correctamente en la sesión Django")
    print("   2. Verificar que api_client._make_request reciba el request correctamente")
    print("   3. Verificar que no haya problemas de CORS o headers")
    print("   4. Agregar logs detallados en la vista seller_chats")

if __name__ == "__main__":
    debug_token_flow()