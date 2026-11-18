# Instalar PNG a PDF

Abre instalador/PNG-a-PDF-Setup-1.2.0.exe y sigue los pasos.

Compatible con Windows 10 y Windows 11 de 64 bits (x64). No necesitas instalar Python. La instalación se realiza para tu usuario, sin pedir permisos de administrador, en la carpeta Programas de tu perfil. Puedes elegir otro destino y crear un acceso directo en el escritorio.

Para desinstalar, usa Configuración > Aplicaciones > PNG a PDF, o el acceso Desinstalar PNG a PDF del menú Inicio. El desinstalador elimina los archivos de la aplicación; no elimina las imágenes ni los PDF que hayas guardado en otras carpetas.

## Avisos de seguridad

Este instalador y la aplicación no tienen firma digital. Crear un instalador no elimina avisos de SmartScreen, bloqueos del Control inteligente ni detecciones del antivirus. No desactives las protecciones para instalarlo. Si aparece una detección de amenaza, conserva el nombre completo y la ruta del archivo afectado para investigarla antes de continuar.

Se realizó un análisis local del ejecutable de la aplicación con Microsoft Defender durante la preparación del instalador, sin amenazas detectadas. Ese resultado corresponde únicamente al equipo y las definiciones utilizadas en esa prueba; no es una auditoría de seguridad ni garantiza que otros equipos o motores no detecten el archivo.

## Reconstruir el instalador

Instala Inno Setup 6 desde https://jrsoftware.org/inno-setup/downloads y ejecuta GENERAR_INSTALADOR.bat. Puedes indicar la ruta de ISCC.exe como primer argumento. El script usa la aplicación de app/; ejecuta antes GENERAR_EXE.bat si cambiaste el código.

El resultado se guarda en instalador/. La suma SHA-256 permite verificar integridad, pero no sustituye una firma digital ni un análisis antivirus.
