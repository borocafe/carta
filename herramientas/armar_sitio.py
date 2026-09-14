#!/usr/bin/env python3
"""
Arma docs/index.html (GitHub Pages) desde fuente/carta.html.

fuente/carta.html es la carta sin <html>/<head>/<body>: el mismo archivo se publica tal cual
como vista previa en claude.ai, y acá se envuelve en un documento completo con metadatos.

Uso:
    python3 herramientas/armar_sitio.py [--url https://borocafe.github.io/carta/]
"""
import argparse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESC = ("Carta de Boró Café: café de especialidad, pan de masa madre, bollería, desayunos y almuerzos. "
        "Av. Los Leones 2380, Providencia.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://borocafe.github.io/carta/")
    a = ap.parse_args()

    s = (RAIZ / "fuente" / "carta.html").read_text(encoding="utf-8")
    titulo = s[s.index("<title>") + len("<title>"):s.index("</title>")]
    cab = s[s.index('<link rel="preconnect"'):s.index("</style>") + len("</style>")]
    cuerpo = s[s.index("</style>") + len("</style>"):].strip()

    doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#f4e8d0">
<meta property="og:type" content="website">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{a.url}">
<meta property="og:image" content="{a.url}assets/logo.webp">
<link rel="icon" href="assets/logo.webp" type="image/webp">
{cab}
</head>
<body>
{cuerpo}
</body>
</html>
"""
    destino = RAIZ / "docs" / "index.html"
    destino.write_text(doc, encoding="utf-8")
    print(f"escrito: {destino.relative_to(RAIZ)} ({len(doc.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
