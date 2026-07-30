"""Script para probar el API directamente y ver errores."""

import requests
import json

API_URL = "http://localhost:8000"

def test_cart():
    """Probar agregar al carrito directamente."""
    
    print("\n" + "="*60)
    print("🧪 PRUEBA DIRECTA DEL API")
    print("="*60 + "\n")
    
    # 1. Login como comprador
    print("1️⃣  Iniciando sesión...")
    login_data = {
        "email": "comprador@merkatolima.com",
        "password": "Comprador123"
    }
    
    response = requests.post(f"{API_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"   ❌ Error en login: {response.status_code}")
        print(f"   {response.text}")
        return
    
    token_data = response.json()
    token = token_data.get('access_token')
    print(f"   ✅ Login exitoso")
    print(f"   Token: {token[:20]}...\n")
    
    # 2. Listar productos disponibles
    print("2️⃣  Listando productos...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/api/v1/products/", headers=headers)
    
    if response.status_code != 200:
        print(f"   ❌ Error listando productos: {response.status_code}")
        return
    
    products_data = response.json()
    products = products_data.get('products', [])
    
    if not products:
        print("   ⚠️  No hay productos en el sistema")
        print("   Necesitas crear un producto primero como vendedor\n")
        return
    
    print(f"   ✅ Encontrados {len(products)} producto(s)\n")
    
    # Mostrar productos
    for i, product in enumerate(products, 1):
        print(f"   Producto {i}:")
        print(f"      ID: {product['id']}")
        print(f"      Nombre: {product['name']}")
        print(f"      Precio: ${product['price']} {product['currency']}")
        print(f"      Inventario: {product['inventory_quantity']}")
        print(f"      Status: {product['status']}")
        print(f"      Disponible: {'✅ Sí' if product['status'] == 'active' and product['inventory_quantity'] > 0 else '❌ No'}")
        print()
    
    # 3. Intentar agregar el primer producto al carrito
    if products:
        product = products[0]
        print(f"3️⃣  Intentando agregar al carrito: {product['name']}")
        print(f"   Product ID: {product['id']}")
        print(f"   Cantidad: 1\n")
        
        cart_data = {
            "product_id": product['id'],
            "quantity": 1
        }
        
        response = requests.post(
            f"{API_URL}/api/v1/orders/cart/items",
            json=cart_data,
            headers=headers
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            cart = response.json()
            print(f"   ✅ Producto agregado al carrito!")
            print(f"   Items en carrito: {len(cart['items'])}")
            print(f"   Total: ${cart['total_amount']} {cart['currency']}")
        else:
            print(f"   ❌ Error al agregar al carrito")
            print(f"   Respuesta: {response.text}")
            
            # Intentar parsear el error
            try:
                error_data = response.json()
                print(f"\n   📋 Detalle del error:")
                print(f"      {error_data.get('detail', 'Sin detalle')}")
            except:
                pass
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        test_cart()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
