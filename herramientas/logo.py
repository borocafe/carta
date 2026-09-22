#!/usr/bin/env python3
"""
Reconstruye el sello de Boró: el archivo original viene recortado y el anillo exterior llega cortado
en los cuatro bordes. Acá se detecta el círculo real, se completa el anillo y se deja un margen.

Uso (necesita PIL y numpy):
    python3 herramientas/logo.py

Escribe:
    marca/logo-completo.webp   maestro RGBA con el anillo cerrado (lo usa el QR)
    docs/assets/logo.webp      640 px, verde del logo, para la portada
    docs/assets/logo-claro.webp 420 px, crema, para el pie oliva
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
ORIGINAL = RAIZ / "marca" / "logo-original.webp"
MAESTRO = RAIZ / "marca" / "logo-completo.webp"
CREMA = (253, 248, 236)  # mismo crema que el texto sobre el bloque verde (--pie-tinta)
MARGEN = 0.035  # del radio, para que el anillo no toque el borde de la imagen


def alfa_y_color(im):
    """Alfa por distancia del papel al trazo, y el color del trazo."""
    arr = np.asarray(im.convert("RGB")).astype(float)
    esquinas = np.concatenate([arr[:30, :30].reshape(-1, 3), arr[:30, -30:].reshape(-1, 3),
                               arr[-30:, :30].reshape(-1, 3), arr[-30:, -30:].reshape(-1, 3)])
    papel = np.median(esquinas, axis=0)
    lum = arr.mean(axis=2)
    trazo = np.median(arr[lum < np.percentile(lum, 20)], axis=0)
    v = trazo - papel
    t = ((arr - papel) @ v) / (v @ v)
    return np.clip((t - 0.06) / 0.88, 0, 1), trazo


def circulo(puntos):
    """Ajuste por mínimos cuadrados: devuelve (cx, cy, r)."""
    x, y = puntos[:, 0], puntos[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    sol, *_ = np.linalg.lstsq(A, x ** 2 + y ** 2, rcond=None)
    cx, cy, c = sol
    return cx, cy, float(np.sqrt(c + cx ** 2 + cy ** 2))


def main():
    im = Image.open(ORIGINAL)
    alfa, trazo = alfa_y_color(im)
    mascara = alfa > 0.5
    alto, ancho = mascara.shape
    cx0, cy0 = ancho / 2, alto / 2
    borde, grosores = [], []
    for ang in np.linspace(0, 2 * np.pi, 1440, endpoint=False):
        dx, dy = np.cos(ang), np.sin(ang)
        r = min(ancho, alto) * 0.72
        while r > 10:
            x, y = int(round(cx0 + dx * r)), int(round(cy0 + dy * r))
            if 0 <= x < ancho and 0 <= y < alto and mascara[y, x]:
                break
            r -= 0.5
        else:
            continue
        x, y = int(round(cx0 + dx * r)), int(round(cy0 + dy * r))
        if min(x, y) <= 2 or x >= ancho - 3 or y >= alto - 3:
            continue  # ese ángulo está cortado por el borde: no sirve para el ajuste
        borde.append((cx0 + dx * r, cy0 + dy * r))
        g = 0.0
        while g < r:
            xi, yi = int(round(cx0 + dx * (r - g))), int(round(cy0 + dy * (r - g)))
            if not mascara[yi, xi]:
                break
            g += 0.5
        grosores.append(g)
    borde = np.array(borde)
    cx, cy, R = circulo(borde)
    grosor = float(np.median(grosores))
    print(f"anillo detectado: centro ({cx:.1f}, {cy:.1f}) · radio {R:.1f} px · grosor {grosor:.1f} px "
          f"· {len(borde)} de 1440 ángulos sin cortar")

    rgba = im.convert("RGBA")
    rgba.putalpha(Image.fromarray((alfa * 255).round().astype(np.uint8)))
    lado = int(round(2 * R * (1 + MARGEN)))
    maestro = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    maestro.alpha_composite(rgba, (int(round(lado / 2 - cx)), int(round(lado / 2 - cy))))

    K = 4  # el anillo completo, dibujado con supermuestreo para que el borde quede limpio
    m = Image.new("L", (lado * K, lado * K), 0)
    d = ImageDraw.Draw(m)
    c = lado * K / 2
    d.ellipse((c - R * K, c - R * K, c + R * K, c + R * K), fill=255)
    ri = (R - grosor) * K
    d.ellipse((c - ri, c - ri, c + ri, c + ri), fill=0)
    anillo = Image.new("RGBA", (lado, lado), tuple(int(v) for v in trazo) + (0,))
    anillo.putalpha(m.resize((lado, lado), Image.LANCZOS))
    maestro.alpha_composite(anillo)
    maestro.save(MAESTRO, "WEBP", quality=92, alpha_quality=100, method=6)

    verde = maestro.resize((640, 640), Image.LANCZOS)
    verde.save(RAIZ / "docs" / "assets" / "logo.webp", "WEBP", quality=82, alpha_quality=90, method=6)
    claro = Image.new("RGBA", (420, 420), CREMA + (0,))
    claro.putalpha(maestro.getchannel("A").resize((420, 420), Image.LANCZOS))
    claro.save(RAIZ / "docs" / "assets" / "logo-claro.webp", "WEBP", quality=82, alpha_quality=90, method=6)

    a = np.asarray(verde.getchannel("A"))
    print(f"maestro {maestro.size} · logo.webp 640 px · opacidad máxima en los bordes: "
          f"{max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max())} (0 = anillo completo, sin cortes)")


if __name__ == "__main__":
    main()
