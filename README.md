# Carta · Boró Café

Carta digital de [Boró Café](https://www.instagram.com/borocafe.cl/) — Av. Los Leones 2380, esquina Tranquila, Providencia.

**En línea:** https://mberlin84.github.io/carta/
**Para el QR:** https://mberlin84.github.io/carta/ir/ (redirige a la carta; cambiá el destino en `docs/ir/index.html` sin reimprimir)

## Estructura

- `docs/` — el sitio publicado por GitHub Pages (rama `main`, carpeta `/docs`).
  - `index.html` — la carta completa, estática, sin dependencias.
  - `assets/` — portada, logo, bandas ilustradas.
  - `ir/` — redirección para el QR impreso.
- `marca/` — logo original, imágenes originales generadas y láminas que ya no se usan.
- `herramientas/generar.py` — genera ilustraciones con ComfyUI (FLUX schnell) en la máquina `win`.
- `herramientas/bandas.py` — convierte una ilustración en banda: iguala el papel y funde los bordes.

## Editar precios

Por ahora se editan directo en `docs/index.html` (buscá el nombre del producto). Cada push a `main`
republica la página en uno o dos minutos.
