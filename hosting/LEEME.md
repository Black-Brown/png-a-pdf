# Descargas estáticas: Render y Vercel

El script `hosting/build.mjs` usa solo Node.js, comprueba las sumas SHA-256 y publica copias de los ejecutables ya compilados. No instala ni ejecuta Python en el servidor. No redirige las descargas a GitHub Releases.

## Render: configuración recomendada

En **New > Static Site**, conecta `Black-Brown/png-a-pdf` y configura:

| Campo | Valor |
| --- | --- |
| Name | `png-a-pdf-downloads` o un nombre disponible |
| Branch | `main` |
| Root Directory | Vacío, raíz del repositorio |
| Build Command | `node hosting/build.mjs` |
| Publish Directory | `hosting/public` |
| Environment Variables | Ninguna |

No elijas Web Service ni agregues un Start Command. No necesitas base de datos ni ejecutar la aplicación de escritorio en Render.

También puedes usar **New > Blueprint** con este repositorio: `render.yaml` declara el mismo sitio estático y añade encabezados para descargar los archivos. Un sitio creado manualmente no importa automáticamente el Blueprint; sus campos se configuran en el formulario y, si se desean, sus encabezados en Settings > Headers.

## URL en Render

Sustituye `TU-SITIO.onrender.com` por el dominio que Render te asigne. No asumas que el nombre de ejemplo estará disponible.

```text
https://TU-SITIO.onrender.com/descargas/v1.2.0/PNG-a-PDF-1.2.0.exe
https://TU-SITIO.onrender.com/descargas/v1.2.0/PNG-a-PDF-Setup-1.2.0.exe
https://TU-SITIO.onrender.com/descargas/v1.2.0/SHA256SUMS.txt
https://TU-SITIO.onrender.com/privacidad.html
```

## Vercel: configuración alternativa

`vercel.json` conserva la opción de usar Vercel sin modificar la configuración de Render:

- Application / Framework Preset: **Other**.
- Root Directory: **./**.
- Build Command: **node hosting/build.mjs**.
- Output Directory: **hosting/public**.
- Install Command: vacío, con override activado si lo pide el formulario.
- Environment Variables: ninguna.

Las rutas de descarga son las mismas, sustituyendo el dominio de Render por el dominio de producción `.vercel.app` asignado.

## Comprobar antes de usar en Partner Center

Después del despliegue, verifica que la URL HTTPS devuelva el ejecutable con estado HTTP 200, sin redirecciones, sin inicio de sesión ni comprobaciones intermedias. Comprueba también que la suma SHA-256 del archivo descargado coincida con la publicada. Un build local correcto no demuestra que una URL aún no desplegada cumpla esas condiciones.

La aplicación portátil no sustituye al instalador en el flujo EXE/MSI de Store. La firma digital y los demás requisitos de certificación siguen pendientes.

## Nuevas versiones

Actualiza `version` y las rutas del script al preparar otra versión. Mantén inalterados los archivos y las URL de versiones enviadas a certificación. `hosting/public` se genera durante el build y no se guarda en Git.

La configuración debe estar en GitHub antes de desplegar. Después de conectar el sitio, Render puede volver a desplegar al recibir nuevos commits en la rama configurada, según sus ajustes de despliegue automático.

Documentación: https://render.com/docs/your-first-deploy y https://render.com/docs/blueprint-spec.
