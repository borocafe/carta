#!/usr/bin/env python3
"""
Dibuja las gráficas vectoriales del flyer y las deja en PNG de alta resolución.

Uso:
    python3 herramientas/flyer_graficas.py

Escribe en flyer/graficas/: el SVG (fuente, editable en Illustrator o Inkscape) y el PNG a 600 px de
alto para armar el PPTX. Son dibujos propios, no imágenes generadas: así se imprimen nítidos a
cualquier tamaño y se pueden recolorear.

  iconos grandes  taza, croissant, sandwich, hoja     círculo verde con el trazo en crema
  iconos chicos   grano, hojas, sillon, carita        solo el trazo, en verde
  del pie         pin, reloj, instagram               en crema, para la barra verde
  decoración      rama-grande, rama-chica, rama-pie   las hojas de las esquinas
"""
import math
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "flyer" / "graficas"

VERDE = "#2F4420"
VERDE_MEDIO = "#46602C"
VERDE_CLARO = "#6E8C3E"
CREMA = "#F7F5E3"


def svg(cuerpo, w=120, h=120, fondo=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{fondo}{cuerpo}</svg>')


# ---------------------------------------------------------------- hojas

def hoja(x, y, largo, ancho, giro, color, nervio=True, opacidad=1.0):
    """Una hoja almendrada apuntando a la derecha, girada `giro` grados sobre (x, y)."""
    l, a = largo, ancho / 2
    d = f"M0,0 C {l*0.25},{-a} {l*0.72},{-a} {l},0 C {l*0.72},{a} {l*0.25},{a} 0,0 Z"
    partes = [f'<path d="{d}" fill="{color}" fill-opacity="{opacidad}"/>']
    if nervio:
        partes.append(f'<path d="M{l*0.06},0 L{l*0.92},0" stroke="{CREMA}" stroke-opacity=".35" '
                      f'stroke-width="{max(0.8, l*0.035)}" fill="none" stroke-linecap="round"/>')
    return f'<g transform="translate({x:.1f},{y:.1f}) rotate({giro:.1f})">{"".join(partes)}</g>'


def rama(n, largo, curva, escala=1.0, colores=(VERDE, VERDE_MEDIO, VERDE_CLARO), salto=18):
    """Tallo curvo con hojas alternadas a lado y lado."""
    pasos = [i / (n - 1) for i in range(n)]
    def punto(t):
        return (largo * t, curva * math.sin(math.pi * t) * -1)
    tallo = "M" + " L".join(f"{punto(t)[0]:.1f},{punto(t)[1]:.1f}" for t in [i / 40 for i in range(41)])
    piezas = [f'<path d="{tallo}" stroke="{VERDE_MEDIO}" stroke-width="{2.2*escala:.1f}" fill="none" '
              f'stroke-linecap="round"/>']
    for i, t in enumerate(pasos):
        x, y = punto(t)
        lado = -1 if i % 2 else 1
        base = math.degrees(math.atan2(curva * -math.pi * math.cos(math.pi * t), largo)) if 0 < t < 1 else 0
        giro = base + lado * salto
        largo_h = (26 - 8 * t) * escala
        piezas.append(hoja(x, y, largo_h, largo_h * 0.5, giro, colores[i % len(colores)]))
    return "".join(piezas)


# ---------------------------------------------------------------- iconos

def circulo(glifo, d=120, relleno=VERDE):
    r = d / 2
    return svg(f'<circle cx="{r}" cy="{r}" r="{r}" fill="{relleno}"/>{glifo}', d, d)


T = dict(stroke=CREMA, fill="none")


def trazo(d, color=CREMA, ancho=4.2, extra=""):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linecap="round" '
            f'stroke-linejoin="round" {extra}/>')


def icono_taza(color=CREMA):
    return ("".join([
        trazo("M34,52 L34,74 A14,14 0 0 0 48,88 L68,88 A14,14 0 0 0 82,74 L82,52 Z", color),
        trazo("M82,58 A10,10 0 0 1 82,78", color),
        trazo("M28,96 L90,96", color),
        trazo("M48,44 C44,38 52,34 48,28", color, 3.4),
        trazo("M58,42 C54,36 62,32 58,26", color, 3.4),
        trazo("M68,44 C64,38 72,34 68,28", color, 3.4),
    ]))


def icono_croissant(color=CREMA):
    # Relleno y no contorno: la media luna vacía se leía como un paraguas. Las puntas se enroscan y
    # las tres rayas son las capas de la masa.
    cuerpo = ("M22,84 C18,48 38,30 60,30 C82,30 102,48 98,84 C90,64 78,56 60,56 C42,56 30,64 22,84 Z")
    capas = ["M44,37 C40,46 38,52 38,60", "M60,33 L60,56", "M76,37 C80,46 82,52 82,60"]
    return ("".join([
        f'<path d="{cuerpo}" fill="{color}"/>',
        f'<circle cx="26" cy="79" r="6" fill="{color}"/>',
        f'<circle cx="94" cy="79" r="6" fill="{color}"/>',
    ] + [trazo(d, VERDE, 3.4) for d in capas]))


def icono_sandwich(color=CREMA):
    return "".join([
        trazo("M26,46 L60,32 L94,46 L60,60 Z", color),
        trazo("M26,60 L60,74 L94,60", color),
        trazo("M26,74 L60,88 L94,74", color),
    ])


def icono_hoja(color=CREMA):
    return "".join([
        trazo("M30,90 C30,54 54,32 92,30 C92,66 70,90 30,90 Z", color),
        trazo("M34,88 C50,70 68,54 88,36", color, 3.2),
    ])


def icono_grano(color=VERDE):
    return "".join([
        trazo(f"M60,22 C86,34 86,86 60,98 C34,86 34,34 60,22 Z", color, 6),
        trazo("M60,26 C50,46 50,74 60,94", color, 5),
    ])


def icono_hojas(color=VERDE):
    return (hoja(58, 62, 42, 20, -38, color, nervio=False)
            + hoja(54, 70, 38, 18, 18, color, nervio=False)
            + trazo("M24,96 C36,86 46,78 56,70", color, 5.5))


def icono_sillon(color=VERDE):
    return "".join([
        trazo("M30,56 L30,80 L90,80 L90,56", color, 6),
        trazo("M24,56 A8,8 0 0 1 40,56 L40,70 L80,70 L80,56 A8,8 0 0 1 96,56 L96,74", color, 6),
        trazo("M34,80 L34,92 M86,80 L86,92", color, 6),
    ])


def icono_carita(color=VERDE):
    return "".join([
        trazo("M60,20 A40,40 0 1 1 59,20 Z", color, 6),
        trazo("M44,50 L44,56 M76,50 L76,56", color, 7),
        trazo("M42,70 C50,82 70,82 78,70", color, 6),
    ])


def icono_pin(color=CREMA):
    return "".join([
        trazo("M60,98 C60,98 90,66 90,46 A30,30 0 1 0 30,46 C30,66 60,98 60,98 Z", color, 7),
        trazo("M60,34 A12,12 0 1 1 59,34 Z", color, 7),
    ])


def icono_reloj(color=CREMA):
    return "".join([
        trazo("M60,16 A44,44 0 1 1 59,16 Z", color, 7),
        trazo("M60,34 L60,62 L80,72", color, 7),
    ])


def icono_instagram(color=CREMA):
    return "".join([
        trazo("M34,20 L86,20 A14,14 0 0 1 100,34 L100,86 A14,14 0 0 1 86,100 L34,100 A14,14 0 0 1 20,86 "
              "L20,34 A14,14 0 0 1 34,20 Z", color, 7),
        trazo("M60,40 A20,20 0 1 1 59,40 Z", color, 7),
        f'<circle cx="86" cy="34" r="5" fill="{color}"/>',
    ])


def icono_corazon(color=VERDE):
    return trazo("M60,94 C18,66 22,32 44,28 C54,26 60,34 60,40 C60,34 66,26 76,28 C98,32 102,66 60,94 Z",
                 color, 6)


GRANDES = {"taza": icono_taza, "croissant": icono_croissant, "sandwich": icono_sandwich, "hoja": icono_hoja}
CHICOS = {"grano": icono_grano, "hojas": icono_hojas, "sillon": icono_sillon, "carita": icono_carita}
PIE = {"pin": icono_pin, "reloj": icono_reloj, "instagram": icono_instagram}


def piezas():
    p = {}
    for n, f in GRANDES.items():
        p[f"icono-{n}"] = (circulo(f()), 120)
    for n, f in CHICOS.items():
        p[f"marca-{n}"] = (svg(f()), 120)
    for n, f in PIE.items():
        p[f"pie-{n}"] = (svg(f()), 120)
    p["corazon"] = (svg(icono_corazon()), 120)
    p["marca-pin"] = (svg(icono_pin(VERDE)), 120)  # el mismo pin, en verde, para el papel crema
    # Ramas: el viewBox deja aire para las hojas que sobresalen del tallo.
    # Las ramas se dibujan sobre un lienzo holgado y después se recorta el PNG: así ninguna hoja
    # queda cortada por el viewBox y la proporción del archivo es la del dibujo.
    oscuro = (VERDE, "#3C5125", VERDE_MEDIO)
    mata = (f'<g transform="translate(160,275) rotate(-54)">{rama(8, 205, 44, 3.4, oscuro)}</g>'
            f'<g transform="translate(160,275) rotate(-14)">{rama(7, 170, 34, 3.0, oscuro)}</g>'
            f'<g transform="translate(160,275) rotate(-92)">{rama(6, 150, 30, 2.8, oscuro)}</g>'
            f'<g transform="translate(160,275) rotate(-34)">{rama(5, 120, 24, 2.4)}</g>'
            f'<g transform="translate(160,275) rotate(-74)">{rama(5, 110, 22, 2.2)}</g>')
    p["rama-grande"] = (svg(mata, 300, 300), 300)
    p["rama-chica"] = (svg(f'<g transform="translate(20,150) rotate(-22)">{rama(5, 120, 24, 2.0)}</g>',
                           220, 180), 180)
    p["rama-pie"] = (svg(f'<g transform="translate(20,40) rotate(20)">{rama(6, 160, 30, 2.4)}</g>'
                         f'<g transform="translate(20,40) rotate(56)">{rama(5, 120, 24, 2.0)}</g>',
                         240, 200), 200)
    p["ramita-sello"] = (svg(f'<g transform="translate(20,110) rotate(-30)">'
                             f'{rama(6, 110, 22, 1.0, (CREMA, CREMA, CREMA))}</g>', 160, 140), 140)
    return p


def main():
    try:
        import cairosvg
    except ImportError:
        sys.exit("falta cairosvg: pip install cairosvg")
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "svg").mkdir(exist_ok=True)
    for nombre, (texto, alto_vb) in piezas().items():
        (SALIDA / "svg" / f"{nombre}.svg").write_text(texto, encoding="utf-8")
        destino = SALIDA / f"{nombre}.png"
        cairosvg.svg2png(bytestring=texto.encode(), write_to=str(destino),
                         output_height=600 if not nombre.startswith(("rama", "ramita")) else 1400,
                         background_color=None)
        if nombre.startswith(("rama", "ramita")):  # recortar el aire que deja el lienzo holgado
            from PIL import Image
            im = Image.open(destino)
            caja = im.getchannel("A").getbbox()
            if caja:
                im.crop(caja).save(destino)
    print(f"{len(piezas())} gráficas en {SALIDA.relative_to(RAIZ)} (PNG de 600 px + SVG)")


if __name__ == "__main__":
    main()
