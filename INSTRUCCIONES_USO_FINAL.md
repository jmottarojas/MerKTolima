# 📖 INSTRUCCIONES DE USO - Sistema de Upload de Imágenes

## 🎯 Para Usuarios (Vendedores)

### Crear un Producto con Imágenes

#### Paso 1: Iniciar Sesión
```
1. Ir a: http://localhost:8001/login/
2. Ingresar credenciales de vendedor
3. Hacer clic en "Iniciar Sesión"
```

#### Paso 2: Ir a Crear Producto
```
1. Hacer clic en "Panel Vendedor" en el menú
2. Hacer clic en "Crear Producto"
O directamente: http://localhost:8001/vendedor/producto/nuevo/
```

#### Paso 3: Llenar Información del Producto

**Información Básica (Obligatorio):**
- Nombre del Producto
- Categoría
- Precio (en pesos colombianos)
- Descripción

**Información Detallada (Obligatorio):**
- Condición (Nuevo/Usado/Reacondicionado)
- Marca
- Modelo

**Especificaciones Técnicas (Solo para Electrónicos):**
- Procesador
- RAM
- Almacenamiento
- Tamaño de Pantalla
- Sistema Operativo
- Conectividad
- Cantidad en inventario

#### Paso 4: Subir Imágenes

**Opción A: Desde tu PC (Recomendado)**
```
1. Hacer clic en la pestaña "Subir desde PC"
2. Hacer clic en "Seleccionar Archivos"
3. Seleccionar 1-5 imágenes (JPG, PNG, GIF, WEBP)
4. Ver los previews de las imágenes
5. La primera imagen será la imagen principal
```

**Opción B: Desde URLs**
```
1. Hacer clic en la pestaña "URL de Imagen"
2. Pegar la URL de la imagen
3. Hacer clic en el ícono del ojo para ver preview
4. Agregar más URLs si deseas (máximo 5)
```

**Requisitos de las Imágenes:**
- Tamaño máximo: 5MB por imagen
- Formatos: JPG, JPEG, PNG, GIF, WEBP
- Cantidad: Mínimo 1, máximo 5 imágenes
- La primera imagen será la principal

#### Paso 5: Crear Producto
```
1. Verificar que todos los campos estén completos
2. Verificar que las imágenes estén cargadas
3. Hacer clic en "Crear Producto"
4. Esperar confirmación
5. Serás redirigido a la lista de productos
```

#### Paso 6: Verificar Producto Creado
```
1. Ir a "Mis Productos"
2. Buscar el producto recién creado
3. Verificar que las imágenes se muestren correctamente
4. Hacer clic en el producto para ver el detalle
5. Verificar que el carrusel de imágenes funcione
```

---

## 🔧 Para Desarrolladores

### Iniciar los Servidores

#### Opción 1: Script Automático
```bash
python start_complete_platform.py
```

#### Opción 2: Manual
```bash
# Terminal 1 - Django (Frontend)
cd frontend
python run_django.py

# Terminal 2 - FastAPI (Backend)
python run_server.py
```

### Verificar que los Servidores Estén Corriendo
```
Django: http://localhost:8001/
FastAPI: http://localhost:8000/docs
```

### Debugging

#### Ver Logs en el Navegador
```
1. Abrir consola del navegador (F12)
2. Ir a la pestaña "Console"
3. Activar "Preserve log" (casilla en la parte superior)
4. Realizar la acción (crear producto)
5. Revisar los logs con emojis
```

#### Logs Esperados
```
📤 Modo: Upload desde PC
📁 Archivos en uploadedFiles: X
🔄 Subiendo archivos al servidor...
   📎 Archivo 0: nombre.jpg
📥 Respuesta upload: 200
📦 Resultado upload: {success: true, ...}
✅ Upload exitoso: X imágenes
📊 Total de URLs obtenidas: X
🔍 URL Container encontrado: SÍ
📝 Creando hidden inputs para URLs...
   ✅ Created hidden input: image_url_1 = /media/...
🔍 Hidden inputs en container: X
📋 Verificando FormData:
📋 Total entries en FormData: XX
   image_url_1: /media/...
📊 Total image_url_ encontrados en FormData: X
🚀 Enviando formulario con X imágenes...
📥 Respuesta recibida: 200
↪️ Redirigiendo a: http://localhost:8001/vendedor/productos/
```

#### Ver Logs del Backend
```
# En la terminal donde corre Django
============================================================
🔍 CREANDO PRODUCTO - INICIO
============================================================
📦 Recopilando URLs de imágenes del formulario...
   image_url_1: '/media/product_images/...' (tipo: <class 'str'>)
   ✅ Agregada imagen 1: /media/product_images/...
📊 Total de imágenes recopiladas: X
✅ Usando X imágenes subidas por el usuario
============================================================
```

### Problemas Comunes

#### Problema: "Debes subir al menos una imagen"
**Solución:**
1. Verificar que los archivos se cargaron (ver previews)
2. Abrir consola y verificar logs
3. Buscar el log "📁 Archivos en uploadedFiles: X"
4. Si es 0, los archivos no se cargaron correctamente
5. Recargar página con Ctrl+Shift+R

#### Problema: Error 404 al subir imágenes
**Solución:**
1. Verificar que Django esté corriendo en puerto 8001
2. Verificar la URL en el código: `/api/upload-images/`
3. Verificar que el endpoint esté registrado en urls.py

#### Problema: Sesión expirada
**Solución:**
1. Volver a iniciar sesión
2. Intentar crear el producto de nuevo
3. Verificar en "Mis Productos" si el producto se creó antes de expirar

#### Problema: Imágenes no se ven en el producto
**Solución:**
1. Verificar que los archivos estén en `frontend/media/product_images/`
2. Verificar que FastAPI esté sirviendo `/media`
3. Abrir la URL de la imagen directamente en el navegador
4. Verificar permisos de la carpeta media

### Estructura de Archivos

```
Merkatolima/
├── frontend/
│   ├── media/
│   │   └── product_images/          # Imágenes subidas
│   ├── static/
│   │   └── js/
│   │       └── image-upload.js      # Comentado
│   ├── templates/
│   │   └── marketplace/
│   │       ├── create_product.html  # Formulario principal
│   │       ├── product_detail.html  # Detalle con carrusel
│   │       └── seller_products.html # Lista de productos
│   └── marketplace/
│       ├── views.py                 # Lógica de backend
│       └── urls.py                  # Rutas
├── src/
│   └── api/
│       └── main.py                  # FastAPI
└── RESUMEN_COMPLETO_CAMBIOS.md     # Este documento
```

### Endpoints Importantes

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/upload-images/` | POST | Subir archivos de imágenes |
| `/vendedor/producto/nuevo/` | GET/POST | Crear producto |
| `/vendedor/productos/` | GET | Lista de productos del vendedor |
| `/producto/<id>/` | GET | Detalle del producto |
| `/media/product_images/<file>` | GET | Servir archivos de imágenes |

### Variables de Entorno

```env
# Django
DEBUG=True
SECRET_KEY=...
ALLOWED_HOSTS=localhost,127.0.0.1

# Media Files
MEDIA_ROOT=frontend/media
MEDIA_URL=/media/

# FastAPI
API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Test Manual

1. **Crear producto con 1 imagen**
   - Verificar que se crea correctamente
   - Verificar que la imagen se muestra

2. **Crear producto con 5 imágenes**
   - Verificar que todas se suben
   - Verificar que el carrusel funciona

3. **Crear producto con URLs**
   - Usar URLs de Unsplash
   - Verificar que se muestran correctamente

4. **Intentar subir archivo muy grande**
   - Verificar que muestra error
   - Verificar que no se sube

5. **Intentar subir archivo no válido**
   - Subir un PDF o TXT
   - Verificar que muestra error

### Test de Compatibilidad

1. **Chrome** - ✅ Funcional
2. **Firefox** - ✅ Funcional
3. **Edge** - ✅ Funcional
4. **Safari** - ✅ Funcional
5. **Navegadores antiguos** - ✅ Compatible (sin for...of)

---

## 📞 Soporte

### Logs de Debugging
- Frontend: Consola del navegador (F12)
- Backend: Terminal de Django
- API: Terminal de FastAPI

### Archivos de Referencia
- `RESUMEN_COMPLETO_CAMBIOS.md` - Cambios técnicos
- `SOLUCION_DEFINITIVA.md` - Solución del problema principal
- `DEBUG_PASO_A_PASO.md` - Guía de debugging

---

**Última actualización:** 16 de Enero de 2026
