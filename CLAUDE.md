# Boró Café — carta digital + QR/NFC

Carta móvil de Boró Café en GitHub Pages: https://borocafe.github.io/carta/ (repo `borocafe/carta`).
Empezó en la sesión en la nube `cse_01NuV3XNUTWVhoeUA9F2QUtr` (14-sep-2026) y se migró a este entorno.

## Flujo de datos (decisión del usuario: planilla → GitHub, sin Google en vivo)

- **`datos/carta.xlsx` es la fuente de precios y productos.** El personal la descarga, la edita y la sube
  por la web de GitHub (`/upload/main/datos`) con cualquier nombre, en `.xlsx` o `.csv`.
- `.github/workflows/publicar-carta.yml` (en cada push a main): `armar_sitio.py` valida y arma la carta →
  `planilla.py normalizar` deja la subida como `datos/carta.xlsx` y borra las demás (commit del bot) →
  deploy con `actions/deploy-pages`. Pages usa `build_type: workflow` (no la rama).
- Si la planilla tiene errores el job falla, no se publica nada y GitHub avisa por correo. Los mensajes
  están escritos para personas: fila, producto y qué corregir.
- La planilla vigente es la de commit más reciente en `datos/` (por eso el checkout usa `fetch-depth: 0`).

## Reglas de la planilla (`herramientas/datos.py`)

- Columnas: Grupo, Sección, Producto, Detalle, Precio, Mostrar. El orden de las filas es el de la carta.
- Grupo o Sección vacíos heredan de la fila de arriba. Cada grupo es un botón de la navegación.
- Una fila sin Producto y con Detalle es una nota de sección. Si empieza con "Todos a" se muestra como sello
  (`.fijo`) y permite productos sin precio.
- Precio: `3700`, `$3.700`, `3.700`, `4500,00` o tamaños `180 ml: 4500 / 500 ml: 9500`.
  Mostrar: Sí/No (vacío = Sí).
- CSV: acepta `,` o `;` y UTF-8 o cp1252 (Excel en español en Windows).
- Mínimo 5 productos visibles, para no publicar una carta vacía por subir el archivo equivocado.

## Diseño (`fuente/carta.html` es plantilla con `<!-- NAV -->`, `<!-- CARTA -->`, `<!-- MES -->`)

- Papel `#f4e8d0`; acento `--marca:#5f672a` (verde del logo `#687030` oscurecido para contraste 5:1);
  Italiana, Cormorant Garamond y Jost; columna de 620 px máx.
- Portada: lámina art déco con el sello al centro (`<h1 class="logo">`). Pie oliva con el sello en crema,
  dirección, Instagram (SVG inline) y "Carta vigente · <mes>".
- Grupos (`h2`) con subsecciones (`h3` verde). Un grupo con una sola sección del mismo nombre (Pan) no repite
  el título. Bandas en grabado antes de Café, Dulces y Pan (`BANDAS` en `armar_sitio.py`, por slug).
- Navegación: hasta 4 grupos van en una fila; con más (hoy 5: Combos, Café, Comida, Dulces, Pan) van de a 3 por
  fila, para que quepan en celular.
- Descartado por el usuario: foto editorial, la banda vectorial de pan con café, la contratapa ilustrada,
  la lista de notas final y la navegación de 10 botones.

## Carta oficial (fuente del contenido)

- `carta_boro_cafe_editable_v3.pptx` (21-09-2026) es la carta oficial impresa: 3 láminas A4 (portada con promos
  y combos, «Café & bebidas» de la barra, «Para comer» de la vitrina). El texto extraído está en
  `marca/carta-oficial-texto.txt`.
- `datos/carta.xlsx` se transcribió de ahí **sin cambiar precios ni nombres**. Cambios respecto de la versión
  anterior del sitio: salen los Desayunos (tostadas, yogurt, pastrami), el cornetto de jamón queso y los panes
  chicos (ciabatta, brioche, baguette); entran Combos y promos de la mañana; los almuerzos y las tartaletas
  dejan de ser precio único; varios precios suben o bajan.
- Los productos con dos precios (Ensaladas, Cornetto relleno, Tartaletas, Helados) usan el formato de tamaños
  `etiqueta: precio / etiqueta: precio`.

## Datos del café

- Nombre **Boró Café**. Dirección: **«Los Leones 2299, Providencia»**, la versión con número de la carta
  oficial (lámina 3), elegida por el usuario. Las láminas 1 y 2 dicen «esq Tranquila» sin número, e Instagram
  dice 2380: si aparece una fuente mejor, hay que revisarlo. Instagram `@borocafe.cl`.
- Falta el horario. `borocafe.cl` está registrado (mayo 2026, "Servicio de alimentación Del Campo Tomicic
  Ltda") y sin DNS.

## Herramientas locales

- Venv con `--system-site-packages` + `segno openpyxl opencv-python-headless`.
- `armar_sitio.py` → `docs/index.html` (generado, en `.gitignore`); `--vista-previa` genera la variante para
  claude.ai.
- `qr.py`: QR a `/carta/ir/`, corrección H, sello al 24 %, tarjeta A6 con ícono NFC. Se verifica con los dos
  detectores de OpenCV, porque el clásico falla en imágenes grandes incluso sin sello.
- ComfyUI en `https://win.tail8f8496.ts.net:8443` (`flux1-schnell-fp8`, Apache 2.0). `generar.py`,
  `bandas.py`. schnell ignora el prompt negativo; con "mesa + pared" sale foto aunque se pida grabado.
- Preview local: `.claude/launch.json` → `carta` (http.server sobre `docs/`).

## Pendiente

- Regla del usuario (21-09-2026): lo que no está en la carta oficial no va en el sitio. Por eso no hay
  horario del local ni sección de desayunos.
- Repo viejo `mberlin84/carta` sigue publicado: archivar o redirigir (preguntado, sin respuesta).
