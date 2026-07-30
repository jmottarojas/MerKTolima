#!/usr/bin/env python3
"""
Script completo para probar la funcionalidad del carousel de imágenes.
"""

import requests
import json
import time
from pathlib import Path

class CarouselTester:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://localhost:8001"
        self.api_url = "http://localhost:8000"
        
    def login_seller(self):
        """Login como vendedor para crear productos."""
        print("🔐 Iniciando sesión como vendedor...")
        
        # Get CSRF token first
        response = self.session.get(f"{self.base_url}/login/")
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False
            
        # Extract CSRF token
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
                
        if not csrf_token:
            print("❌ No se pudo obtener el token CSRF")
            return False
            
        print(f"✅ Token CSRF obtenido: {csrf_token[:20]}...")
        
        # Login with seller credentials
        login_data = {
            'email': 'seller@test.com',
            'password': 'Password123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = self.session.post(
            f"{self.base_url}/login/",
            data=login_data,
            headers={'Referer': f"{self.base_url}/login/"}
        )
        
        if response.status_code == 200 and 'Panel de Vendedor' in response.text:
            print("✅ Login exitoso como vendedor")
            return True
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
    
    def create_test_product(self, product_data):
        """Crear un producto de prueba."""
        print(f"📦 Creando producto: {product_data['name']}")
        
        # Get create product page
        response = self.session.get(f"{self.base_url}/vendedor/producto/nuevo/")
        if response.status_code != 200:
            print(f"❌ Error accediendo a crear producto: {response.status_code}")
            return None
            
        # Extract CSRF token
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
                
        if not csrf_token:
            print("❌ No se pudo obtener el token CSRF para crear producto")
            return None
        
        # Prepare form data
        form_data = {
            'name': product_data['name'],
            'description': product_data['description'],
            'price': str(product_data['price']),
            'category': product_data['category'],
            'quantity': str(product_data['inventory_quantity']),
            'low_stock_threshold': str(product_data['low_stock_threshold']),
            'condition': 'nuevo',  # Required field
            'csrfmiddlewaretoken': csrf_token
        }
        
        # Add image URLs (1-indexed as expected by the form)
        for i, image_url in enumerate(product_data['images'], 1):
            form_data[f'image_url_{i}'] = image_url
        
        # Submit form
        response = self.session.post(
            f"{self.base_url}/vendedor/producto/nuevo/",
            data=form_data,
            headers={'Referer': f"{self.base_url}/vendedor/producto/nuevo/"}
        )
        
        if response.status_code == 302:  # Redirect after successful creation
            print(f"✅ Producto creado exitosamente")
            # Extract product ID from redirect URL if possible
            location = response.headers.get('Location', '')
            if '/product/' in location:
                product_id = location.split('/product/')[1].split('/')[0]
                return product_id
            return True
        else:
            print(f"❌ Error creando producto: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
    
    def test_carousel_functionality(self):
        """Probar la funcionalidad del carousel."""
        print("\n🎠 Probando funcionalidad del carousel...")
        
        # Test products with multiple images
        test_products = [
            {
                "name": "iPhone 15 Pro - Test Carousel",
                "description": "Smartphone de prueba para verificar el carousel de imágenes con múltiples fotos.",
                "price": 4200000,
                "category": "Electrónicos",
                "inventory_quantity": 5,
                "low_stock_threshold": 1,
                "images": [
                    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
                    "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=300&fit=crop",
                    "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=300&fit=crop",
                    "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=400&h=300&fit=crop",
                    "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400&h=300&fit=crop"
                ]
            },
            {
                "name": "MacBook Air M2 - Test Carousel",
                "description": "Laptop de prueba con múltiples ángulos para probar el carousel.",
                "price": 5500000,
                "category": "Electrónicos",
                "inventory_quantity": 3,
                "low_stock_threshold": 1,
                "images": [
                    "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                    "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=300&fit=crop",
                    "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=400&h=300&fit=crop"
                ]
            }
        ]
        
        created_products = []
        
        for product_data in test_products:
            product_id = self.create_test_product(product_data)
            if product_id:
                created_products.append({
                    'id': product_id,
                    'name': product_data['name'],
                    'images_count': len(product_data['images'])
                })
                time.sleep(1)  # Wait between creations
        
        return created_products
    
    def verify_carousel_pages(self, products):
        """Verificar que las páginas muestren el carousel correctamente."""
        print("\n🔍 Verificando páginas con carousel...")
        
        pages_to_check = [
            (f"{self.base_url}/", "Homepage"),
            (f"{self.base_url}/productos/", "Products page"),
            (f"{self.base_url}/vendedor/productos/", "Seller products page")
        ]
        
        for url, page_name in pages_to_check:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    carousel_count = response.text.count('carousel slide')
                    image_badge_count = response.text.count('fas fa-images')
                    
                    print(f"✅ {page_name}: {carousel_count} carousels, {image_badge_count} image badges")
                else:
                    print(f"❌ {page_name}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {page_name}: Error {e}")
        
        # Check individual product pages
        for product in products:
            if isinstance(product['id'], str):
                try:
                    url = f"{self.base_url}/producto/{product['id']}/"
                    response = self.session.get(url)
                    if response.status_code == 200:
                        has_main_carousel = 'productImageCarousel' in response.text
                        has_thumbnails = 'thumbnail-image' in response.text
                        has_indicators = 'carousel-indicators' in response.text
                        
                        print(f"✅ {product['name']}:")
                        print(f"   - Carousel principal: {'✅' if has_main_carousel else '❌'}")
                        print(f"   - Miniaturas: {'✅' if has_thumbnails else '❌'}")
                        print(f"   - Indicadores: {'✅' if has_indicators else '❌'}")
                    else:
                        print(f"❌ {product['name']}: Error {response.status_code}")
                except Exception as e:
                    print(f"❌ {product['name']}: Error {e}")
    
    def generate_test_report(self, products):
        """Generar reporte de pruebas."""
        print("\n" + "="*60)
        print("📊 REPORTE DE PRUEBAS DEL CAROUSEL")
        print("="*60)
        
        if products:
            print(f"✅ Productos creados: {len(products)}")
            for product in products:
                print(f"   📱 {product['name']} ({product['images_count']} imágenes)")
            
            print(f"\n🔗 URLs para probar manualmente:")
            print(f"🏠 Homepage: {self.base_url}/")
            print(f"📋 Productos: {self.base_url}/productos/")
            print(f"🏪 Mis productos: {self.base_url}/vendedor/productos/")
            
            for product in products:
                if isinstance(product['id'], str):
                    print(f"📱 {product['name']}: {self.base_url}/producto/{product['id']}/")
            
            print(f"\n🧪 Test HTML estático: file://{Path(__file__).parent}/test_carousel.html")
            
            print(f"\n✨ Funcionalidades a probar:")
            print(f"   🖱️  Clic en flechas laterales para navegar")
            print(f"   🔘 Clic en indicadores de puntos")
            print(f"   🖼️  Clic en miniaturas (página de detalle)")
            print(f"   ⌨️  Teclas de flecha izquierda/derecha")
            print(f"   📱 Hover sobre tarjetas para ver controles")
            
        else:
            print("❌ No se pudieron crear productos de prueba")
            print("💡 Verifica que:")
            print("   - Los servidores estén ejecutándose")
            print("   - El usuario seller@test.com exista")
            print("   - La autenticación funcione correctamente")
    
    def run_complete_test(self):
        """Ejecutar prueba completa del carousel."""
        print("🎠 INICIANDO PRUEBA COMPLETA DEL CAROUSEL")
        print("="*60)
        
        # Step 1: Login
        if not self.login_seller():
            print("❌ No se pudo hacer login. Abortando pruebas.")
            return
        
        # Step 2: Create test products
        products = self.test_carousel_functionality()
        
        # Step 3: Verify pages
        if products:
            self.verify_carousel_pages(products)
        
        # Step 4: Generate report
        self.generate_test_report(products)


def main():
    """Función principal."""
    tester = CarouselTester()
    
    try:
        tester.run_complete_test()
    except KeyboardInterrupt:
        print("\n⏹️ Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()