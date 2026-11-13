# PNG a PDF

Aplicación de escritorio en español para Windows que convierte una carpeta de imágenes PNG en un solo PDF. Funciona localmente, sin subir tus imágenes a internet.

## Usar la aplicación

No necesitas instalar Python. Abre **`app/PNG a PDF.exe`** con doble clic o usa `ABRIR.bat`.

1. Pulsa **Seleccionar carpeta**.
2. Activa **Incluir subcarpetas** si lo necesitas.
3. Revisa el orden de las imágenes. Selecciona una y usa **Subir** o **Bajar** para cambiar su posición.
4. Pulsa **Guardar PDF** y selecciona el destino.

El ejecutable incluido es para Windows de 64 bits. Puedes copiarlo a otra carpeta y usarlo por separado. Al descargar este repositorio como ZIP, extrae los archivos antes de abrir la aplicación.

## Funciones

- Detecta PNG y PNG con extensión en mayúsculas.
- Ordena los nombres numéricamente: 1, 2, 3… 10.
- Incluye subcarpetas opcionalmente.
- Permite cambiar el orden de las páginas.
- Conserva las proporciones y aplica la orientación EXIF.
- Convierte la transparencia a fondo blanco.
- Informa si una imagen está dañada y conserva el PDF de destino anterior si falla la conversión.

Cada archivo corresponde a una página. En PNG animados se usa la primera imagen. No incluye OCR. Las imágenes se cargan en memoria, por lo que las carpetas muy grandes pueden requerir convertir por grupos.

## Ejecutar desde el código

Requiere Python 3.10 o superior con Tcl/Tk. En Windows, instala Python con la opción de agregarlo al PATH y el componente Tcl/Tk.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe png_a_pdf.py
```

## Generar un nuevo ejecutable

En Windows, ejecuta `GENERAR_EXE.bat`. Crea un entorno virtual, instala las herramientas, ejecuta las pruebas, genera el ejecutable con PyInstaller y actualiza la copia de `app/` y su suma SHA-256.

Para hacerlo manualmente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --exclude-module numpy --name "PNG a PDF" png_a_pdf.py
```

El archivo generado queda en `dist/PNG a PDF.exe`. Copia esa versión a `app/` si deseas incluirla en el repositorio.

## Archivos del proyecto

| Archivo | Contenido |
| --- | --- |
| `png_a_pdf.py` | Ventana de la aplicación |
| `_image_pdf.py` | Lectura de imágenes y generación de PDF |
| `app/PNG a PDF.exe` | Aplicación portátil lista para usar |
| `app/SHA256SUMS.txt` | Suma de verificación del ejecutable |
| `tests/` | Pruebas de conversión |
| `GENERAR_EXE.bat` | Generación del ejecutable en Windows |
| `.github/workflows/build.yml` | Pruebas y compilación automática en GitHub |

## Publicar en GitHub

Este proyecto ya es un repositorio Git local. Para publicarlo, crea en GitHub un repositorio vacío llamado `png-a-pdf`, sin README ni licencia automática. Desde esta carpeta ejecuta, sustituyendo `TU_USUARIO`:

```powershell
git remote add origin https://github.com/TU_USUARIO/png-a-pdf.git
git push -u origin main
```

En GitHub puedes crear una **Release** `v1.0.0` y adjuntar `app/PNG a PDF.exe` y `app/SHA256SUMS.txt`. La compilación automática también deja un ejecutable descargable en los artefactos de cada ejecución de Actions.

## Licencia y dependencias

Distribuido bajo licencia MIT; consulta `LICENSE`. El ejecutable integra Python, Tcl/Tk y Pillow, sujetos a sus propias licencias. PyInstaller se utiliza para empaquetar la aplicación con su excepción para distribución de ejecutables. Consulta `THIRD_PARTY_NOTICES.md`.
