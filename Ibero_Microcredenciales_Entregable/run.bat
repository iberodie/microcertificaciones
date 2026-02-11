@echo off
echo Iniciando Recomendador de Microcredenciales Ibero...
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado. Por favor instala Python 3.9 o superior.
    pause
    exit /b
)

:: Instalar dependencias si es necesario (opcional, puede tomar tiempo)
echo Verificando dependencias...
pip install -r microcredentials_app/requirements.txt >nul 2>&1

:: Ejecutar la app
echo Lanzando aplicacion...
streamlit run microcredentials_app/app.py

pause
