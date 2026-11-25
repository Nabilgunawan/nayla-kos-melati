import bpy, sys, math, random
sys.path.insert(0,"/home/claude/ep02")
from lib import *
from mathutils import Vector
C=bpy.context; R="/home/claude/ep02/tex/"; rnd=random.Random(21)
def img(p,cs='sRGB'):
    i=bpy.data.images.load(p,check_existing=True); i.colorspace_settings.name=cs; return i
# ---------------- procedural materials ----------------
def nodes(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; return m,nt,nt.nodes,nt.links,nt.nodes["Principled BSDF"]
def plaster(hexc,grime=0.35,name=None):
    m,nt,N,L,b=nodes(name or f"plester_{hexc}")
    tc=N.new("ShaderNodeTexCoord"); n1=N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value=3.5; n1.inputs["Detail"].default_value=8
    L.new(tc.outputs["Object"],n1.inputs["Vector"])
    sep=N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"],sep.inputs[0])
    mr=N.new("ShaderNodeMapRange"); mr.inputs[1].default_value=-3.0; mr.inputs[2].default_value=0.5; mr.inputs[3].default_value=1.0; mr.inputs[4].default_value=0.0; L.new(sep.outputs[2],mr.inputs[0])
    ad=N.new("ShaderNodeMath"); ad.operation='MULTIPLY_ADD'; L.new(n1.outputs["Fac"],ad.inputs[0]); ad.inputs[1].default_value=0.6; L.new(mr.outputs[0],ad.inputs[2])
    cl=N.new("ShaderNodeMath"); cl.operation='MULTIPLY'; cl.use_clamp=True; L.new(ad.outputs[0],cl.inputs[0]); cl.inputs[1].default_value=grime
    mx=N.new("ShaderNodeMix"); mx.data_type='RGBA'; L.new(cl.outputs[0],mx.inputs["Factor"]); mx.inputs[6].default_value=lin(hexc)
    c=lin(hexc); mx.inputs[7].default_value=(c[0]*0.45,c[1]*0.42,c[2]*0.38,1); L.new(mx.outputs[2],b.inputs["Base Color"])
    n2=N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value=90; bp=N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=0.25
    L.new(n2.outputs["Fac"],bp.inputs["Height"]); L.new(bp.outputs[0],b.inputs["Normal"]); b.inputs["Roughness"].default_value=0.85
    return m
def tiles(c1,c2,grout,scale,rough=0.3,name="keramik",row=0.5,width=0.5,mortar=0.02,offset=0.0,bump=0.4):
    m,nt,N,L,b=nodes(name); tc=N.new("ShaderNodeTexCoord"); br=N.new("ShaderNodeTexBrick"); L.new(tc.outputs["Object"],br.inputs["Vector"])
    br.offset=offset; br.inputs["Scale"].default_value=scale; br.inputs["Color1"].default_value=lin(c1); br.inputs["Color2"].default_value=lin(c2)
    br.inputs["Mortar"].default_value=lin(grout); br.inputs["Mortar Size"].default_value=mortar; br.inputs["Row Height"].default_value=row; br.inputs["Brick Width"].default_value=width
    L.new(br.outputs["Color"],b.inputs["Base Color"]); bp=N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=bump; bp.invert=True
    L.new(br.outputs["Fac"],bp.inputs["Height"]); L.new(bp.outputs[0],b.inputs["Normal"]); b.inputs["Roughness"].default_value=rough; return m
def concrete(hexc="#8E8C86",name="beton",vs=0.6,th=0.012):
    m,nt,N,L,b=nodes(name); tc=N.new("ShaderNodeTexCoord")
    n=N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value=1.2; n.inputs["Detail"].default_value=10; L.new(tc.outputs["Object"],n.inputs["Vector"])
    vo=N.new("ShaderNodeTexVoronoi"); vo.feature='DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value=vs; L.new(tc.outputs["Object"],vo.inputs["Vector"])
    cr=N.new("ShaderNodeMath"); cr.operation='LESS_THAN'; cr.inputs[1].default_value=th; L.new(vo.outputs["Distance"],cr.inputs[0])
    ramp=N.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color=[x*0.55 for x in lin(hexc)[:3]]+[1]; ramp.color_ramp.elements[1].color=lin(hexc)
    L.new(n.outputs["Fac"],ramp.inputs[0])
    mx=N.new("ShaderNodeMix"); mx.data_type='RGBA'; L.new(cr.outputs[0],mx.inputs["Factor"]); L.new(ramp.outputs[0],mx.inputs[6]); mx.inputs[7].default_value=(0.03,0.03,0.03,1)
    L.new(mx.outputs[2],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.9
    bp=N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=0.35; n2=N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value=40
    L.new(n2.outputs["Fac"],bp.inputs["Height"]); L.new(bp.outputs[0],b.inputs["Normal"]); return m
def wood(hexc="#8A5A35",name="kayu"):
    m,nt,N,L,b=nodes(name); tc=N.new("ShaderNodeTexCoord"); w=N.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value=3; w.inputs["Distortion"].default_value=6; w.inputs["Detail"].default_value=4
    L.new(tc.outputs["Object"],w.inputs["Vector"]); ramp=N.new("ShaderNodeValToRGB"); c=lin(hexc); ramp.color_ramp.elements[0].color=(c[0]*0.6,c[1]*0.55,c[2]*0.5,1); ramp.color_ramp.elements[1].color=c
    L.new(w.outputs["Fac"],ramp.inputs[0]); L.new(ramp.outputs[0],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.45; b.inputs["Coat Weight"].default_value=0.3; return m
def imgmat(path,name,emit=0):
    m,nt,N,L,b=nodes(name); t=N.new("ShaderNodeTexImage"); t.image=img(path); L.new(t.outputs[0],b.inputs["Base Color"])
    if emit: L.new(t.outputs[0],b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value=emit
    return m
def glassdark(name,tint="#22303A",emit=None,es=0): return mat(tint,0.08,0.6,emit=emit,es=es,name=name)
# ---------------- base: ep01 sets (Nayla + kamar) ----------------
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep01/ep01_sets.blend")
for cn in ("set_kampus","set_kota"):
    c=bpy.data.collections.get(cn)
    if c:
        for o in list(c.all_objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
for o in list(bpy.data.objects):
    if o.name.startswith(("CAR","OJOL","oj_")) or (o.parent and o.parent.name.startswith(("CAR","OJOL"))): bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.parent is None and o.name.startswith(("c_","p_")): bpy.data.objects.remove(o,do_unlink=True)
sys.path.insert(0,"/home/claude/ep02"); import chars
rigs=chars.build_all((0,-200))     # parked off-stage, positioned per shot later
# ---------------- EXTERIOR KOS (x=100) ----------------
X=newcol("set_luar"); OX=100
def B(*a,**k): k.setdefault("col",X); return box(*a,**k)
road=concrete("#7F7D77","jalan_gang"); plane("x_gang",(70,7),(OX,-6.5,0.0),road,col=X)
grass=plaster("#6E9A4A",0.6,"rumput"); plane("x_tanah",(90,60),(OX,8,-0.02),grass,col=X)
B("x_selokan",(70,0.7,0.25),(OX,-2.75,-0.1),concrete("#5E5C57","selokan"),0.0)
for i in range(18): B("x_grate",(1.6,0.75,0.05),(OX-30+i*3.6,-2.75,0.03),mat("#3A3A3C",0.5,0.2,0.6),0.01)
wall1=plaster("#E8D9B5",0.4,"dinding_kos"); wall_low=plaster("#7A9A8C",0.5,"dinding_bawah")
teras=tiles("#E9E4DA","#DCD6CA","#B9B2A6",1.4,0.25,"keramik_teras",row=0.5,width=0.5)
roofm=tiles("#9C3E26","#8A3520","#5A2214",1.2,0.6,"genteng",row=0.25,width=0.5,mortar=0.04,offset=0.5,bump=0.8)
# building shell
B("x_kos_wall",(20.4,0.4,5.0),(OX,0.2,2.5),wall1,0.03)
B("x_kos_wainscot",(20.45,0.45,1.1),(OX,0.18,0.55),wall_low,0.02)
B("x_kos_body",(20.4,7,5.0),(OX,3.6,2.5),wall1,0.03)
B("x_teras",(21,2.6,0.3),(OX,-1.3,0.15),teras,0.02)
B("x_teras_edge",(21.1,0.25,0.32),(OX,-2.55,0.16),plaster("#9A968E",0.4,"tepi"),0.02)
# roof: main gable + front canopy
for sy,ang in ((1,1),(-1,-1)):
    r=B("x_roof",(21.5,4.6,0.18),(OX,3.6+sy*2.0,6.15),roofm,0.02); r.rotation_euler=(math.radians(-25*sy),0,0)
B("x_ridge",(21.6,0.35,0.3),(OX,3.6,7.15),mat("#7A2E1A",0.6,0.1),0.05)
can=B("x_canopy",(21.4,3.2,0.14),(OX,-1.25,4.75),roofm,0.02); can.rotation_euler=(math.radians(12),0,0)
B("x_gutter",(21.4,0.18,0.18),(OX,-2.85,4.4),mat("#C9C9C6",0.4,0.2,0.3),0.02)
for i in range(5): cyl("x_col",0.14,4.4,(OX-10+i*5,-2.3,2.35),plaster("#F0E6CE",0.2,"tiang"),col=X)
B("x_lisplang",(21.4,0.06,0.35),(OX,-2.86,4.62),mat("#5B3A26",0.5,0.2),0.01)
# units
UNITS=[]
curt=["#E8A0B4","#9FC5E8","#F6D28B","#8E8E7A"]
for u in range(4):
    cx=OX-7.5+u*5; UNITS.append(cx); n=u+1; dusty=(n==4)
    door=wood("#7B4A2A" if not dusty else "#5E4A3A",f"pintu{n}")
    B(f"x_door{n}_frame",(1.55,0.12,3.75),(cx-1.0,-0.03,1.88),mat("#4A2E1C",0.5,0.2),0.02)
    B(f"x_door{n}",(1.3,0.1,3.55),(cx-1.0,-0.07,1.78),door,0.02)
    for zz in (2.6,1.2): B(f"x_door{n}_panel",(0.95,0.03,0.9),(cx-1.0,-0.13,zz),door,0.04)
    sph(f"x_door{n}_knob",0.06,(cx-0.5,-0.18,1.8),mat("#C9A24A",0.2,0,0.9),col=X)
    pl=plane(f"x_no{n}",(0.36,0.36),(cx-1.0,-0.13,3.85),imgmat(R+f"no{n}.png",f"nomor{n}"),rot=(math.radians(90),0,0),col=X)
    # window with frame, glass, curtain, teralis
    B(f"x_win{n}_frame",(1.9,0.14,1.6),(cx+1.2,-0.02,2.55),mat("#F4F1EA",0.4,0.2),0.02)
    gl=B(f"x_win{n}_glass",(1.65,0.04,1.35),(cx+1.2,-0.08,2.55),glassdark(f"kaca{n}","#2B3A44" if not dusty else "#3B3A2E",emit="#FFD89A" if n==3 else ("#40FF70" if dusty else None),es=0.0),0.0)
    B(f"x_win{n}_curtain",(0.8,0.03,1.3),(cx+0.82,-0.05,2.55),plaster(curt[u],0.1,f"gorden{n}"),0.01)
    for k in range(7): B(f"x_win{n}_bar",(0.035,0.035,1.5),(cx+0.42+k*0.26,-0.16,2.55),mat("#2E2E30",0.4,0.3,0.7),0.0)
    for zz in (1.9,3.2): B(f"x_win{n}_rail",(1.75,0.035,0.035),(cx+1.2,-0.16,zz),mat("#2E2E30",0.4,0.3,0.7),0.0)
    B(f"x_win{n}_sill",(2.0,0.3,0.1),(cx+1.2,-0.16,1.72),mat("#D8D2C6",0.6,0.1),0.02)
    # wall sconce + light
    cyl(f"x_sconce{n}",0.12,0.25,(cx+0.15,-0.15,3.85),mat("#FFF3D6",0.3,0,emit="#FFE2A8",es=0.0,name=f"lampu_teras{n}"),rot=(math.radians(90),0,0),col=X)
    bpy.ops.object.light_add(type='POINT',location=(cx+0.15,-0.6,3.7)); l=C.object; l.name=f"L_teras{n}"; l.data.color=(1,0.8,0.55); l.data.energy=0; l.data.use_shadow=False; l.data.shadow_soft_size=0.3; link(l,X)
    if not dusty:
        B(f"x_mat{n}",(1.0,0.6,0.03),(cx-1.0,-0.55,0.31),plaster(["#C0392B","#2E86AB","#7CB342"][u],0.3,f"keset{n}"),0.01)
        for sx,ss in ((0,0),(0.35,0.15)):
            for f2 in (-0.07,0.07): B(f"x_sandal{n}",(0.12,0.32,0.04),(cx-1.6+sx+f2,-0.9-ss,0.33),mat(["#E74C3C","#3498DB","#F1C40F"][u],0.5,0.1),0.04)
        # shoe rack + pot plant + bin
        B(f"x_rack{n}",(0.9,0.35,0.55),(cx+2.1,-0.45,0.58),wood("#9A6B43",f"rak{n}"),0.02)
        for k in range(3): B(f"x_shoe{n}",(0.18,0.3,0.12),(cx+1.8+k*0.3,-0.45,0.92),mat(["#FFFFFF","#222222","#B03A2E","#2C3E50"][rnd.randrange(4)],0.5,0.1),0.04)
        cyl(f"x_pot{n}",0.22,0.4,(cx+0.3,-0.6,0.5),plaster("#A0522D",0.2,"pot"),col=X)
        for k in range(5): sph(f"x_leaf{n}",0.18,(cx+0.3+rnd.uniform(-0.15,0.15),-0.6+rnd.uniform(-0.15,0.15),0.85+k*0.08),mat("#3E8E41",0.5,0.1),scale=(1,1,1.6),col=X)
    else:
        sph("x_melati_pot",0.2,(cx+0.3,-0.55,0.45),plaster("#7A5A45",0.3,"pot_tua"),col=X)
        for k in range(9): sph("x_melati",0.045,(cx+0.3+rnd.uniform(-0.18,0.18),-0.55+rnd.uniform(-0.18,0.18),0.68+rnd.uniform(0,0.15)),mat("#FFFFFF",0.4,0.1),col=X)
        B("x_gembok_hasp",(0.3,0.06,0.08),(cx-0.45,-0.17,1.95),mat("#6B4A2E",0.7,0,0.6),0.01)
        torus("x_gembok",0.07,0.018,(cx-0.45,-0.2,1.86),mat("#7A4A25",0.7,0,0.6),rot=(math.radians(90),0,0),col=X)
        B("x_gembok_body",(0.14,0.07,0.16),(cx-0.45,-0.2,1.74),mat("#6E4426",0.75,0,0.6),0.02)
        for k in range(14): B("x_daun_kering",(0.12,0.08,0.01),(cx-1.6+rnd.uniform(0,2.6),-0.3-rnd.uniform(0,1.6),0.31),mat(rnd.choice(["#8B6B3D","#6E5230","#A0814F"]),0.8,0),0.01).rotation_euler=(0,0,rnd.uniform(0,3))
        #cw=plane("x_sarang",(1.0,1.0),(cx+2.35,-0.2,4.3),mat("#DDDDDD",0.9,0),rot=(math.radians(90),0,math.radians(45)),col=X)
        bpy.ops.object.light_add(type='POINT',location=(cx+1.2,0.6,2.6)); lg=C.object; lg.name="L_hijau"; lg.data.color=(0.25,1,0.4); lg.data.energy=0; lg.data.use_shadow=False; link(lg,X)
    if n==3:
        bpy.ops.object.light_add(type='POINT',location=(cx+1.2,0.8,2.6)); l3=C.object; l3.name="L_kamar3"; l3.data.color=(1,0.8,0.5); l3.data.energy=0; l3.data.use_shadow=False; link(l3,X)
# signboard, meter box, cables, gallon, broom, trash
plane("x_papan",(3.2,0.95),(OX-4.9,-0.02,4.25),imgmat(R+"papan_kos.png","papan"),rot=(math.radians(90),0,0),col=X)
B("x_meteran",(0.5,0.25,0.7),(OX+9.6,-0.15,3.2),mat("#BFC3C7",0.4,0.2,0.4),0.03)
cyl("x_galon",0.28,0.85,(OX-9.2,-0.7,0.75),mat("#9FD3F0",0.05,0.6,name="galon"),col=X)
cyl("x_tong",0.35,0.8,(OX+12.6,-3.6,0.4),mat("#2E7D32",0.5,0.2),col=X)
c=cyl("x_sapu",0.03,1.6,(OX-9.6,-0.3,1.1),wood("#B0884F","gagang"),col=X); c.rotation_euler=(math.radians(12),0,0)
# clothesline area left of kos
cyl("x_jem_p1",0.06,3.2,(OX-13,-1.0,1.6),mat("#888888",0.4,0.2,0.6),col=X); cyl("x_jem_p2",0.06,3.2,(OX-13,3.0,1.6),mat("#888888",0.4,0.2,0.6),col=X)
for z in (3.0,2.7): cyl("x_jem_tali",0.012,4.0,(OX-13,1.0,z),mat("#DDDDDD",0.5,0),rot=(math.radians(90),0,0),col=X)
for k,(cc,hh) in enumerate([("#E57373",1.0),("#64B5F6",0.8),("#FFF176",0.9),("#81C784",1.1)]): B("x_baju",(0.06,0.7,hh),(OX-13,-0.4+k*0.9,3.0-hh/2),plaster(cc,0.15,f"baju{k}"),0.03)
gown=B("x_baju_putih",(0.06,0.8,2.2),(OX-13,2.4,1.9),plaster("#F4F2EC",0.08,"baju_putih"),0.04); gown.hide_render=True
wv=gown.modifiers.new("w","WAVE"); wv.height=0.06; wv.width=0.5; wv.use_normal=True
# Ibu Kos house (attached, x 10..20)
hw=plaster("#F3C987",0.35,"dinding_rumah")
B("x_rumah",(10,9,6.0),(OX+15.3,4.3,3.0),hw,0.03)
B("x_rumah_low",(10.05,0.3,1.0),(OX+15.3,-0.2,0.5),plaster("#B56F3A",0.5,"lis_rumah"),0.02)
for sy in (1,-1):
    r=B("x_roof_r",(10.8,5.6,0.2),(OX+15.3,4.3+sy*2.45,7.0),tiles("#5E6E7A","#566570","#2E3840",1.2,0.6,"genteng_abu",row=0.25,mortar=0.04,offset=0.5,bump=0.8),0.02); r.rotation_euler=(math.radians(-27*sy),0,0)
B("x_rumah_teras",(9.6,3.2,0.35),(OX+15.3,-1.6,0.17),tiles("#B8604A","#A9553F","#7A3A2A",1.6,0.35,"teraso",row=0.5,width=0.5),0.02)
for k in (0,1): B(f"x_rdoor{k}",(0.9,0.1,3.7),(OX+13.9+k*0.95,-0.12,1.95),wood("#5A3520","pintu_rumah"),0.02)
for wx in (OX+11.4,OX+18.2):
    B("x_rwin_f",(2.2,0.14,1.9),(wx,-0.1,2.7),mat("#FFFFFF",0.4,0.2),0.02); B("x_rwin_g",(1.95,0.05,1.65),(wx,-0.16,2.7),glassdark("kaca_rumah","#30414C",emit="#FFE0A8",es=0.0),0.0)
    B("x_rwin_c",(0.9,0.03,1.6),(wx-0.5,-0.13,2.7),plaster("#C8A2C8",0.1,"gorden_rumah"),0.01)
plane("x_no12",(0.6,0.3),(OX+12.6,-0.14,3.95),imgmat(R+"no12.png","no12"),rot=(math.radians(90),0,0),col=X)
for k in (0,1): B("x_kursi",(0.8,0.8,0.12),(OX+16.8+k*1.4,-1.5,0.9),wood("#6D4C2F","kursi"),0.04); B("x_kursi_back",(0.8,0.1,0.9),(OX+16.8+k*1.4,-1.1,1.35),wood("#6D4C2F","kursi"),0.03)
cyl("x_meja",0.45,0.08,(OX+17.5,-1.9,1.0),wood("#6D4C2F","kursi"),col=X); cyl("x_meja_kaki",0.06,0.65,(OX+17.5,-1.9,0.65),mat("#333333",0.4,0.2),col=X)
cyl("x_sangkar",0.3,0.6,(OX+19.2,-0.6,3.6),mat("#C8A25A",0.4,0.2,0.4),col=X); sph("x_burung",0.1,(OX+19.2,-0.6,3.55),mat("#F1C40F",0.4,0.2),col=X)
for k in range(9): B("x_pagar",(0.08,0.08,1.4),(OX+10.6+k*1.15,-3.2,0.7),mat("#2F3B45",0.4,0.3,0.6),0.01)
for z in (0.4,1.25): B("x_pagar_rail",(9.4,0.06,0.06),(OX+15.2,-3.2,z),mat("#2F3B45",0.4,0.3,0.6),0.01)
# motorbike
bpy.ops.object.empty_add(location=(OX+20.5,-1.6,0)); mb=C.object; mb.name="MOTOR"; link(mb,X)
for p in [B("mb_body",(1.7,0.45,0.55),(OX+20.5,-1.6,0.85),mat("#C0392B",0.25,0.6),0.18),cyl("mb_w1",0.38,0.15,(OX+21.3,-1.6,0.38),mat("#1D1D1D",0.6,0),rot=(math.radians(90),0,0),col=X),
          cyl("mb_w2",0.38,0.15,(OX+19.7,-1.6,0.38),mat("#1D1D1D",0.6,0),rot=(math.radians(90),0,0),col=X),B("mb_seat",(0.9,0.42,0.14),(OX+20.3,-1.6,1.18),mat("#1E1E1E",0.4,0.3),0.06),
          B("mb_handle",(0.1,0.8,0.08),(OX+21.2,-1.6,1.45),mat("#333333",0.3,0.3,0.6),0.02)]: p.parent=mb
# mango tree + bushes
cyl("x_trunk",0.35,4.5,(OX+24,3,2.25),wood("#6B4A2B","batang"),col=X)
for k in range(7): sph("x_canopy",rnd.uniform(1.6,2.2),(OX+24+rnd.uniform(-1.4,1.4),3+rnd.uniform(-1.2,1.2),5.2+rnd.uniform(-0.5,1.2)),plaster("#3F7A35",0.5,"daun"),col=X)
for k in range(10): sph("x_semak",rnd.uniform(0.5,0.8),(OX-16+rnd.uniform(-2,2)+k*0.1,rnd.uniform(-1.5,5),0.4),plaster("#4C8A3B",0.5,"semak"),scale=(1,1,0.7),col=X)
# neighbor houses across the gang (facing +y)
for k,(hx,colr,rc) in enumerate([(OX-14,"#BFD8E8","#6B4F3A"),(OX-2,"#F2B8A2","#8A3A28"),(OX+10,"#D7E8B8","#4E5B66"),(OX+22,"#EBD7F5","#7A3828")]):
    B(f"n_rumah{k}",(10.5,8,5.2),(hx,-15.5,2.6),plaster(colr,0.45,f"tetangga{k}"),0.03)
    for sy in (1,-1):
        r=B(f"n_roof{k}",(11.2,5,0.2),(hx,-15.5+sy*2.2,6.0),tiles("#9C3E26","#8A3520","#5A2214",1.2,0.6,"genteng",row=0.25,mortar=0.04,offset=0.5,bump=0.8) if k%2==0 else tiles("#5E6E7A","#566570","#2E3840",1.2,0.6,"genteng_abu",row=0.25,mortar=0.04,offset=0.5,bump=0.8),0.02); r.rotation_euler=(math.radians(-27*sy),0,0)
    B(f"n_door{k}",(1.4,0.12,3.4),(hx-2,-11.45,1.7),wood(["#5A3520","#7B4A2A","#3E2A1A","#6B3F25"][k],f"npintu{k}"),0.02)
    for wx in (hx+1.2,hx+3.5):
        B(f"n_winf{k}",(1.8,0.14,1.5),(wx,-11.45,2.5),mat("#FFFFFF",0.4,0.2),0.02); B(f"n_wing{k}",(1.55,0.05,1.25),(wx,-11.38,2.5),glassdark(f"nkaca{k}","#2A3946",emit="#FFD9A0",es=0.0),0.0)
    B(f"n_ac{k}",(0.9,0.35,0.6),(hx+4.6,-11.3,4.0),mat("#ECECEC",0.4,0.2),0.04)
    for j in range(8): B(f"n_pagar{k}",(0.07,0.07,1.3),(hx-4.5+j*1.2,-10.0,0.65),mat(["#1E2A33","#5B2C2C","#2C3E50","#3E3E3E"][k],0.4,0.3,0.6),0.01)
    B(f"n_rail{k}",(9.0,0.06,0.06),(hx-0.3,-10.0,1.1),mat(["#1E2A33","#5B2C2C","#2C3E50","#3E3E3E"][k],0.4,0.3,0.6),0.01)
    cyl(f"n_pot{k}",0.25,0.45,(hx+3,-10.5,0.22),plaster("#A0522D",0.2,"pot"),col=X); sph(f"n_plant{k}",0.45,(hx+3,-10.5,0.8),plaster("#4C8A3B",0.5,"semak"),col=X)
# power poles, cables, street lamp
for px in (OX-20,OX+2,OX+24):
    cyl("x_tiang",0.13,9,(px,-3.5,4.5),concrete("#9A9893","tiang_listrik"),col=X); B("x_tiang_arm",(0.12,1.6,0.12),(px,-3.5,8.5),mat("#555555",0.4,0.2,0.6),0.01)
for i in range(2):
    a=Vector((OX-20+i*22,-3.0,8.4)); b2=Vector((OX+2+i*22,-3.0,8.4))
    for dy in (0,-0.9):
        cd=bpy.data.curves.new("kabel","CURVE"); cd.dimensions='3D'; cd.bevel_depth=0.018; sp=cd.splines.new('BEZIER'); sp.bezier_points.add(2)
        mid=(a+b2)/2+Vector((0,dy,-1.1))
        for bp,co in zip(sp.bezier_points,[a+Vector((0,dy,0)),mid,b2+Vector((0,dy,0))]): bp.co=co; bp.handle_left_type=bp.handle_right_type='AUTO'
        o=bpy.data.objects.new("x_kabel",cd); X.objects.link(o); cd.materials.append(mat("#151515",0.6,0))
cyl("x_lampujalan",0.08,6,(OX-6,-3.3,3),mat("#3A3A3A",0.4,0.2,0.6),col=X); B("x_lampu_arm",(0.1,1.4,0.1),(OX-6,-3.9,6.0),mat("#3A3A3A",0.4,0.2,0.6),0.01)
sph("x_lampu_head",0.22,(OX-6,-4.6,5.9),mat("#FFF2D0",0.2,0,emit="#FFE0A0",es=0.0,name="lampu_jalan"),scale=(1.4,1,0.6),col=X)
bpy.ops.object.light_add(type='POINT',location=(OX-6,-4.6,5.6)); lj=C.object; lj.name="L_jalan"; lj.data.color=(1,0.78,0.5); lj.data.energy=0; lj.data.use_shadow=False; link(lj,X)
# a cat sleeping by Nayla's door (detail)
sph("x_kucing",0.28,(UNITS[2]-0.2,-1.0,0.5),mat("#E3A35B",0.5,0.2),scale=(1.4,0.9,0.7),col=X); sph("x_kucing_kepala",0.18,(UNITS[2]+0.15,-1.05,0.62),mat("#E3A35B",0.5,0.2),col=X)
# ---------------- KAMAR 4 interior (x=50) ----------------
K4=newcol("set_kamar4"); KX=50
dust=concrete("#7A7468","lantai_debu",vs=2.2,th=0.006)
box("k4_floor",(7,7,0.2),(KX,0.5,-0.1),dust,0.02,K4)
w4=plaster("#8F9A86",0.9,"dinding_kusam")
for nm,sz,lc in [("k4_wb",(7,0.3,5.5),(KX,4.1,2.75)),("k4_wl",(0.3,7,5.5),(KX-3.6,0.5,2.75)),("k4_wr",(0.3,7,5.5),(KX+3.6,0.5,2.75))]: box(nm,sz,lc,w4,0.02,K4)
cl=box("k4_ceiling",(7.4,7.4,0.2),(KX,0.5,5.6),w4,0.0,K4)
box("k4_neon_holder",(1.6,0.12,0.12),(KX+0.6,3.85,4.6),mat("#DDDDDD",0.4,0.2),0.02,K4)
cyl("k4_neon",0.05,1.4,(KX+0.6,3.75,4.5),mat("#C8FFD0",0.1,0,emit="#50FF7A",es=0.0,name="neon_hijau"),rot=(0,math.radians(90),0),col=K4)
bpy.ops.object.light_add(type='POINT',location=(KX+0.6,3.2,4.3)); ln=C.object; ln.name="L_neon"; ln.data.color=(0.3,1,0.45); ln.data.energy=0; ln.data.use_shadow=False; link(ln,K4)
box("k4_bedframe",(2.4,3.4,0.5),(KX-2.1,2.2,0.25),wood("#4E3B2C","kayu_tua"),0.04,K4)
for k in range(4): box("k4_slat",(2.3,0.12,0.06),(KX-2.1,1.0+k*0.8,0.53),wood("#4E3B2C","kayu_tua"),0.01,K4)
c2=box("k4_chair",(0.9,0.9,0.1),(KX+2.2,1.2,0.9),wood("#4E3B2C","kayu_tua"),0.02,K4); c2.rotation_euler=(0,math.radians(12),math.radians(20))
for k in range(5): box("k4_kardus",(rnd.uniform(0.6,1.0),rnd.uniform(0.5,0.8),rnd.uniform(0.4,0.7)),(KX+1.6+rnd.uniform(-0.3,0.9),3.2+rnd.uniform(-0.3,0.3),0.3+k*0.45),plaster("#A07A4C",0.5,"kardus"),0.02,K4).rotation_euler=(0,0,rnd.uniform(-0.3,0.3))
for k in range(0): plane("k4_sarang",(1.2,1.2),(KX+rnd.choice([-3.4,3.4]),rnd.uniform(-1,3.8),rnd.uniform(4,5.3)),mat("#CFCFCF",0.9,0),rot=(0,math.radians(90),rnd.uniform(0,1)),col=K4)
box("k4_win",(1.8,0.1,1.4),(KX-1.5,3.95,2.7),glassdark("kaca_kotor","#2B3328"),0.0,K4)
# ---------------- moon / world additions ----------------
wn=C.scene.world.node_tree.nodes; wl=C.scene.world.node_tree.links
e3=wn.new("ShaderNodeTexEnvironment"); e3.image=img(R+"hdri_malam.hdr",'Linear Rec.709'); wl.new(wn["W_MAP"].outputs[0],e3.inputs[0])
wl.new(e3.outputs[0],wn["W_MALAM"].inputs[7])     # malam = HDRI malam (bukan warna polos)
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep02/ep02_sets.blend")
print("SETS2 OK",len(bpy.data.objects))
