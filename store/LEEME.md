# Preparación para Microsoft Store

## Estado

Se prepararon la política de privacidad, un borrador de la ficha en español, los recursos visuales y la herramienta para construir un MSIX x64. No se ha publicado la aplicación ni enviado a certificación. La identidad definitiva de Partner Center todavía debe proporcionarse.

## 1. Privacidad

Si tu formulario muestra **Proporcionar texto de la directiva de privacidad**, selecciona esa opción y pega el texto de `PRIVACIDAD.md`. Si solicita una URL, debes hospedar públicamente la política antes de completar ese campo. Revisa el texto y confirma un medio de soporte público que coincida con la sección de contacto.

## 2. Identidad

En tu aplicación de Partner Center abre Administración del producto > Identidad del producto. Copia `identity.example.json` a `identity.json` y completa:

- `PackageName`: valor exacto de `Package/Identity/Name`.
- `Publisher`: valor exacto de `Package/Identity/Publisher`, incluido `CN=`.
- `PublisherDisplayName`: valor exacto de `Package/Properties/PublisherDisplayName`.
- `DisplayName`: nombre de aplicación reservado en Store.
- `Version`: `1.2.0.0`, salvo que Partner Center ya requiera una versión superior.

Son datos de identidad del paquete, no claves ni contraseñas. No uses el nombre visible en lugar de Identity/Name. Si el nombre reservado difiere del nombre de la interfaz, revisaremos el nombre y la política antes del envío.

## 3. Generar el paquete

Requiere Python con Tcl/Tk, las dependencias de desarrollo y Windows SDK (MakeAppx.exe). Ejecuta `GENERAR_MSIX.bat`.

El proceso compila un runtime de aplicación en carpeta con PyInstaller, crea el manifiesto y empaqueta los archivos con MakeAppx. No incluye ni ejecuta el instalador Inno Setup dentro del MSIX. El paquete declara `runFullTrust` para la aplicación Win32 y requiere Windows 10 versión 2004 o posterior, x64. No solicita permisos de red.

El resultado se guarda en `store/dist`. No se firma con un certificado inventado ni se cambian las protecciones de Windows. Un paquete creado para Store sin firma propia no debe presentarse como instalador independiente listo para cualquier equipo.

## 4. Validación pendiente

Antes de enviar la versión final:

- Verificar nombre, editor y versión contra Partner Center.
- Probar la aplicación instalada desde el paquete en un equipo o VM limpios con un método de prueba adecuado.
- Ejecutar Windows App Certification Kit y revisar sus informes.
- Probar con teclado y lector de pantalla. Tkinter puede requerir trabajo adicional de accesibilidad.
- Preparar capturas reales de la versión actual, al menos una de 1366 × 768 o superior.
- Confirmar soporte, privacidad, clasificación por edades, precio y mercados.
- Revisar la ficha y confirmar expresamente el envío a certificación.

El éxito al empaquetar no equivale a una certificación de seguridad ni garantiza la aprobación de Store. La detección de troyano observada en otro equipo sigue pendiente de identificar con su nombre completo.

## Fuentes

- https://learn.microsoft.com/en-us/windows/apps/publish/store-readiness-checklist
- https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-manual-conversion
- https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/screenshots-and-images
