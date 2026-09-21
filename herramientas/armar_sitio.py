#!/usr/bin/env python3
"""
Arma la carta desde la planilla (datos/*.xlsx o datos/*.csv) y la plantilla fuente/carta.html.

Uso:
    python3 herramientas/armar_sitio.py                            # → docs/index.html
    python3 herramientas/armar_sitio.py --vista-previa salida.html # sin <html>/<head>/<body> (claude.ai)

Si la planilla tiene errores no escribe nada y sale con código 1, diciendo qué fila revisar
(en GitHub Actions, como anotaciones de error que llegan por correo).
"""
import argparse
import html
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datos  # noqa: E402

RAIZ = datos.RAIZ
DESC = ("Carta de Boró Café: café de especialidad, pan de masa madre, bollería, desayunos y almuerzos. "
        "Los Leones esq Tranquila, Providencia.")
BANDAS = {"cafe": "banda-cafe.webp", "dulces": "banda-masas.webp", "pan": "banda-pan-grabado.webp"}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


def esc(t):
    return html.escape(str(t), quote=True)


def plata(n):
    return "$" + f"{n:,}".replace(",", ".")


def item(p):
    nombre = f'<p class="item-nombre">{esc(p["producto"])}</p>'
    detalle = f'<p class="variantes">{esc(p["detalle"])}</p>' if p["detalle"] else ""
    if p["precio"] is None:
        return f'<li class="item">{nombre}{detalle}</li>'
    if isinstance(p["precio"], list):
        tamanos = "".join(f'<span class="size">{esc(e)}<b>{plata(v)}</b></span>' for e, v in p["precio"])
        precio = f'<span class="sizes">{tamanos}</span>'
    else:
        precio = plata(p["precio"])
    return (f'<li class="item"><div class="item-top">{nombre}<span class="dots" aria-hidden="true"></span>'
            f'<span class="precio">{precio}</span></div>{detalle}</li>')


def notas(lista):
    out = []
    for nt in lista:
        clase = "fijo" if datos.normal(nt["detalle"]).startswith("todos a") else "nota"
        out.append(f'<p class="{clase}">{esc(nt["detalle"])}</p>\n')
    return "".join(out)


def carta(grupos):
    usados, nav, partes = set(), [], []

    def unico(base):
        cand, i = base, 2
        while cand in usados:
            cand, i = f"{base}-{i}", i + 1
        usados.add(cand)
        return cand

    for g in grupos:
        gid = unico(datos.slug(g["nombre"]))
        nav.append(f'<a href="#{gid}">{esc(g["nombre"])}</a>')
        if gid in BANDAS:
            partes.append(f'<img class="banda" src="assets/{BANDAS[gid]}" alt="" loading="lazy">')
        # Un grupo con una sola sección del mismo nombre (Pan) no repite el título: sus notas van en la cabecera.
        unica = len(g["secciones"]) == 1 and datos.normal(g["secciones"][0]["nombre"]) == datos.normal(g["nombre"])
        subs = []
        for s in g["secciones"]:
            items = "\n".join(item(p) for p in s["productos"])
            if unica:
                subs.append(f'<div class="sub">\n<ul class="items">\n{items}\n</ul>\n</div>')
            else:
                sid = unico(datos.slug(s["nombre"]))
                subs.append(f'<div class="sub" id="{sid}">\n<h3>{esc(s["nombre"])}</h3>\n{notas(s["notas"])}'
                            f'<ul class="items">\n{items}\n</ul>\n</div>')
        cabecera_notas = notas(g["secciones"][0]["notas"]) if unica else ""
        partes.append(f'<section class="grupo" id="{gid}"><div class="wrap">\n'
                      f'<header class="grupo-cab"><h2>{esc(g["nombre"])}</h2>'
                      f'<div class="filete" aria-hidden="true"><span>◆</span></div>{cabecera_notas}</header>\n'
                      + "\n".join(subs) + "\n</div></section>")

    # Hasta 4 grupos entran en una fila; con más, 3 por fila y el resto abajo (caben en celular).
    columnas = len(grupos) if len(grupos) <= 4 else 3
    nav_html = (f'<nav class="nav" aria-label="Secciones de la carta">'
                f'<div class="nav-inner" style="grid-template-columns:repeat({columnas},1fr)">\n'
                + "\n".join(nav) + "\n</div></nav>")
    return nav_html, "<main>\n" + "\n".join(partes) + "\n</main>"


def documento(fragmento, url):
    titulo = fragmento[fragmento.index("<title>") + len("<title>"):fragmento.index("</title>")]
    cab = fragmento[fragmento.index('<link rel="preconnect"'):fragmento.index("</style>") + len("</style>")]
    cuerpo = fragmento[fragmento.index("</style>") + len("</style>"):].strip()
    return f"""<!doctype html>
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
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}assets/logo.webp">
<link rel="icon" href="assets/logo.webp" type="image/webp">
{cab}
</head>
<body>
{cuerpo}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://borocafe.github.io/carta/")
    ap.add_argument("--vista-previa", type=Path)
    a = ap.parse_args()

    try:
        archivo = datos.archivo_vigente()
        grupos, filas = datos.validar(datos.leer(archivo), archivo.name)
    except datos.ErrorPlanilla as e:
        en_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        for err in e.errores:
            print(f"::error title=Revisa la planilla::{err}" if en_actions else f"✗ {err}")
        print("La carta NO se actualizó: corrige lo indicado y vuelve a subir la planilla.")
        sys.exit(1)

    nav, principal = carta(grupos)
    hoy = date.today()
    plantilla = (RAIZ / "fuente" / "carta.html").read_text(encoding="utf-8")
    for marca in ("<!-- NAV -->", "<!-- CARTA -->", "<!-- MES -->"):
        if marca not in plantilla:
            sys.exit(f"fuente/carta.html no tiene la marca {marca}")
    fragmento = (plantilla.replace("<!-- NAV -->", nav).replace("<!-- CARTA -->", principal)
                 .replace("<!-- MES -->", f"{MESES[hoy.month - 1]} {hoy.year}"))

    if a.vista_previa:
        a.vista_previa.write_text(fragmento, encoding="utf-8")
        destino = a.vista_previa
    else:
        destino = RAIZ / "docs" / "index.html"
        destino.write_text(documento(fragmento, a.url), encoding="utf-8")

    secciones = sum(len(g["secciones"]) for g in grupos)
    visibles = sum(len(s["productos"]) for g in grupos for s in g["secciones"])
    ocultos = sum(1 for f in filas if f["tipo"] == "producto" and not f["mostrar"])
    print(f"planilla: datos/{archivo.name} · {len(grupos)} grupos · {secciones} secciones · {visibles} productos"
          + (f" ({ocultos} ocultos)" if ocultos else "") + f" → {destino}")


if __name__ == "__main__":
    main()
