import requests
import json

try:
    # Test backend connection
    response = requests.get('http://localhost:8000/api/v1/products/')
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Backend conectado')
        print(f'📊 Estructura de respuesta: {type(data)}')
        print(f'📊 Claves disponibles: {list(data.keys()) if isinstance(data, dict) else "No es dict"}')
        
        # Extract products from response
        if isinstance(data, dict):
            products = data.get('products', data.get('items', []))
            if not products and 'data' in data:
                products = data['data']
        else:
            products = data
            
        print(f'📦 Productos encontrados: {len(products) if isinstance(products, list) else "Estructura inesperada"}')
        
        if isinstance(products, list) and products:
            # Check if any products have multiple images
            multi_image_products = []
            for p in products:
                if isinstance(p, dict) and len(p.get('images', [])) > 1:
                    multi_image_products.append(p)
                    
            print(f'📸 Productos con múltiples imágenes: {len(multi_image_products)}')
            
            if multi_image_products:
                for i, product in enumerate(multi_image_products[:3]):
                    print(f'  {i+1}. {product.get("name", "Sin nombre")} - {len(product.get("images", []))} imágenes')
                    print(f'     ID: {product.get("id")}')
            else:
                print('⚠️ No hay productos con múltiples imágenes para probar el carousel')
                
            # Show first few products
            print('\n📦 Primeros productos:')
            for i, product in enumerate(products[:3]):
                if isinstance(product, dict):
                    images_count = len(product.get('images', []))
                    print(f'  {i+1}. {product.get("name", "Sin nombre")} - {images_count} imagen(es)')
                    if product.get('images'):
                        print(f'     Primera imagen: {product["images"][0][:50]}...')
        else:
            print('⚠️ No hay productos válidos encontrados')
    else:
        print(f'❌ Error en backend: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error conectando al backend: {e}')