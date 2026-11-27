"""Plan A01 : gros plan Brahim, réplique L1 chuchotée façon film d'espionnage.
Il se penche vers les caisses, regarde à gauche, à droite, puis hausse les sourcils
sur « Hna f l'marché ? ».
Rendu « en deux » : 12 poses/s, sortie 24 fps.
Usage : python scripts/shot_A01.py <version>
"""
import importlib
import math
import os
import subprocess
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import anim_lib as A  # noqa: E402
import lib_toon as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = sys.argv[-1]
FPS = 24
PRE = 12  # 0,5 s avant la réplique
LINE = "L1"
wav = os.path.join(ROOT, "audio", "scene_A", LINE + ".wav")
cues = os.path.join(ROOT, "audio", "scene_A", LINE + ".json")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
T.setup_render(scene, bg="#F7DDA4", fps=FPS)
importlib.import_module("set_marche").build()
root = importlib.import_module("char_brahim").build(loc=(-1.3, 0.25, 0))
root.rotation_euler = (0, 0, math.radians(22))
O = bpy.data.objects

# --- lip sync
end = A.lipsync(O["br_bouche_repos"], cues, PRE + 1, FPS, drop=0.03, fwd=0.012, gain=1.3)
last = end + 20
scene.frame_start, scene.frame_end = 1, last

# --- jeu : penché, regard à gauche, à droite, sourcils
body, head = O["brahim_corps"], O["brahim_tete"]
A.pose(body, 1, rot=(0, 0, 0))
A.pose(body, 10, rot=(8, 0, 0))            # se penche en avant, conspirateur
A.pose(body, end - 30, rot=(8, 0, 0))
A.pose(body, end - 22, rot=(2, 0, 0))      # se redresse : « Hna f l'marché ? »
A.pose(body, last, rot=(2, 0, 0))
A.pose(head, 1, rot=(0, 0, 0))
A.pose(head, 24, rot=(-4, 0, 25))          # regarde à gauche
A.pose(head, 50, rot=(-4, 0, 25))
A.pose(head, 62, rot=(-4, 0, -25))         # puis à droite
A.pose(head, 92, rot=(-4, 0, -25))
A.pose(head, 104, rot=(4, 0, 0))           # face caméra
A.pose(head, last, rot=(4, 0, 0))
pupils = [O["br_pupille_G"], O["br_pupille_D"]]
for p in pupils:
    b = tuple(p.location)
    A.pose(p, 1, loc_delta=(0, 0, 0), base=b)
    A.pose(p, 20, loc_delta=(0.014, 0.004, 0), base=b)
    A.pose(p, 56, loc_delta=(-0.014, 0.004, 0), base=b)
    A.pose(p, 100, loc_delta=(0, 0, 0), base=b)
    A.set_constant(p)  # saccades oculaires nettes
brows = [O["br_sourcil_G"], O["br_sourcil_D"]]
for br in brows:
    b = tuple(br.location)
    A.pose(br, 1, loc_delta=(0, 0, -0.02), base=b)          # sourcils froncés
    A.pose(br, end - 26, loc_delta=(0, 0, -0.02), base=b)
    A.pose(br, end - 20, loc_delta=(0, 0, 0.04), base=b)    # étonnés
    A.pose(br, last, loc_delta=(0, 0, 0.04), base=b)
A.blinks([O["br_oeil_G"], O["br_oeil_D"]] + pupils, [40, 118, end - 8])

# --- caméra : gros plan épaules, légère contre-plongée
target = T.empty("cam_cible", (-1.2, 0.2, 1.45))
cd = bpy.data.cameras.new("cam")
cd.lens = 50
cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cam.location = (0.15, -2.55, 1.3)
tr = cam.constraints.new("TRACK_TO")
tr.target = target
scene.camera = cam

# --- rendu en deux
frames = os.path.join(ROOT, "render", "frames", f"A01_{VER}")
os.makedirs(frames, exist_ok=True)
scene.frame_step = 2
scene.render.filepath = os.path.join(frames, "f_")
t = time.time()
bpy.ops.render.render(animation=True)
rt = time.time() - t
n = len([f for f in os.listdir(frames) if f.endswith(".png")])
print(f"RENDER {n} images en {rt:.0f} s ({rt / n:.2f} s/image)")

# --- montage : images tenues 2 frames, audio, sous-titres
srt = os.path.join(frames, "sub.srt")
t0 = PRE / FPS
t1 = end / FPS
fmt = lambda s: f"00:00:{int(s):02d},{int((s % 1) * 1000):03d}"
open(srt, "w").write(f"1\n{fmt(t0)} --> {fmt(t1)}\nAch hada ? L'maticha b 3 dirhams l'kilo ? Hna f l'marché ?\n"
                     "C'est quoi ça ? La tomate à 3 DH le kilo ? Ici, au marché ?\n")
out = os.path.join(ROOT, "render", f"A01_{VER}.mp4")
if os.path.exists(out):
    sys.exit(f"REFUS : {out} existe déjà")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / 2), "-pattern_type", "glob",
                "-i", os.path.join(frames, "f_*.png"), "-itsoffset", str(t0), "-i", wav,
                "-vf", f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=16,Outline=2,MarginV=30'",
                "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                "-c:a", "aac", "-b:a", "160k", out], check=True)
print("VIDEO", out)
