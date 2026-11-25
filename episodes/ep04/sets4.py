import bpy, sys, math, random
sys.path.insert(0,"/home/claude/ep04")
from lib import *
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep03/ep03_sets.blend")
C=bpy.context; O=bpy.data.objects; M=bpy.data.materials; R="/home/claude/ep04/tex/"; rnd=random.Random(8)
import chars4; chars4.build4((40,-200))
def img(p): return bpy.data.images.load(p,check_existing=True)
def imgmat(p,name,emit=0):
    m=bpy.data.materials.new(name); m.use_nodes=True; t=m.node_tree.nodes.new("ShaderNodeTexImage"); t.image=img(p); b=m.node_tree.nodes["Principled BSDF"]
    m.node_tree.links.new(t.outputs[0],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.6
    if emit: m.node_tree.links.new(t.outputs[0],b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value=emit
    return m
def L(name,loc,col,kind='POINT',size=None,rot=None,colr=(1,1,1)):
    bpy.ops.object.light_add(type=kind,location=loc); l=C.object; l.name=name; l.data.energy=0; l.data.use_shadow=False; l.data.color=colr
    if size: l.data.size=size
    if rot: l.rotation_euler=rot
    link(l,col); return l
conc=M["jalan_gang"]; seng=M["seng"]; kayu=M.get("kayu") or M["pintu3"]; rumput=M["rumput"]; semak=M["semak"]; daun=M["daun"]
red=mat("#C62828",0.3,0.4,name="sepatu_merah")
# ---- PABRIK (x=200)
P=newcol("set_pabrik"); X=200
box("pb_lantai",(20,14,0.2),(X,2,-0.1),conc,0.0,P)
for nm,sz,lc in [("pb_wb",(20,0.3,7),(X,9,3.5)),("pb_wl",(0.3,14,7),(X-10,2,3.5)),("pb_wr",(0.3,14,7),(X+10,2,3.5))]: box(nm,sz,lc,seng,0.0,P)
c=box("pb_atap",(20.5,14.5,0.2),(X,2,7.1),seng,0.0,P)
for k in range(4):
    rx=X-7+k*4.2
    for lvl in range(4):
        box("pb_rak",(3.2,1.0,0.08),(rx,7.6,0.4+lvl*1.2),mat("#5E6A75",0.5,0.2,0.6),0.01,P)
        for j in range(6): box("pb_sepatu",(0.36,0.75,0.28),(rx-1.3+j*0.52,7.6,0.6+lvl*1.2),mat(rnd.choice(["#3E2723","#1A1A1A","#ECEFF1","#5D4037","#1565C0","#C62828"]),0.4,0.3),0.08,P)
    for sx in (-1.55,1.55): box("pb_tiang_rak",(0.08,1.0,4.8),(rx+sx,7.6,2.4),mat("#5E6A75",0.5,0.2,0.6),0.0,P)
for k in range(3):
    box("pb_meja_jahit",(2.4,1.2,0.1),(X-5+k*4.5,3.0,1.45),mat("#C9B48A",0.5,0.2),0.02,P)
    for sx in (-1,1): box("pb_kaki",(0.1,1.1,1.4),(X-5+k*4.5+sx*1.1,3.0,0.7),mat("#555555",0.4,0.3,0.6),0.0,P)
    box("pb_mesin",(0.9,0.4,0.55),(X-5+k*4.5,3.0,1.78),mat("#2E3B4E",0.3,0.4),0.06,P)
    for j in range(3): box("pb_kardus",(0.9,0.8,0.7),(X-6+k*4.5+j*0.3,4.6,0.35+j*0.7),M.get("kardus") or mat("#A07A4C",0.6,0),0.03,P)
cyl("pb_meja_istirahat",0.9,0.06,(X+6.5,-1.5,1.4),mat("#E53935",0.4,0.2,name="plastik_merah"),col=P); cyl("pb_meja_kaki",0.08,1.4,(X+6.5,-1.5,0.7),mat("#E53935",0.4,0.2),col=P)
for sx in (-1,1): box("pb_kursi",(0.8,0.8,0.08),(X+6.5+sx*1.4,-1.5,0.95),mat("#1E88E5",0.4,0.2),0.05,P)
cyl("pb_termos",0.15,0.55,(X+6.2,-1.3,1.72),mat("#43A047",0.3,0.4),col=P)
box("pb_jam_absen",(0.6,0.25,0.9),(X+9.8,-0.5,3.0),mat("#BDBDBD",0.3,0.3,0.4),0.04,P)
plane("pb_papan",(4.0,0.96),(X,8.82,5.6),imgmat(R+"papan_pabrik.png","papan_pabrik"),rot=(math.radians(90),0,math.radians(180)),col=P)
for k in range(3): L(f"L_pabrik{k}",(X-6+k*6,2,6.6),P,'AREA',4,None,(0.9,0.97,1))
# ---- WARUNG (gang, front of neighbour house 0)
Wc=newcol("set_warung"); WX,WY=86.0,-10.6
box("w_etalase",(2.6,0.9,1.1),(WX,WY,0.55),mat("#6D4C41",0.5,0.2),0.03,Wc)
box("w_kaca",(2.5,0.8,0.7),(WX,WY,1.45),mat("#DDF4FF",0.05,0.6,name="kaca_etalase"),0.02,Wc)
for j in range(14): cyl("w_lilin",0.035,0.35,(WX-1.1+j*0.16,WY-0.1,1.3),mat("#FFFDF5",0.6,0),col=Wc)
for j in range(8): box("w_sachet",(0.18,0.02,0.32),(WX-1.2+j*0.33,WY-0.5,2.6),mat(rnd.choice(["#FFB300","#E53935","#3949AB","#43A047"]),0.4,0.2),0.0,Wc)
cyl("w_tali",0.01,2.8,(WX,WY-0.5,2.8),mat("#222222",0.5,0),rot=(0,math.radians(90),0),col=Wc)
plane("w_papan",(2.8,0.67),(WX,-11.4,3.6),imgmat(R+"papan_warung.png","papan_warung"),rot=(math.radians(90),0,math.radians(180)),col=Wc)
box("w_bangku",(2.0,0.5,0.1),(WX+2.4,WY+0.2,0.8),kayu,0.02,Wc)
L("L_warung",(WX,WY+1.5,3.0),Wc,colr=(1,0.85,0.6))
# ---- SUNGAI & SAWAH (x=250)
S=newcol("set_sungai"); SX=250
plane("sg_tanah",(80,60),(SX,10,0),rumput,col=S)
water=mat("#2E4E4A",0.04,0.0,name="air"); wn=water.node_tree.nodes; nz=wn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value=6; bp=wn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value=0.25
water.node_tree.links.new(nz.outputs["Fac"],bp.inputs["Height"]); water.node_tree.links.new(bp.outputs[0],wn["Principled BSDF"].inputs["Normal"]); wn["Principled BSDF"].inputs["Specular IOR Level"].default_value=0.8
plane("sg_air",(80,7),(SX,2.0,-0.35),water,col=S)
for sy in (-1,1): box("sg_tebing",(80,1.2,0.8),(SX,2.0+sy*4.0,-0.2),M["beton"] if "beton" in M else conc,0.1,S)
plane("sg_dasar",(80,7),(SX,2.0,-0.6),mat("#3B3A30",0.9,0),col=S)
for k in range(26): sph("sg_batu",rnd.uniform(0.2,0.5),(SX+rnd.uniform(-12,12),rnd.choice([-1.7,-2.0,5.8,6.0])+rnd.uniform(-0.4,0.4),0.0),mat(rnd.choice(["#7A7A72","#8E8C84","#6E6A60"]),0.8,0),scale=(1.3,1,0.6),col=S)
batu=sph("sg_batu_besar",0.55,(SX+1.2,-2.3,0.05),mat("#8A877E",0.8,0),scale=(1.6,1.1,0.55),col=S)
for k in range(10):
    bx=SX+rnd.choice([-1,1])*rnd.uniform(4,14); by=rnd.choice([-3.5,7.5])+rnd.uniform(-1,1)
    for j in range(7):
        h=rnd.uniform(6,10); b=cyl("sg_bambu",0.09,h,(bx+rnd.uniform(-0.6,0.6),by+rnd.uniform(-0.6,0.6),h/2),mat("#6E8B3D",0.5,0.2,name="bambu"),col=S); b.rotation_euler=(rnd.uniform(-0.12,0.12),rnd.uniform(-0.12,0.12),0)
    for j in range(5): sph("sg_daun_bambu",rnd.uniform(1.0,1.6),(bx+rnd.uniform(-1.5,1.5),by+rnd.uniform(-1.5,1.5),rnd.uniform(6,9)),daun,scale=(1.4,1.4,0.7),col=S)
for k in range(60): cone("sg_rumput",0.08,0.0,rnd.uniform(0.6,1.3),(SX+rnd.uniform(-15,15),rnd.choice([-2.6,6.6])+rnd.uniform(-1.2,1.2),0.4),mat("#7C9A3E",0.7,0),S)
for j in range(9): box("sg_jembatan",(0.35,8.6,0.08),(SX-8+j*0.38,2.0,0.25),M["bambu"],0.02,S)
for sx in (-1.6,1.6): box("sg_pegangan",(0.06,8.6,0.06),(SX-6.5+sx,2.0,1.1),M["bambu"],0.0,S)
plane("sg_sawah",(40,20),(SX,-18,-0.05),mat("#5A7A4A",0.3,0.3,name="sawah_air"),col=S)
for k in range(28): box("sg_padi",(40,0.18,0.45),(SX,-26+k*0.62,0.2),mat("#7DAA3C",0.7,0),0.0,S)
box("sg_pematang",(40,0.8,0.3),(SX,-8.4,0.1),mat("#6B5233",0.9,0),0.05,S)
# red shoes, bag, incense, flowers on the big rock
for sx in (-0.13,0.13):
    s=box("sg_sepatu",(0.22,0.5,0.18),(SX+1.2+sx,-2.35,0.42),red,0.07,S)
box("sg_tas",(0.55,0.25,0.42),(SX+2.0,-2.4,0.42),mat("#4E342E",0.5,0.2),0.06,S)
cyl("sg_abu",0.15,0.03,(SX+0.4,-2.5,0.4),mat("#3A3A3A",0.9,0),col=S)
for j in range(3): cyl("sg_dupa",0.008,0.25,(SX+0.4+j*0.05,-2.5,0.52),mat("#5D4037",0.7,0),col=S)
for j in range(14): sph("sg_bunga",0.045,(SX+0.7+rnd.uniform(-0.2,0.2),-2.2+rnd.uniform(-0.2,0.2),0.42),mat(rnd.choice(["#E53935","#FFFFFF","#FFEB3B","#F48FB1","#FF9800"]),0.5,0),col=S)
L("L_senter_warga",(SX,-4,3),S,colr=(1,0.95,0.85))
# ---- PASAR (x=300)
Pz=newcol("set_pasar"); PX=300
box("ps_lantai",(10,24,0.2),(PX,0,-0.1),conc,0.0,Pz)
cols=["#E53935","#1E88E5","#43A047","#FB8C00","#8E24AA","#00897B"]
for side in (-1,1):
    for k in range(5):
        y=-9+k*4; x=PX+side*3.0
        box("ps_meja",(2.2,3.2,0.1),(x,y,1.0),kayu,0.02,Pz)
        for sx in (-1,1):
            for sy in (-1,1): box("ps_tiang",(0.08,0.08,3.2),(x+sx*1.0,y+sy*1.5,1.6),mat("#555555",0.4,0.2,0.6),0.0,Pz)
        t=box("ps_terpal",(2.6,3.6,0.03),(x+side*0.2,y,3.25),mat(cols[(k+side)%6],0.7,0),0.0,Pz); t.rotation_euler=(0,math.radians(-side*12),0)
        for j in range(4):
            cyl("ps_keranjang",0.3,0.3,(x+rnd.uniform(-0.6,0.6),y-1.1+j*0.75,1.2),mat("#A1887F",0.8,0),col=Pz)
            for q in range(4): sph("ps_isi",0.11,(x+rnd.uniform(-0.7,0.7),y-1.1+j*0.75+rnd.uniform(-0.15,0.15),1.42),mat(rnd.choice(["#E53935","#FDD835","#43A047","#FB8C00","#8D6E63"]),0.6,0),col=Pz)
SPX,SPY=PX+3.0,7.0
for j in range(40): sph("ps_bunga",0.06,(SPX+rnd.uniform(-0.8,0.8),SPY+rnd.uniform(-1.2,0),1.12),mat(rnd.choice(["#E53935","#FFFFFF","#FFEB3B","#F48FB1"]),0.5,0),col=Pz)
for j in range(10): box("ps_kemenyan",(0.18,0.14,0.08),(SPX+rnd.uniform(-0.8,0.8),SPY+rnd.uniform(0.3,1.2),1.1),mat("#4E342E",0.7,0),0.02,Pz)
plane("ps_papan_lapak",(2.2,0.53),(SPX-1.15,SPY,2.7),imgmat(R+"papan_lapak.png","papan_lapak"),rot=(math.radians(90),0,math.radians(-90)),col=Pz)
for k in range(30):
    h=rnd.uniform(6,10); b=cyl("ps_bambu",0.09,h,(PX+rnd.uniform(-5,5),14+rnd.uniform(0,6),h/2),M["bambu"],col=Pz)
plane("ps_tanah_ujung",(12,10),(PX,16,0),rumput,col=Pz)
L("L_pasar",(PX,0,6),Pz,'AREA',8,None,(1,0.95,0.85))
# ---- GUBUK DUKUN (x=350)
G=newcol("set_gubuk"); GX=350
plane("gb_tanah",(40,40),(GX,0,0),mat("#3B3226",0.9,0,name="tanah_gelap"),col=G)
for k in range(140):
    x=GX+rnd.uniform(-18,18); y=rnd.uniform(-18,18)
    if abs(x-GX)<1.4 and y<6: continue
    if abs(x-GX)<4 and 4<y<10: continue
    h=rnd.uniform(7,12); b=cyl("gb_bambu",0.09,h,(x,y,h/2),M["bambu"],col=G); b.rotation_euler=(rnd.uniform(-0.1,0.1),rnd.uniform(-0.1,0.1),0)
bam=mat("#8D7B5A",0.8,0,name="anyaman"); bn=bam.node_tree.nodes; br=bn.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value=8; br.inputs["Color1"].default_value=lin("#9C8A63"); br.inputs["Color2"].default_value=lin("#7D6B48"); br.inputs["Mortar"].default_value=lin("#4A3B26")
bam.node_tree.links.new(br.outputs["Color"],bn["Principled BSDF"].inputs["Base Color"])
for nm,sz,lc in [("gb_wb",(5,0.15,3.2),(GX,9.5,1.6)),("gb_wl",(0.15,4,3.2),(GX-2.5,7.5,1.6)),("gb_wr",(0.15,4,3.2),(GX+2.5,7.5,1.6)),("gb_wfl",(1.6,0.15,3.2),(GX-1.7,5.5,1.6)),("gb_wfr",(1.6,0.15,3.2),(GX+1.7,5.5,1.6))]: box(nm,sz,lc,bam,0.0,G)
for sy in (-1,1):
    r=box("gb_atap",(5.8,2.8,0.12),(GX,7.5+sy*1.15,3.6),mat("#5D4A2E",0.9,0,name="atap_ijuk"),0.0,G); r.rotation_euler=(math.radians(-28*sy),0,0)
box("gb_tikar",(3.0,2.5,0.03),(GX,7.6,0.02),mat("#C8A96A",0.8,0),0.0,G)
for j in range(12):
    a=j/12*2*math.pi; cx,cy=GX+math.cos(a)*1.0,7.0+math.sin(a)*0.7
    cyl("gb_lilin",0.04,rnd.uniform(0.15,0.3),(cx,cy,0.12),mat("#FFFDF0",0.6,0),col=G); sph("gb_api",0.03,(cx,cy,0.3),mat("#FFB300",0.2,0,emit="#FFB300",es=0.0,name="api_lilin"),scale=(1,1,1.8),col=G)
cyl("gb_nampan",0.35,0.04,(GX+0.9,6.6,0.05),mat("#B08D57",0.3,0.2,0.6),col=G)
for j in range(20): sph("gb_bunga",0.045,(GX+0.9+rnd.uniform(-0.25,0.25),6.6+rnd.uniform(-0.25,0.25),0.1),mat(rnd.choice(["#E53935","#FFFFFF","#FFEB3B","#F48FB1","#FF9800"]),0.5,0),col=G)
box("gb_cermin",(0.9,0.06,1.2),(GX-1.2,9.3,1.2),mat("#D9E3E8",0.02,0.0,1.0),0.03,G)
box("gb_kain",(2.2,0.05,1.4),(GX+0.8,9.35,1.7),mat("#111111",0.9,0),0.0,G)
L("L_lilin",(GX,7.0,0.9),G,colr=(1,0.6,0.25)); L("L_lilin2",(GX+0.8,6.4,0.6),G,colr=(1,0.55,0.2))
# ---- PAPAN PETUNJUK (x=400)
B=newcol("set_papan"); BX=400
box("pp_dinding",(6,0.3,5),(BX,0.4,2.5),M["dinding_kusam"],0.0,B)
cork=mat("#B58A5A",0.9,0,name="gabus"); cn=cork.node_tree.nodes; nn=cn.new("ShaderNodeTexNoise"); nn.inputs["Scale"].default_value=80; cork.node_tree.links.new(nn.outputs["Fac"],cn["Principled BSDF"].inputs["Roughness"])
box("pp_gabus",(3.6,0.06,2.4),(BX,0.22,2.6),cork,0.02,B)
items=[("pp_foto_melati",R+"foto_melati.png",(-1.1,3.2),(0.6,0.75)),("pp_foto_sepatu",R+"foto_sepatu.png",(0.9,3.3),(0.6,0.6)),("pp_peta",R+"peta_kasus.png",(0.0,2.2),(1.2,0.85)),("pp_koran",R+"buku_lama.png",(-1.2,1.8),(0.6,0.8))]
pins={}
for nm,tx,(x,z),(w,h) in items:
    plane(nm,(w,h),(BX+x,0.18,z),imgmat(tx,nm),rot=(math.radians(90),0,0),col=B)
    pins[nm]=Vector((BX+x,0.15,z+h/2-0.06)); sph(nm+"_pin",0.035,pins[nm],mat("#E53935",0.3,0.3),col=B)
for a,b in [("pp_foto_melati","pp_peta"),("pp_foto_sepatu","pp_peta"),("pp_koran","pp_peta"),("pp_foto_melati","pp_foto_sepatu")]:
    cd=bpy.data.curves.new("benang","CURVE"); cd.dimensions='3D'; cd.bevel_depth=0.008; sp=cd.splines.new('POLY'); sp.points.add(1)
    sp.points[0].co=(*pins[a],1); sp.points[1].co=(*pins[b],1); o=bpy.data.objects.new("pp_benang",cd); B.objects.link(o); cd.materials.append(mat("#D32F2F",0.4,0.2))
L("L_papan",(BX,-2.5,3.5),B,'AREA',3,(math.radians(70),0,0),(1,0.95,0.85))
# ---- KAMAR 4 malam kejadian
K4=bpy.data.collections["set_kamar4"]; KX=50
k=box("k4_kasur_terbalik",(2.2,3.2,0.35),(KX-1.9,2.0,0.9),mat("#E8E2D0",0.7,0),0.12,K4); k.rotation_euler=(0,math.radians(-55),0)
for j in range(10):
    a=j/10*2*math.pi; cyl("k4_lilin_ring",0.04,0.08,(KX+0.2+math.cos(a)*0.75,0.6+math.sin(a)*0.75,0.04),mat("#F3EBD8",0.7,0),col=K4)
cyl("k4_lelehan",0.85,0.01,(KX+0.2,0.6,0.005),mat("#EFE6D0",0.4,0,name="lelehan"),col=K4)
for j in range(6): c=cyl("k4_lilin_jatuh",0.04,0.3,(KX+rnd.uniform(-2.5,2.5),rnd.uniform(-1.5,3),0.05),mat("#FFFDF5",0.6,0),rot=(math.radians(90),0,rnd.uniform(0,3)),col=K4)
cyl("k4_abu",0.25,0.02,(KX+3.1,3.6,0.01),mat("#3A3A3A",0.9,0),col=K4)
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep04/ep04_sets.blend"); print("SETS4 OK",len(O))
