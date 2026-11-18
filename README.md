# PNG a PDF

<img src="assets/app.png" alt="Icono de PNG a PDF" width="88">

Convierte una carpeta de imágenes PNG en un solo PDF desde una aplicación de escritorio en español. Revisa las imágenes, ajusta el orden de las páginas y guarda el documento en tu equipo.

**Versión actual: 1.2.0 · Windows 10 y Windows 11 de 64 bits (x64).**

## Descargar y abrir

No necesitas instalar Python para utilizar los ejecutables incluidos:

- **[Instalador 1.2.0](instalador/PNG-a-PDF-Setup-1.2.0.exe):** asistente en español, acceso desde Inicio, acceso directo opcional y desinstalador. Se instala para el usuario actual, sin solicitar permisos de administrador.
- **[Aplicación portátil](app/PNG%20a%20PDF.exe):** abre el archivo con doble clic o utiliza `ABRIR.bat`.

Si descargas el repositorio como ZIP, extrae los archivos antes de ejecutarlos. Las sumas de verificación están en `app/SHA256SUMS.txt` e `instalador/SHA256SUMS.txt`. El repositorio conserva únicamente el instalador de la versión actual.

## Cómo funciona

1. Pulsa **Elegir carpeta** y selecciona tus imágenes PNG.
2. Activa **Incluir subcarpetas** si lo necesitas.
3. Selecciona una imagen para verla en el panel de vista previa.
4. Haz **doble clic** en la lista o en la vista previa para abrirla en una ventana grande. También puedes pulsar **Enter** sobre la imagen seleccionada; cierra la ventana con **Esc**.
5. Cambia el orden con **Subir** y **Bajar**.
6. Pulsa **Exportar PDF** y elige dónde guardarlo.

Atajos: **Ctrl+O** para seleccionar carpeta y **Ctrl+S** para exportar.

## Funciones

- Detección de archivos `.png` y `.PNG`, con orden numérico por nombre.
- Inclusión opcional de subcarpetas y orden manual de páginas.
- Vista previa con dimensiones, tamaño y número de página.
- Ventana ampliada redimensionable, sin perder la vista previa lateral.
- Icono propio de imagen y documento PDF en la aplicación y el instalador.
- Conservación de proporciones y aplicación de la orientación EXIF.
- Transparencia convertida a fondo blanco.
- Procesamiento local, sin cuentas, anuncios ni envío de imágenes a servidores.
- Avisos de archivos dañados; si falla la conversión, se conserva el PDF de destino anterior.

Cada archivo corresponde a una página. En PNG animados se usa la primera imagen. No incluye OCR. Las imágenes se cargan en memoria, por lo que las carpetas muy grandes pueden requerir convertir por grupos.

## Novedades de 1.2.0

La versión actual incorpora la ventana ampliada con doble clic y el nuevo icono. Incluye también el diseño moderno y la vista previa introducidos anteriormente. Consulta el historial de cambios en [CHANGELOG.md](CHANGELOG.md).

## Seguridad y privacidad

La aplicación y el instalador todavía no tienen firma digital. Un instalador no elimina avisos de Windows ni sustituye una revisión de una detección antivirus. No se recomienda desactivar las protecciones para ejecutarlo.

Consulta la [política de privacidad](PRIVACIDAD.md) y los [detalles de instalación](INSTALACION.md). La suma SHA-256 sirve para comprobar integridad; no sustituye una firma digital.

## Ejecutar desde el código

Requiere Python 3.10 o superior con Tcl/Tk. En Windows, agrega Python al PATH e incluye el componente Tcl/Tk durante su instalación.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe png_a_pdf.py
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Para comprobar el doble clic y la ventana ampliada con una sesión gráfica disponible:

```powershell
.\.venv\Scripts\python.exe tests/check_viewer.py
```

## Generar ejecutables

- **`GENERAR_EXE.bat`:** instala las dependencias de desarrollo, ejecuta las pruebas y reconstruye la aplicación portátil con el icono y los metadatos de versión. Actualiza `app/` y su suma de verificación.
- **`GENERAR_INSTALADOR.bat`:** requiere Inno Setup 6 y genera `instalador/PNG-a-PDF-Setup-1.2.0.exe`. Reconstruye primero el ejecutable si cambiaste el código. El script de instalación está en `installer/PNG-a-PDF.iss`.
- **GitHub Actions:** `.github/workflows/build.yml` ejecuta las pruebas y genera el ejecutable portátil como artefacto descargable.

Para distribuir una versión desde GitHub Releases, adjunta la aplicación portátil o el instalador y la suma SHA-256 correspondiente.

## Microsoft Store

La preparación de MSIX está en [store/LEEME.md](store/LEEME.md). Incluye la ficha en español, los iconos y una plantilla de identidad de Partner Center.

`GENERAR_MSIX.bat` requiere Windows SDK y los datos exactos de `store/identity.json`. La cuenta debe usar el flujo **MSIX o PWA** para ese paquete; el producto reservado como **EXE o MSI** utiliza otro flujo. El nombre reservado comunicado para Store es **IMG TO PDF CONVERTER**; la identidad MSIX definitiva sigue pendiente.

La preparación local no significa que la aplicación esté publicada o certificada. Faltan confirmar la identidad, probar el paquete instalado, preparar las capturas y completar la revisión de Store.

## Código y licencia

`png_a_pdf.py` contiene la interfaz y `_image_pdf.py` la conversión. Los recursos del icono están en `assets/`; `tools/generate_icon.py` permite regenerarlos en Windows.

Licencia MIT: consulta [LICENSE](LICENSE). Python, Tcl/Tk, Pillow y PyInstaller tienen sus propias condiciones, indicadas en [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Descargas directas en Render o Vercel

La guía está en [hosting/LEEME.md](hosting/LEEME.md). Para **Render**, elige **Static Site**, rama `main`, raíz vacía, Build Command `node hosting/build.mjs` y Publish Directory `hosting/public`. No se necesitan variables de entorno ni un servicio Python. También puedes crear un Blueprint a partir de `render.yaml`.

Se conserva `vercel.json` como alternativa: preset **Other**, raíz `./`, el mismo comando de build y la misma carpeta de salida; el comando de instalación queda vacío.

El build publica la aplicación portátil y el instalador bajo `/descargas/v1.2.0/`, sus sumas SHA-256 y la política de privacidad en `/privacidad.html`. Copia los archivos reales al sitio; no redirige a GitHub. Después de desplegar, verifica la URL pública, la respuesta HTTP 200 sin redirecciones y la suma del archivo descargado. La firma y los demás requisitos de Store siguen pendientes.
