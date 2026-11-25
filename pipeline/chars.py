import bpy, sys, math
sys.path.insert(0,"/home/claude/ep02")
from lib import *; from char import *
from mathutils import Vector
def adel_extras(O,HC,add):
    w=mat("#FFFFFF",0.5,0.1)
    add(rbox("Adel_band_collar",(0.5,0.08,0.1),O+Vector((0,-0.30,2.12)),w,0.03))
    add(rbox("Adel_seam_placket",(0.03,0.02,0.85),O+Vector((0,-0.315,1.62)),mat("#D9D4CA",0.5,0),0.01))
    for z in (1.95,1.75,1.55,1.35): add(sph("Adel_seam_btn",0.022,O+Vector((0,-0.33,z)),mat("#BDB6A8",0.3,0.2)))
    st=mat("#7A4A2A",0.4,0.2)
    s=box("Adel_bag_strap",(0.06,0.04,1.25),O+Vector((0.05,-0.33,1.65)),st,0.01); s.rotation_euler=(0,math.radians(-38),0); add(s)
    add(rbox("Adel_bag",(0.42,0.16,0.34),O+Vector((-0.52,-0.12,1.18)),mat("#8B5A33",0.45,0.25),0.06))
def dimas_extras(O,HC,add):
    d=mat("#152C80",0.5,0.1)
    for i,z in enumerate([1.95,1.75,1.55,1.35]): add(rbox(f"Dimas_seam{i}",(1.0-0.04*(3-i),0.64,0.025),O+Vector((0,0,z)),d,0.01))
    add(rbox("Dimas_zip",(0.04,0.02,0.95),O+Vector((0,-0.318,1.66)),mat("#333333",0.4,0.3),0.01))
    t=torus("Dimas_band_hood",0.30,0.10,O+Vector((0,0.03,2.16)),fabric("#1F3FB0")); t.scale=(1.05,0.95,0.85); add(t)
    add(sph("Dimas_band_hoodback",0.40,O+Vector((0,0.30,1.96)),fabric("#1F3FB0"),scale=(0.95,0.25,0.85)))
def ibu_extras(O,HC,add):
    g=mat("#111111",0.25,0.3)
    for sx in (1,-1):
        t=torus(f"Ibu_glass{sx}",0.088,0.013,HC+Vector((sx*0.155,-0.405,0.03)),g,rot=(math.radians(90),0,0)); add(t)
        a=box(f"Ibu_glassarm{sx}",(0.02,0.4,0.02),HC+Vector((sx*0.245,-0.2,0.05)),g,0.005); add(a)
    add(box("Ibu_glassbridge",(0.07,0.02,0.02),HC+Vector((0,-0.41,0.05)),g,0.005))
    add(rbox("Ibu_band_inner",(0.36,0.05,0.75),O+Vector((0,-0.30,1.75)),mat("#2B2B2E",0.5,0.1),0.04))
    add(rbox("Ibu_band_shirt",(0.22,0.06,0.3),O+Vector((0,-0.31,2.0)),mat("#D9D9DC",0.5,0.1),0.03))
    for sx in (1,-1):
        l=rbox(f"Ibu_lapel{sx}",(0.12,0.05,0.62),O+Vector((sx*0.17,-0.315,1.85)),fabric("#6B3FB5"),0.03); l.rotation_euler=(0,math.radians(sx*18),0); add(l)
    for z in (1.55,1.40): add(sph("Ibu_band_btn",0.03,O+Vector((0.12,-0.33,z)),mat("#4A2C80",0.3,0.3)))
CH={
 "Adel":dict(skin="#C9853E",top="#EDE8DE",bottom="#C4B08B",shoes="#1C1C1F",hair=dict(type="hijab",color="#B39470"),extras=[adel_extras]),
 "Dimas":dict(skin="#F2C51F",top="#1F3FB0",bottom="#1A1A1D",shoes="#141416",hair=dict(type="curly",color="#4B2A18"),extras=[dimas_extras]),
 "Ibu":dict(skin="#F2C51F",top="#7E4FC7",bottom="#1E2A4A",shoes="#1A1A22",hair=dict(type="bob",color="#141414"),extras=[ibu_extras]),
 "Kunti":dict(skin="#D9D8D2",top="#F2F0EA",bottom="#F2F0EA",ghost=True,noface=True,hair=dict(type="ghost")),
}
def build_all(base):
    rigs={}
    for i,(n,cfg) in enumerate(CH.items()): rigs[n]=make_char(n,cfg,(base[0]+i*2.2,base[1],0))
    return rigs
if __name__=="__main__":
    bpy.ops.wm.open_mainfile(filepath="/home/claude/nayla/nayla_v1.blend")
    for n in ["floor","key","fill","rim","cam_ortho","cam_p"]:
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True)
    rigs=build_all((2.2,0))
    sc=bpy.context.scene
    w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(1,1,1,1); w.node_tree.nodes["Background"].inputs[1].default_value=0.25
    def area(n,loc,e,s,t=(4.4,0,1.6)):
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=e; l.data.size=s
        l.rotation_euler=(Vector(t)-l.location).to_track_quat('-Z','Y').to_euler()
    area("k",(-2,-9,7),900,5); area("f",(12,-6,3),300,5); area("r",(5,8,6),700,4)
    bpy.ops.mesh.primitive_plane_add(size=60); bpy.context.object.is_shadow_catcher=True
    bpy.ops.object.camera_add(location=(4.4,-15,2.3),rotation=(math.radians(88),0,0)); c=bpy.context.object; c.data.lens=40; sc.camera=c
    sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.cycles.use_denoising=True; sc.render.film_transparent=True
    sc.render.resolution_x=1200; sc.render.resolution_y=560; sc.view_settings.view_transform='Standard'
    sc.render.filepath="/home/claude/ep02/lineup.png"; bpy.ops.render.render(write_still=True)
