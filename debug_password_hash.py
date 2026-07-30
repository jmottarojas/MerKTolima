#!/usr/bin/env python3
"""Script para debuggear el problema del password hash."""

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
from src.shared.db_models import UserDB
from src.shared.auth import verify_password


async def debug_password_hash():
    """Debuggear el problema del password hash."""
    # Obtener sesión de base de datos
    db_session = get_db_session()
    # Crear repositorio SQLAlchemy
    repository = SQLAlchemyUserRepository(db_session)
    # Crear servicio de usuarios
    user_service = UserService(repository)
    
    email = "test@merktolima.com"
    password = "Test123!"
    
    try:
        print("🔍 Debuggeando autenticación...")
        
        # 1. Verificar que el usuario existe
        user = await user_service.get_user_by_email(email)
        if user:
            print(f"✅ Usuario encontrado: {user.email} (ID: {user.id})")
        else:
            print("❌ Usuario no encontrado")
            return
        
        # 2. Obtener el hash de la base de datos directamente
        db_user = db_session.query(UserDB).filter(UserDB.id == user.id).first()
        if db_user:
            print(f"✅ Usuario DB encontrado: {db_user.email}")
            print(f"📝 Password hash: {db_user.password_hash[:20]}...")
            
            # 3. Verificar el password manualmente
            is_valid = verify_password(password, db_user.password_hash)
            print(f"🔐 Password válido: {is_valid}")
            
            if not is_valid:
                print("❌ El password no coincide con el hash almacenado")
                
                # Verificar si el hash está en el formato correcto
                if db_user.password_hash.startswith('$2b$'):
                    print("✅ Hash en formato bcrypt correcto")
                else:
                    print(f"❌ Hash en formato incorrecto: {db_user.password_hash[:10]}...")
            
        else:
            print("❌ Usuario no encontrado en la base de datos")
        
        # 4. Probar la autenticación completa
        credentials = LoginCredentials(email=email, password=password)
        try:
            token = await user_service.authenticate_user(credentials)
            print(f"✅ Autenticación exitosa!")
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        
    finally:
        db_session.close()


if __name__ == "__main__":
    print("🚀 Debuggeando problema de password hash...")
    asyncio.run(debug_password_hash())