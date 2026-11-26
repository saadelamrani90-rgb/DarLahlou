"""Line-up : personnages côte à côte, même échelle, + rangée silhouettes.
Usage : python scripts/lineup.py <nom_sortie> perso1 perso2 ..."""
import importlib, math, os, subprocess, sys
import bpy
sys.path.insert(0, os.path.dirname(__file__))
import lib_toon as T
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_name, chars = sys.argv[1], sys.argv[2:]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
T.setup_render(scene, w=1920, h=1080)
step = 1.25
for i, c in enumerate(chars):
    importlib.import_module(f"char_{c}").build(loc=((i - (len(chars) - 1) / 2) * step, 0, 0))
cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = 4.3
cam = bpy.data.objects.new("cam", cd); scene.collection.objects.link(cam)
cam.location = (0, -10, 1.05); cam.rotation_euler = (math.radians(90), 0, 0); scene.camera = cam
tmp = os.path.join(ROOT, "render", "tests"); os.makedirs(tmp, exist_ok=True)
a, b = os.path.join(tmp, "lineup_a.png"), os.path.join(tmp, "lineup_b.png")
scene.render.filepath = a; bpy.ops.render.render(write_still=True)
scene.view_layers[0].material_override = T.flat("silhouette", "#1A1210")
scene.render.filepath = b; bpy.ops.render.render(write_still=True)
out = os.path.join(ROOT, "render", "model_sheets", f"{out_name}.png")
if os.path.exists(out): sys.exit(f"REFUS : {out} existe déjà")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-i", b, "-filter_complex",
                "[0:v][1:v]hstack=inputs=2,scale=3840:-1", out], check=True)
print("SHEET", out)
