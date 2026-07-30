# Marketplace Platform

Una plataforma de marketplace con arquitectura de microservicios desarrollada en Python.

## Estructura del Proyecto

```
marketplace-platform/
├── src/
│   ├── shared/           # Código compartido entre servicios
│   │   ├── database.py   # Configuración de base de datos
│   │   ├── models.py     # Modelos base y estructuras comunes
│   │   └── auth.py       # Utilidades de autenticación
│   ├── services/         # Microservicios
│   │   ├── users/        # Servicio de usuarios
│   │   ├── products/     # Servicio de productos
│   │   ├── orders/       # Servicio de pedidos
│   │   ├── payments/     # Servicio de pagos
│   │   └── notifications/ # Servicio de notificaciones
│   └── api/              # API Gateway
│       └── main.py       # Aplicación principal FastAPI
├── tests/                # Tests
├── requirements.txt      # Dependencias Python
├── pyproject.toml       # Configuración del proyecto
└── .env.example         # Variables de entorno de ejemplo
```

## Configuración

1. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

## Comandos Disponibles

- `make install` - Instalar dependencias
- `make test` - Ejecutar tests
- `make test-cov` - Ejecutar tests con cobertura
- `make lint` - Ejecutar linting
- `make format` - Formatear código
- `make run` - Ejecutar el servidor API
- `make clean` - Limpiar archivos temporales

## Testing

El proyecto utiliza:
- **pytest** para tests unitarios
- **hypothesis** para property-based testing
- **pytest-cov** para cobertura de código

Ejecutar tests:
```bash
pytest
```

Ejecutar tests con cobertura:
```bash
pytest --cov=src --cov-report=html
```

## Desarrollo

1. El código debe seguir las convenciones de PEP 8
2. Usar type hints en todas las funciones
3. Escribir tests para toda nueva funcionalidad
4. Mantener cobertura de tests > 80%

## Servicios

- **API Gateway**: Punto de entrada único, maneja autenticación y enrutamiento
- **User Service**: Gestión de usuarios, registro y autenticación
- **Product Service**: CRUD de productos, inventario y búsqueda
- **Order Service**: Carrito de compras y procesamiento de pedidos
- **Payment Service**: Procesamiento de pagos y integración con gateways
- **Notification Service**: Envío de notificaciones por email y en plataforma