import bpy, json, math, random, sys
from mathutils import Vector
sys.path.insert(0,"/home/claude/ep02")
from lib import box, mat, link, newcol, plane
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep02/ep02_sets.blend")
C=bpy.context; sc=C.scene; FPS=12; O=bpy.data.objects
TL=json.load(open("/home/claude/ep02/timeline.json")); TOTAL=TL["total"]; NF=int(TOTAL*FPS); sc.frame_start=1; sc.frame_end=NF; sc.render.fps=12
W=sc.world.node_tree.nodes; cam=O["CAM"]; tgt=O["CAM_TGT"]; sun=O["SUN"]
# ---------- pre-step: pivots, kamar4 front wall/door, fake green window, flashlight ----------
def pivot(name,loc,members):
    bpy.ops.object.empty_add(location=loc); p=C.object; p.name=name
    for m in members: mw=m.matrix_world.copy(); m.parent=p; m.matrix_parent_inverse=p.matrix_world.inverted()
    return p
p_door4=pivot("PIV_door4",(105.85,-0.07,0),[o for o in O if o.name.startswith("x_door4") and "frame" not in o.name])
p_room=pivot("PIV_roomdoor",(4.48,-2.5,0),[O["k_door"],O["k_doorknob"]])
K4=bpy.data.collections["set_kamar4"]; w4=bpy.data.materials["dinding_kusam"]
for nm,sz,lc in [("k4_fl",(3.25,0.3,5.5),(48.0,-3.0,2.75)),("k4_fr",(2.65,0.3,5.5),(52.25,-3.0,2.75)),("k4_ft",(1.4,0.3,1.9),(50.25,-3.0,4.55))]: box(nm,sz,lc,w4,0.02,K4)
d4=box("k4_door",(1.3,0.1,3.55),(50.25,-3.05,1.78),bpy.data.materials["pintu4"],0.02,K4)
p_k4=pivot("PIV_k4door",(49.6,-3.05,0),[d4])
gp=plane("fake_hijau",(2.2,1.6),(-1.0,6.0,3.2),mat("#40FF70",0.5,0,emit="#40FF70",es=0.0,name="kaca_hijau_luar"),rot=(math.radians(90),0,0))
bpy.ops.object.light_add(type='POINT',location=(-1.0,5.4,3.2)); lfg=C.object; lfg.name="L_fakehijau"; lfg.data.color=(0.3,1,0.45); lfg.data.use_shadow=False
bpy.ops.object.light_add(type='SPOT',location=(0,0,0)); sen=C.object; sen.name="L_senter"; sen.data.spot_size=math.radians(38); sen.data.spot_blend=0.35; sen.data.color=(1,0.95,0.85); sen.data.use_shadow=False
bpy.ops.object.light_add(type='POINT',location=(0,-2.3,2.6)); lhp=C.object; lhp.name="L_hp"; lhp.data.color=(0.7,0.85,1); lhp.data.use_shadow=False; lhp.data.shadow_soft_size=0.2
# ---------- helpers ----------
def T(f): return (f-1)/FPS
def ss(x): x=max(0,min(1,x)); return x*x*(3-2*x)
SH=TL["shots"]; CL=TL["clips"]
def shot_at(t):
    for s in SH:
        if s["start"]<=t<s["end"]: return s
    return SH[-1]
SPK={"nayla":"Nayla","ibukos":"Ibu","adel":"Adel","dimas":"Dimas"}
LIPS={k:json.load(open(f"/home/claude/ep02/audio/lips_{k}.json"))["mouthCues"] for k in SPK}
def clip_of(char,t):
    for c in CL:
        if SPK.get(c["spk"])==char and c["dst"]<=t<c["dst"]+c["dur"]: return c
    return None
def last_clip(char,t):
    lc=None
    for c in CL:
        if SPK.get(c["spk"])==char and c["dst"]<=t: lc=c
    return lc
EMO={"ceria":(0,9),"cemas":(6,12),"penasaran":(8,0),"curiga":(7,12),"mikir":(10,0),"bingung":(9,15),"tegas":(5,12),"takut":(11,11),
     "panik":(11,11),"tenang":(0,12),"beku":(2,12),"senyum":(0,9)}
VIS={"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8}
def viseme(spk,c,t):
    src=c["src"][0]+(t-c["dst"])
    for q in LIPS[spk]:
        if q["start"]<=src<q["end"]: return q["value"]
    return "X"
NAY_OVR={"tiptoe":"takut","door_reveal":"takut","pov":"takut","scream":"takut","run":"panik","lean_door":"panik","report":"panik","freeze":"beku","ending":"beku","whisper":"beku"}
def emo_for(char,t,s):
    if char=="Nayla" and s["act"] in NAY_OVR and not clip_of("Nayla",t): return NAY_OVR[s["act"]]
    lc=last_clip(char,t)
    if lc: return lc["emo"]
    return {"Nayla":"cemas","Adel":"ceria","Dimas":"senyum","Ibu":"tenang"}[char]
# ---------- shot specs ----------
# cam: (loc0,tgt0,lens,loc1,tgt1,fstop,shake)   chars: name:(x,y,z,rotz[,x1,y1,rotz1])
S={
"s1":dict(cam=((0,-3.25,2.78),(0,-1.6,2.74),35,(0,-3.1,2.78),(0,-1.6,2.74),1.2,1),chars={"Nayla":(0,-1.6,0,0)}),
"s2":dict(cam=((-0.6,-0.4,3.0),(-1.0,4.6,3.1),30,None,None,2.0,0),chars={"Nayla":(-1.0,2.4,0,180)}),
"s3":dict(cam=((96.5,-9.3,8.5),(101,0,2.4),18,(97,-9.3,6.0),(101,0,2.4),6,0),chars={"Nayla":(101.0,-1.3,0.3,0),"Adel":(96.6,-0.9,0.3,0),"Dimas":(91.6,-0.9,0.3,0)}),
"s4":dict(cam=("track",),chars={"Nayla":(90.5,-1.45,0.3,90,100.5,-1.45,90),"Dimas":(91.4,-0.75,0.3,-15),"Adel":(96.4,-0.75,0.3,-10)}),
"s5":dict(cam=((106.5,-5.6,2.6),(106.6,0,2.1),30,(106.6,-3.3,2.45),(106.6,0,2.1),2.5,0),chars={"Nayla":(103.4,-1.5,0.3,60)}),
"s6":dict(cam=((104.6,-6.0,2.45),(105.4,-1.0,2.2),35,None,None,2.2,0),chars={"Nayla":(104.6,-1.3,0.3,0)}),
"s7":dict(cam=((99.5,-8.8,3.0),(104.5,0,2.2),22,None,None,4,0),chars={}),
"s8":dict(cam=((-1.0,4.25,2.85),(-1.0,2.9,2.75),32,None,None,1.6,0),chars={"Nayla":(-1.0,2.9,0,180)}),
"s9":dict(cam=((107.4,-3.9,2.6),(108.7,0,2.6),38,(107.5,-3.4,2.6),(108.7,0,2.6),2,0),chars={}),
"s10":dict(cam=((0.6,-4.4,2.9),(0,0.6,2.6),35,None,None,1.8,0),chars={"Nayla":(0,0.6,0,0)}),
"s11":dict(cam=((82.6,0.6,2.4),(87.0,1.6,2.1),26,(83.0,0.7,2.4),(87.0,1.6,2.1),3,0),chars={"Nayla":(89.8,-1.6,0.3,-95)}),
"s12":dict(cam=((88.5,-2.5,2.8),(89.8,-1.6,2.75),45,None,None,1.6,0),chars={"Nayla":(89.8,-1.6,0.3,-95)}),
"s13":dict(cam=((108.8,-2.7,2.6),(107.4,-0.9,2.4),34,None,None,1.8,0),chars={"Nayla":(107.0,-1.0,0.3,90)}),
"s14":dict(cam=((-0.8,-2.4,2.8),(-3.1,2.0,2.3),30,None,None,2.0,0),chars={"Nayla":(-3.1,1.8,0.13,0)}),
"s15":dict(cam=((2.3,-1.8,2.9),(3.9,0.3,2.7),38,None,None,1.6,0),chars={"Nayla":(3.85,0.3,0,90)}),
"s16":dict(cam=((0,-4.6,2.5),(0,0.6,2.5),40,None,None,2.0,0),chars={"Nayla":(0,0.6,0,0)}),
"s17":dict(cam=("trackback",),chars={"Nayla":(101.6,-1.4,0.3,90,105.4,-1.4,90)}),
"s18":dict(cam=((104.9,-1.7,2.4),(106.4,-0.3,2.1),30,None,None,1.8,0),chars={"Nayla":(106.5,-1.15,0.3,180)}),
"s19":dict(cam=((50.9,2.3,2.6),(50.25,-3.2,2.3),30,None,None,2.0,0),chars={"Nayla":(50.25,-3.9,0,180),"Kunti":(52.4,3.0,0.25,-25)}),
"s20":dict(cam=((50.25,-2.4,2.75),(47.5,3.0,1.6),28,(50.25,-2.4,2.75),(51.0,3.0,2.0),2.0,1),chars={"Nayla":(50.25,-2.95,0,180),"Kunti":(52.4,3.0,0.25,-25)}),
"s21":dict(cam=((50.4,-1.6,2.7),(48.5,3.0,2.2),35,(50.4,-1.6,2.7),(52.4,3.0,2.4),2.0,0),chars={"Nayla":(50.25,-2.95,0,180),"Kunti":(52.4,3.0,0.25,-25)}),
"s22":dict(cam=((50.25,-0.95,2.78),(50.25,-2.6,2.74),35,None,None,1.4,2),chars={"Nayla":(50.25,-2.6,0,180)}),
"s23":dict(cam=((100.8,-7.6,3.0),(104.5,-1.0,2.0),24,None,None,3,1),chars={"Nayla":(106.4,-1.3,0.3,-90,102.9,-0.9,-90)}),
"s24":dict(cam=((1.0,-2.2,2.7),(3.95,-1.6,2.5),32,None,None,1.8,1),chars={"Nayla":(3.95,-1.6,0,-90)}),
"s25":dict(cam=((96.5,-9.3,7.8),(102,0,2.2),18,(96.8,-9.3,7.3),(102,0,2.2),6,0),chars={"Ibu":(113.5,-1.8,0.35,-30)}),
"s26":dict(cam=((113.3,-6.2,2.5),(113.3,-1.6,2.3),32,None,None,2.2,0),chars={"Nayla":(112.2,-1.5,0.35,55),"Ibu":(114.4,-1.8,0.35,-55)}),
"s27":dict(cam=((113.6,-3.7,2.9),(114.4,-1.8,2.75),45,None,None,1.6,0),chars={"Nayla":(112.2,-1.5,0.35,55),"Ibu":(114.4,-1.8,0.35,-55)}),
"s27b":dict(cam=((112.8,-3.5,2.85),(112.2,-1.5,2.75),45,None,None,1.6,0),chars={"Nayla":(112.2,-1.5,0.35,55),"Ibu":(114.4,-1.8,0.35,-55)}),
"s28":dict(cam=((108.6,-5.0,2.5),(108.7,-1.2,2.4),35,None,None,2.0,0),chars={"Adel":(109.3,-1.25,0.3,25),"Dimas":(108.0,-1.1,0.3,15),"Nayla":(112.2,-1.5,0.35,55),"Ibu":(114.4,-1.8,0.35,-55)}),
"s28d":dict(cam=((107.6,-3.2,2.85),(108.0,-1.1,2.75),45,None,None,1.6,0),chars={"Adel":(109.3,-1.25,0.3,25),"Dimas":(108.0,-1.1,0.3,15),"Nayla":(112.2,-1.5,0.35,55)}),
"s29":dict(cam=((112.7,-3.6,2.85),(112.2,-1.5,2.75),45,(112.4,-2.9,2.8),(112.2,-1.5,2.75),1.4,0),chars={"Nayla":(112.2,-1.5,0.35,55),"Ibu":(114.4,-1.8,0.35,-55)}),
"s30":dict(cam=((106.6,-2.4,2.0),(107.05,-0.2,1.8),45,None,None,1.4,0),chars={}),
"s31":dict(cam=((-1.0,-1.4,2.8),(-1.0,2.6,2.65),35,None,None,1.8,0),chars={"Nayla":(-1.0,2.6,0,0)}),
"s32":dict(cam=((-0.85,0.5,2.8),(-1.0,2.6,2.75),50,None,None,1.2,0),chars={"Nayla":(-1.0,2.6,0,0),"Kunti":(-2.4,3.8,0.2,-15)}),
}
RIGS={n:O[f"{n}_rig"] for n in ("Adel","Dimas","Ibu","Kunti")}; RIGS["Nayla"]=O["Nayla_rig"]
FACE={"Nayla":bpy.data.materials["face"],"Adel":bpy.data.materials["face_Adel"],"Dimas":bpy.data.materials["face_Dimas"],"Ibu":bpy.data.materials["face_Ibu"]}
def walk(tl,period=0.7,amp=28):
    p=math.sin(2*math.pi*tl/period)
    return {"leg.L":(amp*p,0,0),"leg.R":(-amp*p,0,0),"arm.L":(-0.8*amp*p,0,-4),"arm.R":(0.8*amp*p,0,4)},0.05*abs(p)
def pose(ch,s,tl,t,c):
    a=s["act"]; d=s["end"]-s["start"]; br=math.sin(2*math.pi*t/3.2); P={"spine":(1.2*br,0,0),"arm.L":(2*br,0,-3),"arm.R":(-2*br,0,3)}; dz=0
    if c:
        P["head"]=(3*math.sin(2*math.pi*t*1.3),2*math.sin(2*math.pi*t*0.7),3*math.sin(2*math.pi*t*0.45))
        cl=t-c["dst"]
        if cl<1.0 and a not in ("phone_ecu","whisper","ending","freeze","scream"):
            g=math.sin(math.pi*cl); k=hash(c["id"])%3
            if k==0: P["arm.R"]=(-35*g,0,3+18*g)
            elif k==1: P["arm.L"]=(-35*g,0,-3-18*g)
            else: P["arm.L"]=(-25*g,0,-3-12*g); P["arm.R"]=(-25*g,0,3+12*g)
    if ch=="Kunti":
        P={"spine":(0,0,0),"arm.L":(-25,0,8),"arm.R":(-25,0,-8),"head":(8,14,0)}
        if s["cam"]=="s21": P["head"]=(8,14+(-30 if (int(tl*12)//3)%2 else 0),0)
        return P,0.08*math.sin(2*math.pi*t*0.6)
    if ch in ("Adel","Dimas") and a=="walk_teras" and tl<2.5: P["arm.L"]=(0,0,-150); P["hand.L"]=(0,0,25*math.sin(2*math.pi*3*tl))
    if ch=="Dimas" and a in ("dimas_scared","freeze") and t>=s["start"]:
        j=2*math.sin(t*50); P["spine"]=(j,0,0); P["arm.L"]=(-40,0,-20); P["arm.R"]=(-40,0,20)
    if ch!="Nayla": return P,dz
    if a=="phone_ecu": P["spine"]=(6,0,0); P["head"]=(-3,0,P.get("head",(0,0,0))[2])
    if a in ("walk_teras",): w,dz=walk(tl); P.update(w)
    if a=="peek": P["spine"]=(8,0,0); P["head"]=(4,10,0)
    if a=="think" and tl>0.4: P["arm.R"]=(-140,0,-12); P["head"]=(-4,8,0)
    if a in ("look_jemuran","bingung"): P["head"]=(-6,10*math.sin(t*1.5),0)
    if a=="sniff": P["spine"]=(14,0,0); P["head"]=(10+4*max(0,math.sin(2*math.pi*tl*2.2)),0,0)
    if a=="sit_bed": P["leg.L"]=(-90,0,0); P["leg.R"]=(-90,0,0); P["foot.L"]=(90,0,0); P["foot.R"]=(90,0,0); P["arm.L"]=(-55,0,8); P["arm.R"]=(-55,0,-8)
    if a=="ear_wall": P["head"]=(0,0,-55); P["spine"]=(0,8,0)
    if a=="tiptoe": w,dz=walk(tl,1.0,14); P.update(w); P["spine"]=(10,0,0); P["arm.R"]=(-60,0,0)
    if a=="knock":
        k0=(TL_knock-s["start"]); kk=tl-k0; g=math.sin(2*math.pi*kk*3.2) if 0<kk<1.0 else 0
        P["arm.R"]=(-75-12*max(0,g),0,-5); P["arm.L"]=(-60,0,10)
    if a in ("door_reveal","pov"): P["spine"]=(-4,0,0); P["arm.R"]=(-60,0,0)
    if a=="scream": g=ss(tl/0.25); P["arm.L"]=(-10,0,-3-135*g); P["arm.R"]=(-10,0,3+135*g); dz=0.25*max(0,math.sin(math.pi*min(1,tl/0.35)))
    if a=="run": w,dz=walk(tl,0.42,42); P.update(w); P["spine"]=(10,0,0)
    if a=="lean_door": P["spine"]=(-8+4*math.sin(2*math.pi*tl*1.6),0,0); P["head"]=(-15,0,0)
    if a=="report": P["arm.L"]=(-30,0,-3-40*abs(math.sin(t*6))); P["arm.R"]=(-30,0,3+40*abs(math.cos(t*6)))
    if a=="confused": P["arm.L"]=(-15,0,-28); P["arm.R"]=(-15,0,28)
    if a in ("freeze","ending","whisper") : P={"spine":(0,0,0),"arm.L":(0,0,-3),"arm.R":(0,0,3),"head":(0,3 if a=="whisper" else 0,0)}
    return P,dz
TL_knock=[e[0] for e in TL["sfx"] if e[1]=="ketuk"][0]
# ---------- lighting presets ----------
L=lambda n:O[n]
def mat_es(name,v):
    m=bpy.data.materials.get(name)
    if m: i=m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; i.default_value=v; i.keyframe_insert("default_value",frame=CUR)
LIGHTS_K=["L_kos_fill","L_kos_window","L_desklamp","L_teras1","L_teras2","L_teras3","L_teras4","L_jalan","L_kamar3","L_hijau","L_neon","L_fakehijau","L_senter","L_hp"]
def setL(vals):
    for n in LIGHTS_K:
        o=O[n]; o.data.energy=vals.get(n,0); o.data.keyframe_insert("energy",frame=CUR)
def sunset(dirv,e,col):
    sun.rotation_euler=Vector(dirv).normalized().to_track_quat('-Z','Y').to_euler(); sun.data.energy=e; sun.data.color=col
    sun.keyframe_insert("rotation_euler",frame=CUR); sun.data.keyframe_insert("energy",frame=CUR); sun.data.keyframe_insert("color",frame=CUR)
def world(sore,malam,stren):
    W["W_SORE"].inputs["Factor"].default_value=sore; W["W_MALAM"].inputs["Factor"].default_value=malam; W["W_BG"].inputs[1].default_value=stren
    for i in (W["W_SORE"].inputs["Factor"],W["W_MALAM"].inputs["Factor"],W["W_BG"].inputs[1]): i.keyframe_insert("default_value",frame=CUR)
def preset(setn,s,flick,flick2):
    v={}
    if setn=="kamar_malam":
        world(0,1,0.25); sunset((0.2,-1,-0.5),0.6,(0.55,0.65,1.0)); v.update(L_kos_fill=70,L_kos_window=60,L_desklamp=180)
        v["L_fakehijau"]=60*flick; mat_es("kaca_hijau_luar",4*flick); mat_es("layar_laptop",6)
        if s["cam"]=="s1": v["L_hp"]=18
    elif setn=="luar_malam":
        world(0,1,0.35); sunset((-0.4,0.7,-0.6),0.7,(0.55,0.65,1.0)); v.update(L_teras1=45,L_teras2=45,L_teras3=45,L_teras4=45,L_jalan=350,L_kamar3=60)
        v["L_hijau"]=90*flick; mat_es("kaca4",3*flick); mat_es("lampu_teras1",6); mat_es("lampu_jalan",8); mat_es("kaca3",1.5); mat_es("kaca_rumah",1.0); mat_es("nkaca0",1.0)
    elif setn=="kamar4":
        world(0,1,0.12); sunset((0.2,-1,-0.5),0.25,(0.55,0.65,1.0)); v["L_neon"]=130*flick2; mat_es("neon_hijau",12*flick2)
    elif setn=="luar_siang":
        world(0,0,0.9); sunset((0.5,0.8,-0.9),4.0,(1,0.95,0.86))
        for m in ("kaca4","lampu_teras1","lampu_jalan","kaca3","kaca_rumah","nkaca0"): mat_es(m,0)
    elif setn=="luar_pagi":
        world(0,0,0.7); sunset((0.75,0.55,-0.38),3.2,(1,0.82,0.62))
        for m in ("kaca4","lampu_teras1","lampu_jalan","kaca3","kaca_rumah","nkaca0"): mat_es(m,0)
    if s["act"] in ("tiptoe","knock","door_reveal","pov","scream") or s["cam"] in ("s20","s21"): v["L_senter"]=450
    if s["cam"]=="s22": v["L_hp"]=35
    setL(v)
# ---------- bake ----------
rng=random.Random(9); blinks={}
for ch in FACE:
    b=set(); tb=rng.uniform(0.8,2.5)
    while tb<TOTAL: b.add(int(tb*FPS)+1); tb+=rng.uniform(2.3,4.5)
    blinks[ch]=b
def tileloc(i): return ((i%4)*0.25,(3-i//4)*0.25,0.0)
prev_tiles={ch:None for ch in FACE}
PARK=Vector((0,-200,0))
gown=O["x_baju_putih"]; phone=O["phone"]; pscr=O["phone_screen"]
for f in range(1,NF+1):
    CUR=f; t=T(f); s=shot_at(t); tl=t-s["start"]; spec=S[s["cam"]]
    flick=1.0 if (rng.random()>0.22 and int(t*7)%9!=0) else 0.15
    flick2=(1.0 if rng.random()>0.45 else 0.35) if s["cam"] in ("s21","s22") else max(flick,0.35)
    preset(s["set"],s,flick,flick2)
    for ch,rig in RIGS.items():
        c=spec["chars"].get(ch)
        if not c: rig.location=PARK; rig.rotation_euler=(0,0,0)
        else:
            if len(c)>4:
                dur={"s23":1.3}.get(s["cam"],s["end"]-s["start"]); g=min(1,tl/dur)
                x=c[0]+(c[4]-c[0])*g; y=c[1]+(c[5]-c[1])*g; rz=c[3]+(c[6]-c[3])*g
            else: x,y,rz=c[0],c[1],c[3]
            cc=clip_of(ch,t) if ch in FACE else None
            P,dz=pose(ch,s,tl,t,cc)
            rig.location=Vector((x,y,c[2]+dz)); rig.rotation_euler=(0,0,math.radians(rz))
            for b in ["spine","head","arm.L","arm.R","hand.L","hand.R","leg.L","leg.R","hips","foot.L","foot.R"]:
                pb=rig.pose.bones.get(b)
                if pb: pb.rotation_mode='XYZ'; pb.rotation_euler=[math.radians(v) for v in P.get(b,(0,0,0))]; pb.keyframe_insert("rotation_euler",frame=f)
        rig.keyframe_insert("location",frame=f); rig.keyframe_insert("rotation_euler",index=2,frame=f)
        if ch in FACE:
            em=emo_for(ch,t,s); et,mt=EMO[em]
            if f in blinks[ch] and et not in (1,3,12,15): et=1
            cc=clip_of(ch,t)
            if cc:
                spk=[k for k,v in SPK.items() if v==ch][0]; mt=VIS.get(viseme(spk,cc,t),mt)
            if prev_tiles[ch]!=(et,mt) or f==1:
                N=FACE[ch].node_tree.nodes
                N["AT_eyes"].inputs["Location"].default_value=tileloc(et); N["AT_eyes"].inputs["Location"].keyframe_insert("default_value",frame=f)
                N["AT_mouth"].inputs["Location"].default_value=tileloc(mt); N["AT_mouth"].inputs["Location"].keyframe_insert("default_value",frame=f)
                prev_tiles[ch]=(et,mt)
    # camera
    cs=spec["cam"]; d=s["end"]-s["start"]; g=ss(tl/d)
    if cs[0]=="track":
        nx=RIGS["Nayla"].location.x; cl=Vector((nx-0.3,-6.6,2.4)); ct=Vector((nx+0.6,-1.0,2.0)); lens,fs,sh=28,2.2,0
    elif cs[0]=="trackback":
        nx=RIGS["Nayla"].location.x; cl=Vector((nx-3.2,-2.3,2.7)); ct=Vector((nx+2,-1.0,2.0)); lens,fs,sh=28,2.0,1
    else:
        l0,t0,lens,l1,t1,fs,sh=cs
        gg=ss(min(1,tl/0.25)) if s["cam"]=="s21" else g
        cl=Vector(l0).lerp(Vector(l1),gg) if l1 else Vector(l0); ct=Vector(t0).lerp(Vector(t1),gg) if t1 else Vector(t0)
        if s["cam"]=="s32" and tl>d-1.4: ct=ct.lerp(Vector((-2.4,3.8,2.6)),ss((tl-(d-1.4))/0.6))
    if sh: cl=cl+Vector((rng.gauss(0,0.012*sh),rng.gauss(0,0.006*sh),rng.gauss(0,0.012*sh)))
    cam.location=cl; tgt.location=ct; cam.data.lens=lens; cam.data.dof.aperture_fstop=fs
    cam.keyframe_insert("location",frame=f); tgt.keyframe_insert("location",frame=f); cam.data.keyframe_insert("lens",frame=f); cam.data.dof.keyframe_insert("aperture_fstop",frame=f)
    # flashlight
    if s["cam"]=="s20": sen.location=cl; sen.rotation_euler=(ct-cl).to_track_quat('-Z','Y').to_euler()
    elif s["cam"]=="s21": sen.location=Vector((50.3,-2.4,2.2)); sen.rotation_euler=(Vector((52.4,3.0,2.2))-sen.location).to_track_quat('-Z','Y').to_euler()
    else:
        r=RIGS["Nayla"]; fwd=Vector((math.sin(r.rotation_euler.z),-math.cos(r.rotation_euler.z),0))
        sen.location=r.location+fwd*0.6+Vector((0,0,1.9)); sen.rotation_euler=(fwd+Vector((0,0,-0.15))).to_track_quat('-Z','Y').to_euler()
    sen.keyframe_insert("location",frame=f); sen.keyframe_insert("rotation_euler",frame=f)
    if s["cam"]=="s22": lhp.location=Vector((50.25,-1.4,2.9)); lhp.data.color=(0.45,1,0.55)
    else: lhp.location=Vector((0,-2.3,2.6)); lhp.data.color=(0.7,0.85,1)
    lhp.keyframe_insert("location",frame=f); lhp.data.keyframe_insert("color",frame=f)
    # props
    vis=s["cam"] in ("s11","s12"); gown.hide_render=not vis; gown.keyframe_insert("hide_render",frame=f)
    ph=s["act"] in ("tiptoe","knock"); phone.hide_render=pscr.hide_render=not ph; phone.keyframe_insert("hide_render",frame=f); pscr.keyframe_insert("hide_render",frame=f)
    p_door4.rotation_euler=(0,0,math.radians(-14 if s["cam"]=="s7" else 0)); p_door4.keyframe_insert("rotation_euler",index=2,frame=f)
    k=0.0
    if s["cam"]=="s19": k=ss((tl-0.2)/1.3)*80
    elif s["cam"] in ("s20","s21","s22"): k=80
    p_k4.rotation_euler=(0,0,math.radians(k)); p_k4.keyframe_insert("rotation_euler",index=2,frame=f)
    rd=0.0
    if s["cam"]=="s24": rd=(1-ss(tl/0.18))*-70
    p_room.rotation_euler=(0,0,math.radians(rd)); p_room.keyframe_insert("rotation_euler",index=2,frame=f)
    O["fake_hijau"].hide_render=False
def const(ad):
    if ad and ad.action:
        for layer in getattr(ad.action,"layers",[]):
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        for k in fc.keyframe_points: k.interpolation='CONSTANT'
        for fc in getattr(ad.action,"fcurves",[]):
            for k in fc.keyframe_points: k.interpolation='CONSTANT'
for idb in list(bpy.data.objects)+list(bpy.data.materials)+list(bpy.data.lights)+list(bpy.data.cameras)+[sc.world]:
    const(idb.animation_data); nt=getattr(idb,"node_tree",None)
    if nt: const(nt.animation_data)
sc.frame_set(1); sc.render.filepath="//frames/"; sc.render.image_settings.file_format='PNG'
sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1080; sc.render.resolution_y=1920
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep02/ep02.blend"); print("ANIM2 OK",NF)
