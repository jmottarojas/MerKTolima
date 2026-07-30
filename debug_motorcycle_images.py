#!/usr/bin/env python3
"""
Script para debuggear el problema de carga de imágenes con motocicletas
"""

import requests
import json
from pathlib import Path

def test_image_upload():
    """Probar la carga de imágenes directamente"""
    
    print("🔍 DEBUGGING CARGA DE IMÁGENES - MOTOCICLETAS")
    print("=" * 60)
    
    # URL del endpoint de upload
    upload_url = "http://localhost:8001/api/upload-images/"
    
    print(f"📡 URL de upload: {upload_url}")
    
    # Verificar si el servidor está corriendo
    try:
        response = requests.get("http://localhost:8001/")
        print(f"✅ Servidor Django respondiendo: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al servidor Django: {e}")
        return
    
    # Crear una imagen de prueba simple (1x1 pixel PNG)
    # PNG de 1x1 pixel transparente
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Guardar imagen de prueba
    test_image_path = Path("test_motorcycle.png")
    with open(test_image_path, "wb") as f:
        f.write(png_data)
    
    print(f"📁 Imagen de prueba creada: {test_image_path}")
    
    # Probar upload
    try:
        with open(test_image_path, "rb") as f:
            files = {
                'image_0': ('test_motorcycle.png', f, 'image/png')
            }
            
            # Simular headers de Django
            headers = {
                'X-CSRFToken': 'test-token',  # En producción esto vendría de la cookie
                'User-Agent': 'Mozilla/5.0 (Test)'
            }
            
            print("📤 Enviando imagen de prueba...")
            response = requests.post(upload_url, files=files, headers=headers)
            
            print(f"📥 Respuesta del servidor: {response.status_code}")
            print(f"📄 Contenido: {response.text}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("✅ Upload exitoso!")
                    print(f"📊 Resultado: {json.dumps(result, indent=2)}")
                except:
                    print("⚠️ Respuesta no es JSON válido")
            else:
                print(f"❌ Error en upload: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error durante upload: {e}")
    
    finally:
        # Limpiar archivo de prueba
        if test_image_path.exists():
            test_image_path.unlink()
            print(f"🗑️ Archivo de prueba eliminado")

def test_category_handling():
    """Probar el manejo de categorías"""
    
    print("\n🔍 TESTING MANEJO DE CATEGORÍAS")
    print("=" * 40)
    
    categories = [
        'Electrónicos', 'Ropa', 'Hogar', 'Deportes', 
        'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas'
    ]
    
    for category in categories:
        print(f"📂 Categoría: {category}")
        
        # Simular la lógica de get_default_images_by_category
        default_images = {
            'Electrónicos': ['https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=300&fit=crop'],
            'Automóviles': ['https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400&h=300&fit=crop'],
            'Motocicletas': ['https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'],
            'Ropa': ['https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop'],
            'Hogar': ['https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop'],
            'Deportes': ['https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=300&fit=crop'],
            'Libros': ['https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop'],
            'Juguetes': ['https://images.unsplash.com/photo-1558877385-1c4c7e9e1c6e?w=400&h=300&fit=crop'],
            'Belleza': ['https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop']
        }
        
        images = default_images.get(category, ['https://via.placeholder.com/400x300/e9ecef/6c757d?text=Producto'])
        
        if category == 'Motocicletas':
            print(f"   ✅ Motocicletas tiene imágenes por defecto: {len(images)} imagen(es)")
            print(f"   🔗 URL: {images[0]}")
        else:
            print(f"   📊 {len(images)} imagen(es) por defecto")

def main():
    """Función principal"""
    print("🚀 INICIANDO DEBUG DE MOTOCICLETAS")
    print("=" * 60)
    
    test_category_handling()
    test_image_upload()
    
    print("\n💡 RECOMENDACIONES:")
    print("1. Verifica que el servidor Django esté corriendo en puerto 8001")
    print("2. Abre las herramientas de desarrollador del navegador (F12)")
    print("3. Ve a la pestaña 'Console' para ver los logs de JavaScript")
    print("4. Intenta subir una imagen y revisa los mensajes de debug")
    print("5. Si hay errores, copia el mensaje exacto para más ayuda")

if __name__ == "__main__":
    main()