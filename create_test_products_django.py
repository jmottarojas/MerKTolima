#!/usr/bin/env python
"""
Script para crear productos de prueba directamente en Django
"""
import os
import sys
import django
from pathlib import Path

# Add the frontend directory to Python path
frontend_path = Path(__file__).parent / 'frontend'
sys.path.insert(0, str(frontend_path))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merkatolima_frontend.settings')

# Setup Django
django.setup()

# Now we can import Django models
try:
    from marketplace.api_client import api_client
    import requests
    
    print("🚀 Creando productos de prueba para el carousel...")
    
    # Test products with multiple images
    test_products = [
        {
            "name": "iPhone 14 Pro Max",
            "description": "📱 SMARTPHONE PREMIUM\n\n🏷️ CONDICIÓN: Nuevo\n🏭 MARCA: Apple\n📱 MODELO: iPhone 14 Pro Max\n🎨 COLOR: Morado Profundo\n📺 PANTALLA: 6.7 pulgadas Super Retina XDR\n💻 SISTEMA OPERATIVO: iOS 16\n📡 CONECTIVIDAD: 5G, Wi-Fi 6, Bluetooth 5.3\n📷 CÁMARA: Triple cámara 48MP + 12MP + 12MP\n🔋 BATERÍA: Hasta 29 horas de reproducción de video\n💾 ALMACENAMIENTO: 256GB\n🛡️ GARANTÍA: 1 año Apple",
            "price": 4500000,
            "currency": "COP",
            "category": "Electrónicos",
            "inventory_quantity": 8,
            "low_stock_threshold": 2,
            "images": [
                "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=300&fit=crop", 
                "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400&h=300&fit=crop"
            ]
        },
        {
            "name": "MacBook Pro M2 16\"",
            "description": "💻 LAPTOP PROFESIONAL\n\n🏷️ CONDICIÓN: Nuevo\n🏭 MARCA: Apple\n📱 MODELO: MacBook Pro 16 pulgadas\n🖥️ PROCESADOR: Apple M2 Pro\n🧠 MEMORIA RAM: 16GB\n💾 ALMACENAMIENTO: SSD 512GB\n📺 PANTALLA: 16.2 pulgadas Liquid Retina XDR\n💻 SISTEMA OPERATIVO: macOS Ventura\n📡 CONECTIVIDAD: Wi-Fi 6E, Bluetooth 5.3, Thunderbolt 4\n🔋 BATERÍA: Hasta 22 horas\n🎨 COLOR: Gris Espacial\n🛡️ GARANTÍA: 1 año Apple",
            "price": 8500000,
            "currency": "COP",
            "category": "Electrónicos", 
            "inventory_quantity": 3,
            "low_stock_threshold": 1,
            "images": [
                "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=300&fit=crop"
            ]
        },
        {
            "name": "Toyota Corolla 2022",
            "description": "🚗 SEDÁN FAMILIAR\n\n🏷️ CONDICIÓN: Usado\n🏭 MARCA: Toyota\n📱 MODELO: Corolla\n📅 AÑO: 2022\n⏱️ TIEMPO DE USO: 1 año\n🚗 KILOMETRAJE: 15000 km\n⛽ COMBUSTIBLE: Gasolina\n📋 SOAT VIGENTE HASTA: 2024-12-31\n🔍 TECNOMECÁNICA VIGENTE HASTA: 2024-06-30\n💰 IMPUESTOS PAGOS HASTA: 2024-12-31\n🎨 COLOR: Blanco Perla\n⚙️ TRANSMISIÓN: Automática CVT",
            "price": 75000000,
            "currency": "COP",
            "category": "Automóviles",
            "inventory_quantity": 1,
            "low_stock_threshold": 1,
            "images": [
                "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=400&h=300&fit=crop",
                "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=400&h=300&fit=crop"
            ]
        }
    ]
    
    # Create products via direct API calls (simulating authenticated user)
    created_products = []
    
    for i, product_data in enumerate(test_products):
        try:
            print(f"\n📦 Creando producto {i+1}: {product_data['name']}")
            
            # Try to create via direct backend API
            response = requests.post(
                'http://localhost:8000/api/v1/products/',
                json=product_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                product = response.json()
                created_products.append(product)
                print(f"✅ Creado: ID {product.get('id')}")
                print(f"📸 Imágenes: {len(product.get('images', []))}")
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error creando producto {i+1}: {e}")
    
    if created_products:
        print(f"\n🎉 ¡{len(created_products)} productos creados exitosamente!")
        print("\n🔗 URLs para probar el carousel:")
        for product in created_products:
            print(f"  📱 {product.get('name')}: http://localhost:8001/marketplace/product/{product.get('id')}/")
        
        print(f"\n🌐 Otras URLs:")
        print(f"🏠 Homepage: http://localhost:8001/marketplace/")
        print(f"📋 Productos: http://localhost:8001/marketplace/products/")
    else:
        print("\n⚠️ No se pudieron crear productos. Verifica la autenticación del API.")
        
except ImportError as e:
    print(f"❌ Error importando Django: {e}")
    print("💡 Asegúrate de que Django esté instalado y configurado correctamente")
except Exception as e:
    print(f"❌ Error general: {e}")