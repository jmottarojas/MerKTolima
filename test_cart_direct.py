"""Test script to directly test cart functionality with proper authentication."""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
BUYER_EMAIL = "comprador@merkatolima.com"
BUYER_PASSWORD = "Comprador123"
PRODUCT_ID = "e64a6552-a1ac-426a-a333-ebec6a4cef43"

print("\n" + "="*60)
print("🧪 TEST DIRECTO DE CARRITO")
print("="*60)

# Step 1: Login to get token
print("\n1️⃣ Iniciando sesión...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/users/login",
    json={"email": BUYER_EMAIL, "password": BUYER_PASSWORD}
)

print(f"   Status: {login_response.status_code}")
print(f"   Response: {login_response.text}")

if login_response.status_code != 200:
    print("❌ Error en login")
    exit(1)

login_data = login_response.json()
token = login_data.get("access_token")

if not token:
    print("❌ No se recibió token")
    exit(1)

print(f"✅ Token recibido: {token[:30]}...")

# Step 2: Get product to verify it exists
print("\n2️⃣ Verificando producto...")
product_response = requests.get(
    f"{BASE_URL}/api/v1/products/{PRODUCT_ID}"
)

print(f"   Status: {product_response.status_code}")
if product_response.status_code == 200:
    product = product_response.json()
    print(f"   ✅ Producto encontrado: {product.get('name')}")
    print(f"   Inventario: {product.get('inventory_quantity')}")
    print(f"   Estado: {product.get('status')}")
else:
    print(f"   ❌ Producto no encontrado: {product_response.text}")
    exit(1)

# Step 3: Add to cart
print("\n3️⃣ Agregando al carrito...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
cart_data = {
    "product_id": PRODUCT_ID,
    "quantity": 1
}

print(f"   URL: {BASE_URL}/api/v1/orders/cart/items")
print(f"   Headers: {headers}")
print(f"   Data: {cart_data}")

cart_response = requests.post(
    f"{BASE_URL}/api/v1/orders/cart/items",
    headers=headers,
    json=cart_data
)

print(f"\n📥 RESPUESTA:")
print(f"   Status: {cart_response.status_code}")
print(f"   Headers: {dict(cart_response.headers)}")
print(f"   Body: {cart_response.text}")

if cart_response.status_code == 200:
    cart = cart_response.json()
    print(f"\n✅ ÉXITO - Producto agregado al carrito")
    print(f"   Items en carrito: {len(cart.get('items', []))}")
    print(f"   Total: ${cart.get('total_amount')}")
else:
    print(f"\n❌ ERROR - No se pudo agregar al carrito")
    try:
        error_detail = cart_response.json()
        print(f"   Detalle: {error_detail}")
    except:
        print(f"   Texto: {cart_response.text}")

# Step 4: Get cart
print("\n4️⃣ Obteniendo carrito...")
get_cart_response = requests.get(
    f"{BASE_URL}/api/v1/orders/cart",
    headers=headers
)

print(f"   Status: {get_cart_response.status_code}")
if get_cart_response.status_code == 200:
    cart = get_cart_response.json()
    if cart:
        print(f"   ✅ Carrito obtenido")
        print(f"   Items: {len(cart.get('items', []))}")
        print(f"   Total: ${cart.get('total_amount')}")
    else:
        print(f"   ⚠️ Carrito vacío")
else:
    print(f"   ❌ Error: {get_cart_response.text}")

print("\n" + "="*60)
print("🏁 TEST COMPLETADO")
print("="*60 + "\n")
