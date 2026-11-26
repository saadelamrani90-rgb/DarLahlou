"""Construit Si Lhssen, le semsar (v1) à partir de bible/lhssen.json.
Rig par objets : lhssen_root > corps > tete / epaule_G / epaule_D.
Trois téléphones : un à l'oreille (main D), un dans la main G, un dans la poche.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(loc=(0, 0, 0)):
    pal = json.load(open(os.path.join(ROOT, "bible", "lhssen.json")))["palette_hex"]
    acc = pal["accents"]
    skin = T.toon("sl_peau", pal["peau"])
    suit = T.toon("sl_costume", pal["dominante_1_costume"])
    shirt = T.toon("sl_chemise", pal["dominante_2_chemise"])
    dark = T.toon("sl_cheveux", pal["dominante_3_cheveux_chaussures"], levels=2)
    gold = T.toon("sl_or", acc["chaine_or"], levels=2)
    glasses = T.flat("sl_lunettes", acc["lunettes"])
    white = T.toon("sl_blanc_oeil", "#FFFFFF", levels=2)
    black = T.flat("sl_pupille", "#140C08")
    lips = T.flat("sl_bouche", "#6E2A24")
    phones = [T.toon(f"sl_tel_{i}", c, levels=2) for i, c in enumerate(acc["telephones"])]

    root = T.empty("lhssen_root", (0, 0, 0))
    body = T.empty("lhssen_corps", (0, 0, 0), root)

    # jambes longues et maigres, pantalon trop long qui tire-bouchonne
    for s, side in ((-1, "G"), (1, "D")):
        T.limb(f"sl_jambe_{side}", suit, (s * 0.12, 0, 0.12), (s * 0.13, 0, 0.88), 0.1, 0.11, parent=body)
        T.sphere(f"sl_ourlet_{side}", suit, (s * 0.12, -0.02, 0.1), 0.13, scale=(1, 1, 0.45), parent=body)
        T.sphere(f"sl_chaussure_{side}", dark, (s * 0.13, -0.12, 0.04), 0.08, scale=(0.9, 2.3, 0.5), parent=body)

    # veste trop grande : épaules qui débordent
    T.lathe("sl_veste", suit, [
        (0.0, 0.78), (0.34, 0.78), (0.36, 0.90), (0.35, 1.15), (0.37, 1.30), (0.46, 1.37),
        (0.44, 1.42), (0.28, 1.45), (0.12, 1.48), (0.0, 1.48)], scale=(1, 0.68, 1), parent=body)
    # chemise bordeaux ouverte + chaîne en or
    T.sphere("sl_chemise", shirt, (0, -0.235, 1.33), 0.12, scale=(0.95, 0.3, 1.4), parent=body, outline=False)
    lapel = T.toon("sl_revers", "#9C7A47")
    for s in (-1, 1):  # revers de la veste qui forment le V
        T.tube(f"sl_revers_{s}", lapel, [(s * 0.15, -0.215, 1.47, 1.0), (s * 0.08, -0.262, 1.3, 1.0),
                                          (s * 0.01, -0.268, 1.16, 0.6)], 0.035, parent=body, width=0.006)
    T.tube("sl_chaine", gold, [(-0.07, -0.26, 1.45, 1), (-0.045, -0.28, 1.35, 1), (0, -0.285, 1.31, 1),
                               (0.045, -0.28, 1.35, 1), (0.07, -0.26, 1.45, 1)], 0.008, parent=body, outline=False)
    T.sphere("sl_pendentif", gold, (0, -0.29, 1.29), 0.022, scale=(1, 0.4, 1.2), parent=body, outline=False)
    # téléphone n°3 qui dépasse de la poche poitrine
    T.box("sl_poche", suit, (-0.2, -0.235, 1.18), (0.13, 0.02, 0.1), parent=body, width=0.005)
    T.box("sl_tel_poche", phones[2], (-0.2, -0.235, 1.26), (0.08, 0.02, 0.15), parent=body, bevel=0.01, width=0.005)

    # bras G : manche trop longue, téléphone n°2 tenu devant lui
    sh = T.empty("lhssen_epaule_G", (-0.4, 0, 1.36), body)
    T.limb("sl_manche_G1", suit, (-0.4, 0, 1.36), (-0.5, -0.04, 1.02), 0.11, 0.1, parent=sh)
    T.limb("sl_manche_G2", suit, (-0.5, -0.04, 1.02), (-0.36, -0.36, 0.95), 0.1, 0.11, parent=sh)
    T.sphere("sl_main_G", skin, (-0.33, -0.43, 0.96), 0.055, parent=sh, width=0.006)
    T.box("sl_tel_main", phones[1], (-0.3, -0.45, 1.04), (0.09, 0.02, 0.17), parent=sh, bevel=0.01, width=0.005)
    # bras D : téléphone n°1 collé à l'oreille
    sh = T.empty("lhssen_epaule_D", (0.4, 0, 1.36), body)
    T.limb("sl_manche_D1", suit, (0.4, 0, 1.36), (0.52, -0.06, 1.08), 0.11, 0.1, parent=sh)
    T.limb("sl_manche_D2", suit, (0.52, -0.06, 1.08), (0.34, -0.06, 1.6), 0.1, 0.11, parent=sh)
    T.sphere("sl_main_D", skin, (0.3, -0.05, 1.67), 0.055, parent=sh, width=0.006)

    # tête plus étroite, cheveux gominés, regard malin
    head = T.empty("lhssen_tete", (0, 0, 1.48), body)
    hz = 1.73
    T.sphere("sl_tete", skin, (0, 0, hz), 0.26, scale=(0.9, 0.95, 1.1), parent=head)
    T.box("sl_tel_oreille", phones[0], (0.245, -0.02, hz - 0.02), (0.03, 0.09, 0.18), parent=head, bevel=0.01,
          width=0.005)
    T.sphere("sl_cheveux", dark, (0.0, 0.03, hz + 0.08), 0.255, scale=(0.95, 1.0, 0.95), parent=head)
    T.sphere("sl_meche", dark, (-0.06, -0.1, hz + 0.24), 0.09, scale=(1.6, 0.9, 0.55), parent=head)
    T.sphere("sl_oreille_G", skin, (-0.235, 0.02, hz - 0.01), 0.05, scale=(0.5, 0.8, 1.1), parent=head)
    # lunettes noires relevées sur le front
    for s, side in ((-1, "G"), (1, "D")):
        T.sphere(f"sl_verre_{side}", glasses, (s * 0.085, -0.19, hz + 0.19), 0.06, scale=(1.2, 0.35, 0.8),
                 parent=head, width=0.005)
    T.tube("sl_pont", glasses, [(-0.03, -0.215, hz + 0.2, 1), (0, -0.22, hz + 0.205, 1), (0.03, -0.215, hz + 0.2, 1)],
           0.008, parent=head, outline=False)
    for s, side in ((-1, "G"), (1, "D")):
        T.sphere(f"sl_oeil_{side}", white, (s * 0.085, -0.2, hz + 0.04), 0.06, scale=(1, 0.75, 1.1),
                 parent=head, width=0.007)
        T.sphere(f"sl_pupille_{side}", black, (s * 0.085 + 0.012, -0.245, hz + 0.035), 0.025, scale=(1, 0.5, 1.1),
                 parent=head, outline=False, seg=16)
        # paupière mi-close (regard malin)
        T.sphere(f"sl_paupiere_{side}", skin, (s * 0.085, -0.205, hz + 0.065), 0.064, scale=(1.05, 0.8, 0.6),
                 parent=head, width=0.006)
    T.sphere("sl_nez", skin, (0, -0.25, hz - 0.03), 0.055, scale=(0.85, 1.2, 0.9), parent=head, width=0.007)
    # fine moustache crayon (contraste avec celle de Brahim)
    T.tube("sl_moustache", dark, [(-0.1, -0.215, hz - 0.11, 0.5), (-0.04, -0.245, hz - 0.095, 1),
                                  (0.04, -0.245, hz - 0.095, 1), (0.1, -0.215, hz - 0.11, 0.5)],
           0.011, parent=head, outline=False)
    # sourire en coin
    T.tube("sl_bouche_repos", lips, [(-0.07, -0.235, hz - 0.155, 0.6), (0, -0.25, hz - 0.155, 1),
                                     (0.07, -0.23, hz - 0.13, 0.6)], 0.014, parent=head, outline=False)
    root.location = loc  # placé après construction : les pièces suivent
    return root
