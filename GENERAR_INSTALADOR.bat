@echo off
setlocal
cd /d "%~dp0"
set "PNG_ISCC=%~1"
if not defined PNG_ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "PNG_ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined PNG_ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "PNG_ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined PNG_ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "PNG_ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not defined PNG_ISCC (
  echo Instala Inno Setup 6 desde https://jrsoftware.org/inno-setup/downloads
  echo O ejecuta este archivo indicando la ruta completa de ISCC.exe como argumento.
  pause
  exit /b 1
)
"%PNG_ISCC%" "installer\PNG-a-PDF.iss"
if errorlevel 1 exit /b 1
powershell -NoProfile -Command "(Get-FileHash -LiteralPath 'instalador/PNG-a-PDF-Setup-1.2.0.exe' -Algorithm SHA256).Hash.ToLower() + '  PNG-a-PDF-Setup-1.2.0.exe' | Set-Content -Encoding ascii 'instalador/SHA256SUMS.txt'"
if errorlevel 1 exit /b 1
echo Instalador generado en instalador.
pause
