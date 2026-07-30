# 🎯 INSTRUCCIONES PARA PROBAR LA SOLUCIÓN

## ✅ Estado Actual
- ✅ Servidores corriendo (Django en 8001, FastAPI en 8000)
- ✅ Código actualizado con la solución de hidden inputs
- ✅ Logs detallados implementados
- ✅ Carrusel ya implementado en las vistas
- ⏳ **PENDIENTE**: Probar la solución

## 🚀 PASOS PARA PROBAR

### Paso 1: Refrescar el Navegador
1. Abre tu navegador en: `http://localhost:8001/marketplace/`
2. Presiona `Ctrl + Shift + R` para refrescar sin caché
3. Esto asegura que se cargue el nuevo código JavaScript

### Paso 2: Abrir DevTools
1. Presiona `F12` para abrir las herramientas de desarrollador
2. Ve a la pestaña **Console**
3. Deja esta pestaña abierta para ver los logs

### Paso 3: Iniciar Sesión como Vendedor
1. Haz clic en "Iniciar Sesión"
2. Usa estas credenciales:
   - **Email**: `vendedor@merkatolima.com`
   - **Password**: `Vendedor123`
3. Deberías ser redirigido al panel de vendedor

### Paso 4: Ir a Crear Producto
1. En el panel de vendedor, haz clic en "Crear Producto"
2. O ve directamente a: `http://localhost:8001/vendedor/producto/nuevo/`

### Paso 5: Llenar el Formulario
Llena TODOS los campos obligatorios:

**Información Básica:**
- Nombre: `iPhone 15 Pro Max de Prueba`
- Categoría: `Electrónicos`
- Precio: `4000000` (4 millones)
- Descripción: `Este es un producto de prueba para verificar que las imágenes se suben correctamente`

**Información Detallada:**
- Condición: `Nuevo`
- Marca: `Apple`
- Modelo: `iPhone 15 Pro Max`

**Especificaciones Técnicas (para Electrónicos):**
- Procesador: `Apple A17 Pro`
- RAM: `8GB`
- Almacenamiento: `256GB`
- Tamaño de Pantalla: `6.7 pulgadas`
- Sistema Operativo: `iOS 17`
- Conectividad: Selecciona al menos `WiFi` (mantén Ctrl y haz clic)

**Inventario:**
- Cantidad: `10`
- Umbral de stock bajo: `5`

### Paso 6: Subir Imágenes
1. En la sección "Imágenes del Producto", asegúrate de estar en la pestaña **"Subir desde PC"**
2. Haz clic en "Seleccionar Imágenes"
3. Selecciona **2 o 3 imágenes** de tu computadora (JPG, PNG, etc.)
4. Verifica que aparezcan las **previews** de las imágenes
5. Deberías ver algo como:
   ```
   Imágenes Seleccionadas (3/5):
   [Preview 1] [Preview 2] [Preview 3]
   ```

### Paso 7: Crear el Producto
1. Haz clic en el botón **"Crear Producto"**
2. El botón cambiará a "Procesando..." con un spinner
3. **OBSERVA LA CONSOLA** - deberías ver estos logs:

```
🔍 Obteniendo URLs de imágenes...
📁 Archivos subidos: 3
🔄 Subiendo 3 archivos...
📎 Agregando archivo 0: imagen1.jpg (...)
📡 Enviando petición a: http://localhost:8001/marketplace/api/upload-images/
📥 Respuesta del servidor: 200 OK
✅ Subida exitosa: 3 imágenes
🖼️ URLs generadas: ["/media/product_images/abc123.jpg", ...]
📦 URLs obtenidas: ["/media/product_images/abc123.jpg", ...]
📊 Total de URLs: 3
📝 Creando hidden inputs para URLs...
   ✅ Created hidden input: image_url_1 = /media/product_images/abc123.jpg
   ✅ Created hidden input: image_url_2 = /media/product_images/def456.jpg
   ✅ Created hidden input: image_url_3 = /media/product_images/ghi789.jpg
📋 Verificando FormData:
   image_url_1: /media/product_images/abc123.jpg
   image_url_2: /media/product_images/def456.jpg
   image_url_3: /media/product_images/ghi789.jpg
🚀 Enviando formulario con 3 imágenes...
📥 Respuesta recibida: 302
↪️ Redirigiendo a: http://localhost:8001/vendedor/productos/
```

### Paso 8: Verificar el Producto Creado
1. Deberías ser redirigido a "Mis Productos"
2. Busca el producto que acabas de crear
3. Deberías ver:
   - ✅ La primera imagen que subiste
   - ✅ Un badge con "🖼️ 3" indicando 3 imágenes
   - ✅ Flechas para navegar entre las imágenes (carrusel mini)

### Paso 9: Ver el Detalle del Producto
1. Haz clic en "Ver Producto" o en el nombre del producto
2. Deberías ver:
   - ✅ Un **carrusel grande** con todas las imágenes
   - ✅ Indicadores de puntos abajo del carrusel
   - ✅ Flechas de navegación (anterior/siguiente)
   - ✅ Miniaturas clickeables debajo del carrusel
   - ✅ Badge "Imagen Principal" en la primera imagen

### Paso 10: Verificar Logs de Django
En la terminal donde corre Django (Process 4), deberías ver:

```
============================================================
🔄 INICIO DE SUBIDA DE IMÁGENES
============================================================
✅ Usuario autenticado: [user-id]
📦 Archivos recibidos: ['image_0', 'image_1', 'image_2']
📦 Total de archivos: 3
📎 Procesando archivo: imagen1.jpg
   - Tipo: image/jpeg
   - Tamaño: 123456 bytes (0.12 MB)
   - Nombre único: abc123.jpg
   - Directorio: frontend\media\product_images
✅ Archivo guardado en: frontend\media\product_images\abc123.jpg
🔗 URL generada: /media/product_images/abc123.jpg
[... similar para las otras 2 imágenes ...]
============================================================
✅ SUBIDA COMPLETADA
   - Total URLs generadas: 3
   - URLs: ['/media/product_images/abc123.jpg', ...]
============================================================

============================================================
🔍 CREANDO PRODUCTO - INICIO
============================================================
📦 Recopilando URLs de imágenes del formulario...
   image_url_1: '/media/product_images/abc123.jpg' (tipo: <class 'str'>)
   ✅ Agregada imagen 1: /media/product_images/abc123.jpg
   image_url_2: '/media/product_images/def456.jpg' (tipo: <class 'str'>)
   ✅ Agregada imagen 2: /media/product_images/def456.jpg
   image_url_3: '/media/product_images/ghi789.jpg' (tipo: <class 'str'>)
   ✅ Agregada imagen 3: /media/product_images/ghi789.jpg

📊 Total de imágenes recopiladas: 3
📊 URLs de imágenes: ['/media/product_images/abc123.jpg', ...]
✅ Usando 3 imágenes subidas por el usuario
📦 Datos del producto a enviar:
   - Nombre: iPhone 15 Pro Max de Prueba
   - Categoría: Electrónicos
   - Precio: 4000000.0
   - Imágenes: ['/media/product_images/abc123.jpg', ...]
   - Total imágenes: 3
============================================================
✅ Producto creado exitosamente: [product-id]
```

## ✅ RESULTADO ESPERADO

Si todo funciona correctamente:
1. ✅ NO aparece el error "Debes subir al menos una imagen del producto"
2. ✅ El producto se crea exitosamente
3. ✅ Las imágenes que subiste se muestran en el producto
4. ✅ El carrusel funciona y muestra todas las imágenes
5. ✅ NO se generan imágenes por defecto/aleatorias

## ❌ SI HAY PROBLEMAS

### Problema 1: Error "Debes subir al menos una imagen"
**Qué hacer:**
1. Copia TODOS los logs de la consola del navegador
2. Copia TODOS los logs de la terminal de Django
3. Toma un screenshot del error
4. Envía esta información

**Posibles causas:**
- Los hidden inputs no se están creando
- Las URLs no están llegando al FormData
- Hay un error en el upload de archivos

### Problema 2: Las imágenes no se muestran
**Qué hacer:**
1. Verifica que los archivos existen en `frontend/media/product_images/`
2. Intenta acceder directamente a: `http://localhost:8001/media/product_images/[nombre-archivo]`
3. Verifica los logs de Django para ver las URLs generadas

**Posibles causas:**
- Los archivos no se guardaron correctamente
- Las URLs son incorrectas
- Problema con la configuración de archivos estáticos

### Problema 3: El carrusel no funciona
**Qué hacer:**
1. Verifica que el producto tiene más de 1 imagen
2. Abre la consola del navegador y busca errores de JavaScript
3. Verifica que Bootstrap está cargado

**Posibles causas:**
- Solo se subió 1 imagen (el carrusel requiere 2+)
- Error de JavaScript
- Bootstrap no está cargado

## 📸 CAPTURAS RECOMENDADAS

Si todo funciona, toma capturas de:
1. La consola del navegador con los logs
2. La lista de productos mostrando el carrusel mini
3. El detalle del producto con el carrusel grande
4. Los logs de Django en la terminal

## 🎉 SIGUIENTE PASO

Una vez que confirmes que funciona:
1. Prueba editar el producto y cambiar las imágenes
2. Prueba crear otro producto con diferente cantidad de imágenes
3. Prueba con imágenes más grandes
4. Verifica que funciona en diferentes páginas (home, búsqueda, etc.)

---

**¿Listo para probar?** 🚀

Sigue estos pasos en orden y reporta los resultados. Si hay algún problema, copia los logs completos para poder ayudarte mejor.
