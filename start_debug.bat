@echo off
echo 🔧 Iniciando Merkatolima en modo debug...
echo ================================================

echo 🚀 Iniciando servidor backend (FastAPI)...
start "Backend FastAPI" cmd /k "python run_server.py"

timeout /t 3 /nobreak > nul

echo 🌐 Iniciando servidor frontend (Django)...
cd frontend
start "Frontend Django" cmd /k "python run_django.py"

echo.
echo ✅ Servidores iniciados:
echo    📡 Backend (FastAPI): http://localhost:8000
echo    🌐 Frontend (Django): http://localhost:8001
echo    🧪 Test Upload: http://localhost:8001/marketplace/test-upload/
echo.
echo 📝 Para probar la carga de imágenes:
echo    1. Ve a: http://localhost:8001/marketplace/test-upload/
echo    2. Selecciona algunas imágenes
echo    3. Haz clic en 'Subir Imágenes'
echo    4. Revisa la consola del navegador para logs
echo.
echo ⏹️  Cierra las ventanas de comando para detener los servidores
pause