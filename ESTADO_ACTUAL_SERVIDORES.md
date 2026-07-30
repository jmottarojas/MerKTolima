# 🟢 Estado Actual de los Servidores - LISTO PARA PROBAR

## ✅ Servidores Activos y Funcionando

### 🔧 Backend FastAPI (Proceso 6)
- **Puerto**: 8000
- **URL**: http://localhost:8000
- **Estado**: ✅ ACTIVO
- **Características**:
  - ✅ API Gateway funcionando
  - ✅ Archivos media montados en `/media`
  - ✅ **Proxy a Django configurado** (todas las peticiones `/marketplace/*` se redirigen a Django)
  - ✅ 5 usuarios de prueba creados

### 🎨 Frontend Django (Proceso 4)
- **Puerto**: 8001
- **URL**: http://localhost:8001
- **Estado**: ✅ ACTIVO
- **Características**:
  - ✅ Servidor de desarrollo activo
  - ✅ Recarga automática de archivos
  - ✅ Endpoint de subida de imágenes: `/marketplace/api/upload-images/`
  - ✅ URLs relativas configuradas

## 🎯 CÓMO ACCEDER Y PROBAR

### URL Principal (USA ESTA):
```
http://localhost:8000/marketplace/
```

**IMPORTANTE**: Debes usar el puerto **8000** (FastAPI), NO el 8001.

### ¿Por qué usar el puerto 8000?

Porque FastAPI actúa como gateway y:
1. ✅ Hace proxy de todas las peticiones `/marketplace/*` a Django
2. ✅ Sirve los archivos media desde `/media`
3. ✅ Todo funciona de forma integrada

## 🚀 PASOS PARA PROBAR LA SUBIDA DE IMÁGENES

### 1. Abrir el Navegador
```
http://localhost:8000/marketplace/
```

### 2. Iniciar Sesión como Vendedor
- **Email**: `seller@test.com`
- **Password**: `Password123`

### 3. Abrir Consola del Navegador
Presiona **F12** → Pestaña **"Console"**

### 4. Ir a Crear Producto
1. Click en **"Panel Vendedor"**
2. Click en **"Crear Producto"**

### 5. Llenar el Formulario
```
Nombre: Laptop Gaming Test
Categoría: Electrónicos
Precio: 3500000
Descripción: Laptop para probar subida de imágenes
Condición: Nuevo
Marca: ASUS
Modelo: ROG-2024
Cantidad: 5

Especificaciones Técnicas (OBLIGATORIAS para Electrónicos):
- Procesador: AMD Ryzen 7
- RAM: 16GB
- Almacenamiento: 512GB SSD
- Pantalla: 15.6 pulgadas
- Sistema Operativo: Windows 11
- Conectividad: WiFi, Bluetooth, USB-C (Ctrl+Click para múltiples)
```

### 6. Subir Imágenes
1. Ve a la sección **"Imágenes del Producto"**
2. Click en el tab **"Subir desde PC"**
3. Selecciona **2-3 imágenes** (JPG o PNG)
4. Verifica que aparecen los **previews**

### 7. Observar Logs en Consola
Deberías ver:
```
📁 Seleccionados 3 archivos
  - imagen1.jpg (0.25 MB)
  - imagen2.jpg (0.30 MB)
```

### 8. Enviar Formulario
Click en **"Crear Producto"**

### 9. Logs Esperados en Consola
```
🔄 Subiendo 3 archivos...
Archivos a subir: ['imagen1.jpg', 'imagen2.jpg', 'imagen3.jpg']
📎 Agregando archivo 0: imagen1.jpg (262144 bytes, image/jpeg)
📎 Agregando archivo 1: imagen2.jpg (314572 bytes, image/jpeg)
📎 Agregando archivo 2: imagen3.jpg (293847 bytes, image/jpeg)
FormData keys: ['image_0', 'image_1', 'image_2']
🔐 Token CSRF: Presente
📡 Enviando petición a: /marketplace/api/upload-images/
📥 Respuesta del servidor: 200 OK
📦 Resultado completo: {success: true, image_urls: [...], count: 3}
✅ Subida exitosa: 3 imágenes
🖼️ URLs generadas: ['/media/product_images/...', ...]
Obteniendo URLs de imágenes...
URLs obtenidas: ['/media/product_images/...', ...]
Formulario listo para enviar con 3 imágenes
```

### 10. Verificar Resultado
1. Serás redirigido a **"Mis Productos"**
2. Busca el producto **"Laptop Gaming Test"**
3. **VERIFICA**:
   - ✅ Muestra **carrusel** con tus 3 imágenes
   - ✅ **NO** muestra imagen por defecto
   - ✅ Controles de navegación funcionan
   - ✅ Indicadores de puntos funcionan

4. Click en **"Ver"** para detalle completo
5. **VERIFICA**:
   - ✅ Carrusel grande
   - ✅ Miniaturas debajo
   - ✅ Click en miniaturas cambia imagen
   - ✅ Badge "Imagen Principal"

## 🔍 Verificaciones Adicionales

### Verificar Archivos Guardados
Los archivos están en:
```
C:\Python\Marketplace\Merkatolima\frontend\media\product_images\
```

Deberías ver archivos con nombres UUID:
```
abc123-def456-789.jpg
xyz789-abc123-456.jpg
```

### Verificar que FastAPI Sirve las Imágenes
1. Copia una URL de imagen: `/media/product_images/abc123.jpg`
2. Accede en el navegador:
   ```
   http://localhost:8000/media/product_images/abc123.jpg
   ```
3. Debería mostrar la imagen

## 📊 Monitorear Logs del Servidor Django

Si quieres ver los logs mientras pruebas, observa la terminal.

Deberías ver:
```
============================================================
🔄 INICIO DE SUBIDA DE IMÁGENES
============================================================
✅ Usuario autenticado: user_abc123
📦 Archivos recibidos: ['image_0', 'image_1', 'image_2']
📦 Total de archivos: 3

📎 Procesando archivo: imagen1.jpg
   - Tipo: image/jpeg
   - Tamaño: 262144 bytes (0.25 MB)
   - Nombre único: abc123-def456.jpg
✅ Archivo guardado en: C:\...\frontend\media\product_images\abc123-def456.jpg
🔗 URL generada: /media/product_images/abc123-def456.jpg

============================================================
✅ SUBIDA COMPLETADA
   - Total URLs generadas: 3
============================================================
```

## 🎉 Cambios Implementados

1. ✅ **Proxy de Django en FastAPI** - Redirige `/marketplace/*` a Django
2. ✅ **URLs relativas** - Las imágenes usan `/media/...` en lugar de `http://localhost:8001/media/...`
3. ✅ **FastAPI sirve media** - Los archivos son accesibles desde el puerto 8000
4. ✅ **Logs detallados** - Para debugging fácil
5. ✅ **httpx instalado** - Librería para el proxy

## ❌ Si Algo No Funciona

### Error: "Not Found" al subir imágenes
**Solución**: Verifica que estás usando `http://localhost:8000` (no 8001)

### Error: Las imágenes no se muestran
**Solución**: 
1. Verifica en logs de FastAPI: `📁 Media files mounted at /media`
2. Verifica que el directorio `frontend/media/` existe
3. Reinicia FastAPI si es necesario

### Error: "Usuario no autenticado"
**Solución**:
1. Cierra sesión y vuelve a iniciar
2. Limpia cookies del navegador
3. Intenta en ventana de incógnito

## 📞 Reportar Problemas

Si algo no funciona, comparte:
1. ✅ Los logs de la consola del navegador (F12)
2. ✅ En qué paso específico falla
3. ✅ Qué mensaje de error ves
4. ✅ La URL que estás usando

## 🎯 Usuarios de Prueba Disponibles

### Vendedores:
- `seller@test.com` / `Password123`
- `vendedor@merkatolima.com` / `Vendedor123`
- `admin@merkatolima.com` / `Admin123`

### Compradores:
- `buyer@test.com` / `Password123`
- `comprador@merkatolima.com` / `Comprador123`

---

## ✅ TODO ESTÁ LISTO PARA PROBAR

Los servidores están activos y configurados correctamente.

**Abre tu navegador y ve a**: http://localhost:8000/marketplace/

¡Prueba crear un producto con imágenes y verifica que el carrusel funciona! 🚀
