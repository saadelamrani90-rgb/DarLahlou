"""Décor v1 : INT. MARCHÉ DE GROS, MATIN (Casablanca).
Hangar en béton, charpente métallique, caisses en plastique empilées, tomates,
palettes, balance, ardoise des prix, câbles électriques qui pendent, ampoule nue,
rideau métallique entrouvert sur le matin.
Tout est déterministe (graine fixe) : le décor est identique d'un plan à l'autre.
"""
import math
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T  # noqa: E402


def crate(name, col, loc, rot=0.0, tomatoes=False, rng=None):
    w, d, h = 0.6, 0.4, 0.3
    o = T.box(name, col, (loc[0], loc[1], loc[2] + h / 2), (w, d, h), bevel=0.02, width=0.008)
    o.rotation_euler = (0, 0, rot)
    # poignée découpée + lattes d'aération (enfants de la caisse, suivent sa rotation)
    dark = T.flat("caisse_fente", "#1E1A18")
    before = set(bpy.data.objects)
    for (fy, sx, sy) in ((-d / 2 - 0.004, 0.16, 0.01), (d / 2 + 0.004, 0.16, 0.01)):
        T.box(f"{name}_poignee{fy:+.0f}", dark, (0, fy, 0.08), (sx, sy, 0.045), bevel=0, outline=False)
        for k in (-1, 0, 1):
            T.box(f"{name}_latte{fy:+.0f}{k}", dark, (k * 0.17, fy, -0.05), (0.09, sy, 0.025), bevel=0,
                  outline=False)
    for fx in (-w / 2 - 0.004, w / 2 + 0.004):
        T.box(f"{name}_poigneeL{fx:+.1f}", dark, (fx, 0, 0.08), (0.01, 0.12, 0.045), bevel=0, outline=False)
    for ch in set(bpy.data.objects) - before:
        ch.parent = o  # coordonnées locales à la caisse
    if tomatoes:
        red = T.toon("tomate", "#D8382A")
        green = T.flat("queue_tomate", "#3E7D3A")
        for i in range(5):
            for j in range(3):
                x = -0.22 + i * 0.11 + rng.uniform(-0.015, 0.015)
                y = -0.12 + j * 0.12 + rng.uniform(-0.015, 0.015)
                c, s = math.cos(rot), math.sin(rot)
                px, py = loc[0] + c * x - s * y, loc[1] + s * x + c * y
                pz = loc[2] + h + 0.02
                T.sphere(f"{name}_t{i}{j}", red, (px, py, pz), 0.058, scale=(1, 1, 0.85), seg=12,
                         outline=False)
                T.sphere(f"{name}_q{i}{j}", green, (px, py, pz + 0.048), 0.014, scale=(1.4, 1.4, 0.4),
                         seg=8, outline=False)
    return o


def build():
    rng = random.Random(7)
    concrete = T.toon("beton", "#B7A68A")
    wall = T.toon("mur", "#D9A55B")
    wall_low = T.toon("soubassement", "#8FB8A8")
    steel = T.toon("charpente", "#3D5C5E", levels=2)
    shutter = T.toon("rideau", "#9AA3A3")
    morning = T.flat("matin", "#F7DDA4")
    wood = T.toon("palette", "#A57A4C")
    cable = T.flat("cable", "#1E1A18")
    bulb = T.flat("ampoule", "#FFF3C4")
    slate = T.toon("ardoise", "#2F4A3A", levels=2)
    chalk = T.flat("craie", "#F4F1E6")
    crate_cols = [T.toon("caisse_rouge", "#C23B2E"), T.toon("caisse_verte", "#3F8F5A"),
                  T.toon("caisse_bleue", "#2E6FA8"), T.toon("caisse_jaune", "#E3B23C")]

    # sol, mur du fond, murs latéraux
    T.box("sol", concrete, (0, 1, -0.05), (16, 12, 0.1), bevel=0, outline=False)
    T.box("mur_fond", wall, (0, 4.6, 2.5), (16, 0.2, 5), bevel=0, outline=False)
    T.box("soubassement", wall_low, (0, 4.48, 0.6), (16, 0.05, 1.2), bevel=0, outline=False)
    for s in (-1, 1):
        T.box(f"mur_{s}", wall, (s * 6, 1.5, 2.5), (0.2, 7, 5), bevel=0, outline=False)

    # rideau métallique entrouvert sur la lumière du matin (centre-gauche)
    T.box("ouverture", morning, (-1.6, 4.47, 1.4), (2.6, 0.04, 2.8), bevel=0, outline=False)
    T.box("rideau", shutter, (-1.6, 4.4, 2.35), (2.7, 0.08, 0.95), bevel=0.01, width=0.01)
    for k in range(6):
        T.box(f"rideau_lame_{k}", steel, (-1.6, 4.35, 1.95 + k * 0.15), (2.7, 0.02, 0.015), bevel=0, outline=False)
    T.box("rideau_cadre_G", steel, (-2.98, 4.4, 1.4), (0.08, 0.1, 2.85), bevel=0, outline=False)
    T.box("rideau_cadre_D", steel, (-0.22, 4.4, 1.4), (0.08, 0.1, 2.85), bevel=0, outline=False)

    # charpente métallique
    for x in (-4.5, -1.5, 1.5, 4.5):
        T.box(f"poteau_{x}", steel, (x, 4.3, 2.5), (0.18, 0.18, 5), bevel=0, width=0.01)
    T.box("poutre", steel, (0, 4.3, 4.1), (12, 0.2, 0.25), bevel=0, width=0.01)
    for x in (-3, 0, 3):
        T.box(f"traverse_{x}", steel, (x, 1.3, 4.2), (0.15, 6.4, 0.2), bevel=0, width=0.01)

    # câbles électriques qui pendent + ampoule nue
    for i, (x0, x1, sag) in enumerate(((-6, 6, 0.5), (-6, 2, 0.35), (-1, 6, 0.4))):
        pts = []
        for k in range(9):
            t = k / 8
            pts.append((x0 + (x1 - x0) * t, 3.0 - i * 0.6, 3.7 - sag * 4 * t * (1 - t) - i * 0.1, 1))
        T.tube(f"cable_{i}", cable, pts, 0.012, outline=False)
    T.tube("fil_ampoule", cable, [(0.4, 1.6, 3.6, 1), (0.4, 1.6, 2.9, 1)], 0.01, outline=False)
    T.sphere("ampoule", bulb, (0.4, 1.6, 2.82), 0.07, scale=(1, 1, 1.2), width=0.006)

    # piles de caisses en plastique (fond et côtés)
    n = 0
    for (cx, cy, rows, cols) in ((2.6, 3.6, 4, 3), (4.6, 2.6, 5, 2), (-4.6, 3.2, 3, 2), (-3.4, 3.8, 5, 1)):
        for c in range(cols):
            for r in range(rows):
                col = crate_cols[rng.randrange(4)]
                crate(f"caisse_{n}", col, (cx + c * 0.62, cy, r * 0.31), rot=rng.uniform(-0.05, 0.05))
                n += 1

    # palette + caisses de tomates au premier plan, entre les personnages
    T.box("palette_1", wood, (0, 0.55, 0.07), (1.3, 0.9, 0.14), bevel=0.01, width=0.008)
    for k, (dx, dy) in enumerate(((-0.32, 0.33), (0.32, 0.33), (-0.32, 0.77), (0.32, 0.77))):
        crate(f"caisse_tom_{k}", crate_cols[0 if k % 2 == 0 else 1], (dx, dy, 0.14), tomatoes=True, rng=rng)
    crate("caisse_tom_haut", crate_cols[2], (0.0, 0.55, 0.45), rot=0.08, tomatoes=True, rng=rng)
    # tomates à droite, prêtes à partir
    T.box("palette_2", wood, (2.9, 1.2, 0.07), (1.3, 0.9, 0.14), bevel=0.01, width=0.008)
    for k in range(3):
        crate(f"caisse_d_{k}", crate_cols[k % 4], (2.6 + (k % 2) * 0.62, 1.2, 0.14 + (k // 2) * 0.31),
              tomatoes=(k == 2), rng=rng)

    # balance de marché
    T.box("balance_socle", steel, (-3.7, 1.4, 0.45), (0.5, 0.4, 0.9), bevel=0.02, width=0.01)
    T.box("balance_plateau", shutter, (-3.7, 1.4, 0.93), (0.65, 0.5, 0.05), bevel=0.01, width=0.008)
    T.sphere("balance_cadran", chalk, (-3.7, 1.18, 0.6), 0.14, scale=(1, 0.25, 1), width=0.008)

    # ardoise des prix sur chevalet : le gag de départ (3 DH)
    board = T.box("ardoise", slate, (-2.45, 0.9, 1.15), (0.9, 0.05, 0.7), bevel=0.02, width=0.01)
    board.rotation_euler = (math.radians(-8), 0, math.radians(18))
    for s in (-1, 1):
        leg = T.limb(f"chevalet_{s}", wood, (-2.45 + s * 0.35, 0.98, 0.0), (-2.45 + s * 0.3, 0.92, 1.5), 0.025)
    txt = bpy.data.curves.new("prix", "FONT")
    txt.body = "MATICHA\n3 DH / KG"
    txt.align_x = "CENTER"
    txt.align_y = "CENTER"
    txt.size = 0.17
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if os.path.exists(font):
        txt.font = bpy.data.fonts.load(font)
    to = bpy.data.objects.new("prix", txt)
    bpy.context.collection.objects.link(to)
    to.data.materials.append(chalk)
    to.location = (0, -0.03, 0)
    to.rotation_euler = (math.radians(90), 0, 0)
    to.parent = board
    return n


if __name__ == "__main__":
    import importlib
    import time
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    T.setup_render(scene, w=1920, h=1080, bg="#F7DDA4")
    build()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    b = importlib.import_module("char_brahim").build(loc=(-1.0, -0.15, 0))
    b.rotation_euler = (0, 0, math.radians(32))
    l = importlib.import_module("char_lhssen").build(loc=(1.15, -0.05, 0))
    l.rotation_euler = (0, 0, math.radians(-32))
    cd = bpy.data.cameras.new("cam")
    cd.lens = 30
    cam = bpy.data.objects.new("cam", cd)
    scene.collection.objects.link(cam)
    cam.location = (-0.2, -5.0, 1.55)
    cam.rotation_euler = (math.radians(86), 0, 0)
    scene.camera = cam
    out = os.path.join(root, "render", "sets", sys.argv[-1] + ".png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        sys.exit(f"REFUS : {out} existe déjà")
    scene.render.filepath = out
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("RENDER", out, round(time.time() - t, 1), "s")
