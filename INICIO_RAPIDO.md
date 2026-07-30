# 🚀 INICIO RÁPIDO - Prueba en 5 Minutos

## ⚡ Pasos Rápidos

### 1. Refresca el Navegador
```
Ctrl + Shift + R
```

### 2. Abre DevTools
```
F12 → Pestaña Console
```

### 3. Inicia Sesión
```
URL: http://localhost:8001/marketplace/
Email: vendedor@merkatolima.com
Password: Vendedor123
```

### 4. Ve a Crear Producto
```
Panel Vendedor → Crear Producto
```

### 5. Llena el Formulario Mínimo

**Información Básica:**
- Nombre: `Test iPhone`
- Categoría: `Electrónicos`
- Precio: `1000000`
- Descripción: `Producto de prueba`

**Información Detallada:**
- Condición: `Nuevo`
- Marca: `Apple`
- Modelo: `iPhone 15`

**Especificaciones (para Electrónicos):**
- Procesador: `Apple A17 Pro`
- RAM: `8GB`
- Almacenamiento: `256GB`
- Pantalla: `6.7 pulgadas`
- Sistema Operativo: `iOS 17`
- Conectividad: `WiFi` (selecciona al menos uno)

**Inventario:**
- Cantidad: `10`

### 6. Sube 2-3 Imágenes
```
Pestaña "Subir desde PC" → Seleccionar Imágenes → Elige 2-3 fotos
```

### 7. Crear Producto
```
Clic en "Crear Producto"
```

### 8. Verifica los Logs

**En la Consola del Navegador:**
```
✅ Debes ver: 🔍 🔄 ✅ 📝 🚀 ↪️
❌ No debes ver: errores rojos
```

**En la Terminal de Django:**
```
✅ Debes ver: 🔄 ✅ 🔍 ✅
❌ No debes ver: ❌ ERROR
```

### 9. Verifica el Resultado

**En "Mis Productos":**
```
✅ Se ve la imagen que subiste
✅ Badge con "🖼️ 3"
✅ Carrusel con flechas
❌ NO imagen por defecto
```

**En "Ver Producto":**
```
✅ Carrusel grande
✅ Todas las imágenes
✅ Flechas funcionan
✅ Miniaturas clickeables
```

---

## ✅ Si Todo Funciona

¡Perfecto! La solución está funcionando. Puedes:
- Crear más productos
- Editar productos
- Probar con más imágenes

---

## ❌ Si Hay Problemas

### Error: "Debes subir al menos una imagen"

**Verifica:**
1. ¿Viste los logs en la consola?
2. ¿Se crearon los hidden inputs?
3. ¿Django recibió image_url_1?

**Acción:**
- Copia los logs completos
- Lee `GUIA_VISUAL_PRUEBA.md` para comparar

### Las imágenes no se muestran

**Verifica:**
1. ¿Los archivos están en `frontend/media/product_images/`?
2. ¿Las URLs son correctas?
3. ¿Puedes acceder a `http://localhost:8001/media/product_images/[archivo]`?

**Acción:**
- Verifica los logs de Django
- Verifica que los archivos se guardaron

### El carrusel no funciona

**Verifica:**
1. ¿El producto tiene más de 1 imagen?
2. ¿Hay errores en la consola?
3. ¿Bootstrap está cargado?

**Acción:**
- Verifica que subiste 2+ imágenes
- Revisa la consola por errores

---

## 📚 Documentación Completa

Si necesitas más detalles:

1. **INSTRUCCIONES_PRUEBA_FINAL.md** - Guía paso a paso detallada
2. **GUIA_VISUAL_PRUEBA.md** - Qué esperar en cada paso
3. **RESUMEN_SOLUCION_IMAGENES.md** - Explicación del problema y solución
4. **SOLUCION_FINAL_UPLOAD.md** - Detalles técnicos de la implementación
5. **CAMBIOS_REALIZADOS_HOY.md** - Lista completa de cambios

---

## 🆘 Necesitas Ayuda?

Si después de seguir estos pasos aún hay problemas:

1. Copia los logs de la consola del navegador
2. Copia los logs de la terminal de Django
3. Toma screenshots
4. Describe qué paso falló

---

**Tiempo estimado:** 5 minutos
**Dificultad:** Fácil
**Prerequisitos:** Servidores corriendo (Django en 8001, FastAPI en 8000)
