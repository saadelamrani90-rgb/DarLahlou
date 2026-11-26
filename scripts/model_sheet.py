"""Model sheet : face, 3/4, profil, dos + silhouette.
Usage : python scripts/model_sheet.py <personnage> <version>
"""
import importlib
import math
import os
import subprocess
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
char, ver = sys.argv[1], sys.argv[2]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
T.setup_render(scene, w=720, h=1080)
mod = importlib.import_module(f"char_{char}")
root = mod.build()

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.3
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, -10, 0.95)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam

tmp = os.path.join(ROOT, "render", "tests", f"sheet_{char}")
os.makedirs(tmp, exist_ok=True)
views = [("face", 0), ("trois_quarts", 35), ("profil", 90), ("dos", 180)]
paths = []
t0 = time.time()
for name, deg in views:
    root.rotation_euler = (0, 0, math.radians(deg))
    scene.render.filepath = os.path.join(tmp, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    paths.append(scene.render.filepath)
# silhouette : tout en noir (test de lisibilité en ombre chinoise)
root.rotation_euler = (0, 0, 0)
scene.view_layers[0].material_override = T.flat("silhouette", "#1A1210")
scene.render.filepath = os.path.join(tmp, "silhouette.png")
bpy.ops.render.render(write_still=True)
paths.append(scene.render.filepath)
print("RENDER_TIME", round(time.time() - t0, 1))

out = os.path.join(ROOT, "render", "model_sheets", f"{char}_{ver}.png")
if os.path.exists(out):
    sys.exit(f"REFUS : {out} existe déjà (ne jamais écraser une version)")
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
labels = ["FACE", "3/4", "PROFIL", "DOS", "SILHOUETTE"]
inputs, filters = [], []
for i, (p, lab) in enumerate(zip(paths, labels)):
    inputs += ["-i", p]
    dt = f"drawtext=fontfile={font}:text='{lab}':x=(w-tw)/2:y=40:fontsize=34:fontcolor=0x3A2A1E" if os.path.exists(font) else "null"
    filters.append(f"[{i}:v]{dt}[v{i}]")
filters.append("".join(f"[v{i}]" for i in range(len(paths))) + f"hstack=inputs={len(paths)}[out]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
                "-map", "[out]", out], check=True)
print("SHEET", out)
