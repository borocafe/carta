# Boró Café — carta digital + QR

Carta móvil estática de Boró Café publicada en GitHub Pages: https://borocafe.github.io/carta/
Empezó en la sesión en la nube `cse_01NuV3XNUTWVhoeUA9F2QUtr` (claude.ai/code, 14-sep-2026) y se migró a este
entorno. De esa sesión nunca llegaron `menu.json` ni `build.py`: acá la fuente es HTML.

## Estructura

- `fuente/carta.html` — **la fuente de verdad**. Carta sin `<html>/<head>/<body>`: se publica tal cual como vista
  previa en claude.ai (https://claude.ai/artifact/QcrZTnnUy4K4XWVjvqxcsk) y de acá sale la página.
- `herramientas/armar_sitio.py` — envuelve la fuente en un documento completo → `docs/index.html`. Correrlo después
  de cada cambio en la fuente. Nunca editar `docs/index.html` a mano.
- `docs/` — lo que sirve Pages (rama `main`, carpeta `/docs`). `docs/ir/` redirige a `/carta/` y es la URL del QR.
- `docs/assets/` — `portada.webp`, `logo.webp`, `logo-claro.webp`, `banda-cafe.webp`, `banda-masas.webp`,
  `banda-pan-grabado.webp`.
- `marca/` — `logo-original.webp` (941 px), `originales/` (PNG elegidos de ComfyUI), `anteriores/` (láminas en desuso).
  `marca/generadas/` son candidatos descartables, fuera de git.
- `herramientas/generar.py` (ComfyUI), `herramientas/bandas.py` (ilustración → banda), `herramientas/qr.py` (QR).
- `qr/` — `qr-carta.png` (4096 px), `qr-carta.svg`, `tarjeta-mesa.png` y `tarjeta-mesa.pdf` (A6, 300 dpi).

## Datos del café (instagram.com/borocafe.cl, 14-sep-2026)

- Nombre **Boró Café** (con tilde). Dirección **Av. Los Leones 2380, esquina Tranquila, Providencia**.
- Instagram `@borocafe.cl`. El horario no aparece publicado: falta.
- `borocafe.cl` está registrado (NIC Chile, mayo 2026) a nombre de "Servicio de alimentación Del Campo Tomicic Ltda",
  sin DNS configurado. Si se usa como dominio, hay que regenerar el QR antes de imprimir.

## Diseño

- Papel `--paper:#f4e8d0`; acento `--marca:#5f672a` (verde del logo `#687030` oscurecido para contraste 5:1).
  Tipografías: Italiana, Cormorant Garamond y Jost. Columna de 620 px máx.
- Portada: lámina art déco con el sello de Boró al centro, dentro de `<h1 class="logo">`, y "Carta" arriba.
- Navegación: 4 botones del mismo ancho → 4 grupos. Cada grupo tiene un `h2` y subsecciones con `h3` verdes:
  - **Café**: Calientes (con pie "Leche vegetal +$800"), Fríos, Té e infusiones ("Todos a $4.200"), Jugos y bebidas.
  - **Comida**: Desayunos, Sándwiches y salados, Almuerzos ("Todos a $6.990").
  - **Dulces**: Masas y medialunas, Pastelería.
  - **Pan**: Panadería, con la nota "Para llevar a casa".
- Bandas en grabado ilustrado (estilo elegido por el usuario, no foto) antes de Café, Dulces y Pan.
- Pie oliva `--pie:#4b5324`: sello en crema, dirección con link a Maps, ícono de Instagram (SVG `currentColor`)
  + `@borocafe.cl` y "Carta vigente · septiembre 2026".
- Descartado por el usuario: la banda de pan con café en estilo vectorial, la contratapa ilustrada y la lista de notas final.

## Imágenes con ComfyUI

- `https://win.tail8f8496.ts.net:8443` (tailscale serve; la IP:8188 aparece cerrada aunque funcione).
- `flux1-schnell-fp8` + `clip_l` + `t5xxl_fp8_e4m3fn` + `ae.safetensors`. Apache 2.0: uso comercial permitido.
- schnell ignora el prompt negativo (cfg 1.0). Pedir objetos y composición, no adjetivos.
- Con "mesa de madera + pared" Flux ignora el estilo grabado y saca foto. Revisar firmas falsas en las esquinas
  (el pan elegido traía una; se recortó).
- `bandas.py` iguala el papel a `#f4e8d0` con ganancias por canal y funde bordes. Así no se ven costuras.

## QR

- `herramientas/qr.py` requiere `segno` (y `opencv-python-headless` para verificar), en un venv con
  `--system-site-packages` para usar PIL y numpy del sistema.
- Apunta a `https://borocafe.github.io/carta/ir/`, corrección H, sello al 24 % del ancho.
- Se verifica con los dos detectores de OpenCV: el clásico falla en imágenes grandes incluso sin sello.

## Pendiente

- Horario del local.
- Decidir qué hacer con el repo viejo `mberlin84/carta` (sigue publicado): archivar o redirigir.
