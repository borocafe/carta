# Carta · Boró Café

Carta digital de [Boró Café](https://www.instagram.com/borocafe.cl/) — Los Leones esq Tranquila, Providencia.

**En línea:** https://borocafe.github.io/carta/
**QR y NFC de las mesas:** https://borocafe.github.io/carta/ir/ (redirige a la carta)

## Cómo cambiar precios o agregar productos

1. **Descarga la planilla vigente:** https://github.com/borocafe/carta/raw/main/datos/carta.xlsx
2. **Edítala** en Excel, Numbers o Google Sheets. La hoja *Instrucciones* explica cada columna:
   - cambiar un precio → escribe el número nuevo (ej. `3700`)
   - agregar un producto → inserta una fila en su sección
   - sacarlo por un tiempo → `No` en *Mostrar*
3. **Súbela:** entra a https://github.com/borocafe/carta/upload/main/datos, arrastra el archivo
   (sirve `.xlsx` o `.csv`, con cualquier nombre) y aprieta **Commit changes**.
4. En unos 2 minutos la carta está actualizada.

Si algo está mal escrito (un precio con letras, un producto sin precio), **la carta no cambia** y GitHub
avisa por correo qué fila revisar. Se corrige y se vuelve a subir.

Cada subida queda en el historial del repositorio: se puede ver quién cambió qué y volver atrás.

## Cómo funciona

- `datos/carta.xlsx` — la planilla. Es lo único que se edita para precios y productos.
- `fuente/carta.html` — el diseño (plantilla con `<!-- NAV -->`, `<!-- CARTA -->` y `<!-- MES -->`).
- `.github/workflows/publicar-carta.yml` — en cada subida revisa la planilla, arma la carta y la publica en
  GitHub Pages. Si la planilla llegó con otro nombre, la guarda como `datos/carta.xlsx`.
- `docs/` — lo que se publica: `assets/` (portada, logo, ilustraciones) e `ir/` (redirección del QR).
  `docs/index.html` se genera; no se edita ni se versiona.
- `herramientas/` — `armar_sitio.py` (carta), `datos.py` (lectura y revisión de la planilla),
  `planilla.py` (Excel), `qr.py` (QR y tarjeta de mesa), `generar.py` y `bandas.py` (ilustraciones con ComfyUI).
- `qr/` — QR con el sello (PNG y SVG) y tarjeta de mesa A6 (PNG y PDF).
- `marca/` — logo original e ilustraciones originales.

Para armar la carta en local: `pip install openpyxl` y `python3 herramientas/armar_sitio.py`.

## Tarjeta de mesa con NFC

Detrás del QR va un sticker NFC (NTAG213 o NTAG215, 25–30 mm) grabado con la misma URL
`https://borocafe.github.io/carta/ir/` usando la app NFC Tools, y **bloqueado** después de grabarlo.
En mesas o bandejas de metal hace falta un sticker anti-metal.
