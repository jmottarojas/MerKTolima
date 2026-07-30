# Prueba de Verificación: Carga de Imágenes y Carrusel

## Pasos para Probar la Solución

### 1. Iniciar el Servidor

```bash
# Opción 1: Iniciar solo Django
python frontend/manage.py runserver

# Opción 2: Iniciar plataforma completa
python start_complete_platform.py
```

### 2. Probar Creación de Producto con Imágenes

1. **Abrir navegador** y ir a: `http://localhost:8000/marketplace/`
2. **Iniciar sesión** con un usuario vendedor
3. **Ir a "Panel Vendedor"** → **"Crear Producto"**
4. **Abrir consola del navegador** (F12 → Console)
5. **Llenar el formulario:**
   - Nombre: "Producto de Prueba con Imágenes"
   - Categoría: "Electrónicos"
   - Precio: "1000000"
   - Descripción: "Producto para probar la carga de imágenes"
   - Condición: "Nuevo"
   - Marca: "Test"
   - Modelo: "Test-001"
   - Cantidad: "10"

6. **Probar carga de imágenes:**

   **Opción A: Subir desde PC**
   - Click en tab "Subir desde PC"
   - Seleccionar 2-3 imágenes (JPG, PNG)
   - Verificar que aparecen los previews
   - Verificar en consola:
     ```
     Seleccionados X archivos
     Validando archivo: ...
     Archivo agregado: ...
     Total de archivos cargados: X
     ```

   **Opción B: URLs de imágenes**
   - Click en tab "URL de Imagen"
   - Pegar URLs de imágenes de prueba:
     ```
     https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400
     https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400
     ```
   - Click en botón "👁️" para preview

7. **Enviar formulario:**
   - Click en "Crear Producto"
   - Verificar en consola:
     ```
     Obteniendo URLs de imágenes...
     Subiendo X archivos... (si usaste Opción A)
     URLs obtenidas: [...]
     Formulario listo para enviar con X imágenes
     ```

8. **Verificar resultado:**
   - Deberías ser redirigido a "Mis Productos"
   - Buscar el producto creado
   - **Verificar que muestra el carrusel** con las imágenes subidas
   - Click en "Ver" para ver el detalle

### 3. Verificar Carrusel en Detalle del Producto

1. **En la página de detalle del producto:**
   - ✅ Debe mostrar el carrusel con todas las imágenes
   - ✅ Debe tener controles de navegación (flechas)
   - ✅ Debe tener indicadores de puntos
   - ✅ Debe mostrar miniaturas debajo del carrusel
   - ✅ La primera imagen debe tener badge "Imagen Principal"

2. **Probar navegación:**
   - Click en flechas → debe cambiar de imagen
   - Click en puntos → debe ir a esa imagen
   - Click en miniaturas → debe ir a esa imagen

### 4. Probar Edición de Producto

1. **Ir a "Mis Productos"**
2. **Click en "Editar"** en el producto creado
3. **Verificar que muestra las imágenes actuales**
4. **Probar agregar más imágenes:**
   - Subir nuevas imágenes o agregar URLs
   - Guardar cambios
   - Verificar que se actualizaron correctamente

### 5. Verificar en Diferentes Páginas

El carrusel debe funcionar en:
- ✅ Página de inicio (productos destacados)
- ✅ Página de productos (listado)
- ✅ Página de búsqueda
- ✅ Página de detalle del producto
- ✅ Panel del vendedor (mis productos)

## Casos de Prueba Específicos

### Caso 1: Subir 1 imagen
- **Resultado esperado**: Muestra la imagen sin carrusel (solo la imagen)

### Caso 2: Subir 2-5 imágenes
- **Resultado esperado**: Muestra carrusel con controles y navegación

### Caso 3: No subir imágenes
- **Resultado esperado**: Muestra imagen por defecto según categoría

### Caso 4: Mezclar archivos y URLs
- **Resultado esperado**: Solo se usa el método activo (tab seleccionado)

### Caso 5: Archivo muy grande (>5MB)
- **Resultado esperado**: Muestra alerta de error, no permite subir

### Caso 6: Archivo no válido (PDF, TXT)
- **Resultado esperado**: Muestra alerta de error, no permite subir

### Caso 7: Más de 5 imágenes
- **Resultado esperado**: Muestra alerta "Máximo 5 imágenes"

## Debugging

Si algo no funciona, verificar en consola del navegador:

### Errores Comunes:

1. **"getImageUrls is not defined"**
   - Verificar que `image-upload.js` está cargado
   - Verificar en Network tab que el archivo se descargó

2. **"uploadedFiles is not defined"**
   - Verificar que no hay duplicación de variables
   - Verificar que se usa `getUploadedFiles()` en lugar de acceso directo

3. **"Error al subir las imágenes"**
   - Verificar que el endpoint `/marketplace/api/upload-images/` está funcionando
   - Verificar que el token CSRF está presente
   - Verificar permisos de escritura en `media/product_images/`

4. **Carrusel no se muestra**
   - Verificar que `product.images` tiene más de 1 imagen
   - Verificar en el HTML que el carrusel se renderiza
   - Verificar que Bootstrap JS está cargado

### Logs Útiles:

```javascript
// En consola del navegador:
console.log('Archivos cargados:', getUploadedFiles());
console.log('URLs de imágenes:', await getImageUrls());
```

## Resultado Esperado Final

✅ Las imágenes se suben correctamente desde archivos locales
✅ El carrusel se muestra con múltiples imágenes
✅ La navegación del carrusel funciona correctamente
✅ Las miniaturas funcionan correctamente
✅ La edición de productos mantiene las imágenes existentes
✅ No hay errores en la consola del navegador
✅ El sistema funciona en todas las páginas del marketplace
