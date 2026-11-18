@echo off
setlocal
cd /d "%~dp0"
if not exist "store\identity.json" (
  echo Copia store\identity.example.json a store\identity.json y completa los datos exactos de Partner Center.
  pause
  exit /b 1
)
where python >nul 2>nul
if errorlevel 1 (
  echo Instala Python 3.10 o superior con Tcl/Tk y agregalo al PATH.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" tools\build_msix.py
if errorlevel 1 exit /b 1
echo Revisa el paquete y la documentacion antes de enviarlo a Microsoft Store.
pause
