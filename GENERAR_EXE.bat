@echo off
cd /d "%~dp0"
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
".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --exclude-module numpy --name "PNG a PDF" png_a_pdf.py
if errorlevel 1 exit /b 1
copy /y "dist\PNG a PDF.exe" "app\PNG a PDF.exe"
if errorlevel 1 exit /b 1
powershell -NoProfile -Command "(Get-FileHash -LiteralPath 'app/PNG a PDF.exe' -Algorithm SHA256).Hash.ToLower() + '  PNG a PDF.exe' | Set-Content -Encoding ascii 'app/SHA256SUMS.txt'"
echo Ejecutable actualizado en app.
pause
