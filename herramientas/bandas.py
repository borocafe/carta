#!/usr/bin/env python3
"""
Convierte una imagen generada en una banda para la carta: iguala su papel al de la página y funde los bordes.

Uso:
    python3 herramientas/bandas.py marca/generadas/cafe-grabado.png banda-cafe [--recorte-inf 0.06]

Salida: docs/assets/<nombre>.webp (1240 px de ancho = 2x la columna de 620 px)
        marca/generadas/prueba-<nombre>.jpg (la banda sobre papel, para mirar costuras)
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PAPEL = np.array([244, 232, 208], dtype=float)  # --paper:#f4e8d0


def papel_de(im):
    """Color del papel de la imagen: mediana de los píxeles claros y poco saturados."""
    px = im.reshape(-1, 3)
    lum = px.mean(axis=1)
    sat = px.max(axis=1) - px.min(axis=1)
    claros = px[(lum > np.percentile(lum, 70)) & (sat < 60)]
    return np.median(claros, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("origen")
    ap.add_argument("nombre")
    ap.add_argument("--recorte-inf", type=float, default=0.0, help="fracción a recortar abajo (firmas, bordes)")
    ap.add_argument("--recorte-sup", type=float, default=0.0)
    ap.add_argument("--fundido", type=float, default=0.10, help="fracción del alto que se funde arriba y abajo")
    a = ap.parse_args()

    im = Image.open(RAIZ / a.origen).convert("RGB")
    w, h = im.size
    im = im.crop((0, int(h * a.recorte_sup), w, int(h * (1 - a.recorte_inf))))
    arr = np.asarray(im).astype(float)

    origen = papel_de(arr)
    ganancia = PAPEL / origen
    arr = np.clip(arr * ganancia, 0, 255)

    # Fundido a papel liso: arriba/abajo por alto, costados más suave.
    hh, ww, _ = arr.shape
    fy = max(1, int(hh * a.fundido))
    fx = max(1, int(ww * 0.04))
    my = np.ones(hh)
    rampa_y = (1 - np.cos(np.linspace(0, np.pi, fy))) / 2
    my[:fy] = rampa_y
    my[-fy:] = rampa_y[::-1]
    mx = np.ones(ww)
    rampa_x = (1 - np.cos(np.linspace(0, np.pi, fx))) / 2
    mx[:fx] = rampa_x
    mx[-fx:] = rampa_x[::-1]
    m = np.outer(my, mx)[..., None]
    arr = arr * m + PAPEL * (1 - m)

    out = Image.fromarray(arr.round().astype(np.uint8))
    out = out.resize((1240, round(1240 * out.height / out.width)), Image.LANCZOS)
    destino = RAIZ / "docs" / "assets" / f"{a.nombre}.webp"
    out.save(destino, "WEBP", quality=80, method=6)

    prueba = Image.new("RGB", (out.width + 160, out.height + 160), tuple(PAPEL.astype(int)))
    prueba.paste(out, (80, 80))
    prueba.resize((prueba.width // 2, prueba.height // 2)).save(RAIZ / "marca" / "generadas" / f"prueba-{a.nombre}.jpg", quality=85)
    print(f"{a.nombre}: papel origen {origen.round()} -> ganancias {ganancia.round(3)}; "
          f"{out.size[0]}x{out.size[1]}, {destino.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
