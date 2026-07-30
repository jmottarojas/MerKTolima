# Solución: Problema con Carga de Imágenes y Carrusel

## Problema Identificado

Cuando se cargaban imágenes desde archivos locales, no se mostraba el carrusel de imágenes y solo aparecía una imagen por defecto. El problema tenía varias causas:

1. **Código duplicado**: Las funciones de manejo de imágenes estaban duplicadas entre `image-upload.js` y los templates HTML
2. **Conflicto de variables**: La variable `uploadedFiles` estaba definida en múltiples lugares causando conflictos de alcance (scope)
3. **Falta de integración**: El template `edit_product.html` no incluía el archivo `image-upload.js`
4. **Comunicación incorrecta**: Las funciones del template no se comunicaban correctamente con las del archivo JS externo

## Solución Implementada

### 1. Actualización de `frontend/static/js/image-upload.js`

Se agregaron funciones para permitir acceso externo a las variables y funciones internas:

```javascript
/**
 * Obtener archivos cargados (para acceso externo)
 */
function getUploadedFiles() {
    return uploadedFiles;
}

/**
 * Limpiar archivos cargados
 */
function clearUploadedFiles() {
    uploadedFiles = [];
    updateUploadedImagesDisplay();
}
```

La función `getImageUrls()` ya existía y maneja correctamente:
- Subida de archivos al servidor
- Recopilación de URLs de inputs
- Retorno de array de URLs de imágenes

### 2. Actualización de `frontend/templates/marketplace/create_product.html`

**Cambios realizados:**

- ✅ Eliminada la duplicación de la variable `uploadedFiles`
- ✅ Actualizado el listener del formulario para usar `getImageUrls()` de `image-upload.js`
- ✅ Agregada validación mejorada con mensajes de error claros
- ✅ Agregados logs de consola para debugging

**Código actualizado:**

```javascript
// Usar la función getImageUrls() del archivo image-upload.js
console.log('Obteniendo URLs de imágenes...');
const imageUrls = await getImageUrls();
console.log('URLs obtenidas:', imageUrls);

// Validar que se obtuvieron imágenes si se subieron archivos
const uploadedFilesCount = getUploadedFiles().length;
if (uploadedFilesCount > 0 && imageUrls.length === 0) {
    throw new Error('Error al subir las imágenes. Por favor intenta de nuevo.');
}
```

### 3. Actualización de `frontend/templates/marketplace/edit_product.html`

**Cambios realizados:**

- ✅ Agregado el include de `image-upload.js`: `<script src="{% static 'js/image-upload.js' %}"></script>`
- ✅ Eliminada la duplicación de la variable `uploadedFiles`
- ✅ Actualizado el listener del formulario para usar `getImageUrls()` de `image-upload.js`
- ✅ Agregada validación mejorada con mensajes de error claros

## Cómo Funciona Ahora

### Flujo de Carga de Imágenes:

1. **Usuario selecciona archivos** (drag & drop o click)
   - `image-upload.js` maneja la selección
   - Valida tipo, tamaño y extensión
   - Crea previews visuales
   - Almacena archivos en `uploadedFiles`

2. **Usuario envía el formulario**
   - El template llama a `getImageUrls()`
   - `getImageUrls()` detecta el método activo (upload o URL)
   - Si hay archivos: llama a `uploadFiles()` que sube al servidor
   - Si hay URLs: las recopila de los inputs
   - Retorna array de URLs

3. **Formulario procesa las URLs**
   - Crea campos ocultos con las URLs
   - Envía el formulario al backend
   - Backend guarda el producto con las imágenes

4. **Backend procesa las imágenes**
   - Recibe las URLs en `request.POST.get(f'image_url_{i}')`
   - Las agrega al array `images`
   - Si no hay imágenes, usa imagen por defecto según categoría
   - Guarda el producto con las imágenes

5. **Visualización del carrusel**
   - El template `product_detail.html` recibe `product.images`
   - Si hay múltiples imágenes, muestra el carrusel Bootstrap
   - Si hay una sola imagen, muestra solo esa imagen
   - Si no hay imágenes, muestra imagen por defecto

## Verificación de la Solución

Para verificar que todo funciona correctamente:

1. **Abrir la consola del navegador** (F12)
2. **Ir a crear/editar producto**
3. **Subir imágenes desde archivos**
4. **Verificar en consola:**
   ```
   Seleccionados X archivos
   Validando archivo: nombre.jpg, tipo: image/jpeg, tamaño: XXXXX
   Archivo agregado: nombre.jpg
   Total de archivos cargados: X
   ```
5. **Enviar formulario**
6. **Verificar en consola:**
   ```
   Obteniendo URLs de imágenes...
   Subiendo X archivos...
   Respuesta del servidor: 200
   ✅ Subida exitosa: X imágenes
   URLs obtenidas: [url1, url2, ...]
   Formulario listo para enviar con X imágenes
   ```

## Archivos Modificados

1. `frontend/static/js/image-upload.js` - Agregadas funciones de acceso externo
2. `frontend/templates/marketplace/create_product.html` - Integración con image-upload.js
3. `frontend/templates/marketplace/edit_product.html` - Integración con image-upload.js

## Notas Adicionales

- El sistema soporta hasta 5 imágenes por producto
- Tamaño máximo por imagen: 5MB
- Formatos soportados: JPG, JPEG, PNG, GIF, WebP
- Las imágenes se guardan en `media/product_images/`
- La primera imagen es siempre la imagen principal del producto
- El carrusel se muestra automáticamente cuando hay más de una imagen
