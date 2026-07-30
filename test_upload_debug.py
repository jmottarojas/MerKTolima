"""
Script de prueba para verificar la subida de imágenes
"""
import os
import sys
from pathlib import Path

# Agregar el directorio frontend al path
sys.path.insert(0, str(Path(__file__).parent / 'frontend'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merkatolima_frontend.settings')
import django
django.setup()

from django.conf import settings

print("=" * 60)
print("CONFIGURACIÓN DE MEDIA")
print("=" * 60)
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"BASE_DIR: {settings.BASE_DIR}")

# Verificar directorio de imágenes
product_images_dir = Path(settings.MEDIA_ROOT) / 'product_images'
print(f"\nDirectorio de imágenes de productos: {product_images_dir}")
print(f"Existe: {product_images_dir.exists()}")

if not product_images_dir.exists():
    print("Creando directorio...")
    product_images_dir.mkdir(parents=True, exist_ok=True)
    print(f"Directorio creado: {product_images_dir.exists()}")

# Listar archivos existentes
if product_images_dir.exists():
    files = list(product_images_dir.glob('*'))
    print(f"\nArchivos en el directorio: {len(files)}")
    for f in files[:10]:  # Mostrar solo los primeros 10
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

print("\n" + "=" * 60)
print("PRUEBA DE ESCRITURA")
print("=" * 60)

# Intentar crear un archivo de prueba
test_file = product_images_dir / 'test_write.txt'
try:
    with open(test_file, 'w') as f:
        f.write('Test de escritura')
    print(f"✅ Escritura exitosa: {test_file}")
    
    # Limpiar
    test_file.unlink()
    print("✅ Archivo de prueba eliminado")
except Exception as e:
    print(f"❌ Error de escritura: {e}")

print("\n" + "=" * 60)
print("VERIFICACIÓN DE URLS")
print("=" * 60)

# Simular generación de URL
from django.http import HttpRequest
request = HttpRequest()
request.META['HTTP_HOST'] = 'localhost:8000'
request.META['wsgi.url_scheme'] = 'http'

test_filename = 'test-image.jpg'
file_url = f"{request.build_absolute_uri(settings.MEDIA_URL)}product_images/{test_filename}"
print(f"URL generada de ejemplo: {file_url}")

print("\n✅ Verificación completa")
