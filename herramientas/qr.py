#!/usr/bin/env python3
"""
QR de la carta con el sello de Boró al centro, listo para imprenta.

Uso (necesita segno; PIL y numpy; opencv para verificar):
    python3 herramientas/qr.py [--url https://borocafe.github.io/carta/ir/]

Salida en qr/:
    qr-carta.png        3000 px, fondo blanco  · el de siempre, para imprenta
    qr-carta-crema.png  3000 px, fondo crema   · para piezas sobre papel de la marca
    qr-carta.svg        vectorial, fondo blanco · para imprimir a cualquier tamaño
    tarjeta-mesa.png    A6 (105 x 148 mm) a 300 dpi
    tarjeta-mesa.pdf    lo mismo en PDF

Decisiones:
  - Corrección de errores H (30 %): el sello tapa ~5 % del área, con margen de sobra.
  - Módulos redondeados y esquinas dibujadas como marcos: se ve mejor y sigue siendo estándar.
  - El QR apunta a /carta/ir/ (redirección), así el impreso sobrevive a cambios de URL.
  - Cada archivo se lee con los dos detectores de OpenCV antes de darlo por bueno.
"""
import argparse
import base64
import io
from pathlib import Path

import numpy as np
import segno
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
OLIVA = (63, 70, 32)          # tinta: oliva oscuro, contraste ~9:1 sobre blanco y ~5:1 sobre crema
CREMA = (244, 232, 208)       # --paper
BLANCO = (255, 255, 255)
TINTA_SUAVE = (109, 91, 72)
MARGEN = 4                    # zona de silencio en módulos (mínimo del estándar)
LOGO_FRAC = 0.24              # ancho del sello / ancho del símbolo
K = 2                         # supermuestreo al dibujar


def sello(diametro):
    """
    Medallón para el centro del QR: el corazón del sello (la rama y «Boró café») sobre un disco crema
    con aro verde. El anillo de texto chico del sello completo, a este tamaño, sale como una mancha.
    """
    maestro = RAIZ / "marca" / "logo-completo.webp"
    fuente_logo = maestro if maestro.exists() else RAIZ / "marca" / "logo-original.webp"
    orig = Image.open(fuente_logo).convert("RGBA")
    n = orig.width
    c, rc = n / 2, 0.60 * n / 2      # hasta el 60 % del radio: rama + «Boró café», sin el anillo de texto
    contenido = orig.crop((round(c - rc), round(c - rc), round(c + rc), round(c + rc)))

    S = 4  # supermuestreo
    D = diametro * S
    disco = Image.new("RGBA", (D, D), (0, 0, 0, 0))
    d = ImageDraw.Draw(disco)
    d.ellipse((0, 0, D - 1, D - 1), fill=CREMA + (255,))
    aro = max(2, round(D * 0.055))
    d.ellipse((aro / 2, aro / 2, D - aro / 2, D - aro / 2), outline=OLIVA + (255,), width=aro)
    lado = round(D * 0.78)
    contenido = contenido.resize((lado, lado), Image.LANCZOS)
    # En círculo: las esquinas del recorte cuadrado alcanzan el anillo del sello y salían como un cuadrado.
    recorte = Image.new("L", (lado * 4, lado * 4), 0)
    ImageDraw.Draw(recorte).ellipse((0, 0, lado * 4 - 1, lado * 4 - 1), fill=255)
    alfa = contenido.getchannel("A").point(lambda v: v)
    alfa = Image.composite(alfa, Image.new("L", (lado, lado), 0), recorte.resize((lado, lado), Image.LANCZOS))
    contenido.putalpha(alfa)
    disco.alpha_composite(contenido, ((D - lado) // 2, (D - lado) // 2))
    return disco.resize((diametro, diametro), Image.LANCZOS)


def matriz(url):
    q = segno.make(url, error="h", boost_error=False)
    return q, np.array([[bool(c) for c in fila] for fila in q.matrix], dtype=bool)


def zona_logo(n):
    """Centro y radio (en módulos) del hueco del sello, con 1 módulo de aire."""
    c = n / 2
    r = n * LOGO_FRAC / 2
    return c, r, r + 1.0


def _esquinas(n):
    """Las tres casillas de posición, en módulos (x, y) de su esquina superior izquierda."""
    return [(0, 0), (n - 7, 0), (0, n - 7)]


def dibujar(mat, lado=3000, fondo=BLANCO, tinta=OLIVA, sello_al_centro=True):
    n = mat.shape[0]
    total = n + 2 * MARGEN
    mod = lado // total
    lado = mod * total
    c, r, hueco = zona_logo(n)
    esquinas = _esquinas(n)

    m = Image.new("L", (lado * K, lado * K), 0)
    d = ImageDraw.Draw(m)
    punto = mod * K * 0.90  # el módulo redondo, con un pelo de aire alrededor
    for y in range(n):
        for x in range(n):
            if not mat[y, x]:
                continue
            if sello_al_centro and (x + 0.5 - c) ** 2 + (y + 0.5 - c) ** 2 < hueco ** 2:
                continue
            if any(ex <= x < ex + 7 and ey <= y < ey + 7 for ex, ey in esquinas):
                continue  # las esquinas se dibujan aparte
            cx = (x + MARGEN + 0.5) * mod * K
            cy = (y + MARGEN + 0.5) * mod * K
            d.ellipse((cx - punto / 2, cy - punto / 2, cx + punto / 2, cy + punto / 2), fill=255)
    for ex, ey in esquinas:
        x0 = (ex + MARGEN) * mod * K
        y0 = (ey + MARGEN) * mod * K
        p = mod * K
        # Cuadradas a propósito: con esquinas redondeadas los lectores estrictos dejan de leerlo.
        d.rectangle((x0, y0, x0 + 7 * p, y0 + 7 * p), fill=255)
        d.rectangle((x0 + p, y0 + p, x0 + 6 * p, y0 + 6 * p), fill=0)
        d.rectangle((x0 + 2 * p, y0 + 2 * p, x0 + 5 * p, y0 + 5 * p), fill=255)

    im = Image.new("RGB", (lado, lado), fondo)
    capa = Image.new("RGB", (lado, lado), tinta)
    im.paste(capa, (0, 0), m.resize((lado, lado), Image.LANCZOS))
    if sello_al_centro:
        diam = int(2 * r * mod)
        s = sello(diam)
        centro = int((MARGEN + c) * mod)
        im.paste(s, (centro - diam // 2, centro - diam // 2), s)
    return im


def svg(mat, destino, fondo="#ffffff"):
    n = mat.shape[0]
    total = n + 2 * MARGEN
    c, r, hueco = zona_logo(n)
    esquinas = _esquinas(n)
    partes = []
    for y in range(n):
        for x in range(n):
            if not mat[y, x] or (x + 0.5 - c) ** 2 + (y + 0.5 - c) ** 2 < hueco ** 2:
                continue
            if any(ex <= x < ex + 7 and ey <= y < ey + 7 for ex, ey in esquinas):
                continue
            partes.append(f'<circle cx="{x + MARGEN + 0.5}" cy="{y + MARGEN + 0.5}" r="0.45"/>')
    for ex, ey in esquinas:
        x0, y0 = ex + MARGEN, ey + MARGEN
        partes.append(f'<path d="M{x0} {y0}h7v7h-7z M{x0 + 1} {y0 + 1}v5h5v-5z" fill-rule="evenodd"/>')
        partes.append(f'<rect x="{x0 + 2}" y="{y0 + 2}" width="3" height="3"/>')
    b = io.BytesIO()
    sello(512).save(b, "PNG")
    datos = base64.b64encode(b.getvalue()).decode()
    lado_logo, xy = 2 * r, MARGEN + c - r
    color = "#%02x%02x%02x" % OLIVA
    destino.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}">'
        f'<rect width="{total}" height="{total}" fill="{fondo}"/>'
        f'<g fill="{color}">{"".join(partes)}</g>'
        f'<image href="data:image/png;base64,{datos}" x="{xy:.4f}" y="{xy:.4f}" '
        f'width="{lado_logo:.4f}" height="{lado_logo:.4f}"/></svg>\n',
        encoding="utf-8")


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

    def centrado(texto, y, f, color=OLIVA, espaciado=0):
        if espaciado:
            anchos = [d.textlength(ch, font=f) for ch in texto]
            x = (W - (sum(anchos) + espaciado * (len(texto) - 1))) / 2
            for ch, a in zip(texto, anchos):
                d.text((x, y), ch, font=f, fill=color)
                x += a + espaciado
        else:
            d.text(((W - d.textlength(texto, font=f)) / 2, y), texto, font=f, fill=color)

    centrado("CARTA", round(14 * mm), fuente(round(4.2 * mm), "DemiBold"), espaciado=round(1.6 * mm))
    lado_qr, blanco, y_qr = round(78 * mm), round(4 * mm), round(26 * mm)
    d.rounded_rectangle(((W - lado_qr) // 2 - blanco, y_qr - blanco, (W + lado_qr) // 2 + blanco, y_qr + lado_qr + blanco),
                        radius=round(3 * mm), fill=BLANCO)
    t.paste(qr_img.resize((lado_qr, lado_qr), Image.LANCZOS), ((W - lado_qr) // 2, y_qr))
    # Llamado + ícono sin contacto: detrás del QR va un sticker NFC con la misma URL.
    f_cta = fuente(round(5.2 * mm), "Medium")
    llamado = "Escanea o acerca tu celular"
    y_cta = y_qr + lado_qr + round(11 * mm)
    radio, separacion = round(3.2 * mm), round(2.4 * mm)
    x0 = (W - (radio + separacion + d.textlength(llamado, font=f_cta))) / 2
    caja = d.textbbox((x0 + radio + separacion, y_cta), llamado, font=f_cta)
    cy = (caja[1] + caja[3]) / 2
    for k in range(1, 5):
        rr = radio * k / 4
        d.arc((x0 - rr, cy - rr, x0 + rr, cy + rr), start=-50, end=50, fill=OLIVA, width=max(2, round(0.42 * mm)))
    d.text((x0 + radio + separacion, y_cta), llamado, font=f_cta, fill=OLIVA)
    centrado("@borocafe.cl  ·  Av. Los Leones 2299, Providencia", y_qr + lado_qr + round(20 * mm),
             fuente(round(3.0 * mm), "Regular"), color=TINTA_SUAVE)
    t.save(destino_png, dpi=(300, 300))
    t.save(destino_pdf, "PDF", resolution=300)


def verificar(ruta, url):
    """Lee el archivo con zxing (el motor de los celulares) y con los dos detectores de OpenCV."""
    import cv2
    try:
        import zxingcpp
    except ImportError:
        zxingcpp = None
    detectores = (cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco())
    img = cv2.imread(str(ruta))
    h, w = img.shape[:2]
    salida = []
    for ancho in (1600, 600, 300, 200):  # 200 px ≈ un QR chico visto de lejos
        chica = cv2.resize(img, (ancho, round(h * ancho / w)), interpolation=cv2.INTER_AREA)
        ok = any(d.detectAndDecode(chica)[0] == url for d in detectores)
        if zxingcpp is not None:
            res = zxingcpp.read_barcode(Image.fromarray(cv2.cvtColor(chica, cv2.COLOR_BGR2RGB)))
            ok = ok and res is not None and res.text == url
        salida.append(f"{ancho}px={'OK' if ok else 'FALLA'}")
    return ", ".join(salida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://borocafe.github.io/carta/ir/")
    a = ap.parse_args()
    out = RAIZ / "qr"
    out.mkdir(exist_ok=True)
    q, mat = matriz(a.url)
    print(f"QR versión {q.version}, corrección {q.error}, {mat.shape[0]} módulos")

    blanco = dibujar(mat, fondo=BLANCO)
    blanco.save(out / "qr-carta.png", dpi=(300, 300))
    dibujar(mat, fondo=CREMA).save(out / "qr-carta-crema.png", dpi=(300, 300))
    svg(mat, out / "qr-carta.svg")
    tarjeta(blanco, out / "tarjeta-mesa.png", out / "tarjeta-mesa.pdf")

    for nombre in ("qr-carta.png", "qr-carta-crema.png", "tarjeta-mesa.png"):
        print(f"  {nombre}: {verificar(out / nombre, a.url)}")
    for f in sorted(out.iterdir()):
        print(f"  {f.relative_to(RAIZ)}  {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
