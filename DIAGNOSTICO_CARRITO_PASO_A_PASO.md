# 🔍 DIAGNÓSTICO DEL CARRITO - PASO A PASO

## ⚠️ SITUACIÓN ACTUAL

Estás recibiendo error 400 al intentar agregar productos al carrito, pero los logs del servidor FastAPI no muestran la petición. Necesitamos diagnosticar exactamente qué está pasando.

## 📋 PASOS PARA DIAGNOSTICAR

### PASO 1: Crear un Producto Nuevo

**IMPORTANTE:** El servidor FastAPI se reinició, así que todos los productos anteriores se perdieron.

1. Ir a: `http://localhost:8001/login/`
2. Iniciar sesión como: `vendedor@merkatolima.com` / `Vendedor123`
3. Ir a: `http://localhost:8001/vendedor/producto/nuevo/`
4. Crear producto con estos datos EXACTOS:
   ```
   Nombre: TEST CARRITO
   Categoría: Electrónicos
   Precio: 1000000
   Descripción: Producto de prueba para el carrito
   Cantidad Disponible: 50
   Alerta Stock Bajo: 5
   ```
5. Agregar al menos 1 imagen (desde PC o URL)
6. Hacer clic en "Crear Producto"
7. **ANOTAR EL ID DEL PRODUCTO** (aparece en la URL después de crear)

### PASO 2: Verificar el Producto en el API

1. Abrir una nueva pestaña del navegador
2. Ir a esta URL (reemplaza `PRODUCT_ID` con el ID que anotaste):
   ```
   http://localhost:8000/api/v1/products/PRODUCT_ID
   ```
3. **COPIAR Y PEGAR AQUÍ LA RESPUESTA JSON COMPLETA**

Debería verse algo así:
```json
{
  "id": "abc123",
  "name": "TEST CARRITO",
  "inventory_quantity": 50,
  "status": "active",
  ...
}
```

**VERIFICAR:**
- ✅ `"status": "active"` (NO "out_of_stock")
- ✅ `"inventory_quantity": 50` (NO 0)

### PASO 3: Intentar Agregar al Carrito CON CONSOLA ABIERTA

1. Cerrar sesión del vendedor
2. Iniciar sesión como: `comprador@merkatolima.com` / `Comprador123`
3. **ABRIR LA CONSOLA DEL NAVEGADOR (F12)**
4. Ir a la pestaña "Network" (Red)
5. Buscar el producto "TEST CARRITO"
6. Hacer clic en "Ver Detalles"
7. **VERIFICAR EN LA PÁGINA:**
   - ¿Dice "En stock"? ✅ / ❌
   - ¿Muestra "(50 disponibles)"? ✅ / ❌
   - ¿El botón "Agregar al Carrito" está habilitado? ✅ / ❌
8. Hacer clic en "Agregar al Carrito"
9. **EN LA CONSOLA, BUSCAR LA PETICIÓN:**
   - Buscar: `cart/items`
   - Hacer clic en esa petición
   - Ir a la pestaña "Response" (Respuesta)
   - **COPIAR Y PEGAR AQUÍ LA RESPUESTA COMPLETA**

### PASO 4: Revisar Logs del Servidor FastAPI

Después de intentar agregar al carrito, revisar la terminal donde corre el servidor FastAPI.

**BUSCAR ESTAS LÍNEAS:**
```
============================================================
🛒 ADD TO CART REQUEST
============================================================
```

**SI APARECEN:**
- Copiar y pegar TODO el bloque hasta el siguiente `====`

**SI NO APARECEN:**
- Significa que la petición no está llegando al servidor
- Verificar que el servidor esté corriendo en puerto 8000
- Verificar la URL en la consola del navegador

### PASO 5: Información Adicional

Por favor proporciona:

1. **URL completa que aparece en la consola del navegador** para la petición fallida
2. **Status Code** de la petición (200, 400, 404, 500, etc.)
3. **Request Headers** (Encabezados de la petición) - especialmente:
   - `Authorization`
   - `Content-Type`
4. **Request Payload** (Cuerpo de la petición) - debería ser algo como:
   ```json
   {
     "product_id": "abc123",
     "quantity": 1
   }
   ```
5. **Response** (Respuesta completa del servidor)

## 🎯 LO QUE NECESITO SABER

Con esta información podré identificar exactamente dónde está el problema:

- ❓ ¿El producto tiene el status correcto?
- ❓ ¿La petición está llegando al servidor?
- ❓ ¿Qué error exacto está devolviendo el API?
- ❓ ¿El token de autenticación se está enviando correctamente?

## 📝 FORMATO DE RESPUESTA

Por favor responde con este formato:

```
PASO 2 - Verificación del Producto:
[Pegar JSON aquí]

PASO 3 - Verificación en Página:
- En stock: ✅ / ❌
- Muestra cantidad: ✅ / ❌
- Botón habilitado: ✅ / ❌

PASO 3 - Respuesta de la Consola:
[Pegar respuesta aquí]

PASO 4 - Logs del Servidor:
[Pegar logs aquí O indicar "No aparecen logs"]

PASO 5 - Información Adicional:
- URL: [pegar aquí]
- Status Code: [número]
- Request Payload: [pegar aquí]
- Response: [pegar aquí]
```

Con esta información podré darte una solución exacta y definitiva.
