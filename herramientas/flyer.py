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

SERIF = "Cormorant Garamond"
SANS = "Jost"
MANO = "Kaushan Script"

CONTENIDO = {
    "direccion_cabeza": "LOS LEONES ESQ. TRANQUILA\nPROVIDENCIA, SANTIAGO",
    "promo_horario": "De lunes a viernes, 8:00 a 11:00",
    "promos": [
        ("Tu café a ", "2.500",
         "con cualquier compra de salados o dulces\npide un café ristretto, espresso,\namericano o lungo."),
        ("Tu café con leche a ", "3.000",
         "con cualquier compra de salados o dulces, pide tu café\nmocaccino, cappuccino, latte o flat white.\n"
         "Si lo quieres con leche de avena, son 300 pesos adicionales."),
    ],
    "titular": "Tu café de\ncada día",
    "bajada": ("Un lugar acogedor, moderno y natural,\npara disfrutar solo o en buena compañía.\n"
               "Ideal para trabajar, leer, compartir\no simplemente darte un gusto."),
    "iconos": [("taza", "CAFÉ DE\nESPECIALIDAD"), ("croissant", "PASTELERÍA\nARTESANAL"),
               ("sandwich", "SÁNDWICHES\nY SALADOS"), ("hoja", "PRODUCTOS\nDE CALIDAD")],
    "combos_titulo": "NUESTROS COMBOS",
    "combos": [
        ("Desayuno Liviano", "4.900",
         "Café (+ leche, 500 pesos adicionales;\n+ leche de avena, 800 pesos adicionales)\n"
         "+ yogurt con granola y frutos rojos."),
        ("Brunch", "11.900",
         "Café (+ leche, 500 pesos adicionales;\n+ leche de avena, 800 pesos adicionales)\n"
         "+ jugo de naranja + croissant jamón queso\n+ dulce chico (palmera, rollo de canela,\n"
         "media luna, queque o galleta chocochips)."),
        ("Almuerzo + Bebestible", "7.900", "Cualquier almuerzo o wrap + bebida."),
        ("Once de Barrio", "4.900",
         "Café (+ leche, 500 pesos adicionales;\n+ leche de avena, 800 pesos adicionales)\n"
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

# Recuadro de cada foto en mm; el recorte al centro se hace al armar.
RECUADROS = {
    "cafe": ("cafe-s2380.png", 66, 50.5, 69, 28.5),
    "croissant": ("croissant-s2380.png", 66, 80, 69, 25),
    "frio": ("frio-s7.png", 5, 161.3, 42, 18.4),
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


ARCHIVOS_FUENTE = {(SERIF, True): "CormorantGaramond-700.ttf", (SERIF, False): "CormorantGaramond-400.ttf",
                   (SANS, True): "Jost-600.ttf", (SANS, False): "Jost-400.ttf",
                   (MANO, False): "KaushanScript-400.ttf"}


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
    """Un párrafo por salto de línea, todos con el mismo estilo."""
    return [[(l, est)] for l in cadena.split("\n")]


# ---------------------------------------------------------------- la maqueta

def maqueta():
    e = [rect(0, 0, ANCHO, ALTO, PAPEL)]

    # hojas de las esquinas
    e.append(imagen(GRAF / "rama-grande.png", -9, -7, 47, 49))

    # sello y dirección
    e += [disco(16.3, 2.8, 39.4, PAPEL),
          imagen(GRAF / "logo.png", 15, 1.5, 42, 42),
          imagen(GRAF / "marca-pin.png", 15.2, 41.6, 4.2, 4.2),
          texto(20.6, 41.4, 42, 9, parrafos(CONTENIDO["direccion_cabeza"],
                                            estilo(SANS, 7, TINTA_VERDE, negrita=True)), interlineado=1.2)]

    # panel de promos
    e += [rect(60, 3, 76, 46, PANEL, redondeo=3),
          imagen(GRAF / "rama-chica.png", 115, 4, 22, 11),
          texto(63.5, 5.4, 62, 5, parrafos(CONTENIDO["promo_horario"],
                                           estilo(SERIF, 10.5, TINTA_VERDE, negrita=True, espaciado=0.6)))]
    tope = 10.0
    for i, (nombre, precio, detalle) in enumerate(CONTENIDO["promos"]):
        tam = 20 if i == 0 else 17.5
        e.append(texto(63.5, tope, 71, 9,
                       [[(nombre, estilo(SERIF, tam, TINTA_VERDE, negrita=True)),
                         (precio, estilo(SERIF, tam, ROJO, negrita=True))]], interlineado=1.0))
        e.append(texto(63.5, tope + (7.8 if i == 0 else 7.2), 71, 13,
                       parrafos(detalle, estilo(SERIF, 9, TINTA, cursiva=True)), interlineado=1.12))
        if i == 0:
            e.append(linea(63.5, 29.2, w=68))
            tope = 30.6

    # titular, bajada e iconos
    e += [texto(7, 47.5, 58, 18, parrafos(CONTENIDO["titular"], estilo(MANO, 23, TINTA_VERDE)),
                interlineado=1.25),
          imagen(GRAF / "corazon.png", 40.5, 60.8, 5.2, 5.2),
          texto(7, 68.5, 58, 16, parrafos(CONTENIDO["bajada"], estilo(SANS, 8.8, TINTA)), interlineado=1.3)]
    for i, (icono, rotulo) in enumerate(CONTENIDO["iconos"]):
        x = 6.5 + i * 15
        e += [imagen(GRAF / f"icono-{icono}.png", x, 86, 13, 13),
              texto(x - 2.5, 100.5, 18, 8, parrafos(rotulo, estilo(SANS, 6, TINTA_VERDE, negrita=True)),
                    alineacion="centro", interlineado=1.15)]

    # combos
    e += [rect(5, 106, 130, 55, PANEL_SUAVE, redondeo=3),
          texto(5, 107.6, 130, 10, parrafos(CONTENIDO["combos_titulo"],
                                            estilo(SERIF, 23, TINTA_VERDE, negrita=True, espaciado=0.8)),
                alineacion="centro"),
          linea(70.5, 118, h=41), linea(9, 140, w=122)]
    for i, (nombre, precio, detalle) in enumerate(CONTENIDO["combos"]):
        x = 9 + (i % 2) * 62.5
        y = 118.0 if i < 2 else 141.5
        cuerpo = achicar(nombre, SERIF, 15, 43.5, negrita=True)
        e += [texto(x, y + (15 - cuerpo) * 0.12, 44, 7,
                    [[(nombre, estilo(SERIF, cuerpo, TINTA_VERDE, negrita=True))]], interlineado=1.0),
              texto(x + 42, y, 17, 7, [[(precio, estilo(SERIF, 15, ROJO, negrita=True))]],
                    alineacion="der", interlineado=1.0),
              texto(x, y + 5.9, 60, 18, parrafos(detalle, estilo(SANS, 7.2, TINTA)), interlineado=1.2)]

    # franja de abajo
    e += [rect(49, 161.3, 37, 18.4, VERDE, redondeo=2),
          texto(50, 162.8, 35, 16, parrafos(CONTENIDO["sello"], estilo(MANO, 11.5, CREMA)),
                alineacion="centro", interlineado=1.2),
          imagen(GRAF / "ramita-sello.png", 76, 174.2, 9.5, 4.9)]
    for i, (icono, rotulo) in enumerate(CONTENIDO["marcas"]):
        x = 89 + (i // 2) * 23
        y = 162.0 + (i % 2) * 8
        e += [imagen(GRAF / f"marca-{icono}.png", x, y, 5.2, 5.2),
              texto(x + 6, y + 0.3, 17, 7, parrafos(rotulo, estilo(SANS, 5.4, TINTA_VERDE, negrita=True)),
                    interlineado=1.15)]

    # barra verde
    e += [rect(3, 180.5, 134, 16.5, VERDE, redondeo=2),
          imagen(GRAF / "pie-pin.png", 8, 183.4, 4.6, 4.6),
          texto(13.8, 183.5, 35, 8, parrafos(CONTENIDO["pie_direccion"],
                                             estilo(SANS, 6, CREMA, negrita=True)), interlineado=1.2),
          linea(50, 182.6, h=9, color=CREMA, grosor=0.5),
          imagen(GRAF / "pie-reloj.png", 53, 183.4, 4.6, 4.6),
          texto(58.8, 182.1, 27, 11, parrafos(CONTENIDO["pie_horario"], estilo(SANS, 5.8, CREMA)),
                interlineado=1.15),
          linea(86, 182.6, h=9, color=CREMA, grosor=0.5),
          imagen(GRAF / "pie-instagram.png", 89, 183.7, 4.4, 4.4),
          texto(94.8, 184.1, 24, 5, parrafos(CONTENIDO["pie_instagram"], estilo(SANS, 8, CREMA))),
          texto(3, 192.2, 109, 5, parrafos(CONTENIDO["pie_tira"], estilo(SANS, 6, CREMA, espaciado=0.4)),
                alineacion="centro"),
          rect(113, 175, 22, 22, CREMA, redondeo=1.5),
          imagen(RAIZ / "qr" / "qr-carta.png", 115.4, 176.3, 17.2, 17.2),
          texto(113, 193.8, 22, 4, parrafos(CONTENIDO["pie_qr"],
                                              estilo(SANS, 5.2, TINTA_VERDE, negrita=True, espaciado=0.4)),
                alineacion="centro")]

    # fotos al final, y sobre ellas las hojas de la esquina de abajo
    for archivo, x, y, w, h in RECUADROS.values():
        e.append(imagen(recortar(archivo, w, h), x, y, w, h))
    e.append(imagen(GRAF / "rama-pie.png", -8, 152, 34, 25))
    return e


def recortar(archivo, w_mm, h_mm, ppp=300):
    """Recorta la foto al centro con la proporción del recuadro y la deja a 300 ppi."""
    from PIL import Image
    RECORTES.mkdir(parents=True, exist_ok=True)
    destino = RECORTES / archivo
    im = Image.open(FOTOS / archivo).convert("RGB")
    objetivo, (w, h) = w_mm / h_mm, Image.open(FOTOS / archivo).size
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
    caras = [("Cormorant Garamond", "CormorantGaramond-400.ttf", 400, "normal"),
             ("Cormorant Garamond", "CormorantGaramond-400Italic.ttf", 400, "italic"),
             ("Cormorant Garamond", "CormorantGaramond-700.ttf", 700, "normal"),
             ("Cormorant Garamond", "CormorantGaramond-600Italic.ttf", 700, "italic"),
             ("Jost", "Jost-400.ttf", 400, "normal"),
             ("Jost", "Jost-600.ttf", 700, "normal"),
             ("Kaushan Script", "KaushanScript-400.ttf", 400, "normal")]
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
