#!/usr/bin/env python3
"""
Script para iniciar la plataforma completa de Merkatolima
- Backend FastAPI (puerto 8000)
- Frontend Django (puerto 8001)
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_banner():
    """Mostrar banner de inicio"""
    print("=" * 60)
    print("🏪 MERKATOLIMA - MARKETPLACE COLOMBIANO")
    print("=" * 60)
    print("🚀 Iniciando plataforma completa...")
    print()

def check_requirements():
    """Verificar que los archivos necesarios existen"""
    required_files = [
        "run_server.py",
        "frontend/run_django.py",
        ".env"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: Archivo requerido no encontrado: {file}")
            return False
    
    print("✅ Todos los archivos requeridos encontrados")
    return True

def start_backend():
    """Iniciar servidor backend FastAPI"""
    print("🔧 Iniciando Backend FastAPI...")
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "run_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # Dar tiempo para que inicie
        
        if backend_process.poll() is None:
            print("✅ Backend FastAPI iniciado correctamente (puerto 8000)")
            return backend_process
        else:
            print("❌ Error al iniciar Backend FastAPI")
            return None
    except Exception as e:
        print(f"❌ Error al iniciar backend: {e}")
        return None

def start_frontend():
    """Iniciar servidor frontend Django"""
    print("🎨 Iniciando Frontend Django...")
    try:
        frontend_process = subprocess.Popen(
            [sys.executable, "run_django.py"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # Dar tiempo para que inicie
        
        if frontend_process.poll() is None:
            print("✅ Frontend Django iniciado correctamente (puerto 8001)")
            return frontend_process
        else:
            print("❌ Error al iniciar Frontend Django")
            return None
    except Exception as e:
        print(f"❌ Error al iniciar frontend: {e}")
        return None

def show_access_info():
    """Mostrar información de acceso"""
    print("\n" + "=" * 60)
    print("🌐 ACCESO A LA PLATAFORMA")
    print("=" * 60)
    print("🏠 Frontend Web:      http://localhost:8001")
    print("🔧 Backend API:       http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    print()
    print("🤖 CHATBOT MERKABOT:")
    print("   - Busca el botón flotante en la esquina inferior derecha")
    print("   - Disponible en todas las páginas del sitio")
    print("   - Ayuda con compras, ventas y preguntas frecuentes")
    print()
    print("👥 USUARIOS DE PRUEBA:")
    print("   📧 admin@merkatolima.com / admin123")
    print("   📧 vendedor@merkatolima.com / vendedor123")
    print("   📧 comprador@merkatolima.com / comprador123")
    print()
    print("🎯 FUNCIONALIDADES PRINCIPALES:")
    print("   ✅ Catálogo de productos con búsqueda")
    print("   ✅ Carrito de compras y checkout")
    print("   ✅ Panel de vendedor completo")
    print("   ✅ Sistema de notificaciones")
    print("   ✅ Chatbot inteligente MerkaBot")
    print("   ✅ Diseño responsivo (móvil/desktop)")
    print()
    print("=" * 60)
    print("🚀 ¡PLATAFORMA LISTA! Abre http://localhost:8001 en tu navegador")
    print("=" * 60)

def main():
    """Función principal"""
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        sys.exit(1)
    
    # Iniciar servicios
    backend = start_backend()
    if not backend:
        print("❌ No se pudo iniciar el backend. Abortando...")
        sys.exit(1)
    
    frontend = start_frontend()
    if not frontend:
        print("❌ No se pudo iniciar el frontend. Terminando backend...")
        backend.terminate()
        sys.exit(1)
    
    # Mostrar información de acceso
    show_access_info()
    
    try:
        # Mantener los procesos ejecutándose
        print("⏳ Presiona Ctrl+C para detener los servidores...")
        while True:
            time.sleep(1)
            
            # Verificar que los procesos sigan ejecutándose
            if backend.poll() is not None:
                print("❌ Backend se detuvo inesperadamente")
                break
            if frontend.poll() is not None:
                print("❌ Frontend se detuvo inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidores...")
        
        # Terminar procesos
        if backend and backend.poll() is None:
            backend.terminate()
            print("✅ Backend detenido")
            
        if frontend and frontend.poll() is None:
            frontend.terminate()
            print("✅ Frontend detenido")
        
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()