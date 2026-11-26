"""Construit Hajj Brahim Lahlou (v1) à partir de bible/brahim.json.

Hiérarchie = rig minimal par objets (pas d'armature) :
  brahim_root > corps > tete > (yeux, bouche, sourcils, moustache)
                      > epaule_G / epaule_D > bras
Chaque pivot est un Empty : on anime en tournant les pivots (poses clés).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(loc=(0, 0, 0)):
    bible = json.load(open(os.path.join(ROOT, "bible", "brahim.json")))
    pal = bible["palette_hex"]
    acc = pal["accents"]
    skin = T.toon("br_peau", pal["peau"])
    shirt = T.toon("br_chemise", pal["dominante_1_chemise"])
    pants = T.toon("br_pantalon", pal["dominante_2_pantalon"])
    hair = T.toon("br_poils", pal["dominante_3_moustache_cheveux"], levels=2)
    belt = T.toon("br_ceinture", acc["ceinture"], levels=2)
    shoes = T.toon("br_chaussures", acc["chaussures"])
    white = T.toon("br_blanc_oeil", "#FFFFFF", levels=2)
    black = T.flat("br_pupille", "#140C08")
    mouth_m = T.flat("br_bouche", "#5A1E18")
    pen_b = T.toon("br_stylo_bleu", acc["stylo_bleu"], levels=2)
    pen_r = T.toon("br_stylo_rouge", acc["stylo_rouge"], levels=2)
    button = T.toon("br_bouton", "#F7F3EA", levels=2)

    root = T.empty("brahim_root", (0, 0, 0))
    body = T.empty("brahim_corps", (0, 0, 0), root)

    # --- corps en poire : chemise en haut, pantalon en bas
    T.lathe("br_torse", shirt, [
        (0.0, 0.70), (0.40, 0.70), (0.47, 0.80), (0.46, 0.92), (0.41, 1.03),
        (0.33, 1.13), (0.24, 1.20), (0.14, 1.24), (0.0, 1.25)], scale=(1, 0.86, 1), parent=body)
    T.lathe("br_bassin", pants, [
        (0.0, 0.50), (0.30, 0.50), (0.40, 0.56), (0.445, 0.64), (0.45, 0.72), (0.0, 0.72)],
        scale=(1, 0.86, 1), parent=body)
    T.lathe("br_ceinture", belt, [
        (0.455, 0.68), (0.465, 0.69), (0.465, 0.73), (0.455, 0.74)],
        scale=(1, 0.86, 1), parent=body, outline=False)
    T.sphere("br_boucle", T.toon("br_boucle_m", "#D8B04A", levels=2), (0, -0.405, 0.71), 0.035,
             scale=(1.3, 0.4, 0.9), parent=body, width=0.006)
    # boutons tendus (la chemise est trop serrée)
    for i, z in enumerate((0.80, 0.92, 1.03, 1.12)):
        r = {0.80: 0.47, 0.92: 0.46, 1.03: 0.41, 1.12: 0.335}[z]
        T.sphere(f"br_bouton_{i}", button, (0, -r * 0.86 - 0.004, z), 0.018,
                 scale=(1, 0.35, 1), parent=body, outline=False, seg=12)
    # poche + 2 stylos (fonctionnaire)
    T.box("br_poche", shirt, (-0.2, -0.345, 1.03), (0.14, 0.02, 0.12), parent=body, width=0.005)
    T.limb("br_stylo_b", pen_b, (-0.225, -0.35, 1.04), (-0.225, -0.35, 1.13), 0.012, parent=body, width=0.005)
    T.limb("br_stylo_r", pen_r, (-0.185, -0.35, 1.04), (-0.18, -0.35, 1.115), 0.012, parent=body, width=0.005)
    # col
    T.lathe("br_col", shirt, [(0.15, 1.21), (0.17, 1.24), (0.14, 1.27), (0.12, 1.25)], parent=body, width=0.008)

    # --- jambes courtes + chaussures
    for s, side in ((-1, "G"), (1, "D")):
        T.limb(f"br_jambe_{side}", pants, (s * 0.18, 0, 0.10), (s * 0.2, 0, 0.55), 0.12, 0.14, parent=body)
        T.sphere(f"br_chaussure_{side}", shoes, (s * 0.19, -0.06, 0.06), 0.1, scale=(1.05, 1.6, 0.6), parent=body)

    # --- bras : pivot à l'épaule, manche courte, avant-bras peau, main
    for s, side in ((-1, "G"), (1, "D")):
        sh = T.empty(f"brahim_epaule_{side}", (s * 0.38, 0, 1.08), body)
        T.limb(f"br_manche_{side}", shirt, (s * 0.38, 0, 1.08), (s * 0.48, 0, 0.88), 0.1, 0.09, parent=sh)
        T.limb(f"br_avantbras_{side}", skin, (s * 0.48, 0, 0.88), (s * 0.53, -0.02, 0.66), 0.06, 0.055, parent=sh)
        T.sphere(f"br_main_{side}", skin, (s * 0.54, -0.03, 0.6), 0.075, scale=(0.9, 0.8, 1.05), parent=sh)

    # --- tête : grosse, ronde, légèrement en œuf
    head = T.empty("brahim_tete", (0, 0, 1.25), body)
    hz = 1.53
    T.sphere("br_tete", skin, (0, 0, hz), 0.30, scale=(1, 0.95, 1.04), parent=head)
    for s, side in ((-1, "G"), (1, "D")):
        T.sphere(f"br_oreille_{side}", skin, (s * 0.3, 0.02, hz - 0.01), 0.06, scale=(0.5, 0.8, 1.1), parent=head)
        # couronne de cheveux (crâne dégarni)
        T.sphere(f"br_cheveux_{side}", hair, (s * 0.25, 0.08, hz + 0.06), 0.11,
                 scale=(0.55, 1.2, 0.8), parent=head)
    T.sphere("br_cheveux_nuque", hair, (0, 0.2, hz + 0.04), 0.17, scale=(1.35, 0.55, 0.65), parent=head)
    # yeux ronds, pupilles simples
    for s, side in ((-1, "G"), (1, "D")):
        T.sphere(f"br_oeil_{side}", white, (s * 0.1, -0.235, hz + 0.05), 0.075, scale=(1, 0.75, 1.15),
                 parent=head, width=0.008)
        T.sphere(f"br_pupille_{side}", black, (s * 0.1, -0.29, hz + 0.045), 0.03, scale=(1, 0.5, 1.2),
                 parent=head, outline=False, seg=16)
        # sourcils épais, légèrement inclinés
        b = T.limb(f"br_sourcil_{side}", hair, (s * 0.04, -0.27, hz + 0.155), (s * 0.165, -0.24, hz + 0.17),
                   0.022, 0.018, parent=head, width=0.006)
    # gros nez rond
    T.sphere("br_nez", skin, (0, -0.3, hz - 0.03), 0.085, scale=(1, 0.9, 0.95), parent=head)
    # bouche (forme de repos ; les visèmes remplaceront cet objet)
    T.sphere("br_bouche_repos", mouth_m, (0, -0.232, hz - 0.17), 0.06, scale=(1.3, 0.25, 0.45),
             parent=head, width=0.006)
    # moustache épaisse : un seul boudin continu, plus épais au centre
    pts = []
    n = 9
    for i in range(n):
        t = -1 + 2 * i / (n - 1)
        pts.append((0.21 * t, -0.315 + 0.13 * t * t, hz - 0.1 - 0.075 * t * t, 1.0 - 0.45 * t * t))
    T.tube("br_moustache", hair, pts, 0.055, parent=head, width=0.008)
    root.location = loc  # placé après construction : les pièces suivent
    return root


if __name__ == "__main__":
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build()
    out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
