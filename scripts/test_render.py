import bpy, sys, time
eng = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0,0,1))
m = bpy.data.materials.new("toon"); m.use_nodes=True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.8,0.25,0.1,1)
bpy.context.object.data.materials.append(m)
bpy.ops.object.light_add(type='SUN', location=(3,-3,5))
bpy.ops.object.camera_add(location=(0,-6,1.5), rotation=(1.5708,0,0)); s.camera=bpy.context.object
s.render.engine = eng
if eng=='CYCLES': s.cycles.samples=16; s.cycles.device='CPU'
s.render.resolution_x, s.render.resolution_y = 1920,1080
s.render.filepath=f"/home/user/dar-lahlou/render/tests/test_{eng}.png"
t=time.time(); bpy.ops.render.render(write_still=True); print("RENDER_OK",eng,round(time.time()-t,2),"s")
