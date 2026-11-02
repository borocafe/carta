#!/usr/bin/env python3
"""
Arma el flyer de Boró Café, de 14 x 20 cm.

Uso:
    python3 herramientas/flyer.py          # pptx + pdf + png
    python3 herramientas/flyer.py pptx     # solo el editable
    python3 herramientas/flyer.py pdf      # solo el de imprenta

Escribe en flyer/:
    Flyer Boro Cafe.pptx   el editable. Canva lo importa dejando cada texto como caja de texto y cada
                           imagen como elemento aparte; también abre en Keynote, Slides y PowerPoint.
                           (El PDF entra a Canva con el texto más frágil y el SVG entra aplanado.)
    flyer-boro.pdf         el de imprenta: texto vectorial, fotos a 300 ppi.
    flyer-boro.png         300 ppi, para mirarlo o mandarlo por WhatsApp.

Una sola maqueta, dos salidas: `maqueta()` devuelve la lista de elementos (rectángulos, líneas, fotos
y textos, todo en milímetros) y `a_pptx` y `a_html` la dibujan. Así el editable y el de imprenta no se
separan. Las métricas de texto de PowerPoint y de Chrome no son idénticas, así que puede haber medio
milímetro de diferencia entre los dos; manda el PDF.

Texto y precios: CONTENIDO. Tipografías: Cormorant Garamond y Jost (las de la carta) y Kaushan Script
para los dos rótulos a mano; las tres son de Google Fonts, están en Canva y quedaron en
flyer/tipografias/ por si hay que instalarlas en el computador.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FLYER = RAIZ / "flyer"
GRAF = FLYER / "graficas"
FOTOS = FLYER / "fotos"
RECORTES = FOTOS / "recortes"
PPTX = FLYER / "Flyer Boro Cafe.pptx"
PDF = FLYER / "flyer-boro.pdf"
PNG = FLYER / "flyer-boro.png"

ANCHO, ALTO = 140.0, 200.0  # mm

# Colores medidos sobre el flyer original.
PAPEL = "F7F5E3"
VERDE = "314520"
TINTA_VERDE = "2A3A1C"
PANEL = "CDD9B3"
PANEL_SUAVE = "E0E5D0"
ROJO = "8B2D0A"
TINTA = "2B2B26"
CREMA = "F7F5E3"
LINEA = "9AA886"

# El original usa una serif con cuerpo (tipo Times/PT Serif), una sans humanista y una script de pincel
# gruesa. Con Cormorant y Jost —las de la carta— el flyer quedaba pálido y aireado: un flyer de promos
# necesita peso. Las tres son de Google Fonts y están en Canva.
SERIF = "PT Serif"
SANS = "Lato"
MANO = "Pacifico"

CONTENIDO = {
    "direccion_cabeza": "LOS LEONES ESQ. TRANQUILA\nPROVIDENCIA, SANTIAGO",
    "promo_horario": "De lunes a viernes, 8:00 a 11:00",
    "promos": [
        ("Tu café a ", "2.500",
         "con cualquier compra de salados o dulces\npide un café ristretto, espresso,\namericano o lungo."),
        ("Tu café con leche a ", "3.000",
         "con cualquier compra de salados o dulces, pide tu café\nmocaccino, cappuccino, latte o flat white.\n"
         "Si lo quieres con leche de avena, son *300* pesos adicionales."),
    ],
    "titular": "Tu café de\ncada día",
    "bajada": ("Un lugar acogedor, moderno y natural,\npara disfrutar solo o en buena compañía.\n"
               "Ideal para trabajar, leer, compartir\no simplemente darte un gusto."),
    "iconos": [("taza", "CAFÉ DE\nESPECIALIDAD"), ("croissant", "PASTELERÍA\nARTESANAL"),
               ("sandwich", "SÁNDWICHES\nY SALADOS"), ("hoja", "PRODUCTOS\nDE CALIDAD")],
    "combos_titulo": "NUESTROS COMBOS",
    "combos": [
        ("Desayuno Liviano", "4.900",
         "*Café* (+ leche, 500 pesos adicionales;\n+ leche de avena, 800 pesos adicionales)\n"
         "+ yogurt con granola y frutos rojos."),
        ("Brunch", "11.900",
         "*Café* (+ leche, 500 pesos adicionales;\n+ leche de avena, 800 pesos adicionales)\n"
         "+ *jugo de naranja* + croissant jamón queso\n+ dulce chico (palmera, rollo de canela,\n"
         "media luna, queque o galleta chocochips)."),
        ("Almuerzo + Bebestible", "7.900", "Cualquier almuerzo o wrap + bebida."),
        ("Once de Barrio", "4.900",
         "*Café* (+ leche, 500 pesos adicionales;\n+ leche de avena, 800 pesos adicionales)\n"
         "+ dulce chico (palmera, rollo de canela,\nmedia luna, queque o galleta chocochips)."),
    ],
    "sello": "Pan de\nmasa madre\npara llevar",
    "marcas": [("sillon", "AMBIENTE\nACOGEDOR"), ("carita", "TE ESPERAMOS"),
               ("grano", "CAFÉ DE\nESPECIALIDAD"), ("hojas", "INGREDIENTES\nDE CALIDAD")],
    "pie_direccion": "LOS LEONES ESQ. TRANQUILA\nPROVIDENCIA",
    "pie_horario": "De lunes a viernes\n8:00 a 20:30 hrs\nSábado y domingo\n10:00 a 20:30 hrs",
    "pie_instagram": "@borocafe.cl",
    "pie_qr": "NUESTRA CARTA",
    "pie_tira": "CAFÉ  /  PASTELERÍA  /  SÁNDWICHES  /  BRUNCH  /  PRODUCTOS DE CALIDAD",
}


# ---------------------------------------------------------------- piezas de la maqueta

def rect(x, y, w, h, color, redondeo=0):
    return dict(tipo="rect", x=x, y=y, w=w, h=h, color=color, redondeo=redondeo)


def disco(x, y, d, color):
    return dict(tipo="disco", x=x, y=y, w=d, h=d, color=color)


def linea(x, y, w=0, h=0, color=LINEA, grosor=0.75):
    return dict(tipo="linea", x=x, y=y, w=w, h=h, color=color, grosor=grosor)


def imagen(archivo, x, y, w, h):
    return dict(tipo="foto", archivo=Path(archivo), x=x, y=y, w=w, h=h)


def texto(x, y, w, h, lineas, alineacion="izq", interlineado=1.15, rotacion=0):
    """lineas: lista de párrafos; cada párrafo es una lista de (texto, estilo)."""
    return dict(tipo="texto", x=x, y=y, w=w, h=h, lineas=lineas, alineacion=alineacion,
                interlineado=interlineado, rotacion=rotacion)


def estilo(fuente=SANS, tam=10, color=TINTA, negrita=False, cursiva=False, espaciado=0):
    return dict(fuente=fuente, tam=tam, color=color, negrita=negrita, cursiva=cursiva, espaciado=espaciado)


ARCHIVOS_FUENTE = {(SERIF, True): "PTSerif-700.ttf", (SERIF, False): "PTSerif-400.ttf",
                   (SANS, True): "Lato-700.ttf", (SANS, False): "Lato-400.ttf",
                   (MANO, False): "Pacifico-400.ttf"}


def ancho_mm(texto, fuente, tam, negrita=False):
    from PIL import ImageFont
    archivo = FLYER / "tipografias" / ARCHIVOS_FUENTE[(fuente, negrita)]
    f = ImageFont.truetype(str(archivo), 1000)
    return f.getlength(texto) / 1000 * tam * 25.4 / 72


def achicar(texto, fuente, tam, cabe_en, negrita=False, minimo=11):
    """Baja el cuerpo hasta que el texto entre en una línea: los nombres de los combos los escribe
    el local y uno largo, partido en dos, se montaba con el detalle."""
    while tam > minimo and ancho_mm(texto, fuente, tam, negrita) > cabe_en:
        tam -= 0.25
    return tam


def parrafos(cadena, est):
    """Un párrafo por salto de línea. Lo que va entre *asteriscos* sale en negrita, como en el original,
    donde «Café» y «jugo de naranja» están resaltados dentro del detalle."""
    fuerte = dict(est, negrita=True)
    salida = []
    for linea in cadena.split("\n"):
        tramos = [(t, fuerte if i % 2 else est) for i, t in enumerate(linea.split("*")) if t]
        salida.append(tramos or [("", est)])
    return salida


# ---------------------------------------------------------------- la maqueta

# Una grilla explícita en vez de coordenadas sueltas: margen parejo de 5 mm, dos columnas con la misma
# canal, y los bloques separados siempre por el mismo aire. Antes cada bloque caía donde fuera y se
# notaba: paneles que no alineaban con las fotos, sangrados distintos, huecos de 0,3 y de 3 mm.
MARGEN = 5.0
IZQ_X, IZQ_W = 5.0, 56.0      # columna izquierda: sello, titular, bajada e iconos
DER_X, DER_W = 65.0, 70.0     # columna derecha: panel de promos y fotos (canal de 4 mm)
PADDING = 4.0                 # margen interno de los paneles

PROMO_Y, PROMO_H = 4.0, 44.0
FOTO1_Y, FOTO1_H = 50.0, 29.0
FOTO2_Y, FOTO2_H = 80.5, 25.0
COMBOS_Y, COMBOS_H = 107.5, 53.0
FRANJA_Y, FRANJA_H = 162.0, 17.5
BARRA_Y, BARRA_H = 180.5, 16.0

RECUADROS = {
    "cafe": dict(archivo="cafe-s41.png", x=DER_X, y=FOTO1_Y, w=DER_W, h=FOTO1_H),
    "croissant": dict(archivo="croissant-s41.png", x=DER_X, y=FOTO2_Y, w=DER_W, h=FOTO2_H),
    "frio": dict(archivo="frio-s41.png", x=MARGEN, y=FRANJA_Y, w=42, h=FRANJA_H, zoom=1.5, foco=0.74),
}


def maqueta():
    e = [rect(0, 0, ANCHO, ALTO, PAPEL), imagen(GRAF / "rama-grande.png", -9, -7, 47, 49)]

    # ---- sello y dirección, centrados en la columna izquierda
    centro = IZQ_X + IZQ_W / 2
    e += [disco(centro - 18.6, 2.9, 37.2, PAPEL),
          imagen(GRAF / "logo.png", centro - 20, 1.5, 40, 40),
          imagen(GRAF / "marca-pin.png", IZQ_X, 42.9, 4.2, 4.2),
          texto(IZQ_X + 5.4, 42.7, IZQ_W - 5.4, 9,
                parrafos(CONTENIDO["direccion_cabeza"],
                         estilo(SANS, 7, TINTA_VERDE, negrita=True, espaciado=0.2)), interlineado=1.3)]

    # ---- panel de promos
    tx, tw = DER_X + PADDING, DER_W - 2 * PADDING
    e += [rect(DER_X, PROMO_Y, DER_W, PROMO_H, PANEL, redondeo=3),
          imagen(GRAF / "rama-chica.png", DER_X + DER_W - 13, PROMO_Y - 3.4, 18, 9),
          texto(tx, PROMO_Y + 2.2, tw, 5, parrafos(CONTENIDO["promo_horario"],
                estilo(SERIF, 9, TINTA_VERDE, negrita=True, espaciado=0.4)))]
    tope = PROMO_Y + 6.8
    for i, (nombre, precio, detalle) in enumerate(CONTENIDO["promos"]):
        tam = 19 if i == 0 else 14.7
        e += [texto(tx, tope, tw, 9, [[(nombre, estilo(SERIF, tam, TINTA_VERDE, negrita=True)),
                                       (precio, estilo(SERIF, tam, ROJO, negrita=True))]], interlineado=1.0),
              texto(tx, tope + (7.1 if i == 0 else 5.6), tw, 13,
                    parrafos(detalle, estilo(SERIF, 7, TINTA, cursiva=True)), interlineado=1.3)]
        if i == 0:
            e.append(linea(tx, 28.6, w=tw))
            tope = 29.8

    # ---- titular, bajada e iconos
    e += [texto(IZQ_X, 50.6, IZQ_W, 20, parrafos(CONTENIDO["titular"], estilo(MANO, 22, TINTA_VERDE)),
                interlineado=1.2),
          imagen(GRAF / "corazon.png", IZQ_X + 27, 61.4, 5.2, 5.2),
          texto(IZQ_X, 71.4, IZQ_W, 17, parrafos(CONTENIDO["bajada"], estilo(SANS, 8.2, TINTA)),
                interlineado=1.4)]
    paso, lado = IZQ_W / 4, 11.5
    for i, (icono, rotulo) in enumerate(CONTENIDO["iconos"]):
        medio = IZQ_X + paso * i + paso / 2
        e += [imagen(GRAF / f"icono-{icono}.png", medio - lado / 2, 89.5, lado, lado),
              texto(medio - 8.5, 102.0, 17, 8,
                    parrafos(rotulo, estilo(SANS, 5.6, TINTA_VERDE, negrita=True, espaciado=0.15)),
                    alineacion="centro", interlineado=1.2)]

    # ---- combos: dos columnas iguales dentro del panel
    col_w = (ANCHO - 2 * MARGEN - 2 * PADDING - 2.5) / 2
    col_x = [MARGEN + PADDING, MARGEN + PADDING + col_w + 2.5]
    medio_x = col_x[1] - 1.25
    e += [rect(MARGEN, COMBOS_Y, ANCHO - 2 * MARGEN, COMBOS_H, PANEL_SUAVE, redondeo=3),
          texto(MARGEN, COMBOS_Y + 2.1, ANCHO - 2 * MARGEN, 11,
                parrafos(CONTENIDO["combos_titulo"],
                         estilo(SERIF, 25, TINTA_VERDE, negrita=True, espaciado=0.8)), alineacion="centro"),
          linea(medio_x, COMBOS_Y + 11.5, h=COMBOS_H - 13.5, grosor=0.9),
          linea(col_x[0], 140.6, w=col_w * 2 + 2.5, grosor=0.9)]
    for i, (nombre, precio, detalle) in enumerate(CONTENIDO["combos"]):
        x = col_x[i % 2]
        y = 119.4 if i < 2 else 141.7
        ancho_precio = 14.0
        e += [texto(x, y, col_w - ancho_precio, 7,
                    [[(nombre, estilo(SERIF, 12, TINTA_VERDE, negrita=True))]], interlineado=1.0),
              texto(x + col_w - ancho_precio, y, ancho_precio, 7,
                    [[(precio, estilo(SERIF, 12, ROJO, negrita=True))]], alineacion="der", interlineado=1.0),
              texto(x, y + 5.4, col_w, 18, parrafos(detalle, estilo(SANS, 7, TINTA)), interlineado=1.22)]

    # ---- franja: foto fría, sello de pan y las cuatro marcas
    sello_x, sello_w = 49.5, 37.0
    e += [rect(sello_x, FRANJA_Y, sello_w, FRANJA_H, VERDE, redondeo=2),
          texto(sello_x + 1, FRANJA_Y + 1.8, sello_w - 2, 16,
                parrafos(CONTENIDO["sello"], estilo(MANO, 10.5, CREMA)),
                alineacion="centro", interlineado=1.25),
          imagen(GRAF / "ramita-sello.png", sello_x + 27, FRANJA_Y + 10.8, 9, 4.6)]
    for i, (icono, rotulo) in enumerate(CONTENIDO["marcas"]):
        x = 89 + (i // 2) * 23
        y = FRANJA_Y + 0.5 + (i % 2) * 7.7
        e += [imagen(GRAF / f"marca-{icono}.png", x, y, 5.2, 5.2),
              texto(x + 6, y + 0.3, 17, 7,
                    parrafos(rotulo, estilo(SANS, 5.4, TINTA_VERDE, negrita=True, espaciado=0.15)),
                    interlineado=1.2)]

    # ---- barra verde
    by = BARRA_Y
    e += [rect(MARGEN, by, ANCHO - 2 * MARGEN, BARRA_H, VERDE, redondeo=2),
          imagen(GRAF / "pie-pin.png", 9, by + 3.4, 4.4, 4.4),
          texto(14.6, by + 3.3, 34, 8, parrafos(CONTENIDO["pie_direccion"],
                estilo(SANS, 6, CREMA, negrita=True, espaciado=0.15)), interlineado=1.25),
          linea(50, by + 2.2, h=8.5, color=CREMA, grosor=0.5),
          imagen(GRAF / "pie-reloj.png", 53.5, by + 3.4, 4.4, 4.4),
          texto(59.2, by + 1.3, 27, 11, parrafos(CONTENIDO["pie_horario"], estilo(SANS, 5.6, CREMA)),
                interlineado=1.2),
          linea(86, by + 2.2, h=8.5, color=CREMA, grosor=0.5),
          imagen(GRAF / "pie-instagram.png", 89.5, by + 3.8, 4.4, 4.4),
          texto(95.3, by + 4.1, 24, 5, parrafos(CONTENIDO["pie_instagram"], estilo(SANS, 8, CREMA))),
          texto(MARGEN, by + 11.7, 107, 5,
                parrafos(CONTENIDO["pie_tira"], estilo(SANS, 6, CREMA, espaciado=0.4)),
                alineacion="centro"),
          rect(112.5, 175.5, 22.5, 21, CREMA, redondeo=1.5),
          imagen(RAIZ / "qr" / "qr-carta.png", 115.7, 176.8, 16.1, 16.1),
          texto(112.5, 193.5, 22.5, 4, parrafos(CONTENIDO["pie_qr"],
                estilo(SANS, 5.2, TINTA_VERDE, negrita=True, espaciado=0.4)), alineacion="centro")]

    # fotos al final, y sobre ellas las hojas de la esquina de abajo
    for r in RECUADROS.values():
        e.append(imagen(recortar(r["archivo"], r["w"], r["h"], r.get("zoom", 1.0), r.get("foco", 0.5)),
                        r["x"], r["y"], r["w"], r["h"]))
    e.append(imagen(GRAF / "rama-pie.png", -9, 151, 26, 20))
    return e


def recortar(archivo, w_mm, h_mm, zoom=1.0, foco=0.5, ppp=300):
    """Recorta la foto con la proporción del recuadro y la deja a 300 ppi."""
    from PIL import Image
    RECORTES.mkdir(parents=True, exist_ok=True)
    destino = RECORTES / archivo
    im = Image.open(FOTOS / archivo).convert("RGB")
    if zoom > 1:  # acercar sobre un punto del ancho antes de ajustar la proporción
        w0, h0 = im.size
        ancho, alto = int(w0 / zoom), int(h0 / zoom)
        izq = min(max(int(w0 * foco - ancho / 2), 0), w0 - ancho)
        arriba = (h0 - alto) // 2
        im = im.crop((izq, arriba, izq + ancho, arriba + alto))
    objetivo, (w, h) = w_mm / h_mm, im.size
    if w / h > objetivo:
        nuevo = int(h * objetivo)
        im = im.crop(((w - nuevo) // 2, 0, (w - nuevo) // 2 + nuevo, h))
    else:
        nuevo = int(w / objetivo)
        im = im.crop((0, (h - nuevo) // 2, w, (h - nuevo) // 2 + nuevo))
    pedido = (round(w_mm / 25.4 * ppp), round(h_mm / 25.4 * ppp))
    if im.size[0] > pedido[0]:
        im = im.resize(pedido, Image.LANCZOS)
    im.save(destino, quality=95)
    return destino


# ---------------------------------------------------------------- salida editable

def a_pptx(elementos, destino=PPTX):
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Mm, Pt

    ALIN = {"izq": PP_ALIGN.LEFT, "centro": PP_ALIGN.CENTER, "der": PP_ALIGN.RIGHT}
    col = lambda c: RGBColor.from_string(c)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Mm(ANCHO), Mm(ALTO)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    for el in elementos:
        if el["tipo"] in ("rect", "disco"):
            if el["tipo"] == "disco":
                forma = MSO_SHAPE.OVAL
            else:
                forma = MSO_SHAPE.ROUNDED_RECTANGLE if el["redondeo"] else MSO_SHAPE.RECTANGLE
            s = slide.shapes.add_shape(forma, Mm(el["x"]), Mm(el["y"]), Mm(el["w"]), Mm(el["h"]))
            if el["tipo"] == "rect" and el["redondeo"]:
                s.adjustments[0] = el["redondeo"] / min(el["w"], el["h"])
            s.fill.solid()
            s.fill.fore_color.rgb = col(el["color"])
            s.line.fill.background()
            s.shadow.inherit = False
        elif el["tipo"] == "linea":
            s = slide.shapes.add_connector(1, Mm(el["x"]), Mm(el["y"]),
                                           Mm(el["x"] + el["w"]), Mm(el["y"] + el["h"]))
            s.line.color.rgb = col(el["color"])
            s.line.width = Pt(el["grosor"])
        elif el["tipo"] == "foto":
            slide.shapes.add_picture(str(el["archivo"]), Mm(el["x"]), Mm(el["y"]), Mm(el["w"]), Mm(el["h"]))
        else:
            c = slide.shapes.add_textbox(Mm(el["x"]), Mm(el["y"]), Mm(el["w"]), Mm(el["h"]))
            tf = c.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            for i, parrafo in enumerate(el["lineas"]):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.alignment = ALIN[el["alineacion"]]
                p.line_spacing = el["interlineado"]
                for txt, est in parrafo:
                    r = p.add_run()
                    r.text = txt
                    r.font.name = est["fuente"]
                    r.font.size = Pt(est["tam"])
                    r.font.bold = est["negrita"]
                    r.font.italic = est["cursiva"]
                    r.font.color.rgb = col(est["color"])
                    if est["espaciado"]:
                        r.font._rPr.set("spc", str(int(est["espaciado"] * 100)))
            if el["rotacion"]:
                c.rotation = el["rotacion"]
    destino.parent.mkdir(parents=True, exist_ok=True)
    prs.save(destino)
    print(f"escrito: {destino.relative_to(RAIZ)}")
    return destino


# ---------------------------------------------------------------- salida de imprenta

def a_html(elementos, destino):
    ALIN = {"izq": "left", "centro": "center", "der": "right"}
    caras = [("PT Serif", "PTSerif-400.ttf", 400, "normal"),
             ("PT Serif", "PTSerif-400Italic.ttf", 400, "italic"),
             ("PT Serif", "PTSerif-700.ttf", 700, "normal"),
             ("PT Serif", "PTSerif-700Italic.ttf", 700, "italic"),
             ("Lato", "Lato-400.ttf", 400, "normal"),
             ("Lato", "Lato-400Italic.ttf", 400, "italic"),
             ("Lato", "Lato-700.ttf", 700, "normal"),
             ("Pacifico", "Pacifico-400.ttf", 400, "normal")]
    fuentes = "\n".join(
        f"@font-face{{font-family:'{f}';src:url('tipografias/{a}') format('truetype');"
        f"font-weight:{p};font-style:{e}}}" for f, a, p, e in caras)
    partes = []
    for el in elementos:
        pos = f"left:{el['x']}mm;top:{el['y']}mm"
        if el["tipo"] in ("rect", "disco"):
            radio = ";border-radius:50%" if el["tipo"] == "disco" else (
                f";border-radius:{el['redondeo']}mm" if el["redondeo"] else "")
            partes.append(f"<div class='p' style=\"{pos};width:{el['w']}mm;height:{el['h']}mm;"
                          f"background:#{el['color']}{radio}\"></div>")
        elif el["tipo"] == "linea":
            if el["h"]:
                partes.append(f"<div class='p' style=\"{pos};width:0;height:{el['h']}mm;"
                              f"border-left:{el['grosor']}pt solid #{el['color']}\"></div>")
            else:
                partes.append(f"<div class='p' style=\"{pos};width:{el['w']}mm;height:0;"
                              f"border-top:{el['grosor']}pt solid #{el['color']}\"></div>")
        elif el["tipo"] == "foto":
            ruta = os.path.relpath(el["archivo"].resolve(), FLYER.resolve())  # el html vive en flyer/
            partes.append(f"<img class='p' style=\"{pos};width:{el['w']}mm;height:{el['h']}mm\" "
                          f"src='{ruta}'>")
        else:
            giro = f";transform:rotate({el['rotacion']}deg);transform-origin:0 0" if el["rotacion"] else ""
            cuerpo = []
            for parrafo in el["lineas"]:
                tramos = []
                mayor = max(e["tam"] for _, e in parrafo)  # el strut del párrafo manda sobre el interlineado
                for txt, est in parrafo:
                    css = (f"font-family:'{est['fuente']}';font-size:{est['tam']}pt;color:#{est['color']}"
                           f";font-weight:{700 if est['negrita'] else 400}"
                           f";font-style:{'italic' if est['cursiva'] else 'normal'}")
                    if est["espaciado"]:
                        css += f";letter-spacing:{est['espaciado']}pt"
                    tramos.append(f"<span style=\"{css}\">{txt or '&nbsp;'}</span>")
                cuerpo.append(f"<p style=\"font-size:{mayor}pt\">{''.join(tramos)}</p>")
            partes.append(f"<div class='p t' style=\"{pos};width:{el['w']}mm;height:{el['h']}mm;"
                          f"text-align:{ALIN[el['alineacion']]};line-height:{el['interlineado']}{giro}\">"
                          f"{''.join(cuerpo)}</div>")
    html = f"""<!doctype html><meta charset="utf-8"><title>Flyer Boró Café</title>
<style>
{fuentes}
@page{{size:{ANCHO}mm {ALTO}mm; margin:0}}
*{{-webkit-print-color-adjust:exact; print-color-adjust:exact}}
html,body{{margin:0; padding:0; background:#{PAPEL}}}
.hoja{{position:relative; width:{ANCHO}mm; height:{ALTO}mm; overflow:hidden}}
.p{{position:absolute}}
.t p{{margin:0}}
img.p{{display:block; object-fit:cover}}
</style>
<div class="hoja">
{chr(10).join(partes)}
</div>
"""
    destino.write_text(html, encoding="utf-8")
    return destino


def a_pdf(elementos):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from carta_pdf import buscar_chrome, servir

    html = a_html(elementos, FLYER / "flyer-boro.html")
    servidor, puerto = servir(RAIZ)  # el qr vive fuera de flyer/
    try:
        subprocess.run([buscar_chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                        f"--print-to-pdf={PDF}", "--virtual-time-budget=20000",
                        f"http://127.0.0.1:{puerto}/flyer/{html.name}"],
                       check=True, capture_output=True, text=True, timeout=180)
    finally:
        servidor.shutdown()
    print(f"escrito: {PDF.relative_to(RAIZ)} ({PDF.stat().st_size // 1024} KB)")
    subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile", str(PDF), str(PNG.with_suffix(""))],
                   check=True, capture_output=True)
    print(f"escrito: {PNG.relative_to(RAIZ)} ({PNG.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    que = sys.argv[1] if len(sys.argv) > 1 else "todo"
    elems = maqueta()
    if que in ("todo", "pptx"):
        a_pptx(elems)
    if que in ("todo", "pdf"):
        a_pdf(elems)
