"""
Script de prueba completo para verificar el upload de imágenes
"""
import requests
import json
from pathlib import Path

# Configuración
DJANGO_URL = "http://localhost:8001"
FASTAPI_URL = "http://localhost:8000"

def test_upload_endpoint():
    """Probar el endpoint de upload de imágenes"""
    print("\n" + "="*60)
    print("TEST 1: Verificar endpoint de upload")
    print("="*60)
    
    # Crear una imagen de prueba simple (1x1 pixel PNG)
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Intentar subir sin autenticación (debería fallar)
    files = {'image_0': ('test.png', test_image_data, 'image/png')}
    
    try:
        response = requests.post(
            f"{DJANGO_URL}/marketplace/api/upload-images/",
            files=files
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 401:
            print("✅ Endpoint requiere autenticación (correcto)")
        elif response.status_code == 200:
            print("⚠️ Endpoint acepta requests sin autenticación")
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_media_files_access():
    """Verificar que los archivos media son accesibles"""
    print("\n" + "="*60)
    print("TEST 2: Verificar acceso a archivos media")
    print("="*60)
    
    # Verificar que el directorio media existe
    media_dir = Path("frontend/media/product_images")
    
    if media_dir.exists():
        print(f"✅ Directorio media existe: {media_dir}")
        
        # Listar archivos
        files = list(media_dir.glob("*"))
        print(f"📁 Archivos en media: {len(files)}")
        
        if files:
            # Intentar acceder al primer archivo
            test_file = files[0]
            file_url = f"/media/product_images/{test_file.name}"
            
            # Probar desde Django
            try:
                response = requests.get(f"{DJANGO_URL}{file_url}")
                if response.status_code == 200:
                    print(f"✅ Archivo accesible desde Django: {file_url}")
                else:
                    print(f"❌ Error accediendo desde Django: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Probar desde FastAPI
            try:
                response = requests.get(f"{FASTAPI_URL}{file_url}")
                if response.status_code == 200:
                    print(f"✅ Archivo accesible desde FastAPI: {file_url}")
                else:
                    print(f"❌ Error accediendo desde FastAPI: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("⚠️ No hay archivos en el directorio media")
    else:
        print(f"❌ Directorio media no existe: {media_dir}")

def test_product_creation_flow():
    """Simular el flujo completo de creación de producto"""
    print("\n" + "="*60)
    print("TEST 3: Flujo de creación de producto")
    print("="*60)
    
    print("Este test requiere autenticación manual.")
    print("Por favor, sigue estos pasos:")
    print()
    print("1. Abre el navegador en: http://localhost:8001/marketplace/")
    print("2. Inicia sesión como vendedor:")
    print("   - Email: vendedor@merkatolima.com")
    print("   - Password: Vendedor123")
    print("3. Ve a 'Crear Producto'")
    print("4. Abre DevTools (F12) y ve a la pestaña Console")
    print("5. Llena el formulario y sube 2-3 imágenes")
    print("6. Haz clic en 'Crear Producto'")
    print("7. Verifica los logs en la consola del navegador")
    print("8. Verifica los logs en la terminal de Django")
    print()
    print("Logs esperados en el navegador:")
    print("  🔍 Obteniendo URLs de imágenes...")
    print("  🔄 Subiendo X archivos...")
    print("  ✅ Subida exitosa: X imágenes")
    print("  📝 Creando hidden inputs para URLs...")
    print("  🚀 Enviando formulario con X imágenes...")
    print()
    print("Logs esperados en Django:")
    print("  🔄 INICIO DE SUBIDA DE IMÁGENES")
    print("  ✅ Archivo guardado en: ...")
    print("  🔍 CREANDO PRODUCTO - INICIO")
    print("  ✅ Producto creado exitosamente")

def check_servers():
    """Verificar que los servidores están corriendo"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE SERVIDORES")
    print("="*60)
    
    # Verificar Django
    try:
        response = requests.get(f"{DJANGO_URL}/marketplace/", timeout=2)
        if response.status_code == 200:
            print(f"✅ Django corriendo en {DJANGO_URL}")
        else:
            print(f"⚠️ Django responde con status {response.status_code}")
    except Exception as e:
        print(f"❌ Django no responde: {e}")
    
    # Verificar FastAPI
    try:
        response = requests.get(f"{FASTAPI_URL}/docs", timeout=2)
        if response.status_code == 200:
            print(f"✅ FastAPI corriendo en {FASTAPI_URL}")
        else:
            print(f"⚠️ FastAPI responde con status {response.status_code}")
    except Exception as e:
        print(f"❌ FastAPI no responde: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SUITE DE PRUEBAS - UPLOAD DE IMÁGENES")
    print("="*60)
    
    check_servers()
    test_media_files_access()
    test_upload_endpoint()
    test_product_creation_flow()
    
    print("\n" + "="*60)
    print("PRUEBAS COMPLETADAS")
    print("="*60)
    print()
    print("Para probar el flujo completo, sigue las instrucciones del TEST 3")
    print()
