"""Test script para probar el chat a través de Django."""
import requests
import json

# Configuration
DJANGO_URL = "http://localhost:8001"
BUYER_EMAIL = "comprador@merkatolima.com"
BUYER_PASSWORD = "Comprador123"
PRODUCT_ID = "b15800e8-16b3-4ea6-9f94-0a71853f8fed"  # From previous test

print("\n" + "="*60)
print("💬 TEST DE CHAT A TRAVÉS DE DJANGO")
print("="*60)

# Create session to maintain cookies
session = requests.Session()

# Step 1: Login through Django
print("\n1️⃣ Iniciando sesión en Django...")
login_response = session.post(
    f"{DJANGO_URL}/login/",
    data={
        'email': BUYER_EMAIL,
        'password': BUYER_PASSWORD
    }
)

if login_response.status_code == 200 or login_response.status_code == 302:
    print("✅ Login exitoso en Django")
else:
    print(f"❌ Error en login Django: {login_response.status_code}")
    exit(1)

# Step 2: Get CSRF token
csrf_response = session.get(f"{DJANGO_URL}/producto/{PRODUCT_ID}/")
if csrf_response.status_code == 200:
    # Extract CSRF token from cookies
    csrf_token = session.cookies.get('csrftoken')
    print(f"✅ CSRF token obtenido: {csrf_token[:20]}...")
else:
    print(f"❌ Error obteniendo página del producto: {csrf_response.status_code}")
    exit(1)

# Step 3: Test sending message through Django
print("\n2️⃣ Enviando mensaje a través de Django...")
message_data = {
    'product_id': PRODUCT_ID,
    'receiver_id': '496e48dc-49b1-4e93-9eee-7c7233d89c5e',  # Seller ID from previous test
    'message': 'Hola, ¿está disponible este producto? (Test desde Django)'
}

send_response = session.post(
    f"{DJANGO_URL}/api/chat/send/",
    json=message_data,
    headers={
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
)

print(f"Status: {send_response.status_code}")
print(f"Response: {send_response.text}")

if send_response.status_code == 200:
    result = send_response.json()
    if result.get('success'):
        print("✅ Mensaje enviado exitosamente")
        print(f"   Mensaje: {result.get('message', {}).get('message')}")
        print(f"   Filtrado: {'Sí' if result.get('message', {}).get('is_filtered') else 'No'}")
    else:
        print(f"❌ Error: {result.get('error')}")
else:
    print(f"❌ Error HTTP: {send_response.status_code}")

# Step 4: Test getting messages through Django
print("\n3️⃣ Obteniendo mensajes a través de Django...")
messages_response = session.get(
    f"{DJANGO_URL}/api/chat/messages/{PRODUCT_ID}/",
    headers={
        'X-CSRFToken': csrf_token
    }
)

print(f"Status: {messages_response.status_code}")
print(f"Response: {messages_response.text}")

if messages_response.status_code == 200:
    result = messages_response.json()
    if result.get('success'):
        messages = result.get('messages', [])
        print(f"✅ Se obtuvieron {len(messages)} mensajes")
        for i, msg in enumerate(messages, 1):
            print(f"   {i}. {msg.get('message')} {'🛡️' if msg.get('is_filtered') else ''}")
    else:
        print(f"❌ Error: {result.get('error')}")
else:
    print(f"❌ Error HTTP: {messages_response.status_code}")

print("\n" + "="*60)
print("🎯 RESULTADO DEL TEST")
print("="*60)
if send_response.status_code == 200 and messages_response.status_code == 200:
    print("✅ Chat funcionando correctamente a través de Django")
    print("✅ Ahora puedes probar en el navegador:")
    print(f"   URL: {DJANGO_URL}/producto/{PRODUCT_ID}/")
    print("   Usuario: comprador@merkatolima.com / Comprador123")
else:
    print("❌ Hay problemas con el chat a través de Django")
print("="*60 + "\n")