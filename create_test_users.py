#!/usr/bin/env python3
"""Script para crear usuarios de prueba en el sistema."""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.users.service import UserService, UserRegistrationData
from src.services.users.repository import SQLAlchemyUserRepository
from src.shared.database import get_db_session, create_tables


async def create_test_users():
    """Crear usuarios de prueba."""
    # Verificar si usar base de datos
    use_database = os.getenv("USE_DATABASE", "False").lower() == "true"
    
    if use_database:
        # Crear tablas si no existen
        create_tables()
        # Obtener sesión de base de datos
        db_session = get_db_session()
        # Crear repositorio SQLAlchemy
        repository = SQLAlchemyUserRepository(db_session)
        print("🗄️ Usando base de datos SQLAlchemy")
    else:
        # Usar repositorio en memoria
        from src.services.users.repository import InMemoryUserRepository
        repository = InMemoryUserRepository()
        print("💾 Usando repositorio en memoria")
    
    # Crear servicio de usuarios con el repositorio apropiado
    user_service = UserService(repository)
    
    test_users = [
        {
            'email': 'admin@merktolima.com',
            'password': 'Admin123!',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'role': 'seller'
        },
        {
            'email': 'vendedor@merktolima.com',
            'password': 'Vendedor123!',
            'first_name': 'Juan Carlos',
            'last_name': 'Vendedor',
            'role': 'seller'
        },
        {
            'email': 'comprador@merktolima.com',
            'password': 'Comprador123!',
            'first_name': 'María Elena',
            'last_name': 'Compradora',
            'role': 'buyer'
        },
        {
            'email': 'test@merktolima.com',
            'password': 'Test123!',
            'first_name': 'Usuario',
            'last_name': 'Prueba',
            'role': 'buyer'
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            registration_data = UserRegistrationData(**user_data)
            user = await user_service.register_user(registration_data)
            created_users.append(user)
            print(f"✅ Usuario creado: {user.email} ({user.first_name} {user.last_name})")
        except Exception as e:
            print(f"❌ Error creando usuario {user_data['email']}: {e}")
    
    # Cerrar sesión de base de datos si se usó
    if use_database:
        db_session.close()
    
    print(f"\n🎉 Se crearon {len(created_users)} usuarios de prueba exitosamente!")
    print("\n📋 Credenciales de acceso:")
    print("=" * 50)
    
    for user_data in test_users:
        print(f"Email: {user_data['email']}")
        print(f"Contraseña: {user_data['password']}")
        print(f"Rol: {user_data['role']}")
        print("-" * 30)


if __name__ == "__main__":
    print("🚀 Creando usuarios de prueba para Merktolima...")
    asyncio.run(create_test_users())