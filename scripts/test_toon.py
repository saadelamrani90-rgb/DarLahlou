import bpy, time, math
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def toon(name, rgb):
    m=bpy.data.materials.new(name); nt=m.node_tree; nt.nodes.clear()
    geo=nt.nodes.new("ShaderNodeNewGeometry"); dot=nt.nodes.new("ShaderNodeVectorMath"); dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=(0.5,-0.6,0.62)
    ramp=nt.nodes.new("ShaderNodeValToRGB"); cr=ramp.color_ramp; cr.interpolation='CONSTANT'
    r,g,b=rgb; cr.elements[0].color=(r*.45,g*.45,b*.5,1); cr.elements[0].position=0
    e=cr.elements.new(0.05); e.color=(r*.75,g*.75,b*.8,1); cr.elements[1].position=0.55; cr.elements[1].color=(r,g,b,1)
    em=nt.nodes.new("ShaderNodeEmission"); out=nt.nodes.new("ShaderNodeOutputMaterial")
    L=nt.links.new; L(geo.outputs["Normal"],dot.inputs[0]); L(dot.outputs["Value"],ramp.inputs[0]); L(ramp.outputs["Color"],em.inputs[0]); L(em.outputs[0],out.inputs[0])
    return m
def add(op, mat, **kw):
    op(**kw); o=bpy.context.object; o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o
skin=toon("skin",(0.78,0.5,0.32)); shirt=toon("shirt",(0.9,0.88,0.78)); mous=toon("mous",(0.12,0.08,0.06)); floor=toon("floor",(0.75,0.35,0.2)); wall=toon("wall",(0.2,0.6,0.6))
body=add(bpy.ops.mesh.primitive_uv_sphere_add, shirt, radius=1, location=(0,0,1)); body.scale=(1,0.8,1.15)
add(bpy.ops.mesh.primitive_uv_sphere_add, skin, radius=0.75, location=(0,0,2.6))
m=add(bpy.ops.mesh.primitive_cylinder_add, mous, radius=0.12, depth=0.6, location=(0,-0.68,2.45), rotation=(0,math.pi/2,0)); m.scale=(1,1.6,1)
add(bpy.ops.mesh.primitive_plane_add, floor, size=20)
add(bpy.ops.mesh.primitive_plane_add, wall, size=20, location=(0,4,0), rotation=(math.pi/2,0,0))
bpy.ops.object.camera_add(location=(0,-7,2.2), rotation=(math.radians(88),0,0)); s.camera=bpy.context.object
s.world=bpy.data.worlds.new("w")
s.render.engine='CYCLES'; s.cycles.samples=4; s.cycles.use_denoising=False; s.cycles.max_bounces=0
s.render.use_freestyle=True; s.render.line_thickness=1.2
s.view_settings.view_transform='Standard'
s.render.resolution_x,s.render.resolution_y=1920,1080
s.render.filepath="/home/user/dar-lahlou/render/tests/test_toon_cycles.png"
t=time.time(); bpy.ops.render.render(write_still=True); print("RENDER_OK",round(time.time()-t,2))
