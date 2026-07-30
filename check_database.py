#!/usr/bin/env python3
"""Script para verificar la base de datos."""

import sqlite3
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Verificar el contenido de la base de datos."""
    try:
        conn = sqlite3.connect('marketplace.db')
        cursor = conn.cursor()
        
        # Verificar usuarios
        cursor.execute("SELECT id, email, first_name, last_name, password_hash FROM users")
        users = cursor.fetchall()
        
        print(f"📊 Usuarios en la base de datos: {len(users)}")
        print("=" * 60)
        
        for user in users:
            user_id, email, first_name, last_name, password_hash = user
            print(f"ID: {user_id}")
            print(f"Email: {email}")
            print(f"Nombre: {first_name} {last_name}")
            print(f"Password Hash: {password_hash[:20]}..." if password_hash else "No hash")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

if __name__ == "__main__":
    check_database()