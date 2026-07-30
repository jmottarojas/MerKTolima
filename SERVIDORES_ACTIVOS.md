# ✅ Servidores Activos - Merkatolima

## Estado Actual

### 🟢 Backend FastAPI (Proceso ID: 3)
- **Puerto**: 8000
- **URL**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Estado**: ✅ Funcionando correctamente
- **Características**:
  - ✅ Todos los servicios inicializados
  - ✅ 5 usuarios de prueba creados
  - ✅ **Archivos media montados**: `/media` → `C:\Python\Marketplace\Merkatolima\frontend\media`

### 🟢 Frontend Django (Proceso ID: 4)
- **Puerto**: 8001
- **URL**: http://localhost:8001
- **Estado**: ✅ Funcionando correctamente
- **Características**:
  - ✅ Servidor de desarrollo activo
  - ✅ Recarga automática de archivos
  - ✅ Endpoint de subida de imágenes: `/marketplace/api/upload-images/`

## Usuarios de Prueba Disponibles

### 👤 Compradores
- **Email**: `buyer@test.com` | **Password**: `Password123`
- **Email**: `comprador@merkatolima.com` | **Password**: `Comprador123`

### 🏪 Vendedores
- **Email**: `seller@test.com` | **Password**: `Password123`
- **Email**: `vendedor@merkatolima.com` | **Password**: `Vendedor123`
- **Email**: `admin@merkatolima.com` | **Password**: `Admin123`

## Cómo Acceder

### Opción 1: Acceso Principal (Recomendado)
**URL**: http://localhost:8000/marketplace/

Esta es la URL principal que debes usar. FastAPI actúa como gateway y sirve:
- ✅ API Backend
- ✅ Frontend Django (proxy)
- ✅ Archivos media (imágenes de productos)

### Opción 2: Acceso Directo a Django
**URL**: http://localhost:8001/marketplace/

Acceso directo al servidor Django (útil para debugging).

## Probar la Subida de Imágenes

### Paso 1: Iniciar Sesión
1. Ve a: http://localhost:8000/marketplace/
2. Click en "Iniciar Sesión"
3. Usa: `seller@test.com` / `Password123`

### Paso 2: Crear Producto con Imágenes
1. Click en "Panel Vendedor"
2. Click en "Crear Producto"
3. Llena el formulario:
   - Nombre: "Producto de Prueba"
   - Categoría: "Electrónicos"
   - Precio: "1000000"
   - Descripción: "Producto para probar imágenes"
   - Condición: "Nuevo"
   - Marca: "Test"
   - Modelo: "Test-001"
   - Cantidad: "10"
   - Completa las especificaciones técnicas

4. **Subir Imágenes**:
   - Abre la consola del navegador (F12)
   - Ve a la sección "Imágenes del Producto"
   - Click en tab "Subir desde PC"
   - Selecciona 2-3 imágenes (JPG, PNG)
   - Verifica que aparecen los previews

5. **Enviar Formulario**:
   - Click en "Crear Producto"
   - Observa los logs en consola

### Paso 3: Verificar Resultado
1. Deberías ser redirigido a "Mis Productos"
2. Busca el producto recién creado
3. **Verifica**:
   - ✅ Muestra carrusel con las imágenes subidas
   - ✅ No muestra imagen por defecto
   - ✅ Controles de navegación funcionan

4. Click en "Ver" para ver el detalle completo

## Logs Esperados

### En la Consola del Navegador:
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
🖼️ URLs generadas: ['/media/product_images/...', ...]
Formulario listo para enviar con 3 imágenes
```

### En la Terminal de Django (Proceso 4):
```
============================================================
🔄 INICIO DE SUBIDA DE IMÁGENES
============================================================
✅ Usuario autenticado: user_123
📦 Archivos recibidos: ['image_0', 'image_1', 'image_2']
📦 Total de archivos: 3

📎 Procesando archivo: img1.jpg
   - Tipo: image/jpeg
   - Tamaño: 123456 bytes (0.12 MB)
   - Nombre único: abc123-def456.jpg
✅ Archivo guardado en: C:\...\frontend\media\product_images\abc123-def456.jpg
🔗 URL generada: /media/product_images/abc123-def456.jpg

============================================================
✅ SUBIDA COMPLETADA
   - Total URLs generadas: 3
   - URLs: ['/media/product_images/...', ...]
============================================================
```

## Verificar Archivos Guardados

Los archivos se guardan en:
```
C:\Python\Marketplace\Merkatolima\frontend\media\product_images\
```

Puedes verificar que existen con nombres UUID como: `abc123-def456-789.jpg`

## Verificar que FastAPI Sirve las Imágenes

1. Crea un producto con imágenes
2. Copia una URL de imagen (ejemplo: `/media/product_images/abc123.jpg`)
3. Accede directamente en el navegador:
   ```
   http://localhost:8000/media/product_images/abc123.jpg
   ```
4. Debería mostrar la imagen correctamente

## Detener los Servidores

Para detener los servidores, presiona `Ctrl+C` en cada terminal o usa:

```bash
# En Kiro, puedes detener los procesos con:
# Proceso 3 (FastAPI)
# Proceso 4 (Django)
```

## Solución de Problemas

### Si las imágenes no se muestran:

1. **Verifica que FastAPI está sirviendo media**:
   - Busca en los logs: `📁 Media files mounted at /media`
   - Si no aparece, reinicia el servidor FastAPI

2. **Verifica que las imágenes se subieron**:
   - Revisa el directorio: `frontend/media/product_images/`
   - Deberían existir archivos con nombres UUID

3. **Verifica las URLs en el producto**:
   - Abre la consola del navegador
   - Inspecciona el HTML del producto
   - Las URLs deben ser relativas: `/media/product_images/...`
   - NO deben ser absolutas: `http://localhost:8001/media/...`

4. **Verifica los logs**:
   - Consola del navegador (F12)
   - Terminal de Django (Proceso 4)
   - Busca errores o mensajes de advertencia

## Próximos Pasos

Una vez que verifiques que todo funciona:

1. ✅ Crea varios productos con diferentes imágenes
2. ✅ Verifica que el carrusel funciona en todas las páginas
3. ✅ Prueba editar productos y cambiar imágenes
4. ✅ Verifica que las imágenes se muestran en búsquedas
5. ✅ Prueba desde diferentes navegadores

## Archivos de Documentación

- `SOLUCION_FINAL_IMAGENES.md` - Explicación técnica completa
- `INSTRUCCIONES_PRUEBA_UPLOAD.md` - Guía de pruebas detallada
- `SOLUCION_CARRUSEL_IMAGENES.md` - Solución del carrusel
- `test_image_upload_fix.md` - Guía de verificación

¡La plataforma está lista para usar! 🎉
