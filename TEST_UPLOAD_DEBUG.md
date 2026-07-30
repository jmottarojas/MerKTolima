# TEST PLAN - Image Upload Debug

## Current Status
- ✅ Fetch() implementation is in place in `create_product.html`
- ✅ `getImageUrls()` function exists in `image-upload.js`
- ✅ `uploadFiles()` function uploads to `/marketplace/api/upload-images/`
- ✅ Django `upload_images()` view saves files and returns URLs
- ❌ User reports: "Debes subir al menos una imagen del producto" error

## Problem Analysis
The error message appears when `images` array is empty in Django's `create_product()` view.
This means the `image_url_1`, `image_url_2`, etc. fields are NOT reaching Django.

## Possible Causes
1. `getImageUrls()` returns empty array
2. `uploadFiles()` fails silently
3. FormData.append() not working
4. CSRF token issue
5. Fetch request not including FormData properly

## Test Steps

### Step 1: Check Browser Console
User should:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try to create a product with images
4. Look for these emoji logs:
   - 🔍 "Obteniendo URLs de imágenes..."
   - 📦 "URLs obtenidas: [...]"
   - 📊 "Total de URLs: X"
   - 📁 "Archivos subidos: X"
   - 📝 "Agregando URLs al FormData..."
   - ✅ "image_url_1 = /media/..."
   - 🚀 "Enviando formulario con X imágenes..."

### Step 2: Check Network Tab
1. Go to Network tab in DevTools
2. Try to create product
3. Look for TWO requests:
   a) POST to `/marketplace/api/upload-images/` - should return URLs
   b) POST to `/vendedor/producto/nuevo/` - should include image_url_1, etc.

### Step 3: Check Django Logs
Look in the terminal running Django (Process 4) for:
- 🔄 "INICIO DE SUBIDA DE IMÁGENES"
- ✅ "Archivo guardado en: ..."
- 🔗 "URL generada: /media/..."
- 🔍 "CREANDO PRODUCTO - INICIO"
- 📦 "Recopilando URLs de imágenes del formulario..."
- "image_url_1: '...'"

## Expected Behavior
1. User selects images from PC
2. JavaScript shows previews
3. User clicks "Crear Producto"
4. JavaScript calls `uploadFiles()` → uploads to Django
5. Django saves files, returns URLs like `["/media/product_images/abc123.jpg"]`
6. JavaScript appends URLs to FormData as `image_url_1`, `image_url_2`, etc.
7. JavaScript sends FormData to `/vendedor/producto/nuevo/`
8. Django receives `image_url_1`, `image_url_2`, etc. with values
9. Product is created with images

## Quick Fix to Test
If the issue persists, we can add a hidden container in the HTML form to hold the image URLs:

```html
<!-- Add this inside the <form> tag, after {% csrf_token %} -->
<div id="image-url-container" style="display: none;">
    <!-- Hidden inputs will be added here dynamically -->
</div>
```

Then modify the JavaScript to create actual hidden inputs instead of just appending to FormData:

```javascript
// Before sending the form, create hidden inputs
imageUrls.forEach((url, index) => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = `image_url_${index + 1}`;
    input.value = url;
    document.getElementById('image-url-container').appendChild(input);
});
```

## Next Steps
1. User should test with current implementation
2. Check console logs
3. Check network requests
4. Report back what they see
5. If still failing, we'll implement the hidden inputs fix
