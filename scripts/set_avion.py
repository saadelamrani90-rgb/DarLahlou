"""Gag v1 : la tomate en costume et lunettes noires, en classe affaires.
Construit loin du marché (x = 100) pour cohabiter dans la même scène Blender.
Retourne les objets à animer (lunettes, sourcils, nuages)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T  # noqa: E402

X0 = 100.0


def build():
    wall = T.toon("av_paroi", "#EFE6D2")
    sky = T.flat("av_ciel", "#8EC9E8")
    cloud = T.flat("av_nuage", "#FFFFFF")
    seat = T.toon("av_siege", "#2E4A7A")
    seat_l = T.toon("av_siege_cuir", "#3B5C94")
    red = T.toon("av_tomate", "#D8382A")
    leaf = T.toon("av_queue", "#3E7D3A", levels=2)
    suit = T.toon("av_costume", "#1F2A3A")
    shirt = T.toon("av_chemise", "#F4F1E6", levels=2)
    tie = T.toon("av_cravate", "#E9A93B", levels=2)
    black = T.flat("av_noir", "#101010")
    white = T.toon("av_blanc", "#FFFFFF", levels=2)
    juice = T.toon("av_jus", "#F29A2E", levels=2)
    glass = T.flat("av_verre", "#DDEFF5")

    # paroi + hublot avec ciel et nuages qui défilent
    T.box("av_paroi", wall, (X0, 0.9, 1.3), (6, 0.1, 3), bevel=0, outline=False)
    T.box("av_hublot_cadre", T.toon("av_cadre", "#D6CCB6"), (X0 + 0.85, 0.84, 1.35), (0.62, 0.04, 0.82), bevel=0.12,
          width=0.01)
    T.box("av_hublot", sky, (X0 + 0.85, 0.815, 1.35), (0.48, 0.02, 0.68), bevel=0.1, outline=False)
    clouds = []
    for i, (dx, dz, r) in enumerate(((-0.1, 0.15, 0.09), (0.12, -0.12, 0.07), (0.3, 0.05, 0.08))):
        clouds.append(T.sphere(f"av_nuage_{i}", cloud, (X0 + 0.85 + dx, 0.8, 1.35 + dz), r, scale=(1.8, 0.2, 0.8),
                               outline=False))
    # siège classe affaires (large, cuir)
    T.box("av_assise", seat, (X0, 0.25, 0.55), (1.0, 0.8, 0.25), bevel=0.06, width=0.012)
    T.box("av_dossier", seat, (X0, 0.6, 1.15), (1.0, 0.25, 1.2), bevel=0.08, width=0.012)
    T.box("av_coussin", seat_l, (X0, 0.47, 1.2), (0.75, 0.04, 0.9), bevel=0.06, outline=False)
    for s in (-1, 1):
        T.box(f"av_accoudoir_{s}", seat, (X0 + s * 0.55, 0.2, 0.8), (0.18, 0.8, 0.22), bevel=0.05, width=0.01)
    # le verre de jus d'orange sur l'accoudoir droit
    T.limb("av_verre", glass, (X0 + 0.55, 0.0, 0.92), (X0 + 0.55, 0.0, 1.1), 0.045, 0.05, width=0.005)
    T.limb("av_jus", juice, (X0 + 0.55, 0.0, 0.93), (X0 + 0.55, 0.0, 1.05), 0.04, 0.045, outline=False)

    # la tomate : corps rond en costume, tête = la tomate elle-même
    T.lathe("av_veste", suit, [(0.0, 0.62), (0.3, 0.64), (0.36, 0.75), (0.34, 0.88), (0.26, 0.96), (0.0, 0.97)],
            loc=(X0, 0.2, 0), scale=(1, 0.8, 1))
    T.sphere("av_plastron", shirt, (X0, -0.065, 0.86), 0.08, scale=(0.8, 0.25, 1.1), outline=False)
    T.tube("av_cravate", tie, [(X0, -0.095, 0.94, 1.0), (X0, -0.1, 0.86, 1.2), (X0, -0.09, 0.78, 0.6)], 0.02,
           outline=False)
    head = T.sphere("av_tete", red, (X0, 0.15, 1.2), 0.3, scale=(1.08, 1, 0.92))
    for k in range(5):  # collerette de la queue
        a = 2 * math.pi * k / 5
        T.sphere(f"av_feuille_{k}", leaf, (X0 + 0.08 * math.cos(a), 0.15 + 0.08 * math.sin(a), 1.47), 0.06,
                 scale=(1.6, 0.6, 0.3), width=0.005).rotation_euler = (0, 0, a)
    T.limb("av_queue", leaf, (X0, 0.15, 1.46), (X0 + 0.02, 0.15, 1.56), 0.022, 0.015, width=0.005)
    # bras : l'un sur l'accoudoir, l'autre tient le verre
    for s in (-1, 1):
        T.limb(f"av_bras_{s}", suit, (X0 + s * 0.3, 0.2, 0.9), (X0 + s * 0.5, 0.05, 0.85), 0.07, 0.06)
        T.sphere(f"av_main_{s}", white, (X0 + s * 0.52, 0.02, 0.88), 0.05)
    # yeux (cachés au départ derrière les lunettes)
    eyes = []
    for s in (-1, 1):
        eyes.append(T.sphere(f"av_oeil_{s}", white, (X0 + s * 0.09, -0.12, 1.25), 0.055, scale=(1, 0.6, 1.1),
                             width=0.006))
        eyes.append(T.sphere(f"av_pupille_{s}", black, (X0 + s * 0.09, -0.16, 1.24), 0.022, scale=(1, 0.5, 1.2),
                             outline=False, seg=12))
    brows = [T.tube(f"av_sourcil_{s}", black, [(X0 + s * 0.04, -0.15, 1.34, 0.8), (X0 + s * 0.14, -0.13, 1.355, 0.8)],
                    0.012, outline=False) for s in (-1, 1)]
    # lunettes noires (devant les yeux au départ)
    glasses = T.empty("av_lunettes", (X0, -0.17, 1.25))
    for s in (-1, 1):
        T.sphere(f"av_verre_lunette_{s}", black, (X0 + s * 0.095, -0.175, 1.25), 0.07, scale=(1.25, 0.3, 0.85),
                 parent=glasses, width=0.005)
    T.tube("av_pont_lunette", black, [(X0 - 0.03, -0.19, 1.27, 1), (X0, -0.195, 1.275, 1), (X0 + 0.03, -0.19, 1.27, 1)],
           0.008, parent=glasses, outline=False)
    return {"lunettes": glasses, "sourcils": brows, "nuages": clouds, "tete": head}
