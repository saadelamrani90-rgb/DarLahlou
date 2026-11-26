"""Construit Lalla Fatema-Zohra (v1) à partir de bible/fatema.json.
Rig par objets : fatema_root > corps > tete / epaule_G / epaule_D (téléphone dans la main D).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(loc=(0, 0, 0)):
    pal = json.load(open(os.path.join(ROOT, "bible", "fatema.json")))["palette_hex"]
    acc = pal["accents"]
    skin = T.toon("fz_peau", pal["peau"])
    scarf = T.toon("fz_foulard", pal["dominante_1_foulard"])
    dress = T.toon("fz_gandoura", pal["dominante_2_gandoura"])
    trim = T.toon("fz_galon", pal["dominante_3_galons_telephone"])
    slip = T.toon("fz_babouches", acc["babouches"])
    white = T.toon("fz_blanc_oeil", "#FFFFFF", levels=2)
    black = T.flat("fz_pupille", "#140C08")
    cheek = T.flat("fz_joues", acc["joues"])
    lips = T.flat("fz_bouche", acc["bouche"])
    brow = T.toon("fz_sourcils", "#2B1B12", levels=2)
    screen = T.flat("fz_ecran", "#DDF4FF")

    root = T.empty("fatema_root", (0, 0, 0))
    body = T.empty("fatema_corps", (0, 0, 0), root)

    # silhouette en cloche, stable, jusqu'au sol
    T.lathe("fz_robe", dress, [
        (0.0, 0.03), (0.47, 0.03), (0.48, 0.12), (0.46, 0.40), (0.44, 0.65), (0.40, 0.88),
        (0.33, 1.02), (0.22, 1.10), (0.0, 1.12)], scale=(1, 0.9, 1), parent=body)
    T.lathe("fz_ourlet", trim, [(0.475, 0.03), (0.49, 0.04), (0.49, 0.10), (0.48, 0.11)],
            scale=(1, 0.9, 1), parent=body, outline=False)
    T.lathe("fz_ceinture", trim, [(0.445, 0.62), (0.455, 0.63), (0.452, 0.69), (0.44, 0.70)],
            scale=(1, 0.9, 1), parent=body, outline=False)
    for s, side in ((-1, "G"), (1, "D")):
        T.sphere(f"fz_babouche_{side}", slip, (s * 0.16, -0.38, 0.035), 0.08, scale=(0.9, 1.4, 0.45), parent=body)

    # bras gauche : le long du corps
    sh = T.empty("fatema_epaule_G", (-0.3, 0, 1.0), body)
    T.limb("fz_manche_G", dress, (-0.3, 0, 1.0), (-0.47, -0.02, 0.62), 0.1, 0.095, parent=sh)
    T.sphere("fz_main_G", skin, (-0.49, -0.03, 0.55), 0.07, scale=(0.9, 0.8, 1.05), parent=sh)
    # bras droit : téléphone tenu devant elle, écran vers elle
    sh = T.empty("fatema_epaule_D", (0.3, 0, 1.0), body)
    T.limb("fz_manche_D1", dress, (0.3, 0, 1.0), (0.44, -0.12, 0.74), 0.1, 0.095, parent=sh)
    T.limb("fz_manche_D2", dress, (0.44, -0.12, 0.74), (0.26, -0.42, 0.9), 0.095, 0.09, parent=sh)
    T.sphere("fz_main_D", skin, (0.23, -0.47, 0.93), 0.07, scale=(0.9, 0.9, 1.0), parent=sh)
    tel = T.box("fz_telephone", trim, (0.2, -0.47, 1.02), (0.12, 0.025, 0.22), parent=sh, bevel=0.012, width=0.006)
    T.box("fz_telephone_ecran", screen, (0.2, -0.455, 1.02), (0.1, 0.01, 0.19), parent=sh, bevel=0, outline=False)

    # tête encadrée par le foulard
    head = T.empty("fatema_tete", (0, 0, 1.12), body)
    hz = 1.45
    T.sphere("fz_foulard_tete", scarf, (0, 0.05, hz + 0.02), 0.32, scale=(1.0, 1.0, 1.08), parent=head)
    T.lathe("fz_foulard_epaules", scarf, [(0.0, 1.30), (0.22, 1.27), (0.36, 1.13), (0.38, 1.04), (0.30, 1.0), (0.0, 1.0)],
            scale=(1, 0.92, 1), parent=head)
    T.sphere("fz_visage", skin, (0, -0.06, hz - 0.02), 0.27, scale=(0.95, 0.95, 1.0), parent=head)
    for s, side in ((-1, "G"), (1, "D")):
        T.sphere(f"fz_oeil_{side}", white, (s * 0.095, -0.28, hz + 0.04), 0.07, scale=(1, 0.7, 1.15),
                 parent=head, width=0.008)
        T.sphere(f"fz_pupille_{side}", black, (s * 0.095, -0.33, hz + 0.035), 0.03, scale=(1, 0.5, 1.2),
                 parent=head, outline=False, seg=16)
        T.tube(f"fz_cil_{side}", brow, [(s * 0.15, -0.3, hz + 0.09, 0.6), (s * 0.175, -0.29, hz + 0.115, 0.4)],
               0.012, parent=head, outline=False)
        T.tube(f"fz_sourcil_{side}", brow, [(s * 0.05, -0.31, hz + 0.135, 0.7), (s * 0.1, -0.31, hz + 0.16, 1.0),
                                            (s * 0.155, -0.29, hz + 0.145, 0.6)], 0.012, parent=head, outline=False)
        T.sphere(f"fz_joue_{side}", cheek, (s * 0.15, -0.28, hz - 0.07), 0.045, scale=(1, 0.3, 0.7),
                 parent=head, outline=False)
    T.sphere("fz_nez", skin, (0, -0.335, hz - 0.03), 0.05, parent=head, width=0.007)
    # sourire (forme de repos)
    pts = [(0.09 * t, -0.31 + 0.04 * t * t, hz - 0.12 + 0.03 * t * t, 1.0 - 0.4 * t * t) for t in (-1, -0.5, 0, 0.5, 1)]
    T.tube("fz_bouche_repos", lips, pts, 0.018, parent=head, outline=False)
    root.location = loc  # placé après construction : les pièces suivent
    return root
