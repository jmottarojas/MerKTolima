# Instrucciones para Probar la Subida de Imágenes

## Problema Actual

Las imágenes no se están subiendo correctamente y el carrusel muestra imágenes por defecto en lugar de las imágenes subidas.

## Cambios Realizados

1. ✅ Agregados logs detallados en `frontend/static/js/image-upload.js`
2. ✅ Agregados logs detallados en `frontend/marketplace/views.py` (función `upload_images`)
3. ✅ Creada página de prueba simple: `frontend/templates/test_upload_simple.html`

## Pasos para Diagnosticar el Problema

### Paso 1: Iniciar el Servidor Django

```bash
cd frontend
python manage.py runserver
```

O si prefieres iniciar la plataforma completa:

```bash
python start_complete_platform.py
```

### Paso 2: Probar con la Página de Prueba Simple

1. **Abrir navegador** y ir a: `http://localhost:8000/marketplace/test-upload-simple/`

2. **Abrir consola del navegador** (F12 → Console)

3. **Seleccionar 1-2 imágenes** (JPG o PNG)

4. **Click en "Subir Imágenes"**

5. **Observar los logs:**
   - En la página web (sección "Log de Consola")
   - En la consola del navegador (F12)
   - En la terminal donde corre Django

### Paso 3: Verificar Logs en la Terminal

Deberías ver algo como esto en la terminal de Django:

```
============================================================
🔄 INICIO DE SUBIDA DE IMÁGENES
============================================================
✅ Usuario autenticado: user_123
📦 Archivos recibidos: ['image_0', 'image_1']
📦 Total de archivos: 2

📎 Procesando archivo: test1.jpg
   - Tipo: image/jpeg
   - Tamaño: 123456 bytes (0.12 MB)
   - Nombre único: abc123-def456.jpg
   - Directorio: C:\...\frontend\media\product_images
✅ Archivo guardado en: C:\...\frontend\media\product_images\abc123-def456.jpg
   - Tamaño guardado: 123456 bytes
🔗 URL generada: http://localhost:8000/media/product_images/abc123-def456.jpg

============================================================
✅ SUBIDA COMPLETADA
   - Total URLs generadas: 2
   - URLs: ['http://...', 'http://...']
============================================================
```

### Paso 4: Verificar Logs en el Navegador

En la consola del navegador deberías ver:

```
📁 Seleccionados 2 archivos
  - test1.jpg (0.12 MB)
  - test2.jpg (0.15 MB)
🔄 Iniciando subida de 2 archivos...
📎 Agregado: image_0 = test1.jpg
📎 Agregado: image_1 = test2.jpg
🔐 CSRF Token: Presente
📡 Enviando petición a /marketplace/api/upload-images/...
📥 Respuesta: 200 OK
📦 Resultado: {"success":true,"image_urls":[...],"count":2}
✅ ¡Subida exitosa! 2 imágenes
🔗 URL 1: http://localhost:8000/media/product_images/...
🔗 URL 2: http://localhost:8000/media/product_images/...
```

### Paso 5: Verificar Archivos Guardados

Verifica que los archivos se guardaron en:

```
frontend/media/product_images/
```

Deberías ver archivos con nombres como: `abc123-def456-789.jpg`

### Paso 6: Probar en Crear Producto

1. **Ir a**: `http://localhost:8000/marketplace/`
2. **Iniciar sesión** (si no estás logueado)
3. **Ir a "Panel Vendedor"** → **"Crear Producto"**
4. **Abrir consola del navegador** (F12)
5. **Llenar el formulario** con datos de prueba
6. **Ir a la sección "Imágenes del Producto"**
7. **Seleccionar tab "Subir desde PC"**
8. **Seleccionar 2-3 imágenes**
9. **Verificar que aparecen los previews**
10. **Click en "Crear Producto"**
11. **Observar los logs en consola:**

```
🔄 Subiendo 3 archivos...
Archivos a subir: ['img1.jpg', 'img2.jpg', 'img3.jpg']
📎 Agregando archivo 0: img1.jpg (123456 bytes, image/jpeg)
📎 Agregando archivo 1: img2.jpg (234567 bytes, image/jpeg)
📎 Agregando archivo 2: img3.jpg (345678 bytes, image/jpeg)
FormData keys: ['image_0', 'image_1', 'image_2']
🔐 Token CSRF: Presente
📡 Enviando petición a: /marketplace/api/upload-images/
📥 Respuesta del servidor: 200 OK
📦 Resultado completo: {success: true, image_urls: [...], count: 3}
✅ Subida exitosa: 3 imágenes
🖼️ URLs generadas: ['http://...', 'http://...', 'http://...']
```

## Posibles Problemas y Soluciones

### Problema 1: "Usuario no autenticado"

**Síntoma**: Error 401 en la respuesta

**Solución**:
- Asegúrate de estar logueado
- Verifica que la sesión esté activa
- Intenta cerrar sesión y volver a iniciar

### Problema 2: "No se recibieron archivos"

**Síntoma**: El servidor dice que recibió 0 archivos

**Solución**:
- Verifica que los archivos se están agregando al FormData
- Verifica en consola: `FormData keys: ['image_0', 'image_1', ...]`
- Si no aparecen, el problema está en el JavaScript

### Problema 3: "Error al guardar archivo"

**Síntoma**: Error al escribir en disco

**Solución**:
- Verifica permisos del directorio `frontend/media/product_images/`
- Ejecuta: `python test_upload_debug.py` para verificar permisos

### Problema 4: "CSRF Token ausente"

**Síntoma**: Error 403 Forbidden

**Solución**:
- Verifica que el formulario tiene `{% csrf_token %}`
- Verifica que el JavaScript obtiene el token correctamente
- Intenta refrescar la página

### Problema 5: Las imágenes se suben pero no se muestran en el producto

**Síntoma**: Los logs muestran subida exitosa pero el producto muestra imágenes por defecto

**Solución**:
- Verifica que las URLs se están agregando como campos ocultos al formulario
- Verifica en consola: `Formulario listo para enviar con X imágenes`
- Verifica en el backend que `request.POST.get(f'image_url_{i}')` recibe las URLs
- Agrega logs en `create_product` para ver qué URLs recibe

## Agregar Logs Adicionales en create_product

Si las imágenes se suben pero no se guardan en el producto, agrega estos logs en `frontend/marketplace/views.py`:

```python
def create_product(request):
    """Crear nuevo producto."""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        
        # Recopilar URLs de imágenes
        images = []
        print("\n" + "="*60)
        print("🔍 RECOPILANDO IMÁGENES DEL FORMULARIO")
        print("="*60)
        
        for i in range(1, 6):  # Máximo 5 imágenes
            image_url = request.POST.get(f'image_url_{i}')
            print(f"image_url_{i}: {image_url}")
            if image_url and image_url.strip():
                images.append(image_url.strip())
                print(f"✅ Agregada imagen {i}: {image_url}")
        
        print(f"\n📦 Total de imágenes recopiladas: {len(images)}")
        print(f"📦 URLs: {images}")
        print("="*60 + "\n")
        
        # ... resto del código
```

## Resultado Esperado

Después de seguir estos pasos, deberías poder:

1. ✅ Subir imágenes desde archivos locales
2. ✅ Ver los previews de las imágenes seleccionadas
3. ✅ Ver logs detallados en consola y terminal
4. ✅ Ver las URLs generadas
5. ✅ Crear un producto con las imágenes subidas
6. ✅ Ver el carrusel con las imágenes en el detalle del producto

## Siguiente Paso

Una vez que identifiques dónde está fallando (usando los logs), reporta:

1. ¿En qué paso falla?
2. ¿Qué logs aparecen en la consola del navegador?
3. ¿Qué logs aparecen en la terminal de Django?
4. ¿Se crean los archivos en `frontend/media/product_images/`?
5. ¿Las URLs se agregan al formulario como campos ocultos?

Con esta información podremos identificar exactamente dónde está el problema y solucionarlo.
