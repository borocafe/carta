#!/usr/bin/env python3
"""
Genera imágenes para la carta contra el ComfyUI de `win` (FLUX schnell, Apache 2.0).

Uso:
    python3 herramientas/generar.py candidatos     # 3 motivos x 2 estilos -> marca/generadas/

Notas (heredadas del libro infantil y de aurea, verificadas contra la API):
  - schnell corre a cfg=1.0 e IGNORA el prompt negativo: toda la dirección va en positivo.
  - Pedir objetos y composición ("la mitad izquierda es pared lisa"), no cualidades ("minimalista").
  - Techo ~2 MP. Se genera a 1344x784 (proporción de las bandas, ~1,7) y se reduce después.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

B = os.environ.get("COMFY", "https://win.tail8f8496.ts.net:8443")
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "marca" / "generadas"

FOTO = ("Editorial food photograph for a specialty coffee and sourdough bakery menu, shot on 35mm film "
        "with fine natural grain, realistic textures, warm late-morning window light with crisp directional "
        "shadows. Muted earthy palette of cream, warm brown, wheat gold and dark olive green. No text, no logos, "
        "no people. ")
GRABADO = ("Vintage botanical engraving illustration with fine crosshatched ink linework and soft transparent "
           "watercolor washes in cream, warm brown, wheat gold and olive green, printed on aged warm cream paper, "
           "like a nineteenth century natural history plate. No text, no border, no frame, no people. ")

MOTIVOS = {
    "cafe": ("A ceramic cup of cappuccino with a latte art rosetta and a small espresso cup on a saucer sit "
             "in the right third of the frame, with a few roasted coffee beans and a small olive branch beside them. "
             "The left half of the frame is an empty cream plaster tabletop crossed only by long leaf shadows."),
    "masas": ("Three golden laminated croissants with visible flaky layers and one cinnamon roll lie on crinkled "
              "baking paper along the bottom edge of the frame, with a few crumbs and an olive green linen napkin corner. "
              "The upper half of the frame is plain cream linen."),
    "pan": ("A rustic sourdough loaf cut open to show its open airy crumb, dusted with flour, rests on a worn wooden "
            "board in the right half of the frame, with one slice leaning in front and two ears of wheat. "
            "The left half of the frame is a plain cream wall and tabletop in soft shadow."),
}
PAN_V2 = ("A round rustic sourdough boule with a dark blistered caramelized crust, one deep curling ear along its "
          "scoring line and a light dusting of flour sits on a worn wooden board in the right half of the frame. "
          "Next to it lies the other half of a boule cut open, showing an irregular open crumb with large glossy holes. "
          "Two ears of wheat lie beside the board. The left half of the frame is a plain cream wall and tabletop.")
MASAS_V2 = ("Three classic French butter croissants, each with a crescent shape and clearly separated golden "
            "laminated layers, and one cinnamon roll lie in a straight row on crinkled baking paper along the bottom "
            "edge of the frame, with a few flaky crumbs and an olive green linen napkin at the right corner. "
            "The upper half of the frame is plain cream linen.")
ESTILOS = {"foto": FOTO, "grabado": GRABADO}
W, H = 1344, 784


def encolar(etiqueta, prompt, seed):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux1-schnell-fp8.safetensors", "weight_dtype": "fp8_e4m3fn"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5xxl_fp8_e4m3fn.safetensors", "type": "flux"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler",
                                                    "scheduler": "simple", "denoise": 1.0, "model": ["1", 0],
                                                    "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"boro/{etiqueta}", "images": ["8", 0]}},
    }
    req = urllib.request.Request(f"{B}/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))["prompt_id"]
    except urllib.error.HTTPError as e:
        print("RECHAZADO:", etiqueta, e.read().decode()[:600])
        return None


def esperar_y_bajar(pids, limite=1500):
    SALIDA.mkdir(parents=True, exist_ok=True)
    t0, hechos = time.time(), {}
    while time.time() - t0 < limite and len(hechos) < len([p for p in pids.values() if p]):
        time.sleep(8)
        for et, pid in pids.items():
            if et in hechos or not pid:
                continue
            h = json.load(urllib.request.urlopen(f"{B}/history/{pid}", timeout=20))
            if pid not in h:
                continue
            ims = [i for n in h[pid].get("outputs", {}).values() for i in n.get("images", [])]
            if not ims:
                hechos[et] = None
                print(f"[{time.time()-t0:>4.0f}s] {et}: sin imagen ({h[pid]['status'].get('status_str')})", flush=True)
                continue
            im = ims[0]
            destino = SALIDA / f"{et}.png"
            q = f"filename={im['filename']}&subfolder={im['subfolder']}&type={im['type']}"
            urllib.request.urlretrieve(f"{B}/view?{q}", destino)
            hechos[et] = destino
            print(f"[{time.time()-t0:>4.0f}s] {et}: {destino.relative_to(RAIZ)}", flush=True)
    return hechos


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "candidatos"
    pids = {}
    if modo == "candidatos":
        for motivo, escena in MOTIVOS.items():
            for estilo, base in ESTILOS.items():
                et = f"{motivo}-{estilo}"
                pids[et] = encolar(et, base + escena, seed=2380)
                print("encolado", et, pids[et], flush=True)
    elif modo == "rehacer":
        # Segunda tanda: el pan salió como pan de molde y los croissants de la foto, deformes.
        for et, estilo, escena, seed in [
            ("pan-foto-s11", "foto", PAN_V2, 11), ("pan-foto-s23", "foto", PAN_V2, 23),
            ("pan-grabado-s11", "grabado", PAN_V2, 11), ("pan-grabado-s23", "grabado", PAN_V2, 23),
            ("masas-foto-s11", "foto", MASAS_V2, 11), ("masas-foto-s23", "foto", MASAS_V2, 23),
        ]:
            pids[et] = encolar(et, ESTILOS[estilo] + escena, seed=seed)
            print("encolado", et, pids[et], flush=True)
    elif modo == "pan-grabado":
        # Con PAN_V2 el estilo se perdía (salió foto): la escena de mesa y pared empuja a fotografía.
        # Acá el estilo abre y cierra el prompt, y la escena no tiene pared ni mesa.
        escena = ("An engraved illustration of a round rustic sourdough boule with a scored ear and a floured crust, "
                  "drawn with fine ink crosshatching and hatching lines and tinted with pale transparent watercolor "
                  "washes, next to a cut half showing an open holey crumb and two ears of wheat, all resting on nothing "
                  "but plain aged cream paper, placed in the right half of the page, the left half blank paper. "
                  "Visible pen strokes, antique cookbook plate, hand drawn, not a photograph.")
        for seed in (5, 17, 31):
            et = f"pan-grabado-v3-s{seed}"
            pids[et] = encolar(et, GRABADO + escena, seed=seed)
            print("encolado", et, pids[et], flush=True)
    else:
        sys.exit("modo desconocido: " + modo)
    esperar_y_bajar(pids)
