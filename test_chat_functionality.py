"""Test script para probar la funcionalidad del chat."""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
SELLER_EMAIL = "vendedor@merkatolima.com"
SELLER_PASSWORD = "Vendedor123"
BUYER_EMAIL = "comprador@merkatolima.com"
BUYER_PASSWORD = "Comprador123"

print("\n" + "="*60)
print("💬 TEST DE FUNCIONALIDAD DEL CHAT")
print("="*60)

# Step 1: Login as seller and create product
print("\n1️⃣ Creando producto como vendedor...")
seller_login = requests.post(
    f"{BASE_URL}/api/v1/users/login",
    json={"email": SELLER_EMAIL, "password": SELLER_PASSWORD}
)

if seller_login.status_code != 200:
    print(f"❌ Error en login vendedor: {seller_login.text}")
    exit(1)

seller_token = seller_login.json().get("access_token")
seller_id = requests.post(
    f"{BASE_URL}/api/v1/users/login",
    json={"email": SELLER_EMAIL, "password": SELLER_PASSWORD}
).json()

# Get seller ID from token (simplified)
import jwt
seller_payload = jwt.decode(seller_token, options={"verify_signature": False})
seller_user_id = seller_payload.get("sub")

print(f"✅ Vendedor logueado: {seller_user_id}")

# Create product
product_data = {
    "name": "Producto para Chat Test",
    "description": "Este producto es para probar el sistema de chat entre vendedor y comprador",
    "price": 75000,
    "currency": "COP",
    "category": "Electrónicos",
    "images": ["/media/test-chat.jpg"],
    "inventory_quantity": 50,
    "low_stock_threshold": 5
}

product_response = requests.post(
    f"{BASE_URL}/api/v1/products/",
    headers={
        "Authorization": f"Bearer {seller_token}",
        "Content-Type": "application/json"
    },
    json=product_data
)

if product_response.status_code != 200:
    print(f"❌ Error creando producto: {product_response.text}")
    exit(1)

product = product_response.json()
product_id = product.get("id")
print(f"✅ Producto creado: {product.get('name')}")
print(f"   ID: {product_id}")

# Step 2: Login as buyer
print("\n2️⃣ Iniciando sesión como comprador...")
buyer_login = requests.post(
    f"{BASE_URL}/api/v1/users/login",
    json={"email": BUYER_EMAIL, "password": BUYER_PASSWORD}
)

if buyer_login.status_code != 200:
    print(f"❌ Error en login comprador: {buyer_login.text}")
    exit(1)

buyer_token = buyer_login.json().get("access_token")
buyer_payload = jwt.decode(buyer_token, options={"verify_signature": False})
buyer_user_id = buyer_payload.get("sub")

print(f"✅ Comprador logueado: {buyer_user_id}")

# Step 3: Test chat messages
print("\n3️⃣ Probando mensajes de chat...")

# Test messages to send
test_messages = [
    {
        "message": "Hola, ¿está disponible este producto?",
        "should_be_blocked": False,
        "description": "Mensaje normal"
    },
    {
        "message": "¿Cuál es el estado del producto?",
        "should_be_blocked": False,
        "description": "Pregunta sobre el producto"
    },
    {
        "message": "Escríbeme a mi correo usuario@gmail.com",
        "should_be_blocked": True,
        "description": "Mensaje con email (debe ser bloqueado)"
    },
    {
        "message": "Llámame al 300 123 4567 para coordinar",
        "should_be_blocked": True,
        "description": "Mensaje con teléfono (debe ser bloqueado)"
    },
    {
        "message": "Hablemos por whatsapp",
        "should_be_blocked": True,
        "description": "Mensaje con WhatsApp (debe ser bloqueado)"
    },
    {
        "message": "Ve mi perfil en www.instagram.com/usuario",
        "should_be_blocked": True,
        "description": "Mensaje con URL (debe ser bloqueado)"
    }
]

headers = {
    "Authorization": f"Bearer {buyer_token}",
    "Content-Type": "application/json"
}

for i, test_msg in enumerate(test_messages, 1):
    print(f"\n   📝 Test {i}: {test_msg['description']}")
    print(f"      Mensaje: '{test_msg['message']}'")
    
    # Send message
    chat_data = {
        "product_id": product_id,
        "receiver_id": seller_user_id,
        "message": test_msg["message"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/messages",
        headers=headers,
        json=chat_data
    )
    
    if response.status_code == 200:
        result = response.json()
        message_data = result.get("message", {})
        is_blocked = result.get("is_blocked", False)
        warning = result.get("warning")
        
        print(f"      ✅ Enviado exitosamente")
        print(f"      📤 Mensaje final: '{message_data.get('message')}'")
        print(f"      🛡️ Filtrado: {'Sí' if message_data.get('is_filtered') else 'No'}")
        
        if warning:
            print(f"      ⚠️ Advertencia: {warning}")
        
        # Verify filtering worked as expected
        if test_msg["should_be_blocked"] and not message_data.get("is_filtered"):
            print(f"      ❌ ERROR: Mensaje debería haber sido filtrado")
        elif not test_msg["should_be_blocked"] and message_data.get("is_filtered"):
            print(f"      ❌ ERROR: Mensaje no debería haber sido filtrado")
        else:
            print(f"      ✅ Filtrado funcionó correctamente")
    else:
        print(f"      ❌ Error enviando mensaje: {response.text}")

# Step 4: Get all messages
print("\n4️⃣ Obteniendo historial de mensajes...")
messages_response = requests.get(
    f"{BASE_URL}/api/v1/chat/products/{product_id}/messages",
    headers=headers
)

if messages_response.status_code == 200:
    messages = messages_response.json()
    print(f"✅ Se obtuvieron {len(messages)} mensajes")
    
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. {msg.get('message')} {'🛡️' if msg.get('is_filtered') else ''}")
else:
    print(f"❌ Error obteniendo mensajes: {messages_response.text}")

# Step 5: Get chat stats
print("\n5️⃣ Obteniendo estadísticas del chat...")
stats_response = requests.get(
    f"{BASE_URL}/api/v1/chat/products/{product_id}/stats",
    headers=headers
)

if stats_response.status_code == 200:
    stats_data = stats_response.json()
    stats = stats_data.get("stats", {})
    print(f"✅ Estadísticas del chat:")
    print(f"   - Total chats: {stats.get('total_chats')}")
    print(f"   - Total mensajes: {stats.get('total_messages')}")
    print(f"   - Mensajes bloqueados: {stats.get('blocked_messages')}")
    print(f"   - Chats activos: {stats.get('active_chats')}")
else:
    print(f"❌ Error obteniendo estadísticas: {stats_response.text}")

print("\n" + "="*60)
print("🎯 INSTRUCCIONES PARA PROBAR EN EL FRONTEND:")
print("="*60)
print(f"1. Ve a: http://localhost:8001/producto/{product_id}/")
print("2. Inicia sesión como comprador (comprador@merkatolima.com / Comprador123)")
print("3. Desplázate hacia abajo hasta ver 'Preguntas al Vendedor'")
print("4. Prueba enviar mensajes normales y con información de contacto")
print("5. Los mensajes con contacto deben aparecer como [INFORMACIÓN BLOQUEADA]")
print("\n💡 MENSAJES DE PRUEBA:")
print("   ✅ Normal: '¿Está disponible este producto?'")
print("   ❌ Email: 'Escríbeme a usuario@gmail.com'")
print("   ❌ Teléfono: 'Llámame al 300 123 4567'")
print("   ❌ WhatsApp: 'Hablemos por whatsapp'")
print("="*60 + "\n")