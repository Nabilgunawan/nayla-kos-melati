import bpy, json, math, random, sys
from mathutils import Vector
sys.path.insert(0,"/home/claude/ep04")
from lib import box, mat, plane, link
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep04/ep04_sets.blend")
C=bpy.context; sc=C.scene; FPS=12; O=bpy.data.objects; M=bpy.data.materials
TL=json.load(open("/home/claude/ep04/timeline.json")); TOTAL=TL["total"]; NF=int(TOTAL*FPS); sc.frame_start=1; sc.frame_end=NF; sc.render.fps=12
W=sc.world.node_tree.nodes; cam=O["CAM"]; tgt=O["CAM_TGT"]; sun=O["SUN"]
# prestep
O["pb_papan"].rotation_euler.z=0; O["r_ceiling"].visible_camera=True; O["k_ceiling"].visible_camera=True
for o in (O["phone"],O["phone_screen"]): o.hide_render=True
hp=box("ph_body",(0.3,0.55,0.04),(206.9,-1.4,1.45),mat("#222222",0.3,0.4),0.03)
fm=M["foto_melati"]; plane("ph_screen",(0.26,0.48),(206.9,-1.4,1.475),fm)
bpy.ops.object.light_add(type='AREA',location=(49.5,-1.0,4.8)); k4l=C.object; k4l.name="L_k4_siang"; k4l.data.size=5; k4l.data.use_shadow=False; k4l.data.energy=0
sen=O["L_senter"]; sw=O["L_senter_warga"]; piv=O["PIV_k4door"]
def T(f): return (f-1)/FPS
def ss(x): x=max(0,min(1,x)); return x*x*(3-2*x)
SH=TL["shots"]; CL=TL["clips"]
def shot_at(t):
    for s in SH:
        if s["start"]<=t<s["end"]: return s
    return SH[-1]
SPK={"nayla":"Nayla","adel":"Adel","dimas":"Dimas","pakrt":"RT","budarmi":"Darmi","detektif":"Bima","rina":"Rina","sarip":"Sarip","mbahkarto":"Karto"}
LIPS={k:json.load(open(f"/home/claude/ep04/audio/lips_{k}.json"))["mouthCues"] for k in SPK}
def clip_of(ch,t):
    for c in CL:
        if SPK.get(c["spk"])==ch and c["dst"]<=t<c["dst"]+c["dur"]: return c
def last_clip(ch,t):
    lc=None
    for c in CL:
        if SPK.get(c["spk"])==ch and c["dst"]<=t: lc=c
    return lc
EMO={"ceria":(0,9),"cemas":(6,12),"penasaran":(8,0),"mikir":(10,0),"bingung":(9,15),"tegas":(5,12),"takut":(11,11),"tenang":(0,12),"beku":(2,12),"senyum":(0,9),
     "sedih":(6,13),"kaget":(2,11),"serius":(7,12),"seram":(4,14)}
VIS={"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8}
def viseme(spk,c,t):
    src=c["src"][0]+(t-c["dst"])
    for q in LIPS[spk]:
        if q["start"]<=src<q["end"]: return q["value"]
    return "X"
DEF={"Nayla":"cemas","Adel":"cemas","Dimas":"cemas","Ibu":"sedih","RT":"serius","Ronda":"tenang","Darmi":"cemas","Joko":"tenang","Bima":"serius","Rina":"sedih","Sarip":"takut","Karto":"seram","MelatiK":"senyum"}
OVR={("Ibu","s7"):"sedih",("Nayla","s43"):"beku",("Nayla","s44"):"beku",("MelatiK","s3"):"ceria",("MelatiK","s4"):"ceria",("MelatiK","s6"):"ceria"}
def emo_for(ch,t,s):
    if (ch,s["cam"]) in OVR and not clip_of(ch,t): return OVR[(ch,s["cam"])]
    lc=last_clip(ch,t); return lc["emo"] if lc and lc["emo"] else DEF[ch]
PR=dict(RT=(79.4,-7.0,0.03,45),Ronda=(80.9,-6.9,0.03,20),Nayla=(82.9,-8.6,0,-60),Adel=(83.7,-7.8,0,-75),Dimas=(83.5,-9.5,0,-50),Ibu=(77.2,-8.9,0,30),Darmi=(78.2,-9.6,0,15),Joko=(81.6,-10.2,0,-10))
SITPR={"RT","Ronda"}
def cam_(l0,t0,lens,l1=None,t1=None,f=2.0,sh=0): return (l0,t0,lens,l1,t1,f,sh)
CU_RT=cam_((80.6,-8.4,2.4),(79.4,-7.0,2.7),38,None,None,1.8); CU_NA=cam_((81.3,-9.5,2.75),(82.9,-8.6,2.7),40,None,None,1.6)
S={
"s1":dict(cam=cam_((79.0,-13.6,4.5),(81.0,-7.6,1.9),22,(79.0,-12.8,2.8),(81.0,-7.6,1.9),3),chars=PR,sit=SITPR),
"s2":dict(cam=CU_NA,chars=PR,sit=SITPR),
"s3":dict(cam=("trackM",),chars={"MelatiK":(100.5,-6.2,0,-90,94.5,-6.2,-90),"Darmi":(93.0,-7.2,0,60)}),
"s4":dict(cam=cam_((83.5,-10.5,2.5),(81.2,-7.6,2.0),28,None,None,2.5),chars={"MelatiK":(81.8,-8.8,0,-30),"Ronda":(80.9,-6.9,0.03,20)},sit={"Ronda"}),
"s5":dict(cam=cam_((198,-2.5,3.0),(199.5,5.2,2.0),24,(198.4,-1.8,3.0),(199.5,5.2,2.0),3),chars={"MelatiK":(199.2,5.6,0,0)}),
"s6":dict(cam=cam_((88.8,-6.3,2.6),(86.4,-9.8,2.1),28,None,None,2.5),chars={"MelatiK":(87.2,-9.4,0,-150),"Darmi":(85.6,-9.3,0,150)}),
"s7":dict(cam=cam_((78.2,-10.8,2.8),(77.2,-8.9,2.75),40,None,None,1.6),chars=PR,sit=SITPR),
"s8":dict(cam=cam_((79.6,-12.0,2.6),(78.2,-9.6,2.5),35,None,None,2.0),chars=PR,sit=SITPR),
"s9":dict(cam=cam_((103.5,-9.0,2.6),(107.5,0,2.4),26,(103.8,-8.2,2.6),(107.5,0,2.4),3),chars={}),
"s10":dict(cam=cam_((104.4,-5.0,2.8),(106.4,-0.6,2.3),28,None,None,2.5),chars={"RT":(106.4,-1.2,0.3,180),"Ronda":(105.3,-1.5,0.3,170),"Joko":(107.5,-1.6,0.3,190)}),
"s11":dict(cam=cam_((50.6,2.6,2.6),(50.3,-3.0,2.2),28,None,None,2.2,1),chars={"RT":(50.1,-3.7,0,180),"Ronda":(50.8,-4.1,0,180)}),
"s12":dict(cam=cam_((48.2,-1.5,2.9),(47.8,2.5,1.0),26,(52.0,-1.5,2.9),(52.5,2.5,1.2),2.5),chars={}),
"s13":dict(cam=cam_((247,-13,2.8),(248,-8.4,1.6),26,(248,-13,2.8),(249,-8.4,1.6),3),chars={"RT":(244.0,-8.4,0.25,90,249.0,-8.4,90),"Ronda":(242.8,-8.4,0.25,90,247.8,-8.4,90),"Joko":(241.6,-8.4,0.25,90,246.6,-8.4,90),"Darmi":(240.4,-8.4,0.25,90,245.4,-8.4,90)}),
"s14":dict(cam=cam_((243,-5.5,3.0),(250,2,0),24,(243.6,-5.0,3.0),(250,2,0),4),chars={"RT":(247.5,-4.2,0,60),"Joko":(246.4,-4.8,0,50)}),
"s15":dict(cam=cam_((251.0,-3.7,1.15),(251.2,-2.35,0.42),45,(251.1,-3.2,0.95),(251.2,-2.35,0.42),1.4),chars={}),
"s16":dict(cam=cam_((97,-9.6,2.5),(98.5,-5.8,2.0),28,(97.6,-9.6,2.5),(99.4,-5.8,2.0),2.5),chars={"Bima":(95.0,-6.0,0,90,99.2,-6.0,90),"RT":(100.6,-5.6,0,-110)}),
"s17":dict(cam=cam_((50.8,0.0,2.8),(48.6,3.4,2.4),30,None,None,2.0),chars={"Bima":(48.6,3.0,0,180)}),
"s18":dict(cam=cam_((50.5,-1.2,1.2),(48.4,2.0,1.6),24,None,None,2.0),chars={"Bima":(49.3,0.8,0,-130)}),
"s19":dict(cam=cam_((50.2,0.05,3.8),(50.2,0.6,0.0),26,(50.2,0.25,3.2),(50.2,0.6,0.0),3),chars={}),
"s20":dict(cam=cam_((206.5,-5.5,2.6),(206.5,-1.5,2.2),28,None,None,2.2),chars={"Bima":(205.1,-1.5,0.09,90),"Rina":(207.9,-1.5,0.09,-90)},sit={"Bima","Rina"}),
"s21":dict(cam=cam_((206.3,-2.5,2.9),(207.9,-1.5,2.8),40,None,None,1.6),chars={"Bima":(205.1,-1.5,0.09,90),"Rina":(207.9,-1.5,0.09,-90)},sit={"Bima","Rina"}),
"s22":dict(cam=cam_((206.9,-1.78,2.05),(206.9,-1.4,1.45),40,(206.9,-1.62,1.85),(206.9,-1.4,1.45),1.4),chars={"Bima":(205.1,-1.5,0.09,90),"Rina":(207.9,-1.5,0.09,-90)},sit={"Bima","Rina"}),
"s23":dict(cam=cam_((206.5,-2.3,2.9),(205.1,-1.5,2.8),40,None,None,1.6),chars={"Bima":(205.1,-1.5,0.09,90),"Rina":(207.9,-1.5,0.09,-90)},sit={"Bima","Rina"}),
"s24":dict(cam=cam_((88.6,-7.2,2.6),(86.2,-10.2,2.1),28,None,None,2.4),chars={"Bima":(86.6,-9.3,0,10),"Darmi":(86.0,-11.4,0,180)}),
"s25":dict(cam=cam_((86.9,-9.6,2.9),(86.0,-11.4,2.75),40,None,None,1.6),chars={"Bima":(87.6,-9.0,0,20),"Darmi":(86.0,-11.4,0,180)}),
"s26":dict(cam=cam_((249.5,-0.8,1.9),(251.9,-3.2,1.3),26,None,None,2.4),chars={"Bima":(252.0,-3.3,-0.35,-140)}),
"s27":dict(cam=cam_((251.45,-2.9,0.95),(251.2,-2.35,0.42),50,None,None,1.2),chars={"Bima":(252.0,-3.3,-0.35,-140)}),
"s28":dict(cam=cam_((250.6,-3.05,0.95),(250.55,-2.4,0.42),50,None,None,1.2),chars={"Bima":(252.0,-3.3,-0.35,-140)}),
"s29":dict(cam=cam_((299.0,-9,2.8),(300.5,2,1.8),26,(299.3,-6,2.8),(300.6,4,1.8),3),chars={"Bima":(300.0,-6.0,0,180,300.6,3.8,180),"Sarip":(303.6,6.4,0,-90)}),
"s30":dict(cam=cam_((302.0,6.0,2.85),(303.6,6.4,2.75),40,None,None,1.6),chars={"Bima":(301.0,5.0,0,120),"Sarip":(303.6,6.4,0,-90)}),
"s31":dict(cam=cam_((304.2,5.2,2.9),(300.5,16,2.0),28,None,None,4),chars={"Sarip":(303.6,6.4,0,-90),"Bima":(301.0,5.0,0,150)}),
"s32":dict(cam=cam_((400,-2.8,2.6),(400,0.2,2.6),28,(400,-1.7,2.6),(400,0.2,2.6),3),chars={}),
"s33":dict(cam=CU_RT,chars=PR,sit=SITPR),"s34":dict(cam=CU_NA,chars=PR,sit=SITPR),
"s35":dict(cam=cam_((82.2,-10.5,2.7),(83.5,-9.5,2.7),40,None,None,1.6),chars=PR,sit=SITPR),
"s36":dict(cam=cam_((81.8,-10.6,2.5),(79.6,-7.1,2.2),30,None,None,2.2),chars=PR,sit=SITPR),
"s37":dict(cam=cam_((82.1,-8.3,2.75),(83.7,-7.8,2.7),40,None,None,1.6),chars=PR,sit=SITPR),
"s38":dict(cam=("trackB",),chars={"Bima":(350.0,-8.0,0,180,350.0,2.5,180)}),
"s39":dict(cam=cam_((351.6,3.0,2.3),(350,8.0,1.8),26,None,None,2.0),chars={"Karto":(350,8.4,0,0),"Bima":(350.7,4.6,0,170)}),
"s40":dict(cam=cam_((350.0,6.5,2.8),(350,8.4,2.75),40,(350.0,6.9,2.8),(350,8.4,2.75),1.4,1),chars={"Karto":(350,8.4,0,0)}),
"s41":dict(cam=cam_((80.6,-8.4,2.4),(79.4,-7.0,2.7),38,(80.3,-8.0,2.5),(79.4,-7.0,2.7),1.6),chars=PR,sit=SITPR),
"s42":dict(cam=cam_((80.2,-12.4,2.7),(77.0,-8.9,2.6),45,(80.2,-12.4,2.7),(83.6,-8.0,2.6),3),chars=PR,sit=SITPR),
"s43b":dict(cam=CU_NA,chars=PR,sit=SITPR),
"s43":dict(cam=cam_((82.15,-9.05,2.75),(82.9,-8.6,2.72),35,None,None,1.2,2),chars=PR,sit=SITPR),
"s44":dict(cam=cam_((79.0,-12.8,2.7),(81.0,-7.6,1.9),22,None,None,3),chars=PR,sit=SITPR),
}
NAMES=["Nayla","Adel","Dimas","Ibu","RT","Ronda","Darmi","Joko","Bima","Rina","Sarip","Karto","MelatiK","Melati","Kunti"]
RIGS={n:O[f"{n}_rig"] for n in NAMES}
FACE={n:(M["face"] if n=="Nayla" else M[f"face_{n}"]) for n in NAMES if n not in ("Kunti","Melati")}
def walk(tl,period=0.7,amp=28):
    p=math.sin(2*math.pi*tl/period); return {"leg.L":(amp*p,0,0),"leg.R":(-amp*p,0,0),"arm.L":(-0.8*amp*p,0,-4),"arm.R":(0.8*amp*p,0,4)},0.05*abs(p)
def pose(ch,s,tl,t,c,sit,moving):
    cm=s["cam"]; br=math.sin(2*math.pi*(t+hash(ch)%7)/3.2); P={"spine":(1.2*br,0,0),"arm.L":(2*br,0,-3),"arm.R":(-2*br,0,3)}; dz=0
    if sit: P.update({"leg.L":(-90,0,0),"leg.R":(-90,0,0),"foot.L":(90,0,0),"foot.R":(90,0,0),"arm.L":(-45,0,6),"arm.R":(-45,0,-6)})
    if c:
        P["head"]=(3*math.sin(2*math.pi*t*1.3),2*math.sin(2*math.pi*t*0.7),3*math.sin(2*math.pi*t*0.45)); cl=t-c["dst"]
        if cl<1.0 and ch!="Karto":
            g=math.sin(math.pi*cl)
            if hash(c["id"])%2==0: P["arm.R"]=(-55*g-(45 if sit else 0)*(1-g),0,3+15*g)
            else: P["arm.L"]=(-55*g-(45 if sit else 0)*(1-g),0,-3-15*g)
    if moving: w,dz=walk(tl,0.72,24); P.update(w)
    if ch=="MelatiK" and cm=="s3" and tl<1.6: P["arm.L"]=(0,0,-150); P["hand.L"]=(0,0,22*math.sin(2*math.pi*2.5*tl))
    if ch=="MelatiK" and cm=="s4": P["arm.R"]=(-75,0,-10)
    if ch=="MelatiK" and cm=="s5": P["arm.L"]=(-70,0,10); P["arm.R"]=(-70,0,-10); P["head"]=(15,0,0)
    if ch=="MelatiK" and cm=="s6": P["arm.L"]=(-60,0,15); P["arm.R"]=(-60,0,-15)
    if ch in ("RT","Ronda","Joko") and cm=="s10": P["arm.R"]=(-80-10*max(0,math.sin(t*20)),0,-5)
    if ch in ("RT","Ronda") and cm=="s11": P["arm.L"]=(-70,0,0); P["arm.R"]=(-70,0,0); P["spine"]=(8,0,0)
    if cm in ("s13","s14"): P["arm.R"]=(-70,0,-5)
    if ch=="Bima" and cm in ("s17",): P["head"]=(-5,0,15); P["arm.R"]=(-80,0,0)
    if ch=="Bima" and cm=="s18": P["arm.L"]=(-110,0,10); P["arm.R"]=(-110,0,-10); P["spine"]=(20,0,0)
    if ch=="Bima" and cm in ("s26","s27","s28"): P["spine"]=(35,0,0); P["leg.L"]=(-70,0,0); P["leg.R"]=(-40,0,0); P["arm.R"]=(-80,0,0); P["head"]=(20,0,0)
    if ch=="Sarip" and cm=="s31": P["arm.R"]=(-90,0,-60)
    if ch=="Karto": P["head"]=(8,0,0); P["arm.L"]=(-30,0,10); P["arm.R"]=(-30,0,-10)
    if ch=="Nayla" and cm in ("s43","s44"): P={"spine":(0,0,0),"arm.L":(0,0,-3),"arm.R":(0,0,3),"head":(0,0,0)}
    if ch=="Nayla" and cm=="s42": P["head"]=(0,0,-20+40*ss(tl/4))
    if ch=="Ibu" and cm=="s7": P["head"]=(12,0,0); P["arm.R"]=(-120,0,-15)
    return P,dz
LK=["L_teras1","L_teras2","L_teras3","L_teras4","L_jalan","L_kamar3","L_hijau","L_neon","L_bohlam","L_senter","L_warung","L_pabrik0","L_pabrik1","L_pabrik2","L_senter_warga","L_pasar","L_lilin","L_lilin2","L_papan","L_k4_siang"]
def kf(s): s.keyframe_insert("default_value",frame=CUR)
def es(n,v):
    m=M.get(n)
    if m: i=m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; i.default_value=v; kf(i)
def world(a,b,c):
    W["W_SORE"].inputs["Factor"].default_value=a; W["W_MALAM"].inputs["Factor"].default_value=b; W["W_BG"].inputs[1].default_value=c
    for i in (W["W_SORE"].inputs["Factor"],W["W_MALAM"].inputs["Factor"],W["W_BG"].inputs[1]): kf(i)
def sunset(d,e,col):
    sun.rotation_euler=Vector(d).normalized().to_track_quat('-Z','Y').to_euler(); sun.data.energy=e; sun.data.color=col
    sun.keyframe_insert("rotation_euler",frame=CUR); sun.data.keyframe_insert("energy",frame=CUR); sun.data.keyframe_insert("color",frame=CUR)
NIGHT=dict(L_teras1=45,L_teras2=45,L_teras3=45,L_teras4=45,L_jalan=350,L_kamar3=60)
def preset(s,fl,tl):
    st=s["set"]; v={}; night=st in ("posronda","fb_malam","fb_sawah","fb_sungai_malam","gubuk")
    if night: world(0,1,0.3); sunset((-0.4,0.7,-0.6),0.6,(0.55,0.65,1.0)); v.update(NIGHT)
    if st=="posronda":
        b=130
        if s["cam"]=="s44": b=130*(fl if tl<1.2 else 0.0)
        v["L_bohlam"]=b
    if st=="fb_malam": v["L_hijau"]=90*fl
    if st in ("fb_sawah","fb_sungai_malam"): v["L_senter_warga"]=0; v["L_senter"]=380
    if st=="gubuk": v["L_lilin"]=110*(0.85+0.15*fl); v["L_lilin2"]=55; world(0,1,0.12)
    if st=="fb_k4": world(0,1,0.12); sunset((0.2,-1,-0.5),0.25,(0.55,0.65,1)); v["L_neon"]=130
    if st in ("fb_pagi","fb_siang","warung","sungai_siang"): world(0,0,0.9); sunset((0.5,0.8,-0.9),3.8,(1,0.95,0.86))
    if st=="warung": v["L_warung"]=60
    if st=="fb_sore": world(0,0,0.7); sunset((0.8,0.5,-0.35),3.0,(1,0.75,0.5))
    if st=="pabrik": world(0,0,0.35); sunset((0.5,0.8,-0.9),1.0,(1,0.95,0.9)); v.update(L_pabrik0=900,L_pabrik1=900,L_pabrik2=900)
    if st=="pasar": world(0,0,0.8); sunset((0.6,0.6,-0.6),3.2,(1,0.9,0.75)); v["L_pasar"]=250
    if st=="papan": world(0,0,0.3); sunset((0.5,0.8,-0.9),0.5,(1,0.95,0.9)); v["L_papan"]=300
    if st=="k4_siang": world(0,0,0.5); sunset((0.2,-1,-0.6),1.5,(1,0.95,0.86)); v["L_k4_siang"]=400
    for n in LK: O[n].data.energy=v.get(n,0); O[n].data.keyframe_insert("energy",frame=CUR)
    es("lampu_teras1",6 if night else 0); es("lampu_jalan",8 if night else 0); es("bohlam",(10*(v.get("L_bohlam",0)/130)) if st=="posronda" else 0)
    es("kaca4",3*fl if st=="fb_malam" else 0); es("neon_hijau",12 if st=="fb_k4" else 0); es("api_lilin",20 if st=="gubuk" else 0); es("kaca3",1.5 if night else 0)
rng=random.Random(6); blinks={}
for ch in FACE:
    b=set(); tb=rng.uniform(0.5,2.5)
    while tb<TOTAL: b.add(int(tb*FPS)+1); tb+=rng.uniform(2.3,4.5)
    blinks[ch]=b
tile=lambda i:((i%4)*0.25,(3-i//4)*0.25,0.0); prev={c:None for c in FACE}; PARK=Vector((0,-200,0))
for f in range(1,NF+1):
    CUR=f; t=T(f); s=shot_at(t); tl=t-s["start"]; sp=S[s["cam"]]; d=s["end"]-s["start"]
    fl=1.0 if rng.random()>0.3 else 0.2
    preset(s,fl,tl)
    for ch,rig in RIGS.items():
        c=sp["chars"].get(ch)
        if not c: rig.location=PARK; rig.rotation_euler=(0,0,0); moving=False
        else:
            moving=len(c)>4
            if moving: g=min(1,tl/d); x=c[0]+(c[4]-c[0])*g; y=c[1]+(c[5]-c[1])*g; rz=c[3]+(c[6]-c[3])*g
            else: x,y,rz=c[0],c[1],c[3]
            cc=clip_of(ch,t) if ch in FACE else None
            P,dz=pose(ch,s,tl,t,cc,ch in sp.get("sit",set()),moving)
            rig.location=Vector((x,y,c[2]+dz)); rig.rotation_euler=(0,0,math.radians(rz))
            for b in ["spine","head","arm.L","arm.R","hand.L","hand.R","leg.L","leg.R","hips","foot.L","foot.R"]:
                pb=rig.pose.bones.get(b)
                if pb: pb.rotation_mode='XYZ'; pb.rotation_euler=[math.radians(v) for v in P.get(b,(0,0,0))]; pb.keyframe_insert("rotation_euler",frame=f)
        rig.keyframe_insert("location",frame=f); rig.keyframe_insert("rotation_euler",index=2,frame=f)
        if ch in FACE:
            et,mt=EMO[emo_for(ch,t,s)]
            if f in blinks[ch] and et not in (1,3,12,15): et=1
            cc=clip_of(ch,t)
            if cc: mt=VIS.get(viseme([k for k,v in SPK.items() if v==ch][0],cc,t),mt)
            if prev[ch]!=(et,mt) or f==1:
                N=FACE[ch].node_tree.nodes
                for nm,v in (("AT_eyes",et),("AT_mouth",mt)): N[nm].inputs["Location"].default_value=tile(v); N[nm].inputs["Location"].keyframe_insert("default_value",frame=f)
                prev[ch]=(et,mt)
    cs=sp["cam"]
    if cs[0]=="trackM": mx=RIGS["MelatiK"].location.x; cl=Vector((mx-2.2,-10.4,2.6)); ct=Vector((mx+0.2,-6.2,2.0)); lens,fs,sh=26,2.2,0
    elif cs[0]=="trackB": by=RIGS["Bima"].location.y; cl=Vector((351.2,by-3.6,2.5)); ct=Vector((350,by+1.5,2.0)); lens,fs,sh=26,2.2,1
    else:
        l0,t0,lens,l1,t1,fs,sh=cs; g=ss(tl/d)
        cl=Vector(l0).lerp(Vector(l1),g) if l1 else Vector(l0); ct=Vector(t0).lerp(Vector(t1),g) if t1 else Vector(t0)
    if sh: cl=cl+Vector((rng.gauss(0,0.012*sh),rng.gauss(0,0.006*sh),rng.gauss(0,0.012*sh)))
    cam.location=cl; tgt.location=ct; cam.data.lens=lens; cam.data.dof.aperture_fstop=fs
    cam.keyframe_insert("location",frame=f); tgt.keyframe_insert("location",frame=f); cam.data.keyframe_insert("lens",frame=f); cam.data.dof.keyframe_insert("aperture_fstop",frame=f)
    lead=RIGS["RT"] if s["set"] in ("fb_sawah","fb_sungai_malam") else RIGS["Nayla"]
    fwd=Vector((math.sin(lead.rotation_euler.z),-math.cos(lead.rotation_euler.z),0))
    sen.location=lead.location+fwd*0.6+Vector((0,0,1.9)); sen.rotation_euler=(fwd+Vector((0,0,-0.25))).to_track_quat('-Z','Y').to_euler()
    sen.keyframe_insert("location",frame=f); sen.keyframe_insert("rotation_euler",frame=f)
    piv.rotation_euler=(0,0,math.radians(95*ss(tl/0.3) if s["cam"]=="s11" else (95 if s["cam"]=="s12" else 0))); piv.keyframe_insert("rotation_euler",index=2,frame=f)
def const(ad):
    if ad and ad.action:
        for layer in getattr(ad.action,"layers",[]):
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for k in fc.keyframe_points: k.interpolation='CONSTANT'
for idb in list(O)+list(M)+list(bpy.data.lights)+list(bpy.data.cameras)+[sc.world]:
    const(idb.animation_data); nt=getattr(idb,"node_tree",None)
    if nt: const(nt.animation_data)
sc.frame_set(1); sc.render.filepath="//frames/"; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1080; sc.render.resolution_y=1920
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep04/ep04.blend"); print("ANIM4 OK",NF)
