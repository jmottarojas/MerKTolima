"""Script para crear un producto de prueba con inventario."""

import requests
import json

# Configuración
API_URL = "http://localhost:8000"
DJANGO_URL = "http://localhost:8001"

def login_and_create_product():
    """Iniciar sesión como vendedor y crear un producto de prueba."""
    
    print("\n" + "="*60)
    print("🛍️  CREANDO PRODUCTO DE PRUEBA")
    print("="*60 + "\n")
    
    # 1. Iniciar sesión como vendedor en Django
    print("1️⃣  Iniciando sesión como vendedor...")
    session = requests.Session()
    
    # Obtener CSRF token
    response = session.get(f"{DJANGO_URL}/login/")
    csrf_token = session.cookies.get('csrftoken')
    
    # Iniciar sesión
    login_data = {
        'email': 'vendedor@merkatolima.com',
        'password': 'Vendedor123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(
        f"{DJANGO_URL}/login/",
        data=login_data,
        headers={'Referer': f"{DJANGO_URL}/login/"}
    )
    
    if response.status_code == 200 and 'user_id' in session.cookies:
        print("   ✅ Sesión iniciada correctamente\n")
    else:
        print("   ❌ Error al iniciar sesión")
        return
    
    # 2. Crear producto a través del API
    print("2️⃣  Creando producto...")
    
    product_data = {
        "name": "iPhone 15 Pro Max - Producto de Prueba",
        "description": "Smartphone de última generación con cámara profesional y pantalla OLED. Producto creado para pruebas del carrito de compras.",
        "price": 4500000,
        "currency": "COP",
        "category": "Electrónicos",
        "images": [
            "https://images.unsplash.com/photo-1592286927505-c80d1b7e8b8e?w=400",
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400"
        ],
        "inventory_quantity": 25,
        "low_stock_threshold": 5
    }
    
    # Obtener el token de la sesión Django
    cookies = session.cookies.get_dict()
    
    response = requests.post(
        f"{API_URL}/api/v1/products/",
        json=product_data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        product = response.json()
        print("   ✅ Producto creado exitosamente\n")
        print("📦 DETALLES DEL PRODUCTO:\n")
        print(f"   ID: {product['id']}")
        print(f"   Nombre: {product['name']}")
        print(f"   Precio: ${product['price']} {product['currency']}")
        print(f"   Categoría: {product['category']}")
        print(f"   Inventario: {product['inventory_quantity']} unidades")
        print(f"   Status: {product['status']}")
        print(f"   Imágenes: {len(product['images'])} imagen(es)")
        print()
        print("="*60)
        print("✅ PRODUCTO LISTO PARA PRUEBAS")
        print("="*60)
        print()
        print("🧪 PARA PROBAR EL CARRITO:")
        print(f"   1. Ir a: {DJANGO_URL}/login/")
        print("   2. Iniciar sesión como: comprador@merkatolima.com / Comprador123")
        print(f"   3. Ir a: {DJANGO_URL}/producto/{product['id']}/")
        print("   4. Hacer clic en 'Agregar al Carrito'")
        print()
    else:
        print(f"   ❌ Error al crear producto: {response.status_code}")
        print(f"   Respuesta: {response.text}")


if __name__ == "__main__":
    try:
        login_and_create_product()
    except Exception as e:
        print(f"\n❌ Error: {e}")
