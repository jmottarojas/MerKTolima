#!/usr/bin/env python3
"""
Script para iniciar ambos servidores con debug habilitado
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Iniciar servidor backend FastAPI"""
    print("🚀 Iniciando servidor backend (FastAPI)...")
    try:
        # Cambiar al directorio raíz
        os.chdir(Path(__file__).parent)
        
        # Iniciar servidor backend
        backend_process = subprocess.Popen([
            sys.executable, "run_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        return backend_process
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")
        return None

def start_frontend():
    """Iniciar servidor frontend Django"""
    print("🌐 Iniciando servidor frontend (Django)...")
    try:
        # Cambiar al directorio frontend
        os.chdir(Path(__file__).parent / "frontend")
        
        # Iniciar servidor Django con debug
        frontend_process = subprocess.Popen([
            sys.executable, "run_django.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        return frontend_process
    except Exception as e:
        print(f"❌ Error iniciando frontend: {e}")
        return None

def main():
    print("🔧 Iniciando Merkatolima en modo debug...")
    print("=" * 50)
    
    # Iniciar backend
    backend = start_backend()
    if not backend:
        print("❌ No se pudo iniciar el backend")
        return
    
    time.sleep(3)  # Esperar a que el backend inicie
    
    # Iniciar frontend
    frontend = start_frontend()
    if not frontend:
        print("❌ No se pudo iniciar el frontend")
        backend.terminate()
        return
    
    print("\n✅ Servidores iniciados:")
    print("   📡 Backend (FastAPI): http://localhost:8000")
    print("   🌐 Frontend (Django): http://localhost:8001")
    print("   🧪 Test Upload: http://localhost:8001/marketplace/test-upload/")
    print("\n📝 Para probar la carga de imágenes:")
    print("   1. Ve a: http://localhost:8001/marketplace/test-upload/")
    print("   2. Selecciona algunas imágenes")
    print("   3. Haz clic en 'Subir Imágenes'")
    print("   4. Revisa la consola del navegador para logs")
    print("\n⏹️  Presiona Ctrl+C para detener ambos servidores")
    
    try:
        # Mostrar logs en tiempo real
        while True:
            # Leer output del backend
            if backend.poll() is None:
                backend_output = backend.stdout.readline()
                if backend_output:
                    print(f"[BACKEND] {backend_output.strip()}")
            
            # Leer output del frontend
            if frontend.poll() is None:
                frontend_output = frontend.stdout.readline()
                if frontend_output:
                    print(f"[FRONTEND] {frontend_output.strip()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidores...")
        backend.terminate()
        frontend.terminate()
        
        # Esperar a que terminen
        backend.wait()
        frontend.wait()
        
        print("✅ Servidores detenidos")

if __name__ == "__main__":
    main()