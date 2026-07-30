#!/usr/bin/env python3
"""
Script para iniciar tanto el servidor API como el frontend Django de MerkatoliMA.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_api_server():
    """Iniciar el servidor API FastAPI."""
    print("🚀 Iniciando servidor API FastAPI...")
    return subprocess.Popen([
        sys.executable, "run_server.py"
    ], cwd=Path.cwd())

def start_django_server():
    """Iniciar el servidor Django."""
    print("🌐 Iniciando servidor Django Frontend...")
    return subprocess.Popen([
        sys.executable, "run_django.py"
    ], cwd=Path.cwd() / "frontend")

def main():
    """Función principal."""
    print("=" * 60)
    print("🏪 MERKATOLIMA - MARKETPLACE PLATFORM")
    print("=" * 60)
    print("Iniciando servidores...")
    print()
    
    try:
        # Iniciar servidor API
        api_process = start_api_server()
        time.sleep(3)  # Esperar a que el API se inicie
        
        # Iniciar servidor Django
        django_process = start_django_server()
        time.sleep(2)
        
        print()
        print("=" * 60)
        print("✅ SERVIDORES INICIADOS EXITOSAMENTE")
        print("=" * 60)
        print("🔗 API Backend:     http://localhost:8000")
        print("📖 API Docs:       http://localhost:8000/docs")
        print("🌐 Frontend Web:   http://localhost:8001")
        print("=" * 60)
        print("💡 Presiona Ctrl+C para detener ambos servidores")
        print()
        
        # Esperar hasta que el usuario presione Ctrl+C
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servidores...")
            
    except Exception as e:
        print(f"❌ Error al iniciar servidores: {e}")
        return 1
    
    finally:
        # Terminar procesos
        try:
            if 'api_process' in locals():
                api_process.terminate()
                api_process.wait()
            if 'django_process' in locals():
                django_process.terminate()
                django_process.wait()
            print("✅ Servidores detenidos correctamente")
        except:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())