# Boró Café — carta digital + QR/NFC

Carta móvil de Boró Café en GitHub Pages: https://borocafe.github.io/carta/ (repo `borocafe/carta`).
Empezó en la sesión en la nube `cse_01NuV3XNUTWVhoeUA9F2QUtr` (14-sep-2026) y se migró a este entorno.

## Flujo de datos (decisión del usuario: planilla → GitHub, sin Google en vivo)

- **`datos/carta.xlsx` es la fuente de precios y productos.** El personal la descarga, la edita y la sube
  por la web de GitHub (`/upload/main/datos`) con cualquier nombre, en `.xlsx` o `.csv`.
- `.github/workflows/publicar-carta.yml` (en cada push a main): `armar_sitio.py` valida y arma la carta →
  `carta_pdf.py` la imprime a `docs/carta.pdf` → `planilla.py normalizar` deja la subida como
  `datos/carta.xlsx` y borra las demás (commit del bot) → deploy con `actions/deploy-pages`.
  Pages usa `build_type: workflow` (no la rama). El paso del PDF es `continue-on-error`: si falla,
  la carta igual se publica y queda un aviso en el job.
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

- **Paleta: papel crema y un solo verde, el de las sillas del local** (22-09-2026). El usuario descartó la
  paleta sacada de las fotos (madera + azulejo + pizarritas) y pidió volver al diseño anterior cambiando
  el verde oscuro por el de la silla. Papel `#f4e8d0`. La silla se midió en el canto iluminado del asiento
  de la silla del primer plano (el usuario pidió mirar esa, no la del fondo, que está en sombra):
  **`#7a8160`** (`--olive`). Es un tono medio: encima no se lee ni el crema (3.6:1) ni el blanco puro
  (4.0:1) ni la tinta oscura (3.2:1), así que los bloques y el botón activo van al 90 % de ese verde,
  `--pie:#6e7456`, con crema casi blanco `--pie-tinta:#fdf8ec` (4.6:1) — lo más cerca de la silla que
  admite texto legible. Precios y títulos sobre papel, al 70 %: `--marca:#565b45` (5.8:1).
  Italiana, Cormorant Garamond y Jost; columna de 620 px máx.
- **Portada y pie son el mismo gesto** (decisión del usuario, 22-09-2026): bloque verde `--pie` con
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
- **La planilla ya no calca la PPT**: el 6-10-2026 el local subió una versión nueva por la web de GitHub.
  Salió entero el grupo Combos (las seis promos), más Ice Cappuccino, Iced Latte, Pan de chocolate y
  Baguette de roast beef; entraron Espresso naranja, Ice Latte e Ice Moca; Brookie/Brownie bajó a $2.900.
  Quedan dos grupos: «Café & bebidas» y «Para comer». Manda la planilla, no la PPT.

## Flyer de 14 x 20 cm (`flyer/`)

- El local tenía `Flyer 4,2_F.pdf` (Christian del Campo, 28-10-2026, Illustrator): **una sola imagen de
  155 ppi**, sin una línea de texto vectorial. Por eso se rehízo entero; no había nada que rescatar.
- Se entrega **`flyer/Flyer Boro Cafe.pptx`** como editable: Canva importa PowerPoint dejando cada texto
  como caja de texto y cada imagen aparte (el PDF entra más frágil y el SVG, aplanado), y el mismo archivo
  abre en Keynote, Slides y PowerPoint. Al lado van `flyer-boro.pdf` (imprenta) y `flyer-boro.png` (300 ppi).
- **Una maqueta, dos salidas**: `herramientas/flyer.py` tiene el texto en `CONTENIDO`, la maqueta en
  `maqueta()` (rectángulos, discos, líneas, fotos y textos, todo en mm) y dos dibujantes, `a_pptx` y
  `a_html`; el PDF sale del HTML con el mismo Chrome que la carta.
- **La maqueta se apoya en una grilla explícita** (constantes `MARGEN`, `IZQ_X/W`, `DER_X/W`, `PADDING`
  y una `Y` por bloque): margen parejo de 5 mm, canal de 4 mm entre columnas, 4 mm de margen interno en
  los paneles y 2 mm de aire entre bloques. La primera versión ponía cada cosa en coordenadas sueltas y
  se notaba: paneles que no alineaban con las fotos y huecos de 0,3 y de 3 mm en la misma página.
- Lo que va entre `*asteriscos*` en `CONTENIDO` sale en negrita: así «Café», «jugo de naranja» y los
  «300» pesos quedan resaltados dentro del detalle, como en el original. Las métricas de PowerPoint y de Chrome
  no son idénticas: manda el PDF, el PPTX puede pedir medio milímetro de ajuste.
- `herramientas/flyer_graficas.py` dibuja en SVG los iconos, el corazón y las ramas de hojas, y los
  rasteriza a PNG (`flyer/graficas/`, con el SVG al lado). Son dibujos propios: nítidos a cualquier tamaño.
  El sello del logo tiene el **interior transparente**, así que lleva un disco crema detrás o las hojas se
  le meten adentro.
- `herramientas/flyer_fotos.py` genera las tres fotos con FLUX schnell, cada una del tamaño de su recuadro
  a 300 ppi (las del original venían a 155). **Luz difusa y blanco neutro**: la primera tanda pidió «warm
  late-morning light» y las tres salieron anaranjadas, lejos del original, que es fresco y verde. En
  `RECUADROS` cada foto dice además su `zoom` y su `foco` para el recorte.
- **Tipografías: PT Serif, Lato y Pacifico** (no las de la carta). La primera versión usaba Cormorant
  Garamond y Jost por coherencia con la carta y el usuario dijo que se veía **más feo que el original**:
  tenía razón, quedaba pálido y aireado. El original usa una serif con cuerpo tipo Times, una sans
  humanista y una script de pincel gruesa; un flyer de promos necesita peso, no la elegancia de la carta.
  Se compararon especímenes contra el original antes de elegir. Las tres son de Google Fonts, están en
  Canva y quedaron en `flyer/tipografias/`; se instalaron en `~/Library/Fonts` para que el PDF salga bien.
- Los nombres de los combos se ajustan solos con `achicar()`: «Almuerzo + Bebestible» no cabe a 13,5 pt y
  baja hasta entrar, como en el original.
- **El QR del original apuntaba a `borocafe.cl`, que no tiene DNS**: se reemplazó por el del proyecto
  (`qr/qr-carta.png`, a la carta digital), rotulado «NUESTRA CARTA». Se verificó que decodifica desde el
  arte final a 300 y a 150 ppp.
- Diferencias de texto respecto del original, todas avisadas al usuario: «mochaccino» → «mocaccino» (como
  en la carta) y los horarios con dos puntos parejos (`8:00` y no `8.00`).
- Sale a 140 x 200 mm **al corte, sin sangría**. Si la imprenta la pide, hay que rehacerlo a 146 x 206.

## Datos del café

- Nombre **Boró Café**. En la carta se lee **«Los Leones esq Tranquila · Providencia»** (decisión del usuario,
  22-09-2026), pero el enlace al mapa busca «Av. Los Leones 2299, Providencia», como en la lámina 3 de la carta
  oficial. Sin el «Av.» Google Maps mandaba a otra parte; con «Av. Los Leones 2299, Providencia» cae bien
  (el usuario lo verificó). El enlace del pie usa ese texto, sin región. Instagram `@borocafe.cl`.
- **Horario** (del flyer del local, 28-10-2026): lunes a viernes 8:00 a 20:30, sábado y domingo 10:00 a
  20:30. La promo del café barato es de lunes a viernes de 8:00 a 11:00. La carta digital **no** lo muestra
  todavía: la regla del usuario es que solo va lo que está en la carta oficial.
- `borocafe.cl` está registrado (mayo 2026, "Servicio de alimentación Del Campo Tomicic Ltda") y sin DNS:
  por eso el QR del flyer apunta a la carta en GitHub Pages y no al dominio.

## Herramientas locales

- Venv con `--system-site-packages` + `segno openpyxl opencv-python-headless`.
- `armar_sitio.py` → `docs/index.html` (generado, en `.gitignore`); `--vista-previa` genera la variante para
  claude.ai.
- `qr.py`: QR a `/carta/ir/`, corrección H, sello al 24 %, tarjeta A6 con ícono NFC. Se verifica con los dos
  detectores de OpenCV, porque el clásico falla en imágenes grandes incluso sin sello.
- `logo.py`: reconstruye el sello completo desde `marca/logo-original.webp` y escribe las variantes
  (`docs/assets/logo.webp`, `logo-claro.webp` y `manual/img/logo-claro.png`, el sello crema del manual).
- `carta_pdf.py` → `docs/carta.pdf` (generado, en `.gitignore`): Chrome sin interfaz imprime el mismo
  `docs/index.html`, así el PDF nunca se separa de la web. El layout sale del bloque `@media print` de
  `fuente/carta.html`: `@page` sin márgenes (Chrome no pinta el fondo dentro de los márgenes de página),
  portada y pie a sangre ocupando la hoja entera, y un grupo por hoja a dos columnas. Son 5 páginas.
  El pie de la carta lo ofrece con «Descargar la carta en PDF».
- `manual.py` → `manual/Manual carta Boró Café.pdf` (9 páginas, reportlab). La miniatura de la carta se
  dibuja en el PDF (clase `Maqueta`), no son capturas, y la muestra de la planilla se lee de
  `datos/carta.xlsx`. Comparte paleta con la carta: hay que regenerarlo cuando cambian los colores.
- ComfyUI en `https://win.tail8f8496.ts.net:8443` (`flux1-schnell-fp8`, Apache 2.0). `generar.py`,
  `bandas.py` (las ilustraciones ya no se usan en la carta). schnell ignora el prompt negativo; con
  "mesa + pared" sale foto aunque se pida grabado.
- Preview local: `.claude/launch.json` → `carta` (http.server sobre `docs/`).

## Pendiente

- Regla del usuario (21-09-2026): lo que no está en la carta oficial no va en el sitio. Por eso no hay
  horario del local ni sección de desayunos.
- Repo viejo `mberlin84/carta` sigue publicado: archivar o redirigir (preguntado, sin respuesta).
