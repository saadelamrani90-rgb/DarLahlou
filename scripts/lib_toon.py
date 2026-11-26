"""Bibliothèque commune Dar Lahlou : matériaux toon, contours, primitives.

Le cel shading est simulé par une émission (aucune vraie lumière) : la couleur
dépend du produit scalaire entre la normale et une direction de lumière FIXE.
Résultat : rendu rapide sur CPU, sans bruit ni scintillement, identique d'un plan
à l'autre (un seul « étalonnage » pour tout l'épisode).
"""
import math
import bpy
import bmesh

LIGHT_DIR = (0.45, -0.55, 0.70)  # fixe pour toute la série
OUTLINE_COLOR = (0.08, 0.05, 0.04)
OUTLINE_W = 0.012


def hex2rgb(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    # conversion sRGB -> linéaire (Blender travaille en linéaire)
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


_mats = {}


def toon(name, hexcol, levels=3):
    if name in _mats:
        return _mats[name]
    r, g, b = hex2rgb(hexcol)
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    l = LIGHT_DIR
    n = math.sqrt(sum(x * x for x in l))
    dot.inputs[1].default_value = tuple(x / n for x in l)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "CONSTANT"
    shade = (r * 0.55, g * 0.5, b * 0.6, 1)  # ombre légèrement chaude
    light = (r, g, b, 1)
    cr.elements[0].position = 0.0
    cr.elements[0].color = shade
    cr.elements[1].position = 0.70 if levels >= 3 else 0.5
    cr.elements[1].color = light
    if levels >= 3:
        mid = cr.elements.new(0.45)
        mid.color = (r * 0.8, g * 0.78, b * 0.82, 1)
    # le dot va de -1 à 1 : on le remappe en 0..1
    mp = nt.nodes.new("ShaderNodeMapRange")
    mp.inputs["From Min"].default_value = -1
    mp.inputs["From Max"].default_value = 1
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    L = nt.links.new
    L(geo.outputs["Normal"], dot.inputs[0])
    L(dot.outputs["Value"], mp.inputs["Value"])
    L(mp.outputs["Result"], ramp.inputs[0])
    L(ramp.outputs["Color"], em.inputs[0])
    L(em.outputs[0], out.inputs["Surface"])
    _mats[name] = m
    return m


def flat(name, hexcol):
    """Couleur pleine, sans ombrage (pupilles, fonds)."""
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*hex2rgb(hexcol), 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    _mats[name] = m
    return m


def outline_mat():
    if "outline" in _mats:
        return _mats["outline"]
    m = bpy.data.materials.new("outline")
    m.use_backface_culling = True
    nt = m.node_tree
    nt.nodes.clear()
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*OUTLINE_COLOR, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    L = nt.links.new
    L(geo.outputs["Backfacing"], mix.inputs[0])
    L(em.outputs[0], mix.inputs[1])  # face avant de la coque = contour noir
    L(tr.outputs[0], mix.inputs[2])  # face arrière = transparent
    L(mix.outputs[0], out.inputs["Surface"])
    _mats["outline"] = m
    return m


def add_outline(obj, width=OUTLINE_W):
    """Contour par coque inversée (inverted hull), stable et gratuit à rendre."""
    obj.data.materials.append(outline_mat())
    mod = obj.modifiers.new("outline", "SOLIDIFY")
    mod.thickness = -width
    mod.offset = 1
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = len(obj.data.materials) - 1


def _finish(obj, mat, parent=None, smooth=True, outline=True, width=OUTLINE_W):
    obj.data.materials.append(mat)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    if outline:
        add_outline(obj, width)
    if parent is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj


def new_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    return obj


def sphere(name, mat, loc, r, scale=(1, 1, 1), parent=None, seg=32, **kw):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    o = new_obj(name, bm)
    o.location = loc
    o.scale = scale
    return _finish(o, mat, parent, **kw)


def lathe(name, mat, profile, loc=(0, 0, 0), scale=(1, 1, 1), parent=None, seg=40, **kw):
    """Révolution d'un profil [(rayon, z), ...] autour de l'axe Z."""
    bm = bmesh.new()
    rings = []
    for (rad, z) in profile:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), z)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_obj(name, bm)
    o.location = loc
    o.scale = scale
    return _finish(o, mat, parent, **kw)


def limb(name, mat, p0, p1, r0, r1=None, parent=None, seg=20, **kw):
    """Segment de membre arrondi entre deux points (capsule effilée)."""
    r1 = r0 if r1 is None else r1
    from mathutils import Vector
    a, b = Vector(p0), Vector(p1)
    length = (b - a).length
    prof = []
    steps = 6
    for i in range(steps + 1):  # calotte basse
        t = math.pi / 2 * i / steps
        prof.append((r0 * math.sin(t), -r0 * math.cos(t)))
    for i in range(steps + 1):  # calotte haute
        t = math.pi / 2 * i / steps
        prof.append((r1 * math.cos(t), length + r1 * math.sin(t)))
    o = lathe(name, mat, prof, seg=seg, parent=None, **kw)
    o.location = a
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((b - a).normalized())
    if parent is not None:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o


def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    bpy.context.collection.objects.link(e)
    e.location = loc
    if parent is not None:
        e.parent = parent
    bpy.context.view_layer.update()  # matrix_world à jour pour les enfants
    return e


def setup_render(scene, w=1920, h=1080, bg="#F3EAD8", fps=24):
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 0
    scene.cycles.transparent_max_bounces = 8
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.fps = fps
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("fond")
    nt = world.node_tree
    nt.nodes["Background"].inputs[0].default_value = (*hex2rgb(bg), 1)
    scene.world = world


def tube(name, mat, pts, depth, parent=None, **kw):
    """Boudin continu le long de points (x, y, z, épaisseur relative)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = depth
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for p, (x, y, z, r) in zip(sp.points, pts):
        p.co = (x, y, z, 1)
        p.radius = r
    sp.use_endpoint_u = True
    sp.order_u = 3
    sp.resolution_u = 12
    tmp = bpy.data.objects.new(name + "_crv", cu)
    bpy.context.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return _finish(o, mat, parent, **kw)


def box(name, mat, loc, size, parent=None, bevel=0.01, **kw):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = new_obj(name, bm)
    o.location = loc
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
    return _finish(o, mat, parent, smooth=False, **kw)
