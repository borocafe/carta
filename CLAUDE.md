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
- **Portada y pie son el mismo gesto** (decisión del usuario, 22-09-2026): bloque oliva `--pie:#4b5324` con
  filete interior, el sello en crema (`logo-claro.webp`), «Carta» arriba y la bajada en dos líneas. Ya no hay
  lámina ilustrada: `portada.webp` quedó en `marca/anteriores/`. El pie suma dirección, Instagram y la fecha.
- La carta ya no carga ninguna ilustración: la única imagen es el sello (todo el sitio pesa ~170 KB).
- Grupos (`h2`) con subsecciones (`h3` verde), con **las mismas agrupaciones que la carta oficial**:
  Combos, «Café & bebidas» (de la barra) y «Para comer» (de la vitrina). Un grupo con una sola sección del
  mismo nombre no repite el título.
- **Sin ilustraciones entremedio** (decisión del usuario, 21-09-2026): las bandas quedaron en
  `marca/anteriores/` y la única imagen de la carta es la portada.
- **El logo original viene recortado**: su anillo llega cortado en los cuatro bordes. `herramientas/logo.py`
  detecta el círculo real, lo completa, deja 3,5 % de margen y escribe `marca/logo-completo.webp` (maestro, lo
  usa también el QR) más `docs/assets/logo.webp` y `logo-claro.webp`. En la portada el sello va al 86 %.
- **Secciones que empiezan con «Promo»** se muestran como tarjetas (`.promo`), no como lista de precios:
  nombre en serif, precio en verde y la condición debajo, como la portada de la carta impresa.
- Navegación: hasta 4 grupos en una fila; con más, de a 3 por fila. El botón verde **no** usa
  `IntersectionObserver` (fallaba en celulares: el grupo anterior seguía tocando la franja y el verde no
  pasaba al siguiente). Se calcula en cada scroll: gana el último grupo cuyo título ya pasó bajo la barra,
  y al final de la página gana siempre el último.
- Descartado por el usuario: foto editorial, la banda vectorial de pan con café, la contratapa ilustrada,
  la lista de notas final, la navegación de 10 botones y las ilustraciones entre secciones.

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

- Nombre **Boró Café**. En la carta se lee **«Los Leones esq Tranquila · Providencia»** (decisión del usuario,
  22-09-2026), pero el enlace al mapa busca «Av. Los Leones 2299, Providencia», como en la lámina 3 de la carta
  oficial. Sin el «Av.» Google Maps mandaba a otra parte; con «Av. Los Leones 2299, Providencia» cae bien
  (el usuario lo verificó). El enlace del pie usa ese texto, sin región. Instagram `@borocafe.cl`.
- Falta el horario. `borocafe.cl` está registrado (mayo 2026, "Servicio de alimentación Del Campo Tomicic
  Ltda") y sin DNS.

## Herramientas locales

- Venv con `--system-site-packages` + `segno openpyxl opencv-python-headless`.
- `armar_sitio.py` → `docs/index.html` (generado, en `.gitignore`); `--vista-previa` genera la variante para
  claude.ai.
- `qr.py`: QR a `/carta/ir/`, corrección H, sello al 24 %, tarjeta A6 con ícono NFC. Se verifica con los dos
  detectores de OpenCV, porque el clásico falla en imágenes grandes incluso sin sello.
- `logo.py`: reconstruye el sello completo desde `marca/logo-original.webp`.
- ComfyUI en `https://win.tail8f8496.ts.net:8443` (`flux1-schnell-fp8`, Apache 2.0). `generar.py`,
  `bandas.py` (las ilustraciones ya no se usan en la carta). schnell ignora el prompt negativo; con
  "mesa + pared" sale foto aunque se pida grabado.
- Preview local: `.claude/launch.json` → `carta` (http.server sobre `docs/`).

## Pendiente

- Regla del usuario (21-09-2026): lo que no está en la carta oficial no va en el sitio. Por eso no hay
  horario del local ni sección de desayunos.
- Repo viejo `mberlin84/carta` sigue publicado: archivar o redirigir (preguntado, sin respuesta).
