# Linux Paint

Aplicación de dibujo y edición básica de imágenes para escritorio Linux inspirada en el clásico **Paint de Windows**, desarrollada en **Python** con **PyQt6**.

![Icono de Linux Paint](icon.svg)

## Características principales

* **Herramientas de dibujo a mano alzada:** Lápiz/Pincel con grosores configurables (`1 px` a `20 px`), Aerógrafo (spray) y Goma de borrar.
* **Formas geométricas con vista previa en vivo:** Líneas rectas, Rectángulos y Elipses/Círculos (con opción de solo borde o relleno sólido).
* **Relleno y color:** Cubo de pintura rápido (*scanline flood fill*), Cuentagotas (selector de color desde cualquier píxel), paleta rápida de 20 colores clásicos y selector de colores personalizados.
* **Texto enriquecido:** Inserción de texto con selección de familia tipográfica del sistema, tamaño en puntos, **Negrita**, *Cursiva* y <u>Subrayado</u>.
* **Selección, portapapeles y edición avanzada:**
  * Selección rectangular para mover, copiar (`Ctrl+C`), eliminar (`Supr`) o recortar áreas.
  * Pegado directo de imágenes y capturas desde el portapapeles (`Ctrl+V`) con expansión automática del lienzo.
  * **8 tiradores interactivos** en esquinas y bordes para redimensionar imágenes pegadas o selecciones en tiempo real (manteniendo `Shift` conserva la proporción original).
  * Transformaciones sobre la selección o el lienzo completo: Rotar 90°, Voltear horizontal/verticalmente, Invertir colores y redimensionado exacto por porcentaje o píxeles (`Ctrl+R`).
* **Lienzo adaptable y Zoom:** Tamaño de lienzo variable (`Ctrl+E` o arrastrando los tiradores del borde) con barras de desplazamiento y niveles de Zoom desde `50%` hasta `800%`.
* **Historial y archivos:** Deshacer (`Ctrl+Z`) y Rehacer (`Ctrl+Y`) hasta 20 pasos, y exportación/apertura en **PNG**, **JPG** y **BMP**.

## Atajos de teclado

| Atajo | Acción |
| :--- | :--- |
| `Ctrl + N` | Nuevo lienzo en blanco |
| `Ctrl + O` | Abrir imagen (`PNG`, `JPG`, `BMP`) |
| `Ctrl + S` | Guardar dibujo |
| `Ctrl + Z` / `Ctrl + Y` | Deshacer / Rehacer |
| `Ctrl + C` / `Ctrl + V` | Copiar selección / Pegar imagen del portapapeles |
| `Supr` (`Delete`) | Eliminar selección flotante |
| `Enter` | Fijar (estampar) selección flotante en el lienzo |
| `Ctrl + E` | Cambiar tamaño del lienzo |
| `Ctrl + R` | Redimensionar selección o imagen pegada |
| `Ctrl + +` / `Ctrl + -` | Acercar / Alejar Zoom |
| `Ctrl + 0` | Restablecer Zoom al `100%` |

## Instalación y ejecución

1. Clona el repositorio y entra en la carpeta:
   `git clone https://github.com/TU_USUARIO/linux-paint.git && cd linux-paint`
2. Crea un entorno virtual e instala las dependencias:
   `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
3. Ejecuta la aplicación:
   `python main.py`

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**.
