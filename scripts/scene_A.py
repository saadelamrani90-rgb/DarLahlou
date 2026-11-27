"""Scène A (v3) : INT. MARCHÉ DE GROS, MATIN, sur une seule timeline.
Les plans sont des marqueurs de caméra ; les répliques sont posées bout à bout.
Usage :
  python scripts/scene_A.py stills <version>   -> une image par plan (planche de contrôle)
  python scripts/scene_A.py render <version>   -> rendu complet + son + sous-titres
"""
import importlib
import json
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
MODE, VER = sys.argv[-2], sys.argv[-1]
FPS = 24
GAP = 8  # frames entre deux répliques
AUD = os.path.join(ROOT, "audio", "scene_A_v3")
DLG = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "storyboard", "scene_A_dialogue_v3.json")))["repliques"]}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
T.setup_render(scene, bg="#F7DDA4", fps=FPS)
setm = importlib.import_module("set_marche")
setm.build()
gag = importlib.import_module("set_avion").build()
O = bpy.data.objects

BR_LOC, BR_ROT = (-1.5, 0.2, 0), 25
LH_LOC, LH_ROT = (-0.35, -0.15, 0), -40
br = importlib.import_module("char_brahim").build(loc=BR_LOC)
br.rotation_euler = (0, 0, math.radians(BR_ROT))
lh = importlib.import_module("char_lhssen").build(loc=LH_LOC)
lh.rotation_euler = (0, 0, math.radians(LH_ROT))


def center_origin(o):
    """Ramène l'origine au centre de la géométrie (indispensable pour animer l'échelle)."""
    from mathutils import Vector
    c = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    for v in o.data.vertices:
        v.co -= c
    o.location = o.location + c


center_origin(O["sl_bouche_repos"])

# --- accessoires du marché : caisse retournée + téléphone de Brahim + main d'insert
dark = T.toon("tel_br", "#2B2B2B", levels=2)
crate_c = T.toon("caisse_tel", "#3F8F5A")
T.box("caisse_tel_1", crate_c, (-2.3, -0.05, 0.15), (0.6, 0.4, 0.3), bevel=0.02, width=0.008)
T.box("caisse_tel_2", crate_c, (-2.3, -0.05, 0.45), (0.6, 0.4, 0.3), bevel=0.02, width=0.008)
phone = T.empty("tel_pivot", (-2.3, -0.07, 0.615))
T.box("tel_corps", dark, (-2.3, -0.07, 0.615), (0.11, 0.2, 0.018), parent=phone, bevel=0.01, width=0.004)
T.box("tel_ecran", T.flat("tel_ecran_m", "#3FA7D6"), (-2.3, -0.07, 0.626), (0.095, 0.18, 0.004), parent=phone,
      bevel=0, outline=False)
txt = bpy.data.curves.new("tel_nom", "FONT")
txt.body = "LALLA ♥"
txt.align_x, txt.align_y, txt.size = "CENTER", "CENTER", 0.022
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(font):
    txt.font = bpy.data.fonts.load(font)
to = bpy.data.objects.new("tel_nom", txt)
scene.collection.objects.link(to)
to.data.materials.append(T.flat("tel_txt", "#FFFFFF"))
to.location = (-2.3, -0.07, 0.6295)
to.parent = phone
to.matrix_parent_inverse = phone.matrix_world.inverted()
hand = T.sphere("main_insert", T._mats["br_peau"], (-1.62, -0.07, 0.68), 0.075, scale=(1.3, 0.9, 0.6))

# --- caméras
cams = {}


def cam(name, loc, aim, lens):
    tgt = T.empty(f"{name}_cible", aim)
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    c = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(c)
    c.location = loc
    tr = c.constraints.new("TRACK_TO")
    tr.target = tgt
    cams[name] = c
    return c


cam("A_gp_brahim", (-0.05, -2.6, 1.3), (-1.4, 0.15, 1.45), 50)        # = plan A01 validé
cam("B_deux", (-0.9, -4.4, 1.3), (-0.92, 0.0, 1.15), 32)           # plan à deux
cam("C_lhssen", (-1.82, -1.92, 1.6), (-0.35, -0.15, 1.55), 35)      # Si Lhssen, amorce Brahim
cam("D_brahim", (-0.65, -1.61, 1.45), (-1.5, 0.2, 1.4), 38)        # Brahim, contrechamp
cam("E_insert_tel", (-2.3, -0.42, 1.0), (-2.3, -0.07, 0.62), 50)  # insert téléphone
cam("G_avion", (100.0, -2.0, 1.15), (100.0, 0.1, 1.08), 40)         # gag classe affaires

# --- timeline
f = 13  # 0,5 s de noir/respiration
events, subs, shots = [], [], []


def shot(name, frame):
    shots.append((name, frame))


def say(who, lid, mouth, **kw):
    global f
    wav = os.path.join(AUD, lid + ".wav")
    start = f
    end = A.lipsync(O[mouth], os.path.join(AUD, lid + ".json"), start, FPS, **kw) if mouth else \
        start + round(json.load(open(os.path.join(AUD, lid + ".json")))["metadata"]["duration"] * FPS)
    events.append((start / FPS, wav))
    subs.append((start / FPS, end / FPS, DLG[lid]["latin"], DLG[lid]["fr"]))
    f = end + GAP
    return start, end


BRM = dict(drop=0.03, fwd=0.012, gain=1.3)
LHM = dict(drop=0.015, fwd=0.008, gain=1.6)
body_b, head_b, body_l, head_l = O["brahim_corps"], O["brahim_tete"], O["lhssen_corps"], O["lhssen_tete"]
pup_b = [O["br_pupille_G"], O["br_pupille_D"]]
brow_b = [O["br_sourcil_G"], O["br_sourcil_D"]]
base = {o.name: tuple(o.location) for o in pup_b + brow_b}
for o in (body_b, head_b, body_l, head_l):
    A.pose(o, 1, rot=(0, 0, 0))


def brows(frame, dz):
    for o in brow_b:
        A.pose(o, frame, loc_delta=(0, 0, dz), base=base[o.name])


def look(frame, dx, dz=0.0):
    for o in pup_b:
        A.pose(o, frame, loc_delta=(dx, 0.004 if dx or dz else 0, dz), base=base[o.name])


# Si Lhssen hors champ au début
lh_base = tuple(lh.location)
A.pose(lh, 1, loc_delta=(3.5, 0, 0), base=lh_base)

# S01 : A01 (L1) chuchoté, regarde à gauche puis à droite
shot("A_gp_brahim", 1)
brows(1, -0.02)
s, e = say("brahim", "L1", "br_bouche_repos", **BRM)
A.pose(body_b, s, rot=(8, 0, 0))
A.pose(head_b, s + 12, rot=(-4, 0, 25)); A.pose(head_b, s + 38, rot=(-4, 0, 25))
A.pose(head_b, s + 50, rot=(-4, 0, -25)); A.pose(head_b, s + 80, rot=(-4, 0, -25))
A.pose(head_b, s + 92, rot=(4, 0, 0))
look(s + 8, 0.014); look(s + 44, -0.014); look(s + 88, 0)
brows(e - 22, -0.02); brows(e - 16, 0.04)
A.pose(body_b, e - 26, rot=(8, 0, 0)); A.pose(body_b, e - 18, rot=(2, 0, 0))

# S02 : L2 scandalisé, secoue la tête
s, e = say("brahim", "L2", "br_bouche_repos", **BRM)
for i, fr in enumerate(range(s, e, 10)):
    A.pose(head_b, fr, rot=(2, 0, 9 if i % 2 else -9))
A.pose(head_b, e, rot=(2, 0, 0))
brows(s, 0.05)

# S03 : plan à deux. Si Lhssen surgit, Brahim sursaute
shot("B_deux", f)
A.pose(lh, f, loc_delta=(3.5, 0, 0), base=lh_base)
A.pose(lh, f + 8, loc_delta=(0, 0, 0), base=lh_base)
br_base = tuple(br.location)
A.pose(br, f + 8, loc_delta=(0, 0, 0), base=br_base)
A.pose(br, f + 11, loc_delta=(0, 0, 0.14), base=br_base)
A.pose(br, f + 16, loc_delta=(0, 0, 0), base=br_base)
brows(f + 9, 0.07); look(f + 9, 0.016)
f += 18
s, e = say("lhssen", "L3", "sl_bouche_repos", **LHM)
A.pose(head_l, s, rot=(0, 0, 0)); A.pose(head_l, s + 20, rot=(4, 0, 6))
brows(e, 0.0); look(e, 0.016)
s, e = say("brahim", "L4", "br_bouche_repos", **BRM)
A.pose(head_b, s, rot=(0, 8, 0)); A.pose(head_b, e, rot=(0, 8, 0))

# S04 : Si Lhssen compte sur ses doigts (bras gauche qui monte et rebondit)
shot("C_lhssen", f)
sh_l = O["lhssen_epaule_G"]
A.pose(sh_l, f - 1, rot=(0, 0, 0))
s, e = say("lhssen", "L5", "sl_bouche_repos", **LHM)
step = int((e - s) * 0.55 / 5)
for k in range(5):
    A.pose(sh_l, s + k * step, rot=(-28, 0, 0))
    A.pose(sh_l, s + k * step + step // 2, rot=(-18, 0, 0))
A.pose(sh_l, s + 5 * step + 6, rot=(0, 0, 0))
A.pose(head_l, s + 5 * step, rot=(6, 0, 0)); A.pose(head_l, e, rot=(0, 0, 0))

# S05 : contrechamp Brahim, indigné (L6)
shot("D_brahim", f)
A.pose(head_b, f, rot=(0, 0, 0)); A.pose(body_b, f, rot=(2, 0, 0))
s, e = say("brahim", "L6", "br_bouche_repos", **BRM)
A.pose(body_b, s + 6, rot=(-6, 0, 0)); brows(s + 4, 0.06)
A.pose(head_b, e - 12, rot=(-6, 0, 0))

# S06 : GAG classe affaires (3 s, sans dialogue, carillon d'avion)
shot("G_avion", f)
g0 = f
events.append((g0 / FPS, os.path.join(AUD, "sfx_ding.wav")))
gl = gag["lunettes"]
gb = tuple(gl.location)
A.pose(gl, g0, loc_delta=(0, 0, 0), base=gb)
A.pose(gl, g0 + 26, loc_delta=(0, 0, 0), base=gb)
A.pose(gl, g0 + 34, loc_delta=(0, -0.01, -0.075), base=gb)   # baisse ses lunettes
for b in gag["sourcils"]:
    bb = tuple(b.location)
    A.pose(b, g0 + 34, loc_delta=(0, 0, 0), base=bb)
    A.pose(b, g0 + 40, loc_delta=(0, 0, 0.03), base=bb)        # hausse un sourcil
for c in gag["nuages"]:
    cb = tuple(c.location)
    A.pose(c, g0, loc_delta=(0.25, 0, 0), base=cb)
    A.pose(c, g0 + 72, loc_delta=(-0.25, 0, 0), base=cb)
f = g0 + 72

# S07 : plan à deux, l'idée absurde (L7, L8, L9)
shot("B_deux", f)
s, e = say("brahim", "L7", "br_bouche_repos", **BRM)
look(s, 0.0, 0.014); brows(s, 0.03); A.pose(head_b, s, rot=(-8, 6, 0)); A.pose(head_b, e, rot=(-8, 6, 0))
s, e = say("lhssen", "L8", "sl_bouche_repos", **LHM)
A.pose(head_l, s, rot=(0, 0, 0)); A.pose(head_l, s + 6, rot=(8, 0, 0)); A.pose(head_l, s + 12, rot=(0, 0, 0))
look(s, 0.016)
s, e = say("brahim", "L9", "br_bouche_repos", **BRM)
A.pose(head_b, s, rot=(0, 0, 0)); A.pose(body_b, s, rot=(2, 0, 0)); A.pose(body_b, s + 8, rot=(-8, 0, 0))
brows(s + 4, 0.06)

# S08 : Si Lhssen se penche, confidentiel (L10)
shot("C_lhssen", f)
A.pose(body_l, f, rot=(0, 0, 0)); A.pose(body_b, f, rot=(2, 0, 0))
s, e = say("lhssen", "L10", "sl_bouche_repos", **LHM)
A.pose(body_l, s + 8, rot=(12, 0, 0)); A.pose(head_l, s + 8, rot=(4, 0, 0))
A.pose(body_l, e, rot=(12, 0, 0)); A.pose(body_l, e + 10, rot=(0, 0, 0)); A.pose(head_l, e + 10, rot=(0, 0, 0))

# S09 : Brahim rêveur (L11), lent travelling avant
shot("D_brahim", f)
cd = cams["D_brahim"]
D0 = tuple(cd.location)
A.pose(cd, f, loc_delta=(0, 0, 0), base=D0)
s, e = say("brahim", "L11", "br_bouche_repos", **BRM)
A.pose(head_b, s, rot=(-12, 0, 0)); look(s, 0.0, 0.016); brows(s, 0.04)
A.pose(cd, e + 4, loc_delta=(-0.2, 0.45, 0.02), base=D0)

# S10 : insert téléphone qui vibre au même instant, Fatema-Zohra (L12), la main le retourne
shot("E_insert_tel", f)
events.append((f / FPS, os.path.join(AUD, "sfx_vibre.wav")))
pb = tuple(phone.location)
for i in range(0, 18, 2):
    A.pose(phone, f + i, loc_delta=(0.006 if i % 4 else -0.006, 0, 0), base=pb)
A.pose(phone, f + 18, loc_delta=(0, 0, 0), base=pb)
f += 10
s, e = say("fatema", "L12", None)
hb = tuple(hand.location)
A.pose(hand, e - 14, loc_delta=(0, 0, 0), base=hb)
A.pose(hand, e - 6, loc_delta=(-0.68, 0, 0.02), base=hb)
A.pose(phone, e - 6, rot=(0, 0, 0))
A.pose(phone, e - 2, rot=(0, 180, 0), loc_delta=(0, 0, 0.012), base=pb)  # face contre la caisse
A.pose(hand, e + 4, loc_delta=(0, 0, 0), base=hb)
f = e + 6

# S11 : « Tfou... »
shot("D_brahim", f)
A.pose(cd, f, loc_delta=(0, 0, 0), base=D0)
look(f, 0, 0); brows(f, -0.025)
s, e = say("brahim", "L13", "br_bouche_repos", **BRM)
A.pose(head_b, s, rot=(10, 0, 0)); A.pose(body_b, s, rot=(6, 0, 0))

# S12 : plan à deux final, poignée de main, « Machi mochkil. Kolchi f l'qanoun. »
shot("B_deux", f)
sh_b = O["brahim_epaule_D"]
A.pose(sh_b, f, rot=(0, 0, 0)); A.pose(sh_l, f, rot=(0, 0, 0))
A.pose(head_b, f, rot=(0, 0, 0)); A.pose(body_b, f, rot=(0, 0, 0))
A.pose(sh_l, f + 10, rot=(-38, 0, -20))
s, e = say("lhssen", "L14", "sl_bouche_repos", **LHM)
A.pose(sh_b, s + 6, rot=(-50, 0, 25))
for i in range(3):  # la poignée de main secoue
    A.pose(sh_b, e + i * 6, rot=(-46, 0, 25)); A.pose(sh_b, e + i * 6 + 3, rot=(-54, 0, 25))
    A.pose(sh_l, e + i * 6, rot=(-34, 0, -20)); A.pose(sh_l, e + i * 6 + 3, rot=(-42, 0, -20))
last = e + 30

# clignements naturels, espacés
A.blinks([O["br_oeil_G"], O["br_oeil_D"]] + pup_b, list(range(55, last, 83)))
A.blinks([O["sl_oeil_G"], O["sl_oeil_D"], O["sl_pupille_G"], O["sl_pupille_D"]], list(range(70, last, 97)))
for o in pup_b + [O["sl_pupille_G"], O["sl_pupille_D"]]:
    A.set_constant(o)

for name, fr in shots:
    m = scene.timeline_markers.new(name, frame=fr)
    m.camera = cams[name]
scene.camera = cams["A_gp_brahim"]
scene.frame_start, scene.frame_end = 1, last
json.dump({"version": VER, "fps": FPS, "frames": last, "duree_s": round(last / FPS, 2),
           "plans": [{"camera": n, "debut_s": round(fr / FPS, 2)} for n, fr in shots],
           "sous_titres": subs},
          open(os.path.join(ROOT, "storyboard", f"scene_A_plans_{VER}.json"), "w"), ensure_ascii=False, indent=2)
print(f"DUREE {last / FPS:.1f} s, {len(shots)} plans")

out_dir = os.path.join(ROOT, "render", "frames", f"sceneA_{VER}")
os.makedirs(out_dir, exist_ok=True)
if MODE == "stills":
    paths = []
    bounds = [fr for _, fr in shots] + [last]
    for i, (name, fr) in enumerate(shots):
        mid = (fr + bounds[i + 1]) // 2
        scene.frame_set(mid)
        scene.camera = cams[name]
        scene.render.resolution_percentage = 50
        scene.render.filepath = os.path.join(out_dir, f"plan_{i + 1:02d}.png")
        bpy.ops.render.render(write_still=True)
        paths.append(scene.render.filepath)
    sheet = os.path.join(ROOT, "render", "tests", f"sceneA_planche_{VER}.png")
    ins = sum((["-i", p] for p in paths), [])
    n = len(paths)
    lay = "|".join(f"{'+'.join(['w0'] * (i % 4)) or '0'}_{'+'.join(['h0'] * (i // 4)) or '0'}" for i in range(n))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex",
                    "".join(f"[{i}:v]" for i in range(n)) + f"xstack=inputs={n}:layout={lay}:fill=black", sheet],
                   check=True)
    print("PLANCHE", sheet)
    sys.exit(0)

# --- rendu complet « en deux »
scene.frame_step = 2
scene.render.filepath = os.path.join(out_dir, "f_")
t = time.time()
bpy.ops.render.render(animation=True)
rt = time.time() - t
n = len([x for x in os.listdir(out_dir) if x.startswith("f_")])
print(f"RENDER {n} images en {rt:.0f} s ({rt / n:.2f} s/image)")

# --- son : répliques + bruitages posés à leur temps
mix = os.path.join(out_dir, "mix.wav")
ins, flt = [], []
for i, (t0, w) in enumerate(events):
    ins += ["-i", w]
    flt.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=mono,adelay={int(t0 * 1000)}[a{i}]")
flt.append("".join(f"[a{i}]" for i in range(len(events))) + f"amix=inputs={len(events)}:normalize=0[m]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]",
                "-t", str(last / FPS), mix], check=True)
# --- sous-titres darija (latin) + français
srt = os.path.join(out_dir, "sous_titres.srt")


def ts(x):
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int((x % 1) * 1000):03d}"


with open(srt, "w") as fh:
    for i, (a, b, lat, fr) in enumerate(subs, 1):
        fh.write(f"{i}\n{ts(a)} --> {ts(b)}\n{lat}\n{fr}\n\n")
out = os.path.join(ROOT, "render", f"sceneA_{VER}.mp4")
if os.path.exists(out):
    sys.exit(f"REFUS : {out} existe déjà")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS / 2), "-pattern_type", "glob",
                "-i", os.path.join(out_dir, "f_*.png"), "-i", mix,
                "-vf", f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=15,Outline=2,MarginV=26'",
                "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                "-c:a", "aac", "-b:a", "160k", out], check=True)
print("VIDEO", out)
