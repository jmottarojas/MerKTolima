#!/usr/bin/env python3
"""
Script para inicializar usuarios de prueba en el sistema Merkatolima.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.users.service import UserService, UserRegistrationData
from src.services.users.repository import InMemoryUserRepository


async def create_test_users():
    """Crear usuarios de prueba en el sistema."""
    
    print("🚀 Inicializando usuarios de prueba para Merkatolima...")
    
    # Crear servicio de usuarios
    repository = InMemoryUserRepository()
    user_service = UserService(repository)
    
    # Usuarios de prueba
    test_users = [
        {
            "email": "buyer@test.com",
            "password": "Password123",
            "first_name": "Juan",
            "last_name": "Comprador",
            "role": "buyer"
        },
        {
            "email": "seller@test.com", 
            "password": "Password123",
            "first_name": "María",
            "last_name": "Vendedora",
            "role": "seller"
        },
        {
            "email": "admin@merkatolima.com",
            "password": "Admin123",
            "first_name": "Admin",
            "last_name": "Sistema",
            "role": "seller"  # Admin con permisos de vendedor
        },
        {
            "email": "vendedor@merkatolima.com",
            "password": "Vendedor123",
            "first_name": "Carlos",
            "last_name": "Vendedor",
            "role": "seller"
        },
        {
            "email": "comprador@merkatolima.com",
            "password": "Comprador123",
            "first_name": "Ana",
            "last_name": "Compradora",
            "role": "buyer"
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            registration_data = UserRegistrationData(**user_data)
            user = await user_service.register_user(registration_data)
            created_users.append(user)
            print(f"✅ Usuario creado: {user.email} ({user.role})")
            
        except Exception as e:
            print(f"❌ Error creando usuario {user_data['email']}: {e}")
    
    print(f"\n🎉 Se crearon {len(created_users)} usuarios de prueba exitosamente!")
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("👥 USUARIOS DE PRUEBA DISPONIBLES")
    print("="*60)
    
    for user_data in test_users:
        role_emoji = "🛒" if user_data["role"] == "buyer" else "🏪"
        print(f"{role_emoji} {user_data['role'].upper()}: {user_data['email']} / {user_data['password']}")
    
    print("\n🌐 Puedes usar estos usuarios para:")
    print("   - Probar el login en http://localhost:8001")
    print("   - Hacer peticiones a la API en http://localhost:8000")
    print("   - Probar diferentes roles (comprador/vendedor)")
    
    return created_users


async def test_authentication():
    """Probar la autenticación con los usuarios creados."""
    
    print("\n🔐 Probando autenticación...")
    
    repository = InMemoryUserRepository()
    user_service = UserService(repository)
    
    # Primero crear los usuarios
    await create_test_users()
    
    # Probar login
    from src.services.users.service import LoginCredentials
    
    test_credentials = [
        {"email": "buyer@test.com", "password": "Password123"},
        {"email": "seller@test.com", "password": "Password123"}
    ]
    
    for creds in test_credentials:
        try:
            credentials = LoginCredentials(**creds)
            token = await user_service.authenticate_user(credentials)
            print(f"✅ Login exitoso para {creds['email']}")
            print(f"   Token: {token.access_token[:50]}...")
            
        except Exception as e:
            print(f"❌ Error en login para {creds['email']}: {e}")


def main():
    """Función principal."""
    print("🏪 MERKATOLIMA - INICIALIZACIÓN DE USUARIOS DE PRUEBA")
    print("="*60)
    
    try:
        # Ejecutar la creación de usuarios
        asyncio.run(create_test_users())
        
        print("\n💡 NOTA IMPORTANTE:")
        print("   Este script crea usuarios en memoria para pruebas.")
        print("   Para persistir los usuarios, necesitas configurar una base de datos.")
        print("   Los usuarios se perderán al reiniciar el servidor.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()