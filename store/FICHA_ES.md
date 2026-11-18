# Ficha de Microsoft Store: borrador para revisar

## Nombre

Utiliza exactamente el nombre reservado en Partner Center. El nombre actual de la aplicación es PNG a PDF; la identidad y el nombre de Store se confirmarán antes de generar el paquete final.

## Descripción breve

Convierte una carpeta de imágenes PNG en un PDF, con vista previa y orden de páginas personalizable.

## Descripción

Reúne tus imágenes PNG en un solo documento PDF desde una aplicación de escritorio sencilla y en español.

Selecciona una carpeta, revisa sus imágenes y cambia el orden de las páginas antes de exportar. Puedes incluir subcarpetas y abrir cualquier imagen en una ventana independiente con doble clic para verla en grande.

Las conversiones se realizan localmente en tu equipo, sin subir tus imágenes a servidores y sin necesitar una cuenta dentro de la aplicación.

## Características

- Conversión de carpetas de imágenes PNG a un único PDF.
- Inclusión opcional de subcarpetas.
- Orden numérico automático y cambio manual del orden.
- Vista previa lateral con dimensiones y tamaño de cada archivo.
- Ventana ampliada con doble clic o Enter; cierre con Esc.
- Transparencia sobre fondo blanco y respeto de las proporciones de cada imagen.
- Interfaz en español y procesamiento local.

## Novedades de la versión 1.2.0

Ventana ampliada para revisar imágenes con doble clic y nuevo icono de la aplicación.

## Limitaciones que deben quedar claras

Solo se incluyen archivos PNG. Cada archivo se convierte en una página. En PNG animados se utiliza la primera imagen. No se realiza OCR y las carpetas con imágenes grandes pueden consumir bastante memoria.

## Categoría sugerida

Productividad o Utilidades: elige la opción que mejor corresponda entre las disponibles en Partner Center. La clasificación por edades debe completarse contestando el cuestionario según las funciones reales de la aplicación.

## Privacidad y soporte

El texto de la política está en `PRIVACIDAD.md`, en la raíz del repositorio. Si Partner Center ofrece introducir texto, pega su contenido. Si solicita URL, publica ese documento en una página pública y utiliza su enlace.

Falta confirmar un correo o URL de soporte que quieras hacer público. La referencia de contacto de la política debe coincidir con ese medio.

## Capturas pendientes

Se necesitan capturas reales de esta versión, sin fotografías privadas. Incluye al menos una imagen de escritorio de 1366 × 768 píxeles o superior. Recomendadas: lista con vista previa, imagen ampliada y cambio de orden. No presentes un mockup como captura real.

## Notas para certificación: borrador

Aplicación de escritorio Win32 en Python/Tkinter para convertir archivos PNG locales a PDF. Requiere `runFullTrust` para ejecutar la aplicación de escritorio empaquetada y acceder a las carpetas elegidas por el usuario mediante diálogos nativos. No requiere cuenta, servicios remotos ni credenciales para probarla.

Prueba sugerida: seleccionar una carpeta de PNG, revisar la vista previa, abrir una imagen con doble clic y cerrar con Esc, cambiar el orden y exportar el PDF a una carpeta elegida.
