#!/usr/bin/env python3
"""
QR de la carta con el sello de Boró al centro, listo para imprenta.

Uso (necesita segno; PIL y numpy del sistema):
    python3 herramientas/qr.py [--url https://borocafe.github.io/carta/ir/]

Salida en qr/:
    qr-carta.png      4096 px, fondo blanco: para imprenta o para escalar a cualquier tamaño
    qr-carta.svg      módulos vectoriales + sello incrustado
    tarjeta-mesa.png  A6 (105 x 148 mm) a 300 dpi, papel crema
    tarjeta-mesa.pdf  lo mismo en PDF

Decisiones:
  - Corrección de errores H (30 %): el sello tapa ~5 % del área, con margen de sobra.
  - Módulos cuadrados y patrones de posición estándar: lo decorativo es el sello, no el código.
  - El QR apunta a /carta/ir/ (redirección), así el impreso sobrevive a cambios de URL.
"""
import argparse
import base64
import io
from pathlib import Path

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
OLIVA = (63, 70, 32)          # módulos: oliva oscuro, contraste ~9:1 sobre blanco
CREMA = (244, 232, 208)       # --paper
BLANCO = (255, 255, 255)
MARGEN = 4                    # zona de silencio en módulos (mínimo del estándar)
LOGO_FRAC = 0.24              # ancho del sello / ancho del símbolo


def sello(diametro):
    """Sello original recortado en círculo, con un anillo blanco que lo separa de los módulos."""
    orig = Image.open(RAIZ / "marca" / "logo-original.webp").convert("RGBA").resize((diametro, diametro), Image.LANCZOS)
    m = Image.new("L", (diametro * 4, diametro * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, diametro * 4 - 1, diametro * 4 - 1), fill=255)
    orig.putalpha(m.resize((diametro, diametro), Image.LANCZOS))
    return orig


def matriz(url):
    q = segno.make(url, error="h", boost_error=False)
    return q, np.array([[bool(c) for c in fila] for fila in q.matrix], dtype=bool)


def zona_logo(n, modulo_px=None):
    """Centro y radio (en módulos) del hueco del sello, con 1 módulo de aire."""
    c = n / 2
    r = n * LOGO_FRAC / 2
    return c, r, r + 1.0


def png(q, mat, destino, lado=4096):
    n = mat.shape[0]
    total = n + 2 * MARGEN
    mod = lado // total
    lado = mod * total
    im = Image.new("RGB", (lado, lado), BLANCO)
    d = ImageDraw.Draw(im)
    c, r, hueco = zona_logo(n)
    for y in range(n):
        for x in range(n):
            if not mat[y, x]:
                continue
            if (x + 0.5 - c) ** 2 + (y + 0.5 - c) ** 2 < hueco ** 2:
                continue
            x0, y0 = (x + MARGEN) * mod, (y + MARGEN) * mod
            d.rectangle((x0, y0, x0 + mod - 1, y0 + mod - 1), fill=OLIVA)
    diam = int(2 * r * mod)
    s = sello(diam)
    centro = int((MARGEN + c) * mod)
    im.paste(s, (centro - diam // 2, centro - diam // 2), s)
    im.save(destino, dpi=(300, 300))
    return im


def svg(mat, destino):
    n = mat.shape[0]
    total = n + 2 * MARGEN
    c, r, hueco = zona_logo(n)
    rects = []
    for y in range(n):
        for x in range(n):
            if mat[y, x] and (x + 0.5 - c) ** 2 + (y + 0.5 - c) ** 2 >= hueco ** 2:
                rects.append(f"M{x + MARGEN} {y + MARGEN}h1v1h-1z")
    b = io.BytesIO()
    sello(512).save(b, "PNG")
    datos = base64.b64encode(b.getvalue()).decode()
    lado_logo = 2 * r
    xy = MARGEN + c - r
    color = "#%02x%02x%02x" % OLIVA
    destino.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}" shape-rendering="crispEdges">'
        f'<rect width="{total}" height="{total}" fill="#fff"/>'
        f'<path fill="{color}" d="{"".join(rects)}"/>'
        f'<image href="data:image/png;base64,{datos}" x="{xy:.4f}" y="{xy:.4f}" width="{lado_logo:.4f}" height="{lado_logo:.4f}"/>'
        f"</svg>\n",
        encoding="utf-8",
    )


def fuente(tam, peso="Medium"):
    for ruta, idx in (("/System/Library/Fonts/Avenir Next.ttc", {"Regular": 7, "Medium": 5, "DemiBold": 2}.get(peso, 5)),
                      ("/System/Library/Fonts/Helvetica.ttc", 0)):
        try:
            return ImageFont.truetype(ruta, tam, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


def tarjeta(qr_img, destino_png, destino_pdf):
    mm = 300 / 25.4
    W, H = round(105 * mm), round(148 * mm)
    t = Image.new("RGB", (W, H), CREMA)
    d = ImageDraw.Draw(t)
    oliva = OLIVA

    def centrado(texto, y, f, color=oliva, espaciado=0):
        if espaciado:
            anchos = [d.textlength(ch, font=f) for ch in texto]
            total = sum(anchos) + espaciado * (len(texto) - 1)
            x = (W - total) / 2
            for ch, a in zip(texto, anchos):
                d.text((x, y), ch, font=f, fill=color)
                x += a + espaciado
        else:
            d.text(((W - d.textlength(texto, font=f)) / 2, y), texto, font=f, fill=color)

    centrado("CARTA", round(14 * mm), fuente(round(4.2 * mm), "DemiBold"), espaciado=round(1.6 * mm))
    lado_qr = round(78 * mm)
    blanco = round(4 * mm)
    y_qr = round(26 * mm)
    d.rounded_rectangle(((W - lado_qr) // 2 - blanco, y_qr - blanco, (W + lado_qr) // 2 + blanco, y_qr + lado_qr + blanco),
                        radius=round(3 * mm), fill=BLANCO)
    t.paste(qr_img.resize((lado_qr, lado_qr), Image.LANCZOS), ((W - lado_qr) // 2, y_qr))
    # Llamado + ícono sin contacto: detrás del QR va un sticker NFC con la misma URL.
    f_cta = fuente(round(5.2 * mm), "Medium")
    llamado = "Escanea o acerca tu celular"
    y_cta = y_qr + lado_qr + round(11 * mm)
    radio = round(3.2 * mm)
    separacion = round(2.4 * mm)
    ancho = radio + separacion + d.textlength(llamado, font=f_cta)
    x0 = (W - ancho) / 2
    caja = d.textbbox((x0 + radio + separacion, y_cta), llamado, font=f_cta)
    cy = (caja[1] + caja[3]) / 2
    for k in range(1, 5):
        r = radio * k / 4
        d.arc((x0 - r, cy - r, x0 + r, cy + r), start=-50, end=50, fill=oliva, width=max(2, round(0.42 * mm)))
    d.text((x0 + radio + separacion, y_cta), llamado, font=f_cta, fill=oliva)
    centrado("@borocafe.cl  ·  Los Leones esq Tranquila, Providencia", y_qr + lado_qr + round(20 * mm),
             fuente(round(3.0 * mm), "Regular"), color=(109, 91, 72))
    t.save(destino_png, dpi=(300, 300))
    t.save(destino_pdf, "PDF", resolution=300)


def verificar(ruta, url):
    try:
        import cv2
    except ImportError:
        return "sin verificar (falta opencv)"
    # El detector clásico de OpenCV falla con imágenes grandes y nítidas incluso SIN sello (medido);
    # el Aruco lee todas. Cuenta como legible si lo lee cualquiera de los dos.
    detectores = (cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco())
    img = cv2.imread(str(ruta))
    h, w = img.shape[:2]
    resultados = []
    for ancho in (1600, 600, 300):  # también chico, como lo ve un celular desde lejos
        chica = cv2.resize(img, (ancho, round(h * ancho / w)), interpolation=cv2.INTER_AREA)
        ok = any(d.detectAndDecode(chica)[0] == url for d in detectores)
        resultados.append(f"{ancho}px={'OK' if ok else 'FALLA'}")
    return ", ".join(resultados)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://borocafe.github.io/carta/ir/")
    a = ap.parse_args()
    out = RAIZ / "qr"
    out.mkdir(exist_ok=True)
    q, mat = matriz(a.url)
    print(f"QR versión {q.version}, corrección {q.error}, {mat.shape[0]} módulos")
    im = png(q, mat, out / "qr-carta.png")
    svg(mat, out / "qr-carta.svg")
    tarjeta(im, out / "tarjeta-mesa.png", out / "tarjeta-mesa.pdf")
    print("lectura:", verificar(out / "qr-carta.png", a.url))
    print("tarjeta:", verificar(out / "tarjeta-mesa.png", a.url))
    for f in sorted(out.iterdir()):
        print(f"  {f.relative_to(RAIZ)}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
