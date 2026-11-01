#!/usr/bin/env python3
"""
Genera las fotos del flyer contra el ComfyUI de `win` (FLUX schnell, Apache 2.0).

Uso:
    python3 herramientas/flyer_fotos.py            # las tres fotos
    python3 herramientas/flyer_fotos.py cafe       # solo una
    SEMILLA=7 python3 herramientas/flyer_fotos.py  # otra tirada

Las del flyer original venían a 155 ppi: se veían blandas impresas. Acá cada foto se pide del tamaño
de su recuadro a 300 ppi y con algo de holgura para recortar. Igual que en `generar.py`: schnell corre
a cfg=1.0 e ignora el prompt negativo, así que toda la dirección va en el positivo, y se piden objetos
y composición, no adjetivos.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

B = os.environ.get("COMFY", "https://win.tail8f8496.ts.net:8443")
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "flyer" / "fotos"
SEMILLA = int(os.environ.get("SEMILLA", "2380"))

# El aire del flyer: mesa de madera clara, follaje verde desenfocado atrás, luz de mañana.
ESTILO = ("Editorial food photograph for a neighbourhood specialty coffee shop, shot on a 50mm lens at f2 "
          "with shallow depth of field and fine natural grain. Warm late-morning daylight from the left with "
          "soft shadows. The subject sits on a honey-coloured wooden table; behind it, out-of-focus green "
          "garden foliage and warm bokeh. Natural colours, cream, wood brown and leaf green. "
          "No text, no logos, no lettering, no people, no hands. ")

FOTOS = {
    # etiqueta: (escena, ancho, alto)  — proporción = la del recuadro en el flyer
    "cafe": (
        "A wide ceramic cappuccino cup in sage green glaze on a matching saucer, seen from a low three quarter "
        "angle, filled to the brim with milk foam poured into a clean latte art rosetta over caramel coloured "
        "crema. The cup is slightly right of centre and fills most of the frame.",
        1216, 768),
    "croissant": (
        "One single golden butter croissant with a crisp blistered crust and clearly separated laminated layers, "
        "lying on a small speckled stoneware plate, seen from a low three quarter angle. The croissant fills "
        "most of the frame and its curved ends point to the corners.",
        1152, 832),
    "frio": (
        "A tall clear plastic cup of iced latte with a black straw, pale caramel coffee layered over ice cubes "
        "and milk swirls, beaded with condensation, standing on the left third of the wooden table. Behind it, "
        "two small terracotta pots with green plants, far out of focus.",
        1216, 768),
}


def encolar(etiqueta, prompt, ancho, alto, semilla):
    wf = {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "flux1-schnell-fp8.safetensors", "weight_dtype": "fp8_e4m3fn"}},
        "2": {"class_type": "DualCLIPLoader",
              "inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                         "type": "flux"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": ancho, "height": alto, "batch_size": 1}},
        "7": {"class_type": "KSampler",
              "inputs": {"seed": semilla, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple",
                         "denoise": 1.0, "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0],
                         "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"boro-flyer/{etiqueta}", "images": ["8", 0]}},
    }
    req = urllib.request.Request(f"{B}/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))["prompt_id"]
    except urllib.error.HTTPError as e:
        print("RECHAZADO:", etiqueta, e.read().decode()[:600])
        return None


def esperar_y_bajar(pids, limite=1200):
    SALIDA.mkdir(parents=True, exist_ok=True)
    t0, hechos = time.time(), {}
    pendientes = [e for e, p in pids.items() if p]
    while time.time() - t0 < limite and len(hechos) < len(pendientes):
        time.sleep(6)
        for et in pendientes:
            if et in hechos:
                continue
            h = json.load(urllib.request.urlopen(f"{B}/history/{pids[et]}", timeout=20))
            if pids[et] not in h:
                continue
            ims = [i for n in h[pids[et]].get("outputs", {}).values() for i in n.get("images", [])]
            if not ims:
                hechos[et] = None
                print(f"[{time.time()-t0:>4.0f}s] {et}: sin imagen", flush=True)
                continue
            im = ims[0]
            destino = SALIDA / f"{et}-s{SEMILLA}.png"
            q = f"filename={im['filename']}&subfolder={im['subfolder']}&type={im['type']}"
            urllib.request.urlretrieve(f"{B}/view?{q}", destino)
            hechos[et] = destino
            print(f"[{time.time()-t0:>4.0f}s] {et}: {destino.relative_to(RAIZ)}", flush=True)
    return hechos


if __name__ == "__main__":
    quiere = sys.argv[1:] or list(FOTOS)
    pids = {}
    for et in quiere:
        if et not in FOTOS:
            sys.exit(f"no conozco la foto «{et}». Hay: {', '.join(FOTOS)}")
        escena, w, h = FOTOS[et]
        pids[et] = encolar(et, ESTILO + escena, w, h, SEMILLA)
        print("encolado", et, f"{w}x{h}", pids[et], flush=True)
    esperar_y_bajar(pids)
