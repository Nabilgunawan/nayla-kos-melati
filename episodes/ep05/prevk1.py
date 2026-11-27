import bpy, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/tmp/w/ep5/ep05_sets.blend')
O=bpy.data.objects; sc=bpy.context.scene; X0=450
m=bpy.data.materials['tv_layar']; nt=m.node_tree; t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load('/tmp/w/ep5/tex/tvframe.png')
nt.links.new(t.outputs[0],nt.nodes['Principled BSDF'].inputs['Emission Color']); nt.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=2.0
for n,e in (('L_k1_lampu',60),('L_k1_fill',60),('L_k1_window',0),('L_tv',40)):
    if n in O: O[n].data.energy=e
for n,loc,rz in (('Nayla_rig',(X0-1.3,-0.1,0.25),-90),('Dimas_rig',(X0-1.3,1.7,0.25),-90)):
    r=O[n]; r.location=loc; r.rotation_euler=(0,0,math.radians(rz))
    for b in r.pose.bones: b.rotation_mode='XYZ'
    for s in ('L','R'): r.pose.bones[f'leg.{s}'].rotation_euler=(math.radians(-80),0,0); r.pose.bones[f'arm.{s}'].rotation_euler=(math.radians(-50),0,0)
cam=O['CAM']; cam.constraints.clear(); cam.location=(X0+3.2,-2.6,3.4); cam.rotation_euler=(Vector((X0-3.6,0.9,1.6))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=20
sc.camera=cam; sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.use_denoising=True
sc.render.resolution_x=405; sc.render.resolution_y=720; sc.render.resolution_percentage=100; sc.frame_set(1)
sc.world.node_tree.nodes['W_BG'].inputs[1].default_value=0.05
sc.render.filepath='/tmp/w/ep5/prev_k1.png'; bpy.ops.render.render(write_still=True); print('OK')
