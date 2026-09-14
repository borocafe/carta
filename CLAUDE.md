# Boro Café — carta digital + QR

Carta móvil estática para Boro Café, generada desde un solo archivo de datos. Viene de la sesión
en la nube `cse_01NuV3XNUTWVhoeUA9F2QUtr` (claude.ai/code, 14-sep-2026), migrada a este entorno.

## Estructura (según el repo que armó la sesión en la nube)

- `menu.json` — lo único que se edita: secciones, ítems, precios, `qr_destino`.
- `build.py` — genera `docs/index.html` y `docs/ir/index.html` desde `menu.json`. Solo stdlib.
  `python3 build.py --artifact out.html` genera la variante sin `<html>/<head>/<body>`.
- `make_qr.py` — QR en SVG (imprenta), PNG (redes) y `qr/tarjetas-mesa.html` (A4, 4 tarjetas).
- `docs/assets/*.webp` — recortes de las 3 láminas botánicas. En uso: `portada.webp`, `banda-pan.webp`
  (antes de Masas) y `contratapa.webp` (cierre, con el balance de color corregido para calzar con el papel).
  `banda-rama.webp` y `banda-mesa.webp` ya no se usan desde la versión 3.
- `.github/workflows/build.yml` — cada push que toque `menu.json` o `build.py` regenera `docs/`.
- `_redirects` — solo para Cloudflare Pages; GitHub Pages lo ignora.

## Decisiones

- Hosting: GitHub Pages en `mberlin84/carta`, rama `main`, carpeta `/docs`.
- QR dinámico: el impreso apunta a `https://mberlin84.github.io/carta/ir/`, que redirige a `qr_destino`.
  Se cambia el destino editando `menu.json`, sin reimprimir.
- Diseño: papel crema (`--paper:#f4e8d0`), acento terracota, Italiana + Cormorant Garamond + Jost.
  Columna única de 620 px máx, chips de sección pegajosos.
- Secciones de precio fijo (Almuerzos $6.990, Té $4.200) muestran un sello y los ítems van sin precio.
- Sin lista de notas al final (el usuario pidió sacarla). "Leche vegetal +$800" va como `pie` de Cafetería
  caliente. El final es una contratapa: lámina completa con nombre, datos y "Carta vigente · septiembre 2026".
- El zip más reciente de la sesión en la nube es el de las 19:52 UTC (268 KB), con la contratapa.

## Datos del café (confirmados en instagram.com/borocafe.cl, 14-sep-2026)

- Nombre: **Boró Café** (con tilde). La sesión anterior había puesto "Boro Café".
- Bio: "Café de especialidad, bollería, pan masa madre, pizza, desayuno y almuerzo".
- Dirección: **Av. Los Leones 2380, esquina Tranquila, Providencia**. La sesión anterior había puesto "2299".
- Instagram: `@borocafe.cl` → https://www.instagram.com/borocafe.cl/
- Estos datos ya están en la vista previa publicada (https://claude.ai/artifact/QcrZTnnUy4K4XWVjvqxcsk),
  pero **todavía no en `menu.json`**: aplicarlos ahí cuando llegue el zip, o el próximo build los pisa.

- Marca: logo circular verde oliva sobre crema ("BORÓ café · Pan · Café de especialidad · Bollería").
  Verde del logo ≈ `#687030`. En la carta el acento pasó de terracota a `--marca:#5f672a`, que es más oscuro
  para que el texto chico sobre el papel tenga contraste 5:1. El token se renombró de `--terra` a `--marca`:
  replicar ese cambio en `build.py`.
- Logo: original en `marca/logo-original.webp` (941 px, fondo crema). `docs/assets/logo.webp` es la versión
  para la web: 600 px, fondo transparente y todo el trazo en el verde del logo (`#686e31`), para que se apoye
  sobre el papel sin recuadro. Va en la portada, dentro del `<h1 class="logo">`, al 83% del área central
  (= 50% del ancho de la lámina), con "Carta" arriba. Reemplaza al nombre escrito y a la bajada.
  La contratapa sigue con el nombre en texto. Replicar en `build.py`.

- Pie (reemplaza a la contratapa ilustrada, que al usuario no le gustó): bloque oliva `--pie:#4b5324` con
  texto crema. Contiene el sello en crema (`docs/assets/logo-claro.webp`, 400 px, mismo alfa que `logo.webp`),
  la dirección con link a Maps, el ícono de Instagram (SVG inline con `currentColor`) + `@borocafe.cl`,
  un filete y "Carta vigente · septiembre 2026". Ya no usa `contratapa.webp`.

## Imágenes con ComfyUI

- Servidor: `https://win.tail8f8496.ts.net:8443` (tailscale serve; la IP:8188 aparece cerrada aunque funcione).
- Modelo: `flux1-schnell-fp8` + `clip_l` + `t5xxl_fp8_e4m3fn` + VAE `ae.safetensors`. Apache 2.0, uso comercial OK.
- `herramientas/generar.py candidatos` → `marca/generadas/<motivo>-<estilo>.png` (1344×784).
- schnell ignora el prompt negativo (cfg 1.0): la dirección va en positivo, y se piden objetos y
  composición, no adjetivos.
- La banda del pan con café (`banda-pan.webp`) no le gustó al usuario: se reemplaza por imágenes generadas.
- Estilo elegido por el usuario: **grabado ilustrado** (no foto editorial). Bandas: `banda-cafe.webp` antes de
  Cafetería caliente, `banda-masas.webp` antes de Masas y `banda-pan-grabado.webp` antes de Panadería.
- `herramientas/bandas.py <png> <nombre>` iguala el papel de la imagen a `#f4e8d0` con ganancias por canal,
  funde bordes, recorta (`--recorte-sup/--recorte-inf`) y escribe `docs/assets/<nombre>.webp` a 1240 px.
- Lección: con una escena de "mesa de madera + pared", Flux ignora el estilo grabado y saca foto. Para el pan,
  la escena va sin mesa ni pared, "sobre papel crema", y termina con "hand drawn, not a photograph".

## GitHub y QR

- Repo `mberlin84/carta`, rama `main`. GitHub Pages sirve `docs/`: https://mberlin84.github.io/carta/
- `docs/index.html` es la carta como documento completo (se armó desde la vista previa del artifact).
  **No hay generador todavía**: `menu.json` y `build.py` de la sesión en la nube nunca llegaron a este repo.
- `herramientas/qr.py` (necesita `segno`; para verificar, `opencv-python-headless`) genera en `qr/`:
  `qr-carta.png` (4096 px), `qr-carta.svg`, `tarjeta-mesa.png` y `tarjeta-mesa.pdf` (A6, 300 dpi).
  Apunta a `/carta/ir/`, corrección H, sello al 24 % del ancho. Se verifica leyendo con dos detectores
  de OpenCV: el clásico falla en imágenes grandes incluso sin sello, así que no es una señal válida por sí solo.

## Pendiente

- Horario: Instagram no lo publica. Falta pedirlo.
- Push inicial a `mberlin84/carta` (el repo está vacío) y activar Pages desde `/docs`.
- Si se usa dominio propio, regenerar el QR con la URL final antes de imprimir.
