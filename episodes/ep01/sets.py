import bpy, math, random, sys
sys.path.insert(0,"/home/claude/ep01")
from lib import *
from mathutils import Vector
random.seed(7)
bpy.ops.wm.open_mainfile(filepath="/home/claude/nayla/nayla_v1.blend")
C=bpy.context; sc=C.scene
for n in ["floor","key","fill","rim","cam_ortho","cam_p"]:
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o,do_unlink=True)
R="/home/claude/ep01/tex/"
def img(path,cs='sRGB'):
    i=bpy.data.images.load(path,check_existing=True); i.colorspace_settings.name=cs; return i
# ---------- face atlas material ----------
fm=bpy.data.materials["face"]; nt=fm.node_tree; N=nt.nodes; L=nt.links
old=N["FACE"]; mp1=[n for n in N if n.type=='MAPPING'][0]
bsdf=N["Principled BSDF"]; mix0=[n for n in N if n.type=='MIX'][0]; mul0=[n for n in N if n.type=='MATH' and n.operation=='MULTIPLY'][0]
front=[n for n in N if n.type=='MATH' and n.operation=='LESS_THAN'][0]
for n in [old,mix0,mul0]: N.remove(n)
col=lin("#F2C51F"); prev=None
for layer in ["eyes","mouth"]:
    m=N.new("ShaderNodeMapping"); m.name=f"AT_{layer}"; m.inputs["Scale"].default_value=(0.25,0.25,1)
    L.new(mp1.outputs[0],m.inputs[0])
    t=N.new("ShaderNodeTexImage"); t.name=f"TX_{layer}"; t.image=img(R+f"{layer}.png"); t.image.alpha_mode='STRAIGHT'; t.extension='CLIP'; t.interpolation='Cubic'
    L.new(m.outputs[0],t.inputs[0])
    mu=N.new("ShaderNodeMath"); mu.operation='MULTIPLY'; L.new(t.outputs["Alpha"],mu.inputs[0]); L.new(front.outputs[0],mu.inputs[1])
    mx=N.new("ShaderNodeMix"); mx.data_type='RGBA'; L.new(mu.outputs[0],mx.inputs["Factor"])
    if prev is None: mx.inputs[6].default_value=col
    else: L.new(prev.outputs[2],mx.inputs[6])
    L.new(t.outputs["Color"],mx.inputs[7]); prev=mx
L.new(prev.outputs[2],bsdf.inputs["Base Color"])
for nm in ["senyum","tertawa","kaget","kesal","sedih"]:
    i=bpy.data.images.get(nm)
    if i: i.use_fake_user=False

# ---------- foot bones (shoes stay flat when sitting) ----------
rig=bpy.data.objects["Nayla_rig"]; C.view_layer.objects.active=rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); eb=rig.data.edit_bones
for sx,n in ((1,"L"),(-1,"R")):
    b=eb.new(f"foot.{n}"); b.head=(sx*0.24,0,0.18); b.tail=(sx*0.24,-0.35,0.18); b.parent=eb[f"leg.{n}"]
bpy.ops.object.mode_set(mode='OBJECT')
for n in ("L","R"):
    for nm in (f"shoe.{n}",f"sole.{n}"):
        o=bpy.data.objects[nm]; mw=o.matrix_world.copy(); o.parent_bone=f"foot.{n}"; C.view_layer.update(); o.matrix_world=mw
# ---------- props on Nayla ----------
rig=bpy.data.objects["Nayla_rig"]
ph=box("phone",(0.30,0.05,0.52),(0,0,0),mat("#2B2D42",0.3,0.5),0.03)
scr=box("phone_screen",(0.25,0.01,0.44),(0,-0.03,0),mat("#9AD0FF",0.2,0,emit="#BFE3FF",es=1.5),0.01); scr.parent=ph
ph.parent=rig; ph.parent_type='BONE'; ph.parent_bone="hand.R"; ph.location=(0,0.05,-0.15); ph.rotation_euler=(math.radians(90),0,0)
# ---------- WORLD ----------
w=bpy.data.worlds.new("dunia"); sc.world=w; w.use_nodes=True; wn=w.node_tree.nodes; wl=w.node_tree.links; wn.clear()
tc=wn.new("ShaderNodeTexCoord"); mpw=wn.new("ShaderNodeMapping"); mpw.name="W_MAP"; wl.new(tc.outputs["Generated"],mpw.inputs[0])
e1=wn.new("ShaderNodeTexEnvironment"); e1.image=img(R+"hdri_siang.hdr",'Linear Rec.709'); wl.new(mpw.outputs[0],e1.inputs[0])
e2=wn.new("ShaderNodeTexEnvironment"); e2.image=img(R+"hdri_sore.hdr",'Linear Rec.709'); wl.new(mpw.outputs[0],e2.inputs[0])
mA=wn.new("ShaderNodeMix"); mA.data_type='RGBA'; mA.name="W_SORE"; wl.new(e1.outputs[0],mA.inputs[6]); wl.new(e2.outputs[0],mA.inputs[7])
mB=wn.new("ShaderNodeMix"); mB.data_type='RGBA'; mB.name="W_MALAM"; wl.new(mA.outputs[2],mB.inputs[6]); mB.inputs[7].default_value=lin("#0B1430")
bg=wn.new("ShaderNodeBackground"); bg.name="W_BG"; wl.new(mB.outputs[2],bg.inputs[0]); bg.inputs[1].default_value=1.0
out=wn.new("ShaderNodeOutputWorld"); wl.new(bg.outputs[0],out.inputs[0])
# ---------- SUN ----------
bpy.ops.object.light_add(type='SUN',location=(0,0,30)); sun=C.object; sun.name="SUN"; sun.data.angle=math.radians(3)

# ================= KOS =================
K=newcol("set_kos")
def woodmat():
    m=bpy.data.materials.new("lantai_kayu"); m.use_nodes=True; n=m.node_tree.nodes; l=m.node_tree.links
    b=n.new("ShaderNodeTexBrick"); b.inputs["Scale"].default_value=1.2; b.offset=0.5
    b.inputs["Color1"].default_value=lin("#C89A6A"); b.inputs["Color2"].default_value=lin("#B98A5C"); b.inputs["Mortar"].default_value=lin("#8A6440")
    b.inputs["Mortar Size"].default_value=0.01; b.inputs["Brick Width"].default_value=2.2; b.inputs["Row Height"].default_value=0.35
    l.new(b.outputs["Color"],n["Principled BSDF"].inputs["Base Color"]); n["Principled BSDF"].inputs["Roughness"].default_value=0.45
    n["Principled BSDF"].inputs["Coat Weight"].default_value=0.3; return m
box("k_floor",(9.4,8.4,0.2),(0,0.5,-0.1),mat("#C99A68",0.45,0.3),0.02,K)
for i in range(10): box("k_plank",(9.3,0.025,0.01),(0,-3.4+i*0.85,0.003),mat("#9C734B",0.6,0),0.0,K)
plane("k_outside",(40,40),(0,0,-0.22),mat("#B9B1A6",0.9,0),col=K)
wallm=mat("#DCEBD8",0.8,0.0)
for nm,sz,lc in [("k_wall_bl",(2.5,0.3,6),(-3.25,4.55,3)),("k_wall_br",(4.5,0.3,6),(2.25,4.55,3)),("k_wall_bb",(2.0,0.3,2.0),(-1.0,4.55,1.0)),("k_wall_bt",(2.0,0.3,1.6),(-1.0,4.55,5.2)),
                 ("k_wall_l",(0.3,8.4,6),(-4.65,0.5,3)),("k_wall_r",(0.3,8.4,6),(4.65,0.5,3))]:
    box(nm,sz,lc,wallm,0.02,K)
box("k_skirt",(9.0,0.06,0.25),(0,4.38,0.12),mat("#FFFFFF",0.4),0.01,K)
ceil=box("k_ceiling",(9.6,8.6,0.2),(0,0.5,6.1),mat("#F4F1EA",0.8,0),0.0,K); ceil.visible_camera=False
wf=mat("#FFFFFF",0.3,0.3)
for nm,sz,lc in [("k_win_t",(2.2,0.4,0.15),(-1.0,4.45,4.4)),("k_win_b",(2.2,0.5,0.15),(-1.0,4.35,2.0)),("k_win_l",(0.15,0.4,2.5),(-2.05,4.45,3.2)),
                 ("k_win_r",(0.15,0.4,2.5),(0.05,4.45,3.2)),("k_win_m",(0.08,0.3,2.3),(-1.0,4.45,3.2)),("k_win_h",(2.0,0.3,0.08),(-1.0,4.45,3.3))]:
    box(nm,sz,lc,wf,0.02,K)
cur=mat("#F7E3A1",0.7,0)
for sx in (-1,1):
    c=box(f"k_curtain{sx}",(0.7,0.15,3.0),(-1.0+sx*1.45,4.25,3.3),cur,0.02,K)
    wv=c.modifiers.new("wave","WAVE"); wv.height=0.07; wv.width=0.25; wv.speed=0; wv.use_x=True; wv.use_y=False
    sub=c.modifiers.new("sub","SUBSURF"); sub.levels=2; sub.render_levels=2; c.modifiers.move(1,0)
# bed
box("k_bedframe",(2.7,3.5,0.6),(-3.25,2.7,0.3),mat("#A87B53",0.4,0.3),0.06,K)
box("k_mattress",(2.6,3.4,0.35),(-3.25,2.7,0.78),mat("#FFFFFF",0.6,0),0.12,K)
box("k_blanket",(2.75,2.2,0.2),(-3.25,2.1,0.92),mat("#6C9BD2",0.6,0.1),0.1,K)
box("k_pillow",(1.6,0.7,0.35),(-3.25,4.0,1.1),mat("#FFF4E0",0.6,0),0.17,K)
box("k_bear",(0.0,0,0),(0,0,-50),mat("#FFFFFF"),0,K)
# desk + stool
dk=mat("#E8D3B0",0.4,0.3)
box("k_desktop",(2.2,2.9,0.12),(3.4,3.0,1.55),dk,0.03,K)
for x in (2.45,4.3):
    for y in (1.7,4.3): box("k_dleg",(0.12,0.12,1.5),(x,y,0.75),dk,0.02,K)
box("k_stool",(1.0,1.0,0.14),(1.55,2.6,1.0),mat("#E85D75",0.35,0.4),0.07,K)
cyl("k_stoolleg",0.12,0.95,(1.55,2.6,0.47),mat("#444444",0.3,0.3),bev=0.0,col=K)
box("k_laptop",(0.9,1.2,0.06),(3.5,2.6,1.64),mat("#C9CCD3",0.3,0.4,0.6),0.02,K)
scrn=box("k_laptop_scr",(0.05,1.2,0.8),(3.95,2.6,2.05),mat("#C9CCD3",0.3,0.4,0.6),0.02,K); scrn.rotation_euler=(0,math.radians(-12),0)
glow=box("k_laptop_glow",(0.02,1.08,0.68),(3.91,2.6,2.05),mat("#BFDFFF",0.2,0,emit="#CFE6FF",es=3.0,name="layar_laptop"),0.0,K); glow.rotation_euler=(0,math.radians(-12),0)
cyl("k_globe_stand",0.18,0.12,(4.0,4.0,1.67),mat("#C9A227",0.3,0.2,0.8),col=K)
cyl("k_globe_pole",0.03,0.35,(4.0,4.0,1.85),mat("#C9A227",0.3,0.2,0.8),col=K)
gm=bpy.data.materials.new("globe"); gm.use_nodes=True; gt=gm.node_tree.nodes.new("ShaderNodeTexImage"); gt.image=img(R+"peta.png")
gm.node_tree.links.new(gt.outputs[0],gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"]); gm.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value=0.5
g=sph("k_globe",0.32,(4.0,4.0,2.25),gm,col=K)
cyl("k_lamp_base",0.2,0.08,(4.05,1.85,1.65),mat("#F1F1F1",0.3,0.3),col=K)
cyl("k_lamp_arm",0.035,1.1,(4.05,1.85,2.2),mat("#F1F1F1",0.3,0.3),col=K)
cone("k_lamp_shade",0.32,0.12,0.4,(3.85,1.85,2.75),mat("#FFB347",0.4,0.2),K,rot=(0,math.radians(-35),0))
bpy.ops.object.light_add(type='POINT',location=(3.8,1.85,2.55)); dl=C.object; dl.name="L_desklamp"; dl.data.color=(1,0.72,0.42); dl.data.shadow_soft_size=0.25; link(dl,K)
mug=bpy.data.objects.get("mug"); mug.hide_render=False; bpy.data.objects["mug_handle"].hide_render=False; mug.location=(3.0,3.6,1.76); mug.rotation_euler=(0,0,math.radians(120))
# poster + shelf + books
pm=bpy.data.materials.new("poster"); pm.use_nodes=True; pt=pm.node_tree.nodes.new("ShaderNodeTexImage"); pt.image=img(R+"peta.png")
pm.node_tree.links.new(pt.outputs[0],pm.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
pp=plane("k_poster",(2.2,1.4),(3.0,4.38,4.0),pm,rot=(math.radians(90),0,0),col=K)
box("k_shelf",(0.5,2.4,0.08),(4.25,3.0,3.3),dk,0.02,K)
for i,c in enumerate(["#E85D75","#4D96FF","#6BCB77","#FFD93D","#845EC2","#FF9671"]):
    h=random.uniform(0.45,0.65); box(f"k_book{i}",(0.38,0.14,h),(4.25,2.0+i*0.2,3.34+h/2),mat(c,0.5,0.2),0.02,K)
# rug
cyl("k_rug",1.9,0.03,(0,0.2,0.015),mat("#F6C1C7",0.9,0),bev=0.0,col=K)
# door on right wall
box("k_door",(0.12,1.8,4.2),(4.48,-1.6,2.1),mat("#B07A4E",0.4,0.3),0.03,K)
sph("k_doorknob",0.08,(4.38,-0.95,2.0),mat("#D4AF37",0.2,0,0.9),col=K)
# standing fan
fb=mat("#F2F2F2",0.3,0.4); fbl=mat("#7FC8F8",0.3,0.3)
cyl("k_fan_base",0.5,0.12,(-1.3,3.4,0.06),fb,col=K); cyl("k_fan_pole",0.06,2.6,(-1.3,3.4,1.4),fb,col=K)
bpy.ops.object.empty_add(location=(-1.3,3.4,2.75)); fh=C.object; fh.name="FAN_HEAD"; link(fh,K)
mot=sph("k_fan_motor",0.22,(-1.3,3.55,2.75),fb,scale=(1,1.3,1),col=K); mot.parent=fh; mot.matrix_parent_inverse=fh.matrix_world.inverted()
for i,(r,yy) in enumerate([(0.62,3.15),(0.62,3.35)]):
    t=torus(f"k_fan_cage{i}",r,0.025,(-1.3,yy,2.75),fb,rot=(math.radians(90),0,0),col=K); t.parent=fh; t.matrix_parent_inverse=fh.matrix_world.inverted()
bpy.ops.object.empty_add(location=(-1.3,3.25,2.75)); fbe=C.object; fbe.name="FAN_BLADES"; link(fbe,K); fbe.parent=fh; fbe.matrix_parent_inverse=fh.matrix_world.inverted()
for i in range(3):
    a=i*2*math.pi/3; bl=sph(f"k_blade{i}",0.25,(-1.3+0.3*math.cos(a),3.25,2.75+0.3*math.sin(a)),fbl,scale=(1,0.15,0.45),col=K)
    bl.rotation_euler=(0,-a+math.pi/2,0); bl.parent=fbe; bl.matrix_parent_inverse=fbe.matrix_world.inverted()
# rice cooker on cabinet
box("k_cabinet",(1.3,1.1,1.3),(3.7,-1.5,0.65),mat("#FFFFFF",0.4,0.3),0.05,K)
rcm=mat("#FFF7F0",0.25,0.6); cyl("k_rc_body",0.45,0.55,(3.7,-1.5,1.6),rcm,bev=0.08,col=K)
cyl("k_rc_band",0.455,0.12,(3.7,-1.5,1.55),mat("#F38BA0",0.3,0.4),bev=0.02,col=K)
sph("k_rc_lid",0.45,(3.7,-1.5,1.85),rcm,scale=(1,1,0.35),col=K)
box("k_rc_handle",(0.5,0.1,0.08),(3.7,-1.5,2.04),mat("#888888",0.3,0.2),0.03,K)
rcl=sph("k_rc_light",0.05,(3.7,-1.96,1.62),mat("#FF5A36",0.2,0,emit="#FF5A36",es=8.0,name="lampu_rc"),col=K)
# fill lights
bpy.ops.object.light_add(type='AREA',location=(0,-2.5,5.6)); kf=C.object; kf.name="L_kos_fill"; kf.data.size=6; kf.rotation_euler=(math.radians(-30),0,0); link(kf,K)
bpy.ops.object.light_add(type='AREA',location=(-1.0,3.9,3.2)); kw=C.object; kw.name="L_kos_window"; kw.data.size=2.0; kw.data.size_y=2.4; kw.data.shape='RECTANGLE'
kw.rotation_euler=(math.radians(-90),0,0); kw.data.color=(1,0.93,0.82); link(kw,K)
kf.data.use_shadow=False; kw.data.use_shadow=False

# ================= KAMPUS (x=60) =================
P=newcol("set_kampus"); OX=60
plane("p_ground",(50,120),(OX,30,0),mat("#86C35B",0.9,0),col=P)
box("p_path",(50,3.2,0.06),(OX,0.6,0.03),mat("#E3D8C6",0.8,0),0.0,P)
box("p_path2",(3.6,10,0.06),(OX,7,0.03),mat("#E3D8C6",0.8,0),0.0,P)
bm=mat("#F3E9D6",0.6,0.1); gl=mat("#3E5C76",0.1,0.6,emit="#5A7FA3",es=0.3)
box("p_bld",(32,7,10.5),(OX,16,5.25),bm,0.1,P)
box("p_roof",(33,7.6,0.5),(OX,16,10.7),mat("#C0533A",0.5,0.2),0.1,P)
for fl in range(3):
    z=1.8+fl*3.2
    for i in range(12):
        x=OX-14.3+i*2.6
        if abs(x-OX)<2.0 and fl==0: continue
        box("p_win",(1.6,0.2,1.8),(x,12.45,z+0.5),gl,0.03,P)
    box("p_band",(32.2,0.4,0.25),(OX,12.4,z-0.7),mat("#D9C7A6",0.5,0.1),0.02,P)
box("p_door",(3.2,0.3,3.0),(OX,12.45,1.5),mat("#6B4F3A",0.4,0.2),0.03,P)
box("p_canopy",(6,2.5,0.3),(OX,11.4,3.4),mat("#C0533A",0.5,0.2),0.05,P)
for sx in(-1,1): cyl("p_col",0.18,3.3,(OX+sx*2.7,10.4,1.65),bm,col=P)
FL=[("#CE1126","#FFFFFF",None,"h"),("#000000","#DD0000","#FFCE00","h"),("#002395","#FFFFFF","#ED2939","v"),("#009246","#FFFFFF","#CE2B37","v"),("#AE1C28","#FFFFFF","#21468B","h"),("#FFFFFF","#0039A6","#D52B1E","h")]
for i,f in enumerate(FL):
    x=OX-10+i*4
    cyl("p_pole",0.07,8.5,(x,9,4.25),mat("#DDDDDD",0.2,0.2,0.9),col=P); sph("p_poletop",0.14,(x,9,8.55),mat("#D4AF37",0.2,0,0.9),col=P)
    cols=[c for c in f[:3] if c]; n=len(cols)
    for j,c in enumerate(cols):
        if f[3]=="h": o=box("p_flag",(1.9,0.04,1.2/n),(x+0.98,9,7.85-0.6+1.2/n*(n-j-0.5)),mat(c,0.6,0),0.0,P)
        else: o=box("p_flag",(1.9/n,0.04,1.2),(x+0.03+1.9/n*(j+0.5),9,7.85),mat(c,0.6,0),0.0,P)
def tree(name,loc,col,s=1.0):
    cyl(name+"_t",0.25*s,2.2*s,(loc[0],loc[1],1.1*s),mat("#8B5A2B",0.6,0.1),col=col)
    for k in range(3):
        sph(name+"_c",1.3*s*random.uniform(0.8,1.1),(loc[0]+random.uniform(-0.6,0.6)*s,loc[1]+random.uniform(-0.5,0.5)*s,(2.8+k*0.7)*s),mat(random.choice(["#4CAF50","#5DBB63","#43A047"]),0.5,0.2),col=col)
for x,y,s in [(-15,5,1.3),(-9,4,1.0),(9,4.5,1.1),(15,6,1.4),(-20,10,1.5),(21,9,1.5),(-4,24,1.2),(5,-8,1.0),(-12,-6,1.2)]: tree("p_tree",(OX+x,y,0),P,s)
bm2=mat("#8B5A2B",0.5,0.2)
box("p_bench_seat",(3.0,0.9,0.15),(OX+4,3.4,1.0),bm2,0.04,P); box("p_bench_back",(3.0,0.15,0.8),(OX+4,3.85,1.55),bm2,0.04,P)
for sx in(-1,1): box("p_bench_leg",(0.15,0.8,0.95),(OX+4+sx*1.3,3.4,0.47),mat("#333333",0.3,0.3),0.02,P)
for x in(-6,6,14): cyl("p_lamp",0.08,5,(OX+x,2.6,2.5),mat("#333333",0.3,0.3),col=P); sph("p_lamph",0.3,(OX+x,2.6,5.1),mat("#FFF6D5",0.2,0,emit="#FFF2C0",es=0.5),col=P)

# ================= KOTA (x=120) =================
T=newcol("set_kota"); OX=120
box("c_side",(50,4.2,0.25),(OX,-0.1,0.125),mat("#D6CFC4",0.8,0),0.02,T)
box("c_curb",(50,0.25,0.3),(OX,2.0,0.15),mat("#BDB5AA",0.7,0),0.02,T)
box("c_road",(50,8,0.05),(OX,6.1,0.0),mat("#3B3E44",0.85,0),0.0,T)
for i in range(12): box("c_dash",(1.6,0.18,0.02),(OX-23+i*4,6.1,0.04),mat("#F5F5F5",0.6,0),0.0,T)
box("c_side2",(50,3,0.25),(OX,11.6,0.125),mat("#D6CFC4",0.8,0),0.02,T)
plane("c_ground",(50,120),(OX,30,-0.02),mat("#9E9A92",0.9,0),col=T)
def bmat(c):
    m=bpy.data.materials.new("gedung"); m.use_nodes=True; n=m.node_tree.nodes; l=m.node_tree.links; b=n.new("ShaderNodeTexBrick")
    tc=n.new("ShaderNodeTexCoord"); l.new(tc.outputs["Object"],b.inputs["Vector"]); b.inputs["Scale"].default_value=0.5
    b.inputs["Color1"].default_value=lin("#2F4A66"); b.inputs["Color2"].default_value=lin("#FFD58A"); b.inputs["Mortar"].default_value=lin(c)
    b.inputs["Mortar Size"].default_value=0.35; b.inputs["Brick Width"].default_value=1.4; b.inputs["Row Height"].default_value=1.4; b.offset=0
    l.new(b.outputs["Color"],n["Principled BSDF"].inputs["Base Color"]); n["Principled BSDF"].inputs["Roughness"].default_value=0.4
    l.new(b.outputs["Fac"],n["Principled BSDF"].inputs["Emission Strength"]); n["Principled BSDF"].inputs["Emission Color"].default_value=lin("#3A3020")
    return m
x=OX-25
gwin=mat("#35506E",0.08,0.6,emit="#FFD58A",es=0.25)
pal=["#F4A261","#E9C46A","#8ECAE6","#F28482","#B5E48C","#CDB4DB","#FFD6A5","#A0C4FF","#E76F51"]
while x<OX+25:
    wdt=random.uniform(4,8); h=random.uniform(7,26); d=random.uniform(5,9)
    colr=random.choice(pal); bo=box("c_bld",(wdt,d,h),(x+wdt/2,13.5+d/2,h/2),mat(colr,0.55,0.15),0.08,T)
    box("c_bldtop",(wdt+0.3,d+0.3,0.4),(x+wdt/2,13.5+d/2,h+0.2),mat("#EEEEEE",0.5,0.1),0.05,T)
    nx=max(1,int((wdt-0.8)/1.4)); nz=max(1,int((h-1.5)/2.0))
    wn=box("c_win",(0.8,0.12,1.1),(x+0.8+0.4,13.45,1.6),gwin,0.03,T)
    a1=wn.modifiers.new("ax","ARRAY"); a1.count=nx; a1.relative_offset_displace=(1.4/0.8,0,0)
    a2=wn.modifiers.new("az","ARRAY"); a2.count=nz; a2.relative_offset_displace=(0,0,2.0/1.1)
    x+=wdt+random.uniform(0.2,1.5)
for x in range(-22,23,9):
    cyl("c_lamp",0.08,5.5,(OX+x,1.6,2.9),mat("#333333",0.3,0.3),col=T); box("c_lamparm",(1.0,0.1,0.1),(OX+x,2.0,5.6),mat("#333333",0.3,0.3),0.02,T)
    sph("c_lamph",0.22,(OX+x,2.4,5.5),mat("#FFF6D5",0.2,0,emit="#FFE7A8",es=1.5),col=T)
# bus stop
box("c_bs_roof",(4.2,1.8,0.15),(OX+8,0.6,3.8),mat("#2A9D8F",0.4,0.3),0.04,T)
for sx in(-1,1): cyl("c_bs_post",0.07,3.6,(OX+8+sx*1.9,1.2,2.0),mat("#444444",0.3,0.3),col=T)
box("c_bs_bench",(3.4,0.6,0.12),(OX+8,0.3,1.2),mat("#8B5A2B",0.5,0.2),0.03,T)
box("c_bs_back",(4.0,0.1,2.2),(OX+8,-0.3,2.4),mat("#9ED8DB",0.1,0.5),0.02,T)
# cilok cart
cc=mat("#2E86AB",0.4,0.3)
box("c_cart",(2.2,1.2,1.1),(OX-4,0.2,1.15),cc,0.06,T)
box("c_cart_glass",(2.0,1.0,0.7),(OX-4,0.2,2.05),mat("#DDF4FF",0.05,0.6),0.04,T)
for sx in(-1,1): cyl("c_wheel",0.42,0.18,(OX-4+sx*0.7,-0.45,0.65),mat("#222222",0.6,0),rot=(math.radians(90),0,0),col=T)
cyl("c_umb_pole",0.04,2.2,(OX-4,0.2,3.4),mat("#666666",0.3,0.2),col=T)
um=cone("c_umbrella",1.7,0.05,0.7,(OX-4,0.2,4.5),mat("#F94144",0.5,0.2),T)
for i in range(7): sph("c_cilok",0.12,(OX-4.6+i*0.18,0.2+((i%2)*0.15),1.85),mat("#D9B382",0.6,0.1),col=T)
pm1=bpy.data.materials.new("harga"); pm1.use_nodes=True; pn=pm1.node_tree.nodes; pl=pm1.node_tree.links
t1=pn.new("ShaderNodeTexImage"); t1.image=img(R+"harga1.png"); t2=pn.new("ShaderNodeTexImage"); t2.image=img(R+"harga2.png")
pmx=pn.new("ShaderNodeMix"); pmx.data_type='RGBA'; pmx.name="HARGA"; pl.new(t1.outputs[0],pmx.inputs[6]); pl.new(t2.outputs[0],pmx.inputs[7])
pl.new(pmx.outputs[2],pn["Principled BSDF"].inputs["Base Color"])
sign=plane("c_sign",(1.6,0.8),(OX-4,-0.42,1.2),pm1,rot=(math.radians(90),0,0),col=T)
# cars & ojol
def car(name,colr):
    bpy.ops.object.empty_add(location=(0,0,0)); e=C.object; e.name=name; link(e,T)
    parts=[box(name+"_body",(3.2,1.6,0.8),(0,0,0.75),mat(colr,0.25,0.6),0.25,T),box(name+"_cab",(1.9,1.45,0.75),(-0.2,0,1.45),mat("#DDF4FF",0.05,0.6),0.2,T)]
    for sx in(-1,1):
        for sy in(-1,1): parts.append(cyl(name+"_w",0.36,0.25,(sx*1.0,sy*0.75,0.38),mat("#222222",0.6,0),rot=(math.radians(90),0,0),col=T))
    for p in parts: p.parent=e
    return e
for i,c in enumerate(["#E63946","#F1FAEE","#457B9D","#FFB703","#8338EC","#06D6A0"]): car(f"CAR{i}",c)
bpy.ops.object.empty_add(location=(0,0,0)); oj=C.object; oj.name="OJOL"; link(oj,T)
gr=mat("#2DBE60",0.4,0.2)
for p in [box("oj_body",(1.6,0.45,0.5),(0,0,0.85),mat("#333333",0.3,0.4),0.15,T),
          cyl("oj_w1",0.38,0.15,(0.75,0,0.38),mat("#222222",0.6,0),rot=(math.radians(90),0,0),col=T),cyl("oj_w2",0.38,0.15,(-0.75,0,0.38),mat("#222222",0.6,0),rot=(math.radians(90),0,0),col=T),
          box("oj_rider",(0.6,0.6,0.9),(-0.2,0,1.55),gr,0.2,T),sph("oj_helmet",0.35,(-0.1,0,2.25),gr,col=T),box("oj_visor",(0.1,0.45,0.2),(0.22,0,2.25),mat("#222222",0.1,0.6),0.04,T),
          box("oj_box",(0.6,0.55,0.55),(-0.85,0,1.45),gr,0.08,T)]:
    p.parent=oj
# ---------- CAMERA ----------
bpy.ops.object.empty_add(location=(0,0,2)); tg=C.object; tg.name="CAM_TGT"
bpy.ops.object.camera_add(location=(0,-8,2)); cam=C.object; cam.name="CAM"; sc.camera=cam
tr=cam.constraints.new("TRACK_TO"); tr.target=tg; tr.track_axis='TRACK_NEGATIVE_Z'; tr.up_axis='UP_Y'
cam.data.dof.use_dof=True; cam.data.dof.focus_object=tg; cam.data.dof.aperture_fstop=1.4; cam.data.sensor_width=36
# ---------- RENDER defaults (laptop: EEVEE) ----------
sc.render.engine='BLENDER_EEVEE'; sc.eevee.taa_render_samples=24
try: sc.eevee.use_shadows=True
except: pass
sc.render.fps=12; sc.render.resolution_x=1080; sc.render.resolution_y=1920
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Punchy'
sc.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep01/ep01_sets.blend")
print("SETS OK", len(bpy.data.objects))
