#!/usr/bin/env python3
"""Script para probar el login directamente."""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.users.service import UserService, LoginCredentials
from src.services.users.repository import SQLAlchemyUserRepository
from src.shared.database import get_db_session


async def test_login():
    """Probar el login directamente."""
    # Obtener sesión de base de datos
    db_session = get_db_session()
    # Crear repositorio SQLAlchemy
    repository = SQLAlchemyUserRepository(db_session)
    # Crear servicio de usuarios
    user_service = UserService(repository)
    
    # Probar login
    credentials = LoginCredentials(
        email="test@merktolima.com",
        password="Test123!"
    )
    
    try:
        print("🔐 Probando login...")
        token = await user_service.authenticate_user(credentials)
        print(f"✅ Login exitoso!")
        print(f"Token: {token.access_token[:50]}...")
        print(f"Tipo: {token.token_type}")
        print(f"Expira en: {token.expires_in} segundos")
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        
        # Verificar si el usuario existe
        try:
            user = await user_service.get_user_by_email("test@merktolima.com")
            if user:
                print(f"✅ Usuario encontrado: {user.email} ({user.first_name} {user.last_name})")
            else:
                print("❌ Usuario no encontrado")
        except Exception as e2:
            print(f"❌ Error buscando usuario: {e2}")
    
    finally:
        db_session.close()


if __name__ == "__main__":
    print("🚀 Probando autenticación directa...")
    asyncio.run(test_login())