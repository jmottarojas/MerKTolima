# Merkatolima - Frontend Web Application

## 🏪 Descripción

Merkatolima es una plataforma de marketplace completa desarrollada con Django que se conecta con el backend FastAPI. Ofrece una experiencia de usuario moderna y profesional con diseño responsivo y funcionalidades completas de e-commerce.

## ✨ Características Principales

### 🎨 Diseño y UX
- **Diseño Profesional**: Interfaz moderna con colores corporativos (binotinto #722F37 y amarillo oro #FFD700)
- **Responsive**: Compatible con dispositivos móviles, tablets y desktop
- **Bootstrap 5**: Framework CSS moderno para componentes y layouts
- **Font Awesome**: Iconografía profesional
- **Google Fonts**: Tipografía Poppins para mejor legibilidad

### 🔐 Sistema de Autenticación
- **Registro de usuarios**: Compradores y vendedores
- **Inicio de sesión**: Autenticación basada en sesiones
- **Gestión de perfiles**: Actualización de información personal
- **Roles diferenciados**: Funcionalidades específicas por tipo de usuario

### 🛒 Funcionalidades de Compra
- **Catálogo de productos**: Navegación por categorías y búsqueda avanzada
- **Carrito de compras**: Gestión completa de productos seleccionados
- **Proceso de checkout**: Flujo completo de compra con información de envío
- **Historial de pedidos**: Seguimiento de compras realizadas

### 🏪 Panel de Vendedor
- **Dashboard completo**: Estadísticas y resumen de actividad
- **Gestión de productos**: Crear, editar y administrar inventario
- **Gestión de pedidos**: Seguimiento de ventas y estados
- **Herramientas de vendedor**: Funcionalidades específicas para comerciantes

### 🔍 Búsqueda y Filtros
- **Búsqueda inteligente**: Por nombre, descripción y categoría
- **Filtros avanzados**: Por precio, categoría y disponibilidad
- **Resultados paginados**: Navegación eficiente de productos

### 🤖 Chatbot Inteligente MerkaBot
- **Asistente virtual**: Ayuda contextual en todas las páginas
- **Preguntas frecuentes**: Respuestas categorizadas por temas
- **Guías de compra**: Asistencia paso a paso para compradores
- **Soporte de ventas**: Ayuda para vendedores y publicación de productos
- **Interfaz moderna**: Diseño responsivo con animaciones
- **Navegación inteligente**: Redirección automática a páginas relevantes

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Backend FastAPI ejecutándose en http://localhost:8000

### Instalación de Dependencias

```bash
cd frontend
python -m pip install -r requirements.txt
```

### Configuración de Base de Datos

```bash
python manage.py migrate
```

### Crear Directorio de Archivos Estáticos

```bash
mkdir static
```

## 🏃‍♂️ Ejecución

### Opción 1: Script Individual
```bash
cd frontend
python run_django.py
```

### Opción 2: Script Completo (API + Frontend)
```bash
python start_marketplace.py
```

### Opción 3: Django Tradicional
```bash
cd frontend
python manage.py runserver 0.0.0.0:8001
```

## 🌐 Acceso a la Aplicación

- **Frontend Web**: http://localhost:8001
- **API Backend**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 👥 Usuarios de Prueba

### Comprador
- **Email**: buyer@test.com
- **Contraseña**: Password123
- **Rol**: Comprador

### Vendedor
- **Email**: seller@test.com
- **Contraseña**: Password123
- **Rol**: Vendedor

## 📱 Páginas Disponibles

### Páginas Públicas
- **Inicio** (`/`): Página principal con productos destacados
- **Productos** (`/productos/`): Catálogo completo con filtros
- **Búsqueda** (`/buscar/`): Búsqueda avanzada de productos
- **Detalle de Producto** (`/producto/<id>/`): Información completa del producto

### Páginas de Autenticación
- **Registro** (`/registro/`): Crear nueva cuenta
- **Iniciar Sesión** (`/login/`): Acceso a cuenta existente
- **Perfil** (`/perfil/`): Gestión de información personal

### Páginas de Comprador
- **Carrito** (`/carrito/`): Gestión de productos seleccionados
- **Checkout** (`/checkout/`): Proceso de compra
- **Mis Pedidos** (`/pedidos/`): Historial de compras
- **Detalle de Pedido** (`/pedido/<id>/`): Información específica del pedido

### Páginas de Vendedor
- **Panel de Vendedor** (`/vendedor/`): Dashboard principal
- **Mis Productos** (`/vendedor/productos/`): Gestión de inventario
- **Crear Producto** (`/vendedor/producto/nuevo/`): Agregar nuevo producto
- **Editar Producto** (`/vendedor/producto/<id>/editar/`): Modificar producto existente
- **Mis Pedidos** (`/vendedor/pedidos/`): Gestión de ventas

### Páginas de Notificaciones
- **Notificaciones** (`/notificaciones/`): Centro de mensajes del usuario

## 🎨 Personalización de Diseño

### Colores Corporativos
```css
:root {
    --binotinto: #722F37;
    --amarillo-oro: #FFD700;
    --binotinto-light: #8B4A52;
    --binotinto-dark: #5A252A;
    --amarillo-oro-light: #FFED4E;
    --amarillo-oro-dark: #E6C200;
}
```

### Componentes Personalizados
- **Tarjetas de producto**: Efectos hover y animaciones
- **Botones**: Gradientes y transiciones suaves
- **Navegación**: Barra superior con búsqueda integrada
- **Footer**: Información corporativa y enlaces útiles

## 🔧 Configuración Técnica

### Variables de Entorno
```python
# frontend/merkatolima_frontend/settings.py
API_BASE_URL = 'http://localhost:8000'  # URL del backend FastAPI
DEBUG = True  # Modo desarrollo
SECRET_KEY = 'django-insecure-merkatolima-dev-key-2024'
```

### Integración con API
- **Cliente HTTP**: Requests para comunicación con FastAPI
- **Manejo de errores**: Gestión robusta de respuestas de API
- **Autenticación**: Tokens JWT almacenados en sesiones Django
- **Cache de sesión**: Información de usuario persistente

## 📊 Funcionalidades Especiales

### 🤖 Chatbot MerkaBot
- **Ubicación**: Botón flotante en esquina inferior derecha
- **Funcionalidades principales**:
  - Preguntas frecuentes categorizadas (pagos, envíos, seguridad, etc.)
  - Guías de compra paso a paso
  - Asistencia para vendedores y publicación de productos
  - Soporte técnico integrado
  - Navegación inteligente del sitio
- **Tecnología**: JavaScript vanilla con CSS3 animations
- **Responsive**: Adaptado para móviles y desktop
- **Integración**: Disponible en todas las páginas del sitio

### Generación de Productos de Prueba
- **Endpoint AJAX**: `/api/generar-productos-prueba/`
- **Productos automáticos**: 8 productos de diferentes categorías
- **Imágenes placeholder**: URLs de ejemplo para visualización
- **Inventario realista**: Cantidades y precios variados

### Gestión de Carrito
- **Persistencia**: Carrito vinculado al usuario
- **Actualización dinámica**: Cambios en tiempo real
- **Validación de stock**: Verificación de disponibilidad
- **Cálculos automáticos**: Subtotales y totales

### Sistema de Búsqueda
- **Búsqueda por texto**: Nombre y descripción de productos
- **Filtros múltiples**: Categoría, precio mínimo y máximo
- **Resultados paginados**: Navegación eficiente
- **URLs amigables**: Parámetros de búsqueda en URL

## 🛠️ Estructura del Proyecto

```
frontend/
├── manage.py                          # Script principal de Django
├── run_django.py                      # Script personalizado de inicio
├── requirements.txt                   # Dependencias Python
├── db.sqlite3                         # Base de datos SQLite
├── static/                            # Archivos estáticos
│   ├── css/
│   │   └── chatbot.css               # Estilos del chatbot
│   └── js/
│       └── chatbot.js                # Lógica del chatbot
├── templates/                         # Plantillas HTML
│   ├── base.html                      # Plantilla base
│   └── marketplace/                   # Plantillas de la app
│       ├── home.html                  # Página de inicio
│       ├── login.html                 # Inicio de sesión
│       ├── register.html              # Registro
│       ├── products.html              # Lista de productos
│       ├── product_detail.html        # Detalle de producto
│       ├── cart.html                  # Carrito de compras
│       ├── search.html                # Búsqueda
│       ├── profile.html               # Perfil de usuario
│       └── seller_dashboard.html      # Panel de vendedor
├── marketplace/                       # Aplicación Django principal
│   ├── __init__.py
│   ├── views.py                       # Vistas de la aplicación
│   ├── urls.py                        # URLs de la aplicación
│   ├── api_client.py                  # Cliente para comunicación con API
│   └── apps.py                        # Configuración de la app
└── merkatolima_frontend/              # Configuración del proyecto
    ├── __init__.py
    ├── settings.py                    # Configuración Django
    ├── urls.py                        # URLs principales
    └── wsgi.py                        # Configuración WSGI
```

## 🔍 Debugging y Desarrollo

### Logs de Django
```bash
# Ver logs en tiempo real
python manage.py runserver --verbosity=2
```

### Verificación de API
```bash
# Probar conexión con backend
curl http://localhost:8000/health
```

### Inspección de Sesiones
```python
# En Django shell
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all()
```

## 🚀 Despliegue en Producción

### Configuraciones Necesarias
1. **DEBUG = False** en settings.py
2. **ALLOWED_HOSTS** configurado apropiadamente
3. **Servidor web** (Nginx + Gunicorn recomendado)
4. **Base de datos** PostgreSQL o MySQL
5. **Archivos estáticos** servidos por servidor web
6. **Variables de entorno** para configuración sensible

### Comandos de Despliegue
```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

## 📞 Soporte y Contacto

Para soporte técnico o consultas sobre el desarrollo:
- **Email**: info@merkatolima.com
- **Documentación API**: http://localhost:8000/docs
- **Repositorio**: Consultar documentación del proyecto principal

---

**Merkatolima** - El marketplace colombiano que conecta compradores y vendedores con la mejor experiencia de compra online.