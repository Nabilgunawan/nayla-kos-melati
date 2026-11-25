import bpy, sys, math, random
sys.path.insert(0,"/home/claude/ep03")
from lib import *
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep02/ep02_sets.blend")
C=bpy.context; R="/home/claude/ep03/tex/"; rnd=random.Random(5); O=bpy.data.objects
import chars3
chars3.build3((20,-200))
def img(p,cs='sRGB'):
    i=bpy.data.images.load(p,check_existing=True); i.colorspace_settings.name=cs; return i
def imgmat(p,name,rough=0.6,emit=0):
    m=bpy.data.materials.new(name); m.use_nodes=True; t=m.node_tree.nodes.new("ShaderNodeTexImage"); t.image=img(p); b=m.node_tree.nodes["Principled BSDF"]
    m.node_tree.links.new(t.outputs[0],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=rough
    if emit: m.node_tree.links.new(t.outputs[0],b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value=emit
    return m
pl=bpy.data.materials["dinding_kos"]
def plaster(h,g,n): 
    import importlib; return bpy.data.materials.get(n) or mat(h,0.85,0.0,name=n)
tilesm=bpy.data.materials["keramik_teras"]; wood=bpy.data.materials["pintu3"]; roof=bpy.data.materials["genteng"]
# ================= RUANG TAMU IBU KOS (x=150) =================
T=newcol("set_ruangtamu"); X0=150
box("r_floor",(9.4,8.4,0.2),(X0,0.5,-0.1),tilesm,0.02,T)
wall=bpy.data.materials["dinding_rumah"]
for nm,sz,lc in [("r_wb",(9.4,0.3,6),(X0,4.6,3)),("r_wl",(0.3,8.4,6),(X0-4.7,0.5,3)),("r_wr",(0.3,8.4,6),(X0+4.7,0.5,3))]: box(nm,sz,lc,wall,0.02,T)
box("r_lis",(9.3,0.08,0.3),(X0,4.42,0.15),mat("#7A4A2A",0.5,0.2),0.01,T)
c=box("r_ceiling",(9.6,8.6,0.2),(X0,0.5,6.1),mat("#F4F1EA",0.8,0),0.0,T); c.visible_camera=False
sofa=mat("#B5546A",0.7,0.05,name="sofa_bunga")
sn=sofa.node_tree.nodes; vo=sn.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value=6; rr=sn.new("ShaderNodeValToRGB"); rr.color_ramp.elements[0].color=lin("#F2C3CC"); rr.color_ramp.elements[1].position=0.25; rr.color_ramp.elements[1].color=lin("#9E3B55")
sofa.node_tree.links.new(vo.outputs["Distance"],rr.inputs[0]); sofa.node_tree.links.new(rr.outputs[0],sn["Principled BSDF"].inputs["Base Color"])
box("r_sofa_seat",(4.4,1.6,0.6),(X0-0.5,2.6,0.75),sofa,0.15,T); box("r_sofa_back",(4.4,0.5,1.4),(X0-0.5,3.4,1.35),sofa,0.15,T)
for sx in (-1,1): box("r_sofa_arm",(0.5,1.6,1.0),(X0-0.5+sx*2.3,2.6,0.95),sofa,0.15,T)
for k in range(3): box("r_bantal",(0.9,0.3,0.7),(X0-1.9+k*1.4,3.1,1.35),mat(["#F6D28B","#9FC5E8","#C8E6C9"][k],0.8,0),0.12,T)
box("r_kursi",(1.6,1.5,0.6),(X0+3.0,0.6,0.75),sofa,0.15,T); box("r_kursi_back",(0.5,1.5,1.4),(X0+3.6,0.6,1.35),sofa,0.15,T)
for sy in (-1,1): box("r_kursi_arm",(1.6,0.4,1.0),(X0+3.0,0.6+sy*0.75,0.95),sofa,0.12,T)
box("r_meja",(2.6,1.4,0.08),(X0-0.3,0.9,0.95),mat("#CFE8F0",0.05,0.6,name="kaca_meja"),0.02,T)
for x in (-1.4,0.8):
    for y in (0.35,1.45): cyl("r_meja_kaki",0.05,0.9,(X0+x,y,0.45),mat("#5A3A22",0.5,0.2),col=T)
box("r_renda",(1.6,0.9,0.01),(X0-0.3,0.9,1.0),mat("#FFFFFF",0.9,0),0.0,T)
for k,(dx,cc) in enumerate([(-0.7,"#F2D3A0"),(0.0,"#E8B080"),(0.6,"#F6E3B8")]):
    cyl("r_toples",0.18,0.4,(X0-0.3+dx,0.75,1.2),mat("#DDF0FF",0.05,0.5,name="toples"),col=T); cyl("r_toples_isi",0.15,0.25,(X0-0.3+dx,0.75,1.13),mat(cc,0.6,0),col=T)
    cyl("r_toples_tutup",0.19,0.06,(X0-0.3+dx,0.75,1.43),mat("#C0392B",0.4,0.3),col=T)
for k in range(4): cyl("r_gelas",0.08,0.22,(X0-1.1+k*0.6,1.25,1.1),mat("#C87A35",0.2,0.4,name="teh"),col=T)
cyl("r_jam",0.45,0.08,(X0-2.8,4.43,4.6),mat("#6B3F25",0.4,0.3),rot=(math.radians(90),0,0),col=T)
cyl("r_jam_muka",0.38,0.02,(X0-2.8,4.38,4.6),mat("#F8F3E6",0.5,0),rot=(math.radians(90),0,0),col=T)
bpy.ops.object.empty_add(location=(X0-2.8,4.36,4.6)); jp=C.object; jp.name="JAM_JARUM"; link(jp,T)
for nm,L,w in (("r_jarum_m",0.32,0.03),("r_jarum_j",0.22,0.04)):
    j=box(nm,(w,0.01,L),(X0-2.8,4.36,4.6+L/2),mat("#111111",0.4,0),0.0,T); j.parent=jp; j.matrix_parent_inverse=jp.matrix_world.inverted()
box("r_lemari",(2.4,0.8,3.2),(X0+3.2,4.0,1.6),bpy.data.materials.get("kayu") or wood,0.03,T)
box("r_lemari_kaca",(2.1,0.05,2.6),(X0+3.2,3.58,1.8),mat("#CFE8F0",0.05,0.6,name="kaca_lemari"),0.0,T)
for k in range(6): cyl("r_piring",0.25,0.04,(X0+2.45+(k%3)*0.75,3.75,1.0+(k//3)*1.2),mat("#FFFFFF",0.2,0.5),rot=(math.radians(80),0,0),col=T)
box("r_meja_tv",(2.4,0.9,0.9),(X0-3.4,0.4,0.45),bpy.data.materials.get("kayu") or wood,0.03,T)
box("r_tv",(1.4,1.1,1.1),(X0-3.4,0.4,1.5),mat("#2A2A2A",0.4,0.3),0.12,T); box("r_tv_layar",(0.02,0.8,0.85),(X0-2.68,0.4,1.55),mat("#1A2025",0.1,0.6),0.04,T).rotation_euler=(0,0,0)
box("r_karpet",(4.6,3.2,0.03),(X0-0.3,1.1,0.015),mat("#8E3B2E",0.9,0,name="karpet"),0.0,T)
# photos on wall (+ Melati photo frame, texture set later)
fr=mat("#5A3520",0.4,0.3)
for k,(x,z,w,h) in enumerate([(-1.6,4.3,0.9,1.1),(-0.4,4.5,0.8,1.0),(0.8,4.3,0.9,1.1),(1.9,4.6,0.7,0.9)]):
    box(f"r_frame{k}",(w+0.12,0.06,h+0.12),(X0+x,4.42,z),fr,0.01,T)
    plane(f"r_foto{k}",(w,h),(X0+x,4.38,z),imgmat(R+f"foto_keluarga{k%4}.png",f"foto{k}"),rot=(math.radians(90),0,0),col=T)
box("r_frame_melati",(1.25,0.07,1.55),(X0+0.2,4.42,2.75),mat("#C9A24A",0.3,0.3,0.6),0.02,T)
plane("r_foto_melati",(1.1,1.4),(X0+0.2,4.37,2.75),mat("#888888",0.6,0,name="foto_melati"),rot=(math.radians(90),0,0),col=T)
box("r_window",(2.6,0.12,2.2),(X0+4.62,1.0,3.0),mat("#FFFFFF",0.4,0.2),0.02,T).rotation_euler=(0,0,math.radians(90))
for sy in (-1,1): box("r_gorden",(0.15,0.9,2.6),(X0+4.45,1.0+sy*1.2,3.1),mat("#C8A2C8",0.8,0,name="gorden_ruang"),0.02,T)
bpy.ops.object.light_add(type='AREA',location=(X0,-1.5,5.6)); a=C.object; a.name="L_rt_fill"; a.data.size=7; a.data.use_shadow=False; a.rotation_euler=(math.radians(-25),0,0); link(a,T)
bpy.ops.object.light_add(type='AREA',location=(X0+4.3,1.0,3.0)); a=C.object; a.name="L_rt_jendela"; a.data.size=2.2; a.data.use_shadow=False; a.rotation_euler=(0,math.radians(-90),0); a.data.color=(1,0.93,0.82); link(a,T)
# ================= POS RONDA (gang, x≈80) =================
P=newcol("set_posronda"); PX,PY=80.0,-7.2
woodr=bpy.data.materials.get("kayu") or wood
box("pr_bale",(3.6,2.4,0.15),(PX,PY,0.85),woodr,0.02,P)
for sx in (-1,1):
    for sy in (-1,1): box("pr_tiang",(0.15,0.15,3.6),(PX+sx*1.75,PY+sy*1.15,1.8),woodr,0.01,P)
    for sy in (-1,1): box("pr_kaki",(0.12,0.12,0.8),(PX+sx*1.6,PY+sy*1.0,0.4),woodr,0.01,P)
zinc=mat("#9AA0A6",0.35,0.1,0.7,name="seng"); zn=zinc.node_tree.nodes; wv=zn.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value=10; bp=zn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=0.6
zinc.node_tree.links.new(wv.outputs["Fac"],bp.inputs["Height"]); zinc.node_tree.links.new(bp.outputs[0],zn["Principled BSDF"].inputs["Normal"])
r=box("pr_atap",(4.4,3.2,0.06),(PX,PY,3.7),zinc,0.0,P); r.rotation_euler=(math.radians(-10),0,0)
box("pr_dinding",(3.6,0.08,1.0),(PX,PY-1.15,1.4),woodr,0.01,P)
plane("pr_papan",(2.0,0.66),(PX,PY+1.2,3.1),imgmat(R+"papan_ronda.png","papan_ronda"),rot=(math.radians(90),0,math.radians(180)),col=P)
k=cyl("pr_kentongan",0.16,1.0,(PX+1.55,PY+1.0,2.6),woodr,col=P); box("pr_kentongan_lubang",(0.05,0.2,0.6),(PX+1.55,PY+0.84,2.6),mat("#1A1206",0.8,0),0.01,P)
cyl("pr_bohlam_kabel",0.01,0.6,(PX,PY,3.3),mat("#111111",0.5,0),col=P)
sph("pr_bohlam",0.13,(PX,PY,2.95),mat("#FFF4C8",0.2,0,emit="#FFE6A0",es=0.0,name="bohlam"),col=P)
bpy.ops.object.light_add(type='POINT',location=(PX,PY,2.8)); lb=C.object; lb.name="L_bohlam"; lb.data.color=(1,0.82,0.55); lb.data.use_shadow=False; lb.data.energy=0; link(lb,P)
box("pr_catur",(0.8,0.8,0.05),(PX-0.3,PY+0.1,0.95),bpy.data.materials.get("keramik_teras"),0.01,P)
for i in range(10): cyl("pr_bidak",0.05,0.14,(PX-0.6+rnd.uniform(0,0.6),PY-0.2+rnd.uniform(0,0.6),1.05),mat("#111111" if i%2 else "#F2F2F2",0.3,0.3),col=P)
cyl("pr_termos",0.13,0.5,(PX+1.1,PY+0.6,1.17),mat("#C0392B",0.3,0.4),col=P); cyl("pr_gelas",0.07,0.18,(PX+0.8,PY+0.5,1.0),mat("#3B2A1A",0.2,0.4,name="kopi"),col=P)
# buku warga: open book with swappable page
bpy.ops.object.empty_add(location=(PX+0.5,PY-0.3,0.95)); bk=C.object; bk.name="BUKU"; link(bk,P)
cov=box("pr_buku_sampul",(0.9,0.62,0.04),(PX+0.5,PY-0.3,0.95),mat("#4A2A1A",0.6,0.1),0.01,P); cov.parent=bk; cov.matrix_parent_inverse=bk.matrix_world.inverted()
pm=bpy.data.materials.new("halaman"); pm.use_nodes=True; pn=pm.node_tree.nodes; t1=pn.new("ShaderNodeTexImage"); t1.image=img(R+"buku_lama.png"); t2=pn.new("ShaderNodeTexImage"); t2.image=img(R+"buku_baru.png")
mx=pn.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.name="HALAMAN"; pm.node_tree.links.new(t1.outputs[0],mx.inputs[6]); pm.node_tree.links.new(t2.outputs[0],mx.inputs[7]); pm.node_tree.links.new(mx.outputs[2],pn["Principled BSDF"].inputs["Base Color"])
rgh=pn["Principled BSDF"].inputs["Roughness"]; rgh.default_value=0.7
for sx,nm in ((-1,"kiri"),(1,"kanan")):
    pg=plane(f"pr_halaman_{nm}",(0.42,0.58),(PX+0.5+sx*0.215,PY-0.3,0.98),pm,col=P); pg.parent=bk; pg.matrix_parent_inverse=bk.matrix_world.inverted()
for k in range(3): box("pr_sandal",(0.15,0.32,0.04),(PX-1+k*0.6,PY-1.6,0.02),mat(["#2E86AB","#C0392B","#111111"][k],0.5,0.1),0.04,P)
# ================= door plate 3 -> 4 (exterior unit 3) =================
p3=O["x_no3"]
plane("x_no4_bawah",(0.36,0.36),(101.5,-0.125,3.85),imgmat(R+"no4_merah.png","nomor4_merah"),rot=(math.radians(90),0,0),col=bpy.data.collections["set_luar"])
p3.location.y=-0.14
# ================= kamar 4 front wall + door (for flashback break-in) =================
K4=bpy.data.collections["set_kamar4"]; w4=bpy.data.materials["dinding_kusam"]
for nm,sz,lc in [("k4_fl",(3.25,0.3,5.5),(48.0,-3.0,2.75)),("k4_fr",(2.65,0.3,5.5),(52.25,-3.0,2.75)),("k4_ft",(1.4,0.3,1.9),(50.25,-3.0,4.55))]: box(nm,sz,lc,w4,0.02,K4)
d4=box("k4_door",(1.3,0.1,3.55),(50.25,-3.05,1.78),bpy.data.materials["pintu4"],0.02,K4)
bpy.ops.object.empty_add(location=(49.6,-3.05,0)); pv=C.object; pv.name="PIV_k4door"; d4.parent=pv; d4.matrix_parent_inverse=pv.matrix_world.inverted()
# flashlight + phone light
bpy.ops.object.light_add(type='SPOT',location=(0,0,0)); sen=C.object; sen.name="L_senter"; sen.data.spot_size=math.radians(40); sen.data.spot_blend=0.35; sen.data.use_shadow=False; sen.data.energy=0
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep03/ep03_sets.blend"); print("SETS3 OK",len(O))
