# 📦 CREAR PRODUCTO DE PRUEBA PARA EL CARRITO

## ⚠️ PROBLEMA ACTUAL

El error "400 Bad Request" al agregar al carrito significa que el producto no está disponible. Esto puede ser porque:
1. El producto tiene `status != "active"`
2. El producto tiene `inventory_quantity = 0`

## ✅ SOLUCIÓN: Crear Producto Nuevo

### Paso 1: Iniciar Sesión como Vendedor
```
URL: http://localhost:8001/login/
Usuario: vendedor@merkatolima.com
Contraseña: Vendedor123
```

### Paso 2: Ir a Crear Producto
```
URL: http://localhost:8001/vendedor/producto/nuevo/
```

### Paso 3: Llenar el Formulario

**Información Básica:**
- Nombre: `iPhone 15 Pro Max - Prueba Carrito`
- Categoría: `Electrónicos`
- Precio: `4500000` (COP)
- Descripción: `Smartphone de última generación para pruebas del carrito`

**Inventario:**
- Cantidad Disponible: `25` ⬅️ **IMPORTANTE: Debe ser mayor a 0**
- Alerta de Stock Bajo: `5`

**Imágenes:**
Puedes:
- Subir imágenes desde tu PC, O
- Usar URLs de ejemplo:
  ```
  https://images.unsplash.com/photo-1592286927505-c80d1b7e8b8e?w=400
  https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400
  ```

### Paso 4: Crear Producto
1. Hacer clic en "Crear Producto"
2. **VERIFICAR**: Debe aparecer mensaje "Producto creado exitosamente"
3. Anotar el ID del producto (aparece en la URL)

### Paso 5: Verificar el Producto
1. Ir a: `http://localhost:8001/vendedor/productos/`
2. **VERIFICAR**:
   - ✅ El producto aparece en la lista
   - ✅ Muestra "25 en stock"
   - ✅ Badge verde "Disponible" (no "Agotado")

## 🧪 PROBAR EL CARRITO

### Paso 1: Cerrar Sesión
1. Hacer clic en tu nombre en el navbar
2. Seleccionar "Cerrar Sesión"

### Paso 2: Iniciar Sesión como Comprador
```
URL: http://localhost:8001/login/
Usuario: comprador@merkatolima.com
Contraseña: Comprador123
```

### Paso 3: Buscar el Producto
1. Ir a: `http://localhost:8001/productos/`
2. Buscar "iPhone 15 Pro Max - Prueba Carrito"
3. Hacer clic en "Ver Detalles"

### Paso 4: Verificar Disponibilidad
**ANTES de agregar al carrito, verificar:**
- ✅ Dice "En stock"
- ✅ Muestra "(25 disponibles)"
- ✅ El botón "Agregar al Carrito" está habilitado (no gris)

### Paso 5: Agregar al Carrito
1. Seleccionar cantidad: `2`
2. Hacer clic en "Agregar al Carrito"
3. **VERIFICAR**:
   - ✅ Aparece mensaje verde: "Producto agregado al carrito"
   - ✅ Badge del carrito en navbar muestra "2"
   - ✅ NO aparece error 400

### Paso 6: Ver el Carrito
1. Hacer clic en "Carrito" en el navbar
2. **VERIFICAR**:
   - ✅ El carrito muestra el producto
   - ✅ Cantidad: 2
   - ✅ Subtotal correcto
   - ✅ Total correcto

## 🔍 SI SIGUE DANDO ERROR 400

### Opción A: Verificar en la Consola del Navegador
1. Abrir consola (F12)
2. Ir a pestaña "Network"
3. Intentar agregar al carrito
4. Buscar la petición POST a `/api/v1/orders/cart/items`
5. Ver la respuesta del servidor

**Posibles mensajes de error:**
- `"Product ... is not available"` → El status del producto no es "active"
- `"Insufficient inventory"` → El inventario es 0 o menor que la cantidad solicitada
- `"Product ... not found"` → El ID del producto no existe

### Opción B: Verificar el Producto Directamente

Abre esta URL en el navegador (reemplaza `PRODUCT_ID` con el ID real):
```
http://localhost:8000/api/v1/products/PRODUCT_ID
```

**Verificar en la respuesta JSON:**
```json
{
  "id": "...",
  "name": "iPhone 15 Pro Max - Prueba Carrito",
  "inventory_quantity": 25,  ⬅️ Debe ser > 0
  "status": "active",        ⬅️ Debe ser "active"
  ...
}
```

Si `status` no es "active" o `inventory_quantity` es 0:
1. Editar el producto como vendedor
2. Cambiar la cantidad a un número mayor a 0
3. Guardar cambios
4. Verificar nuevamente

## 📊 DATOS IMPORTANTES

### Status del Producto
El producto solo está disponible si:
- `status == "active"` Y
- `inventory_quantity > 0`

### Cómo se Determina el Status
- Al crear: `status = "active"` si `inventory_quantity > 0`, sino `"out_of_stock"`
- Al editar: Si cambias inventario de 0 a >0, el status cambia a "active"

### Validaciones del Carrito
El API valida:
1. ✅ Producto existe
2. ✅ Producto está disponible (`is_available == True`)
3. ✅ Hay suficiente inventario
4. ✅ Cantidad es válida (> 0 y <= max permitido)

## 🎯 RESULTADO ESPERADO

Después de crear un producto nuevo con inventario > 0:
- ✅ El producto debe tener `status = "active"`
- ✅ Debe aparecer como "En stock" para compradores
- ✅ Debe poder agregarse al carrito sin error 400
- ✅ El carrito debe mostrar el producto correctamente

## ⚠️ NOTA IMPORTANTE

Los productos se almacenan en memoria (InMemory), por lo que:
- ❌ Se pierden al reiniciar el servidor FastAPI
- ✅ Persisten mientras el servidor esté corriendo
- ✅ Puedes crear múltiples productos para pruebas

Si reinicias el servidor FastAPI, necesitarás crear los productos nuevamente.
