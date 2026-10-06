#!/usr/bin/env python3
"""
Imprime la carta publicada a PDF: docs/carta.pdf

Usa Chrome sin interfaz sobre el mismo docs/index.html que se publica, así el PDF y la web nunca se
separan: lo que manda es el bloque @media print de fuente/carta.html.

Uso (después de armar_sitio.py):
    python3 herramientas/carta_pdf.py

Chrome se busca solo (macOS y los runners de GitHub lo traen). Se puede forzar con la variable CHROME.
La página se sirve por http en un puerto local: con file:// Chrome a veces no espera las fuentes.
"""
import os
import shutil
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITIO = RAIZ / "docs"
SALIDA = SITIO / "carta.pdf"

CANDIDATOS = [
    os.environ.get("CHROME"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
]


def buscar_chrome():
    for c in CANDIDATOS:
        if not c:
            continue
        ruta = c if Path(c).is_file() else shutil.which(c)
        if ruta:
            return ruta
    sys.exit("No encontré Chrome ni Chromium para imprimir el PDF. Instálalo o define la variable CHROME.")


def servir():
    """Sirve docs/ en un puerto libre, en segundo plano."""
    class Mudo(SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = partial(Mudo, directory=str(SITIO))
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor, servidor.server_address[1]


def main():
    if not (SITIO / "index.html").exists():
        sys.exit("Falta docs/index.html: corre antes herramientas/armar_sitio.py")
    chrome = buscar_chrome()
    servidor, puerto = servir()
    try:
        subprocess.run([
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",  # Chrome viejo
            f"--print-to-pdf={SALIDA}",
            "--virtual-time-budget=20000",  # que alcancen a llegar las tipografías de Google
            f"http://127.0.0.1:{puerto}/index.html",
        ], check=True, capture_output=True, text=True, timeout=180)
    except subprocess.CalledProcessError as e:
        sys.exit(f"Chrome no pudo imprimir la carta:\n{e.stderr.strip()}")
    finally:
        servidor.shutdown()

    if not SALIDA.exists() or SALIDA.stat().st_size < 10_000:
        sys.exit("El PDF salió vacío o no se escribió.")
    datos = SALIDA.read_bytes()
    paginas = datos.count(b"/Type /Page") - datos.count(b"/Type /Pages")
    print(f"escrito: {SALIDA.relative_to(RAIZ)} ({SALIDA.stat().st_size // 1024} KB, {paginas} páginas)")


if __name__ == "__main__":
    main()
