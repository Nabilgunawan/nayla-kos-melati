import bpy, json, math, random, sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep03/ep03_sets.blend")
C=bpy.context; sc=C.scene; FPS=12; O=bpy.data.objects; M=bpy.data.materials
TL=json.load(open("/home/claude/ep03/timeline.json")); TOTAL=TL["total"]; NF=int(TOTAL*FPS); sc.frame_start=1; sc.frame_end=NF; sc.render.fps=12
W=sc.world.node_tree.nodes; cam=O["CAM"]; tgt=O["CAM_TGT"]; sun=O["SUN"]
# ---- prestep
fm=M["foto_melati"]; n=fm.node_tree.nodes; t=n.new("ShaderNodeTexImage"); t.image=bpy.data.images.load("/home/claude/ep03/tex/foto_melati.png"); fm.node_tree.links.new(t.outputs[0],n["Principled BSDF"].inputs["Base Color"])
O["r_frame_melati"].location.z=3.3; O["r_foto_melati"].location.z=3.3
for k in range(4): O[f"r_frame{k}"].location.z+=0.7; O[f"r_foto{k}"].location.z+=0.7
O["r_ceiling"].visible_camera=True; O["k_ceiling"].visible_camera=True; O["BUKU"].location=(78.6,-8.05,0.95); ph=O["phone"]; phs=O["phone_screen"]
sen=O["L_senter"]; pivk4=O["PIV_k4door"]; plate=O["x_no3"]; P0=plate.location.copy(); R0=plate.rotation_euler.copy()
k3=M["kaca3"].node_tree.nodes["Principled BSDF"]; hal=M["halaman"].node_tree.nodes["HALAMAN"].inputs["Factor"]; halr=M["halaman"].node_tree.nodes["Principled BSDF"].inputs["Roughness"]
def T(f): return (f-1)/FPS
def ss(x): x=max(0,min(1,x)); return x*x*(3-2*x)
SH=TL["shots"]; CL=TL["clips"]
def shot_at(t):
    for s in SH:
        if s["start"]<=t<s["end"]: return s
    return SH[-1]
SPK={"nayla":"Nayla","ibukos":"Ibu","adel":"Adel","dimas":"Dimas","pakrt":"RT","pakronda":"Ronda"}
LIPS={k:json.load(open(f"/home/claude/ep03/audio/lips_{k}.json"))["mouthCues"] for k in SPK}
def clip_of(ch,t):
    for c in CL:
        if SPK.get(c["spk"])==ch and c["dst"]<=t<c["dst"]+c["dur"]: return c
def last_clip(ch,t):
    lc=None
    for c in CL:
        if SPK.get(c["spk"])==ch and c["dst"]<=t: lc=c
    return lc
EMO={"ceria":(0,9),"cemas":(6,12),"penasaran":(8,0),"mikir":(10,0),"bingung":(9,15),"tegas":(5,12),"takut":(11,11),"panik":(11,11),"tenang":(0,12),
     "beku":(2,12),"senyum":(0,9),"lelah":(4,12),"sedih":(6,13),"kaget":(2,11),"serius":(7,12)}
VIS={"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8}
def viseme(spk,c,t):
    src=c["src"][0]+(t-c["dst"])
    for q in LIPS[spk]:
        if q["start"]<=src<q["end"]: return q["value"]
    return "X"
OVR={("Nayla","s26"):"beku",("Nayla","s29"):"beku",("Nayla","s30"):"beku",("Nayla","s28"):"cemas",("Melati","s7"):"senyum",("Adel","s25"):"takut",("Dimas","s23"):"takut"}
DEF={"Nayla":"cemas","Adel":"cemas","Dimas":"cemas","Ibu":"sedih","RT":"serius","Ronda":"tenang","Melati":"senyum"}
def emo_for(ch,t,s):
    if (ch,s["cam"]) in OVR and not clip_of(ch,t): return OVR[(ch,s["cam"])]
    lc=last_clip(ch,t); return lc["emo"] if lc and lc["emo"] else DEF[ch]
RT_=dict(RT=(79.4,-7.0,0.03,45),Ronda=(80.9,-6.9,0.03,20),Nayla=(82.9,-8.6,0,-60),Adel=(83.7,-7.8,0,-75),Dimas=(83.5,-9.5,0,-50))
RG=dict(Dimas=(148.0,2.5,0.15,0),Nayla=(149.2,2.5,0.15,0),Adel=(150.4,2.5,0.15,0),Ibu=(153.0,0.6,0.15,-90))
SEAT_RT={"RT","Ronda"}; SEAT_RG={"Dimas","Nayla","Adel","Ibu"}
def cam_(l0,t0,lens,l1=None,t1=None,f=2.0,sh=0): return (l0,t0,lens,l1,t1,f,sh)
S={
"s1":dict(cam=cam_((-0.8,-2.4,2.8),(-3.1,2.0,2.4),30,(-1.0,-2.0,2.8),(-3.1,2.0,2.4),1.8),chars={"Nayla":(-3.1,1.8,0.12,0)},sit={"Nayla"}),
"s2":dict(cam=cam_((107.5,-8.5,3.6),(112,-1.2,2.3),26,(108,-8.0,3.4),(112,-1.2,2.3),3),chars={"Ibu":(113.5,-1.8,0.35,-30)}),
"s3":dict(cam=cam_((147.2,-3.6,3.3),(150,2.0,1.9),20,None,None,4),chars=RG,sit=SEAT_RG),
"s4":dict(cam=cam_((150.9,0.25,2.95),(153.0,0.6,2.8),40,None,None,1.6),chars=RG,sit=SEAT_RG),
"s5":dict(cam=cam_((150.2,-0.5,2.9),(153,0.6,2.8),32,(151.0,0.0,2.9),(153,0.6,2.8),1.8),chars=RG,sit=SEAT_RG),
"s6":dict(cam=cam_((149.2,0.35,2.95),(149.2,2.5,2.85),40,None,None,1.6),chars=RG,sit=SEAT_RG),
"s7":dict(cam=cam_((85.6,-3.6,2.4),(87.9,1.4,2.2),28,(85.9,-3.2,2.4),(87.9,1.4,2.2),3),chars={"Melati":(88.2,1.5,0,-90)}),
"s8":dict(cam=cam_((83.0,0.7,2.4),(87,1.6,2.1),26,(83.3,0.8,2.4),(87,1.6,2.1),3),chars={}),
"s9":dict(cam=cam_((151.6,0.6,3.4),(150.2,4.37,3.4),26,None,None,2.5),chars=RG,sit=SEAT_RG),
"s10":dict(cam=cam_((150.2,3.0,3.32),(150.2,4.37,3.3),40,(150.2,3.45,3.31),(150.2,4.37,3.3),1.6),chars=RG,sit=SEAT_RG),
"s11":dict(cam=cam_((150.6,3.7,3.42),(150.6,4.37,3.42),60,(150.6,3.95,3.42),(150.6,4.37,3.42),1.6),chars=RG,sit=SEAT_RG),
"s12":dict(cam=cam_((151.0,-1.2,2.7),(153,0.6,2.55),30,None,None,2.0),chars=RG,sit=SEAT_RG),
"s13":dict(cam=("track",),chars={"Nayla":(93.5,-6.0,0,-90,86.5,-6.0,-90),"Adel":(94.7,-6.6,0,-90,87.7,-6.6,-90),"Dimas":(95.9,-5.6,0,-90,88.9,-5.6,-90)}),
"s14":dict(cam=cam_((79.0,-12.8,2.7),(81.0,-7.6,1.9),22,None,None,3),chars=RT_,sit=SEAT_RT),
"s15":dict(cam=cam_((80.6,-8.4,2.4),(79.4,-7.0,2.7),38,None,None,1.8),chars=RT_,sit=SEAT_RT),
"s16":dict(cam=cam_((50.6,2.6,2.6),(50.3,-3.0,2.2),28,None,None,2.2,1),chars={"RT":(50.1,-3.6,0,180),"Ronda":(50.8,-4.0,0,180)}),
"s17":dict(cam=cam_((82.0,-8.7,2.5),(80.9,-6.9,2.6),34,None,None,1.8),chars=RT_,sit=SEAT_RT),
"s18":dict(cam=cam_((81.3,-9.5,2.75),(82.9,-8.6,2.7),40,None,None,1.6),chars=RT_,sit=SEAT_RT),
"s19":dict(cam=cam_((80.6,-8.4,2.4),(79.4,-7.0,2.7),38,(80.3,-8.0,2.5),(79.4,-7.0,2.7),1.6),chars=RT_,sit=SEAT_RT),
"s20":dict(cam=cam_((78.385,-8.22,2.25),(78.385,-8.0,0.98),34,None,None,1.4),chars=RT_,sit=SEAT_RT),
"s21":dict(cam=cam_((81.3,-9.5,2.75),(82.9,-8.6,2.7),40,None,None,1.6),chars=RT_,sit=SEAT_RT),
"s22":dict(cam=cam_((82.2,-10.5,2.7),(83.5,-9.5,2.7),40,None,None,1.6),chars=RT_,sit=SEAT_RT),
"s23":dict(cam=cam_((78.6,-8.22,2.3),(78.6,-8.0,0.98),30,None,None,1.4),chars=RT_,sit=SEAT_RT),
"s24":dict(cam=cam_((82.1,-8.3,2.75),(83.7,-7.8,2.7),40,None,None,1.6),chars=RT_,sit=SEAT_RT),
"s25":dict(cam=cam_((78.815,-8.2,2.1),(78.815,-8.05,0.98),40,(78.815,-8.12,1.86),(78.815,-8.05,0.98),1.2),chars=RT_,sit=SEAT_RT),
"s26":dict(cam=cam_((82.15,-9.05,2.75),(82.9,-8.6,2.72),35,None,None,1.2,2),chars=RT_,sit=SEAT_RT),
"s27":dict(cam=cam_((80.6,-8.41,2.4),(79.4,-7.0,2.7),38,None,None,1.6),chars=RT_,sit=SEAT_RT),
"s28":dict(cam=cam_((98.8,-3.2,2.9),(101.5,-0.2,3.0),28,None,None,2.2),chars={"Nayla":(98.2,-1.4,0.3,90,101.4,-1.15,180)}),
"s29":dict(cam=cam_((101.4,-3.3,2.95),(101.4,-1.1,2.95),40,None,None,1.6),chars={"Nayla":(101.4,-1.1,0.3,0)}),
"s30":dict(cam=cam_((99.5,-8.8,3.0),(103.0,0,2.3),22,None,None,4),chars={"Nayla":(101.4,-1.1,0.3,180)}),
}
NAMES=["Nayla","Adel","Dimas","Ibu","RT","Ronda","Melati","Kunti"]
RIGS={n:O[f"{n}_rig"] for n in NAMES}
FACE={n:(M["face"] if n=="Nayla" else M[f"face_{n}"]) for n in NAMES if n!="Kunti"}
def walk(tl,period=0.7,amp=28):
    p=math.sin(2*math.pi*tl/period)
    return {"leg.L":(amp*p,0,0),"leg.R":(-amp*p,0,0),"arm.L":(-0.8*amp*p,0,-4),"arm.R":(0.8*amp*p,0,4)},0.05*abs(p)
def pose(ch,s,tl,t,c,sit):
    cm=s["cam"]; d=s["end"]-s["start"]; br=math.sin(2*math.pi*(t+hash(ch)%7)/3.2)
    P={"spine":(1.2*br,0,0),"arm.L":(2*br,0,-3),"arm.R":(-2*br,0,3)}; dz=0
    if sit: P.update({"leg.L":(-90,0,0),"leg.R":(-90,0,0),"foot.L":(90,0,0),"foot.R":(90,0,0),"arm.L":(-45,0,6),"arm.R":(-45,0,-6)})
    if c:
        P["head"]=(3*math.sin(2*math.pi*t*1.3),2*math.sin(2*math.pi*t*0.7),3*math.sin(2*math.pi*t*0.45)); cl=t-c["dst"]
        if cl<1.0:
            g=math.sin(math.pi*cl); k=hash(c["id"])%2
            if k==0: P["arm.R"]=(-55*g-(45 if sit else 0)*(1-g),0,3+15*g)
            else: P["arm.L"]=(-55*g-(45 if sit else 0)*(1-g),0,-3-15*g)
    if ch=="Ibu" and cm=="s2": P["arm.L"]=(0,0,-150); P["hand.L"]=(0,0,25*math.sin(2*math.pi*2.5*tl))
    if ch=="Ibu" and cm=="s4" and tl<1.4: g=math.sin(math.pi*tl/1.4); P["arm.R"]=(-45-90*g,0,-10)
    if ch=="Melati" and cm=="s7": g=math.sin(2*math.pi*tl*0.5); P["arm.L"]=(-150,0,-10+8*g); P["arm.R"]=(-150,0,10-8*g); P["head"]=(-10,0,0)
    if ch=="Adel" and cm in ("s9","s10","s11") : P["spine"]=(0,0,35); P["head"]=(-25,0,55); P["arm.R"]=(-160,0,-20)
    if ch=="Dimas" and cm=="s22": P["arm.R"]=(-80,0,-10); P["hand.R"]=(0,0,20*math.sin(t*9))
    if ch=="RT" and cm in ("s19","s27"): P["head"]=(22,0,15); P["arm.R"]=(-70,0,-20)
    if ch=="RT" and cm in ("s20","s23","s25"): P["head"]=(22,0,15); P["arm.R"]=(-20,0,-5); P["arm.L"]=(-20,0,5)
    if ch in ("RT","Ronda") and cm=="s16": P["arm.L"]=(-70,0,0); P["arm.R"]=(-70,0,0); P["spine"]=(8,0,0)
    if ch=="Nayla" and cm=="s1": P["spine"]=(10,0,0); P["head"]=(12,0,0); P["arm.L"]=(-60,0,10); P["arm.R"]=(-60,0,-10)
    if ch=="Nayla" and cm in ("s26","s29","s30"): P={"spine":(0,0,0),"arm.L":(0,0,-3),"arm.R":(0,0,3),"head":(0,0,0)}
    if cm=="s13": w,dz=walk(tl,0.75,24); P.update(w)
    if ch=="Nayla" and cm=="s28" and tl<2.0: w,dz=walk(tl,0.8,22); P.update(w)
    if ch=="Nayla" and cm=="s13": P["arm.R"]=(-60,0,0)
    if ch=="Nayla" and cm in ("s21","s18") and not c: P["head"]=(10,0,-10)
    return P,dz
# ---- lights
LK=["L_kos_fill","L_kos_window","L_desklamp","L_teras1","L_teras2","L_teras3","L_teras4","L_jalan","L_kamar3","L_hijau","L_neon","L_bohlam","L_rt_fill","L_rt_jendela","L_senter"]
def kf(sock): sock.keyframe_insert("default_value",frame=CUR)
def es(name,v):
    m=M.get(name)
    if m: i=m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; i.default_value=v; kf(i)
def world(a,b,c):
    W["W_SORE"].inputs["Factor"].default_value=a; W["W_MALAM"].inputs["Factor"].default_value=b; W["W_BG"].inputs[1].default_value=c
    for i in (W["W_SORE"].inputs["Factor"],W["W_MALAM"].inputs["Factor"],W["W_BG"].inputs[1]): kf(i)
def sunset(d,e,col):
    sun.rotation_euler=Vector(d).normalized().to_track_quat('-Z','Y').to_euler(); sun.data.energy=e; sun.data.color=col
    sun.keyframe_insert("rotation_euler",frame=CUR); sun.data.keyframe_insert("energy",frame=CUR); sun.data.keyframe_insert("color",frame=CUR)
def setL(v):
    for n in LK: O[n].data.energy=v.get(n,0); O[n].data.keyframe_insert("energy",frame=CUR)
NIGHT=dict(L_teras1=45,L_teras2=45,L_teras3=45,L_teras4=45,L_jalan=350,L_kamar3=60)
def preset(s,fl):
    st=s["set"]; v={}; green3=False
    if st=="kamar_pagi": world(0,0,0.6); sunset((0.35,-1,-0.75),3.0,(1,0.92,0.8)); v.update(L_kos_fill=120,L_kos_window=260)
    elif st=="luar_pagi": world(0,0,0.7); sunset((0.75,0.55,-0.38),3.2,(1,0.82,0.62))
    elif st=="ruangtamu": world(0,0,0.45); sunset((-1,0.25,-0.55),2.0,(1,0.9,0.75)); v.update(L_rt_fill=250,L_rt_jendela=400)
    elif st in ("luar_malam","flash_malam","posronda"):
        world(0,1,0.35); sunset((-0.4,0.7,-0.6),0.7,(0.55,0.65,1.0)); v.update(NIGHT)
        if st=="posronda": v["L_bohlam"]=130
        if st=="flash_malam": v["L_hijau"]=90
        if s["cam"]=="s30": green3=True; v["L_kamar3"]=90*fl
        if s["cam"] in ("s13","s28"): v["L_senter"]=420
    elif st=="flash_k4": world(0,1,0.12); sunset((0.2,-1,-0.5),0.25,(0.55,0.65,1)); v["L_neon"]=130
    night=st in ("luar_malam","flash_malam","posronda")
    es("lampu_teras1",6 if night else 0); es("lampu_jalan",8 if night else 0); es("kaca_rumah",1 if night else 0); es("nkaca0",1 if night else 0)
    es("bohlam",10 if st=="posronda" else 0); es("kaca4",3 if st=="flash_malam" else 0); es("neon_hijau",12 if st=="flash_k4" else 0)
    k3.inputs["Emission Color"].default_value=(0.25,1,0.4,1) if green3 else (1,0.85,0.6,1); kf(k3.inputs["Emission Color"])
    k3.inputs["Emission Strength"].default_value=(3*fl if green3 else (1.5 if night else 0)); kf(k3.inputs["Emission Strength"])
    O["L_kamar3"].data.color=(0.3,1,0.45) if green3 else (1,0.8,0.5); O["L_kamar3"].data.keyframe_insert("color",frame=CUR)
    setL(v)
# ---- bake
rng=random.Random(4); blinks={}
for ch in FACE:
    b=set(); tb=rng.uniform(0.5,2.5)
    while tb<TOTAL: b.add(int(tb*FPS)+1); tb+=rng.uniform(2.3,4.5)
    blinks[ch]=b
tile=lambda i:((i%4)*0.25,(3-i//4)*0.25,0.0); prev={c:None for c in FACE}; PARK=Vector((0,-200,0))
gown=O["x_baju_putih"]; jam=O["JAM_JARUM"]
for f in range(1,NF+1):
    CUR=f; t=T(f); s=shot_at(t); tl=t-s["start"]; sp=S[s["cam"]]; d=s["end"]-s["start"]
    fl=1.0 if rng.random()>0.3 else 0.2
    preset(s,fl)
    for ch,rig in RIGS.items():
        c=sp["chars"].get(ch)
        if not c: rig.location=PARK; rig.rotation_euler=(0,0,0)
        else:
            if len(c)>4:
                dur=2.0 if s["cam"]=="s28" else d; g=min(1,tl/dur)
                x=c[0]+(c[4]-c[0])*g; y=c[1]+(c[5]-c[1])*g; rz=c[3]+(c[6]-c[3])*(ss((tl-1.6)/0.4) if s["cam"]=="s28" else g)
            else: x,y,rz=c[0],c[1],c[3]
            cc=clip_of(ch,t) if ch in FACE else None
            P,dz=pose(ch,s,tl,t,cc,ch in sp.get("sit",set()))
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
    if cs[0]=="track":
        nx=RIGS["Nayla"].location.x; cl=Vector((nx+0.4,-9.6,2.4)); ct=Vector((nx-0.5,-6.0,2.0)); lens,fs,sh=26,2.2,0
    else:
        l0,t0,lens,l1,t1,fs,sh=cs; g=ss(tl/d)
        cl=Vector(l0).lerp(Vector(l1),g) if l1 else Vector(l0); ct=Vector(t0).lerp(Vector(t1),g) if t1 else Vector(t0)
    if sh: cl=cl+Vector((rng.gauss(0,0.012*sh),rng.gauss(0,0.006*sh),rng.gauss(0,0.012*sh)))
    cam.location=cl; tgt.location=ct; cam.data.lens=lens; cam.data.dof.aperture_fstop=fs
    cam.keyframe_insert("location",frame=f); tgt.keyframe_insert("location",frame=f); cam.data.keyframe_insert("lens",frame=f); cam.data.dof.keyframe_insert("aperture_fstop",frame=f)
    r=RIGS["Nayla"]; fwd=Vector((math.sin(r.rotation_euler.z),-math.cos(r.rotation_euler.z),0))
    sen.location=r.location+fwd*0.6+Vector((0,0,1.9)); sen.rotation_euler=(fwd+Vector((0,0,-0.2))).to_track_quat('-Z','Y').to_euler()
    sen.keyframe_insert("location",frame=f); sen.keyframe_insert("rotation_euler",frame=f)
    gown.hide_render=s["cam"] not in ("s7","s8"); gown.keyframe_insert("hide_render",frame=f)
    hp=s["cam"] not in ("s13","s28")
    for o in (ph,phs): o.hide_render=hp; o.keyframe_insert("hide_render",frame=f)
    pivk4.rotation_euler=(0,0,math.radians(95*ss(tl/0.3) if s["cam"]=="s16" else 0)); pivk4.keyframe_insert("rotation_euler",index=2,frame=f)
    hv=1.0 if (s["cam"]=="s23" and tl>d*0.5) or s["n"]>=24 else 0.0
    hal.default_value=hv; hal.keyframe_insert("default_value",frame=f); halr.default_value=0.3 if hv else 0.7; halr.keyframe_insert("default_value",frame=f)
    jam.rotation_euler=(0,math.radians(-6*t),0); jam.keyframe_insert("rotation_euler",index=1,frame=f)
    fall=0.0
    if s["n"]>28 or (s["cam"]=="s28" and tl>1.8): fall=1.0 if s["n"]>28 else ss((tl-1.8)/0.35)
    plate.location=P0+Vector((0,-0.15*fall,-3.5*fall)); plate.rotation_euler=(R0.x-math.radians(80)*fall,R0.y,R0.z+math.radians(25)*fall)
    plate.keyframe_insert("location",frame=f); plate.keyframe_insert("rotation_euler",frame=f)
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
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep03/ep03.blend"); print("ANIM3 OK",NF)
