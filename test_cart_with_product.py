"""Test script to create product and test cart functionality."""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
SELLER_EMAIL = "vendedor@merkatolima.com"
SELLER_PASSWORD = "Vendedor123"
BUYER_EMAIL = "comprador@merkatolima.com"
BUYER_PASSWORD = "Comprador123"

print("\n" + "="*60)
print("🧪 TEST COMPLETO: CREAR PRODUCTO Y AGREGAR AL CARRITO")
print("="*60)

# Step 1: Login as seller
print("\n1️⃣ Iniciando sesión como vendedor...")
seller_login = requests.post(
    f"{BASE_URL}/api/v1/users/login",
    json={"email": SELLER_EMAIL, "password": SELLER_PASSWORD}
)

if seller_login.status_code != 200:
    print(f"❌ Error en login vendedor: {seller_login.text}")
    exit(1)

seller_token = seller_login.json().get("access_token")
print(f"✅ Token vendedor: {seller_token[:30]}...")

# Step 2: Create product
print("\n2️⃣ Creando producto de prueba...")
product_data = {
    "name": "Producto Test Carrito",
    "description": "Producto para probar funcionalidad del carrito",
    "price": 50000,
    "currency": "COP",
    "category": "Electrónicos",
    "images": ["/media/test.jpg"],
    "inventory_quantity": 100,
    "low_stock_threshold": 10
}

product_response = requests.post(
    f"{BASE_URL}/api/v1/products/",
    headers={
        "Authorization": f"Bearer {seller_token}",
        "Content-Type": "application/json"
    },
    json=product_data
)

print(f"   Status: {product_response.status_code}")
if product_response.status_code != 200:
    print(f"   ❌ Error: {product_response.text}")
    exit(1)

product = product_response.json()
product_id = product.get("id")
print(f"   ✅ Producto creado: {product.get('name')}")
print(f"   ID: {product_id}")
print(f"   Inventario: {product.get('inventory_quantity')}")

# Step 3: Login as buyer
print("\n3️⃣ Iniciando sesión como comprador...")
buyer_login = requests.post(
    f"{BASE_URL}/api/v1/users/login",
    json={"email": BUYER_EMAIL, "password": BUYER_PASSWORD}
)

if buyer_login.status_code != 200:
    print(f"❌ Error en login comprador: {buyer_login.text}")
    exit(1)

buyer_token = buyer_login.json().get("access_token")
print(f"✅ Token comprador: {buyer_token[:30]}...")

# Step 4: Add to cart
print("\n4️⃣ Agregando producto al carrito...")
headers = {
    "Authorization": f"Bearer {buyer_token}",
    "Content-Type": "application/json"
}
cart_data = {
    "product_id": product_id,
    "quantity": 2
}

print(f"   URL: {BASE_URL}/api/v1/orders/cart/items")
print(f"   Data: {cart_data}")

cart_response = requests.post(
    f"{BASE_URL}/api/v1/orders/cart/items",
    headers=headers,
    json=cart_data
)

print(f"\n📥 RESPUESTA ADD TO CART:")
print(f"   Status: {cart_response.status_code}")
print(f"   Body: {cart_response.text[:500]}")

if cart_response.status_code == 200:
    cart = cart_response.json()
    print(f"\n✅ ÉXITO - Producto agregado al carrito")
    print(f"   Items en carrito: {len(cart.get('items', []))}")
    print(f"   Total: ${cart.get('total_amount')} {cart.get('currency')}")
    
    # Show cart items
    for item in cart.get('items', []):
        print(f"   - Producto: {item.get('product_id')}")
        print(f"     Cantidad: {item.get('quantity')}")
        print(f"     Precio unitario: ${item.get('unit_price')}")
        print(f"     Subtotal: ${item.get('total_price')}")
else:
    print(f"\n❌ ERROR - No se pudo agregar al carrito")
    try:
        error_detail = cart_response.json()
        print(f"   Detalle: {json.dumps(error_detail, indent=2)}")
    except:
        print(f"   Texto: {cart_response.text}")

# Step 5: Get cart
print("\n5️⃣ Obteniendo carrito completo...")
get_cart_response = requests.get(
    f"{BASE_URL}/api/v1/orders/cart",
    headers=headers
)

print(f"   Status: {get_cart_response.status_code}")
if get_cart_response.status_code == 200:
    cart = get_cart_response.json()
    if cart:
        print(f"   ✅ Carrito obtenido")
        print(f"   ID: {cart.get('id')}")
        print(f"   User ID: {cart.get('user_id')}")
        print(f"   Items: {len(cart.get('items', []))}")
        print(f"   Total: ${cart.get('total_amount')} {cart.get('currency')}")
    else:
        print(f"   ⚠️ Carrito vacío (null)")
else:
    print(f"   ❌ Error: {get_cart_response.text}")

print("\n" + "="*60)
print("🏁 TEST COMPLETADO")
print("="*60 + "\n")
