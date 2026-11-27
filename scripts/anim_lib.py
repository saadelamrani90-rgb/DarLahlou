"""Outils d'animation économes : lip sync Rhubarb, clignements, poses clés."""
import json

import bpy

# formes de bouche Rhubarb -> (largeur, ouverture) relatives à la bouche de repos
VISEMES = {
    "X": (1.0, 0.6),   # repos
    "A": (0.9, 0.3),   # M B P (fermée)
    "B": (1.0, 1.0),   # consonnes, légèrement ouverte
    "C": (1.1, 1.6),   # E, ouverte
    "D": (1.3, 2.4),   # A, grande ouverte
    "E": (0.8, 1.8),   # O arrondie
    "F": (0.55, 1.1),  # OU / W, en cul de poule
    "G": (1.0, 0.7),   # F V
    "H": (1.0, 1.4),   # L
}


def _constant(obj):
    ad = obj.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves if hasattr(ad.action, "fcurves") else []:
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def set_constant(obj):
    """Interpolation constante (bouche, clignements) : pas de morphing mou."""
    try:
        _constant(obj)
    except Exception:
        pass
    # Blender 5 : actions en couches/slots
    ad = obj.animation_data
    if ad and ad.action:
        for layer in getattr(ad.action, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:
                            k.interpolation = "CONSTANT"


def lipsync(mouth, cues_path, start_frame, fps=24, drop=0.02, fwd=0.0, gain=1.0):
    """Anime l'échelle (et la position verticale) de la bouche selon Rhubarb."""
    base_s = tuple(mouth.scale)
    base_l = tuple(mouth.location)
    cues = json.load(open(cues_path))["mouthCues"]

    def key(frame, shape):
        w, o = VISEMES[shape]
        o2 = 1 + (o - 1) * gain if shape != "X" else o
        mouth.scale = (base_s[0] * w, base_s[1] * (1 + 0.6 * max(o2 - 1, 0)), base_s[2] * o2)
        mouth.location = (base_l[0], base_l[1] - fwd * max(o2 - 1, 0), base_l[2] - drop * (o2 - 1))
        mouth.keyframe_insert("scale", frame=frame)
        mouth.keyframe_insert("location", frame=frame)

    key(1, "X")
    for c in cues:
        key(start_frame + round(c["start"] * fps), c["value"])
    end = start_frame + round(cues[-1]["end"] * fps)
    key(end, "X")
    mouth.scale, mouth.location = base_s, base_l
    set_constant(mouth)
    return end


def blinks(objs, frames, dur=3):
    """Clignements : écrase les yeux (blancs + pupilles) en hauteur."""
    for o in objs:
        s = tuple(o.scale)
        o.keyframe_insert("scale", frame=1)
        for f in frames:
            o.scale = (s[0], s[1], s[2] * 0.08)
            o.keyframe_insert("scale", frame=f)
            o.scale = s
            o.keyframe_insert("scale", frame=f + dur)
        set_constant(o)


def pose(obj, frame, rot=None, loc_delta=None, base=None):
    """Pose clé : rotation (degrés) et/ou décalage de position par rapport à la base."""
    import math
    if rot is not None:
        obj.rotation_euler = tuple(math.radians(a) for a in rot)
        obj.keyframe_insert("rotation_euler", frame=frame)
    if loc_delta is not None:
        b = base if base is not None else tuple(obj.location)
        obj.location = tuple(x + d for x, d in zip(b, loc_delta))
        obj.keyframe_insert("location", frame=frame)
