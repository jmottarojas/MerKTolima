# 📸 GUÍA VISUAL - Qué Esperar al Probar

## 🎯 Esta guía te muestra exactamente qué deberías ver en cada paso

---

## 1️⃣ PASO 1: Formulario de Crear Producto

### Lo que debes ver:
```
┌─────────────────────────────────────────────────────────┐
│ Crear Nuevo Producto                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Información Básica                                      │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Nombre del Producto *                           │   │
│ │ [iPhone 15 Pro Max de Prueba              ]    │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌──────────────────┐  ┌──────────────────────────┐   │
│ │ Categoría *      │  │ Precio (COP) *           │   │
│ │ [Electrónicos ▼] │  │ $ [4000000      ] COP    │   │
│ └──────────────────┘  └──────────────────────────┘   │
│                                                         │
│ Imágenes del Producto                                   │
│ ┌─────────────────────────────────────────────────┐   │
│ │ [Subir desde PC] [URL de Imagen]               │   │
│ │                                                 │   │
│ │     📤 Arrastra y suelta tus imágenes aquí     │   │
│ │        o haz clic para seleccionar archivos    │   │
│ │                                                 │   │
│ │     [Seleccionar Imágenes]                     │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ [💾 Crear Producto]  [❌ Cancelar]                     │
└─────────────────────────────────────────────────────────┘
```

---

## 2️⃣ PASO 2: Después de Seleccionar Imágenes

### Lo que debes ver:
```
┌─────────────────────────────────────────────────────────┐
│ Imágenes Seleccionadas (3/5):                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ [img1]   │  │ [img2]   │  │ [img3]   │            │
│  │          │  │          │  │          │            │
│  │  [❌]    │  │  [❌]    │  │  [❌]    │            │
│  │Principal │  │          │  │          │            │
│  │imagen1.jpg│  │imagen2.jpg│  │imagen3.jpg│          │
│  │0.5 MB    │  │0.8 MB    │  │1.2 MB    │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Indicadores importantes:**
- ✅ Badge "Principal" en la primera imagen
- ✅ Botón [❌] para eliminar cada imagen
- ✅ Nombre y tamaño de cada archivo
- ✅ Contador "3/5" mostrando cuántas imágenes has subido

---

## 3️⃣ PASO 3: Consola del Navegador (DevTools)

### Lo que debes ver al hacer clic en "Crear Producto":

```
Console
─────────────────────────────────────────────────────────
🔍 Obteniendo URLs de imágenes...
📁 Archivos subidos: 3
🔄 Subiendo 3 archivos...
Archivos a subir: (3) ['imagen1.jpg', 'imagen2.jpg', 'imagen3.jpg']
📎 Agregando archivo 0: imagen1.jpg (524288 bytes, image/jpeg)
📎 Agregando archivo 1: imagen2.jpg (838860 bytes, image/jpeg)
📎 Agregando archivo 2: imagen3.jpg (1258291 bytes, image/jpeg)
FormData keys: (3) ['image_0', 'image_1', 'image_2']
🔐 Token CSRF: Presente
📡 Enviando petición a: http://localhost:8001/marketplace/api/upload-images/
📥 Respuesta del servidor: 200 OK
📦 Resultado completo: {success: true, image_urls: Array(3), count: 3}
✅ Subida exitosa: 3 imágenes
🖼️ URLs generadas: (3) ['/media/product_images/abc123.jpg', '/media/product_images/def456.jpg', '/media/product_images/ghi789.jpg']
📦 URLs obtenidas: (3) ['/media/product_images/abc123.jpg', '/media/product_images/def456.jpg', '/media/product_images/ghi789.jpg']
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

**Puntos clave:**
- ✅ Cada paso tiene un emoji para fácil identificación
- ✅ Se muestran las URLs generadas
- ✅ Se confirma la creación de hidden inputs
- ✅ Se verifica que el FormData incluye las URLs
- ✅ Redirección exitosa (302)

---

## 4️⃣ PASO 4: Lista de Productos (Mis Productos)

### Lo que debes ver:
```
┌─────────────────────────────────────────────────────────┐
│ Mis Productos                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │ ┌────────────────────────────────────────┐   │     │
│  │ │  [◀]  [Imagen 1 del producto]    [▶]  │   │     │
│  │ │                                        │   │     │
│  │ │       🖼️ 3                            │   │     │
│  │ └────────────────────────────────────────┘   │     │
│  │                                              │     │
│  │ iPhone 15 Pro Max de Prueba                 │     │
│  │ Electrónicos                                 │     │
│  │ $ 4.000.000 COP                             │     │
│  │                                              │     │
│  │ [👁️ Ver] [✏️ Editar] [🗑️ Eliminar]         │     │
│  └──────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Indicadores importantes:**
- ✅ Carrusel mini con flechas [◀] [▶]
- ✅ Badge "🖼️ 3" indicando 3 imágenes
- ✅ La imagen principal se muestra
- ✅ Puedes navegar entre las imágenes con las flechas

---

## 5️⃣ PASO 5: Detalle del Producto

### Lo que debes ver:
```
┌─────────────────────────────────────────────────────────┐
│ iPhone 15 Pro Max de Prueba                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │                                                │   │
│  │  [◀]      [IMAGEN GRANDE]              [▶]    │   │
│  │                                                │   │
│  │           Imagen Principal                     │   │
│  │                                                │   │
│  │           ● ○ ○  (indicadores)                │   │
│  └────────────────────────────────────────────────┘   │
│                                                         │
│  Miniaturas:                                           │
│  ┌────┐  ┌────┐  ┌────┐                              │
│  │img1│  │img2│  │img3│                              │
│  └────┘  └────┘  └────┘                              │
│                                                         │
│  Descripción:                                          │
│  Este es un producto de prueba...                      │
│                                                         │
│  Especificaciones:                                     │
│  🖥️ PROCESADOR: Apple A17 Pro                         │
│  🧠 MEMORIA RAM: 8GB                                   │
│  💾 ALMACENAMIENTO: 256GB                              │
│  📺 PANTALLA: 6.7 pulgadas                             │
│  💻 SISTEMA OPERATIVO: iOS 17                          │
│                                                         │
│  Precio: $ 4.000.000 COP                              │
│  [🛒 Agregar al Carrito]                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Características del carrusel:**
- ✅ Imagen grande (400px de alto)
- ✅ Flechas de navegación [◀] [▶]
- ✅ Indicadores de puntos (● ○ ○)
- ✅ Miniaturas clickeables debajo
- ✅ Badge "Imagen Principal" en la primera
- ✅ Transiciones suaves entre imágenes

---

## 6️⃣ PASO 6: Terminal de Django

### Lo que debes ver:
```
============================================================
🔄 INICIO DE SUBIDA DE IMÁGENES
============================================================
✅ Usuario autenticado: 12345
📦 Archivos recibidos: ['image_0', 'image_1', 'image_2']
📦 Total de archivos: 3

📎 Procesando archivo: imagen1.jpg
   - Tipo: image/jpeg
   - Tamaño: 524288 bytes (0.50 MB)
   - Nombre único: abc123.jpg
   - Directorio: frontend\media\product_images
✅ Archivo guardado en: frontend\media\product_images\abc123.jpg
   - Tamaño guardado: 524288 bytes
🔗 URL generada: /media/product_images/abc123.jpg

[... similar para imagen2.jpg y imagen3.jpg ...]

============================================================
✅ SUBIDA COMPLETADA
   - Total URLs generadas: 3
   - URLs: ['/media/product_images/abc123.jpg', '/media/product_images/def456.jpg', '/media/product_images/ghi789.jpg']
============================================================

[15/Jan/2026 23:15:30] "POST /marketplace/api/upload-images/ HTTP/1.1" 200 245

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
📊 URLs de imágenes: ['/media/product_images/abc123.jpg', '/media/product_images/def456.jpg', '/media/product_images/ghi789.jpg']
✅ Usando 3 imágenes subidas por el usuario

📦 Datos del producto a enviar:
   - Nombre: iPhone 15 Pro Max de Prueba
   - Categoría: Electrónicos
   - Precio: 4000000.0
   - Imágenes: ['/media/product_images/abc123.jpg', '/media/product_images/def456.jpg', '/media/product_images/ghi789.jpg']
   - Total imágenes: 3
============================================================

✅ Producto creado exitosamente: f622cad2-f640-4930-ae02-90329a7c7f70
[15/Jan/2026 23:15:31] "POST /vendedor/producto/nuevo/ HTTP/1.1" 302 0
[15/Jan/2026 23:15:31] "GET /vendedor/productos/ HTTP/1.1" 200 30383
```

---

## ❌ LO QUE NO DEBES VER

### 🚫 Errores que NO deben aparecer:
```
❌ "Debes subir al menos una imagen del producto"
❌ "Error al subir las imágenes"
❌ "Error del servidor: 500"
❌ image_url_1: '' (vacío)
❌ Total de imágenes recopiladas: 0
```

### 🚫 Comportamientos incorrectos:
- ❌ Se genera una imagen por defecto de Unsplash
- ❌ Solo se muestra 1 imagen cuando subiste 3
- ❌ El carrusel no aparece
- ❌ Las imágenes no se muestran (icono roto 🖼️❌)
- ❌ El botón "Crear Producto" se queda en "Procesando..." sin terminar

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca cada punto cuando lo verifiques:

### En el Navegador:
- [ ] Las previews de las imágenes aparecen después de seleccionarlas
- [ ] El contador muestra "X/5" correctamente
- [ ] Los logs con emojis aparecen en la consola
- [ ] Se muestran las URLs generadas en los logs
- [ ] Se confirma la creación de hidden inputs
- [ ] La redirección funciona (302)

### En Django:
- [ ] Los logs muestran "INICIO DE SUBIDA DE IMÁGENES"
- [ ] Se procesan todos los archivos
- [ ] Se guardan en `frontend/media/product_images/`
- [ ] Se generan URLs correctas (`/media/product_images/...`)
- [ ] Los logs muestran "CREANDO PRODUCTO - INICIO"
- [ ] Los campos `image_url_1`, `image_url_2`, etc. tienen valores
- [ ] Se muestra "Producto creado exitosamente"

### En la Interfaz:
- [ ] El producto aparece en "Mis Productos"
- [ ] Se ve la primera imagen
- [ ] El badge muestra el número correcto de imágenes
- [ ] El carrusel mini funciona (flechas navegables)
- [ ] En el detalle, el carrusel grande funciona
- [ ] Los indicadores de puntos funcionan
- [ ] Las miniaturas son clickeables
- [ ] NO hay imágenes por defecto/aleatorias

---

## 🎉 SI TODO ESTÁ ✅

¡Felicidades! La solución funciona correctamente. Ahora puedes:
1. Crear más productos con diferentes cantidades de imágenes
2. Editar productos existentes
3. Probar con imágenes más grandes
4. Verificar que funciona en todas las páginas

## 🆘 SI ALGO ESTÁ ❌

1. Toma screenshots de lo que ves
2. Copia los logs completos (navegador y Django)
3. Indica exactamente en qué paso falló
4. Describe qué esperabas vs qué obtuviste
