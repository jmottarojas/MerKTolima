import requests
import json

# Test product data with multiple images
test_product = {
    "name": "Smartphone Samsung Galaxy Test",
    "description": "Smartphone de prueba para testing del carousel de imágenes. Incluye múltiples fotos para verificar la funcionalidad de deslizamiento.",
    "price": 850000,
    "currency": "COP",
    "category": "Electrónicos",
    "inventory_quantity": 10,
    "low_stock_threshold": 2,
    "images": [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400&h=300&fit=crop"
    ]
}

try:
    print("🚀 Creando producto de prueba con múltiples imágenes...")
    
    # Create product via API
    response = requests.post(
        'http://localhost:8000/api/v1/products/',
        json=test_product,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code in [200, 201]:
        product = response.json()
        print(f"✅ Producto creado exitosamente!")
        print(f"📦 ID: {product.get('id')}")
        print(f"📱 Nombre: {product.get('name')}")
        print(f"📸 Imágenes: {len(product.get('images', []))}")
        print(f"🔗 URL de prueba: http://localhost:8001/marketplace/product/{product.get('id')}/")
        
        # Test another product with different category
        test_product2 = {
            "name": "Laptop Gaming MSI Test",
            "description": "Laptop gaming de prueba con múltiples ángulos y vistas detalladas para probar el carousel.",
            "price": 2500000,
            "currency": "COP", 
            "category": "Electrónicos",
            "inventory_quantity": 5,
            "low_stock_threshold": 1,
            "images": [
                "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&h=300&fit=crop"
            ]
        }
        
        response2 = requests.post(
            'http://localhost:8000/api/v1/products/',
            json=test_product2,
            headers={'Content-Type': 'application/json'}
        )
        
        if response2.status_code in [200, 201]:
            product2 = response2.json()
            print(f"\n✅ Segundo producto creado!")
            print(f"📦 ID: {product2.get('id')}")
            print(f"💻 Nombre: {product2.get('name')}")
            print(f"📸 Imágenes: {len(product2.get('images', []))}")
            print(f"🔗 URL de prueba: http://localhost:8001/marketplace/product/{product2.get('id')}/")
        
        print(f"\n🌐 URLs para probar:")
        print(f"🏠 Homepage: http://localhost:8001/marketplace/")
        print(f"📋 Productos: http://localhost:8001/marketplace/products/")
        print(f"🧪 Test HTML: file://{__file__.replace('create_test_product.py', 'test_carousel.html')}")
        
    else:
        print(f"❌ Error creando producto: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")