import bpy, json, math, random, sys
from mathutils import Vector, Euler
bpy.ops.wm.open_mainfile(filepath="/home/claude/ep01/ep01_sets.blend")
sc=bpy.context.scene; FPS=12
TL=json.load(open("/home/claude/ep01/timeline.json")); LIPS=json.load(open("/home/claude/ep01/audio/lips.json"))["mouthCues"]
TOTAL=TL["total"]; NF=int(round(TOTAL*FPS)); sc.frame_start=1; sc.frame_end=NF
rig=bpy.data.objects["Nayla_rig"]; pb=rig.pose.bones; cam=bpy.data.objects["CAM"]; tgt=bpy.data.objects["CAM_TGT"]
sun=bpy.data.objects["SUN"]; W=sc.world.node_tree.nodes
def T(f): return (f-1)/FPS
def ss(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,b,t): return Vector(a).lerp(Vector(b),t)
SET_O={"kos_pagi":(0,0),"kos_malam":(0,0),"kampus":(60,0),"kota":(120,0)}
# ---------------- shot specs ----------------
# cam: (loc0,tgt0,lens,loc1,tgt1,fstop,shake)  coords relative to set origin
CAM={
"ecu_hand":((0,-3.25,2.78),(0,-1.6,2.74),35,None,None,1.2,1),
"ms_pullback":((0,-4.6,2.6),(0,-1.2,2.3),35,(0,-7.6,2.4),(0,0.6,2.1),1.8,1),
"ms_eye":((0,-7.2,2.3),(0,0.6,2.0),40,None,None,2.0,0),
"mcu_push":((0,-6.0,2.6),(0,0.6,2.5),45,(0,-4.7,2.65),(0,0.6,2.55),2.0,0),
"wide_high":((0.6,-9.0,8.5),(0,1.4,1.0),22,None,None,4.0,0),
"wide_pan":((-2.6,-8.2,3.6),(-1.2,1.6,1.8),22,(2.4,-8.2,3.6),(1.2,1.6,1.8),4.0,0),
"ins_desk":((0.6,-0.6,3.0),(3.4,3.0,1.8),30,(0.9,-0.2,2.9),(3.4,3.2,1.8),1.6,0),
"ins_fan":((-0.4,0.6,2.8),(-1.3,3.35,2.75),40,None,None,1.4,2),
"cu_rice":((1.3,-4.4,2.5),(3.3,-1.2,2.0),35,(1.6,-4.0,2.45),(3.3,-1.2,2.05),1.6,0),
"est_low":((-3,-6.5,0.7),(0,12,6.5),18,(-2,-6.5,0.9),(0.5,12,6.5),6.0,0),
"track_side":(None,None,35,None,None,2.2,0),
"ms_k":((1,-6.6,2.3),(1,0.6,2.2),40,None,None,2.0,0),
"cu_zoom":((1,-6.0,2.7),(1,0.6,2.72),45,(1,-3.6,2.75),(1,0.6,2.75),2.0,0),
"cu_static":((1,-3.5,2.75),(1,0.6,2.72),50,None,None,2.0,0),
"ms_k2":((-0.6,-6.2,2.6),(1,0.6,2.0),35,None,None,2.0,0),
"low_hero":((1,-3.2,0.55),(1,0.6,2.7),20,None,None,3.0,0),
"mw_bench":((3.0,-3.6,2.3),(4,3.3,1.9),32,(3.3,-3.2,2.3),(4,3.3,1.95),2.2,0),
"cu_phone":((4.6,0.4,2.5),(4,3.4,2.45),45,None,None,1.6,0),
"est_tilt":((-8,-15,10),(2,7,0.5),55,(-6,-15,10),(4,7,0.5),0.35,0),
"track_front":(None,None,35,None,None,2.0,0),
"ms_c":((1,-6.4,2.4),(1,0.4,2.2),35,None,None,2.2,0),
"ins_ojol":((-2.5,-4.2,1.5),(1,4,1.6),26,None,None,3.0,0),
"ins_cilok":((-6.4,-5.6,2.3),(-3.3,-0.3,1.7),30,(-6.0,-5.0,2.2),(-3.3,-0.3,1.7),2.0,0),
"wide_traffic":((-10,-13,7),(1,5,1),32,(-8,-13,7),(2,5,1),3.0,0),
"cu_gaze":((1.9,-2.7,2.9),(1,0.4,2.75),55,None,None,1.6,0),
"crane_sunset":((4,-4.0,1.4),(1,0.4,2.6),28,(6.5,-9.5,6.5),(1,6,4.5),5.0,0),
"est_night":((0.4,-9.6,6.2),(0.5,1.6,1.6),22,None,None,4.0,0),
"ms_desk":((0.4,-3.7,2.7),(1.55,2.6,2.45),35,None,None,1.8,0),
"cu_desk":((0.9,-1.0,3.0),(1.55,2.6,2.9),45,(1.0,-0.6,3.0),(1.55,2.6,2.9),1.6,0),
"ins_items":((2.0,0.4,2.5),(3.6,2.5,1.9),32,(2.4,1.0,2.3),(3.7,2.6,1.9),1.4,0),
"ms_desk2":((-0.6,-3.1,2.8),(1.55,2.6,2.3),35,None,None,1.8,0),
"wide_fan":((-4.2,-1.2,2.9),(-0.8,2.4,2.4),26,None,None,3.0,0),
"mcu_follow":((0,-5.0,2.7),(0,0.6,2.5),45,None,None,2.0,0),
"ins_rice2":((2.5,-3.4,2.0),(3.7,-1.5,1.75),50,None,None,1.4,0),
"cu_shock":((0,-3.5,2.75),(0,0.6,2.72),50,None,None,2.0,2),
"run_ecu":((0,-3.25,2.78),(0,-1.6,2.74),35,None,None,1.2,1),
}
# nayla: (x0,y0,rotz,x1,y1,rotz1, seated)
NAY={1:(0,-1.6,0),2:(0,-1.6,0,0,0.6,0),3:(0,0.6,0),4:(0,0.6,0),5:(0,0.6,-10),6:(0,0.6,0),7:(0,0.6,40,1.0,1.4,40),8:(-0.4,1.4,0),
9:(2.85,-0.75,45),10:(-6,0.6,90,-2.0,0.6,90),11:(-1.5,0.6,90,2.0,0.6,90),12:(1,0.6,0),13:(1,0.6,0),14:(1,0.6,0),15:(1,0.6,0),16:(1,0.6,0),
17:(4,3.25,0,None,None,None,"bench"),18:(4,3.25,0,None,None,None,"bench"),19:(80,0,0),20:(6,0.4,-90,2.0,0.4,-90),21:(1,0.4,0),22:(-1.5,0.2,0),
23:(-2.5,-0.8,20),24:(1,0.4,0),25:(1,0.4,-20),26:(1,0.4,180),27:(1.55,2.6,90,None,None,None,"stool"),28:(1.55,2.6,30,None,None,None,"stool"),
29:(1.55,2.6,30,None,None,None,"stool"),30:(1.55,2.6,60,None,None,None,"stool"),31:(1.55,2.6,30,None,None,None,"stool"),32:(-0.3,1.3,-153),
33:(0,0.6,0),34:(0,0.6,0),35:(0,0.6,0),36:(0,0.6,0,0,-1.6,0)}
SEAT={"bench":1.075,"stool":1.07}
SH=TL["shots"]; assert len(SH)==36, len(SH)
def shot_at(t):
    for s in SH:
        if s["start"]<=t<s["end"]: return s
    return SH[-1]
clips=TL["clips"]
def clip_at(t):
    for c in clips:
        if c["dst"]<=t<c["dst"]+c["dur"]: return c
    return None
def last_clip(t):
    lc=clips[0]
    for c in clips:
        if c["dst"]<=t: lc=c
    return lc
EMO=TL["emo"]
OVR=[(19.72+1.6,23.09,"kesal"),(28.1,31.97,"ceria"),(58.98+1.2,63.25,"pasrah"),(75.31,78.81,"jahil"),(83.35+2.0,90.17,"lembut"),(90.17,93.3,"lembut"),
     (C:=0,0,"x")]
OVR=[o for o in OVR if o[2]!="x"]
c33=[c for c in clips if c["id"]=="u33"][0]; OVR.append((c33["dst"]+c33["dur"],c33["dst"]+c33["dur"]+2.2,"deadpan"))
OVR.append((SH[34]["start"]+0.6,SH[35]["start"],"panik")); OVR.append((SH[35]["start"],TOTAL+1,"panik"))
def emo_at(t):
    for a,b,e in OVR:
        if a<=t<b: return e
    return last_clip(t)["emo"]
VIS={"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8}
def viseme_at(t,c):
    src=c["src"][0]+(t-c["dst"])
    for q in LIPS:
        if q["start"]<=src<q["end"]: return q["value"]
    return "X"
rng=random.Random(11); blinks=set(); tb=1.5
while tb<TOTAL: blinks.add(int(tb*FPS)+1); tb+=rng.uniform(2.4,4.4)
# ---------------- pose library ----------------
def walk(tl,period=0.7,amp=28):
    p=math.sin(2*math.pi*tl/period)
    return {"leg.L":(amp*p,0,0),"leg.R":(-amp*p,0,0),"arm.L":(-0.8*amp*p,0,-4),"arm.R":(0.8*amp*p,0,4)}, 0.05*abs(math.sin(2*math.pi*tl/period))
def pose_for(s,tl,t,speaking,clip):
    a=s["act"]; d=s["end"]-s["start"]; P={}; dz=0
    br=math.sin(2*math.pi*t/3.2)
    P["spine"]=(1.2*br,0,0); P["arm.L"]=(2*br,0,-3); P["arm.R"]=(-2*br,0,3); P["head"]=(0,0,0)
    if speaking:
        P["head"]=(3*math.sin(2*math.pi*t*1.3),2*math.sin(2*math.pi*t*0.7),3*math.sin(2*math.pi*t*0.45))
        if clip:
            cl=t-clip["dst"]; k=hash(clip["id"])%3
            if cl<1.0 and a in("talk","sit_talk","talk_fan","talk_shrug"):
                g=math.sin(math.pi*min(1,cl/1.0))
                if k==0: P["arm.R"]=(-35*g,0,3+18*g)
                elif k==1: P["arm.L"]=(-35*g,0,-3-18*g)
                else: P["arm.L"]=(-25*g,0,-3-12*g); P["arm.R"]=(-25*g,0,3+12*g)
    if a=="too_close": P["spine"]=(9,0,0); P["head"]=(-4,0,0)
    if a=="step_back":
        if tl<0.8: w,dz=walk(tl,0.4,22); P.update(w)
        elif tl<1.8: g=math.sin(math.pi*(tl-0.8)); P["arm.R"]=(-40*g,0,3+110*g); P["head"]=(0,-6*g,0)
    if a=="wave" and tl<1.8:
        P["arm.L"]=(0,0,-150); P["hand.L"]=(0,0,25*math.sin(2*math.pi*3*tl))
    if a=="present": g=ss(tl/0.5); P["arm.R"]=(-30*g,0,3+65*g); P["head"]=(0,0,25*g)
    if a=="arms_open": g=ss(tl/0.4); P["arm.L"]=(-10*g,0,-3-70*g); P["arm.R"]=(-10*g,0,3+70*g)
    if a in("walk_desk","walk_in","walk","walk_city"):
        w,dz=walk(tl); P.update(w)
    if a=="fan_gag" and tl>1.2:
        sh=math.sin(2*math.pi*tl*7)*2; P["arm.L"]=(-20,0,-150); P["arm.R"]=(-20,0,150); P["spine"]=(sh,0,0); P["head"]=(0,sh*2,0)
    if a=="hug_rice":
        g=ss(tl/0.6); P["arm.L"]=(-70*g,0,-3+20*g); P["arm.R"]=(-70*g,0,3-20*g); P["spine"]=(14*g,0,0); P["head"]=(0,10*g*math.sin(2*math.pi*tl*0.6),0)
    if a=="silly": P["arm.R"]=(-20,0,80); P["head"]=(0,14*(1 if (clip and clip["id"]=="u14") else -1),0)
    if a=="deadpan": P={"spine":(0,0,0),"arm.L":(0,0,-3),"arm.R":(0,0,3),"head":(0,0,0)}
    if a=="talk_shrug" and clip and t-clip["dst"]<0.7:
        g=math.sin(math.pi*(t-clip["dst"])/0.7); P["arm.L"]=(-15*g,0,-3-28*g); P["arm.R"]=(-15*g,0,3+28*g); P["spine"]=(0,0,0)
    if a=="hero":
        P["arm.L"]=(15,0,-38); P["arm.R"]=(15,0,38); P["spine"]=(-6,0,0); P["head"]=(-8,P["head"][1],P["head"][2])
        if clip and clip["id"]=="u21": dz=0.08*abs(math.sin(2*math.pi*t*3)); P["head"]=(-12,0,0)
    if a in("sit_phone","phone_buzz"):
        P["leg.L"]=(-90,0,0); P["leg.R"]=(-90,0,0); P["foot.L"]=(90,0,0); P["foot.R"]=(90,0,0); P["arm.R"]=(-78,0,-12); P["hand.R"]=(0,0,0); P["head"]=(14,0,-6)
        if speaking and a=="sit_phone" and (t%3)<1.4: P["head"]=(0,0,0)
        if a=="phone_buzz" and not speaking: P["hand.R"]=(4*math.sin(t*60),0,4*math.cos(t*47))
    if a=="watch_ojol": P["head"]=(0,0,-45+90*ss(tl/d))
    if a=="point_cilok": g=ss(tl/0.4); P["arm.R"]=(-45*g,0,3+60*g); P["head"]=(0,0,20*g)
    if a=="gaze": P["head"]=(-4,0,6*math.sin(2*math.pi*t*0.15))
    if a=="gaze_far": P["head"]=(-10,0,0); P["arm.L"]=(0,0,-3); P["arm.R"]=(0,0,3)
    if a in("sit_desk_idle","sit_talk"):
        P["leg.L"]=(-90,0,0); P["leg.R"]=(-90,0,0); P["foot.L"]=(90,0,0); P["foot.R"]=(90,0,0)
        if a=="sit_desk_idle": ty=math.sin(t*25)*4; P["arm.L"]=(-65+ty,0,10); P["arm.R"]=(-65-ty,0,-10); P["head"]=(10,0,0)
    if a=="talk_fan": pass
    if a=="shock":
        dz=0.35*max(0,math.sin(math.pi*min(1,tl/0.35))); g=ss(tl/0.25); P["arm.L"]=(-10,0,-3-135*g); P["arm.R"]=(-10,0,3+135*g)
    if a=="run_cam":
        if tl<1.3: w,dz=walk(tl,0.42,42); P.update(w); P["spine"]=(10,0,0)
        else: P["head"]=(-4,0,0); P["spine"]=(9,0,0)
    return P,dz
def path(s,tl):
    n=s["n"]; spec=NAY[n]; d=s["end"]-s["start"]; ox,oy=SET_O[s["set"]]
    x0,y0,r0=spec[0],spec[1],spec[2]
    if len(spec)>=6 and spec[3] is not None:
        dur={2:0.8,36:1.3}.get(n,d); g=min(1,tl/dur) if n in(2,36) else tl/d
        x=x0+(spec[3]-x0)*g; y=y0+(spec[4]-y0)*g; r=r0+(spec[5]-r0)*g
    else: x,y,r=x0,y0,r0
    seat=spec[6] if len(spec)>6 else None
    return Vector((ox+x,oy+y,0)),r,seat
# ---------------- bake ----------------
rig.animation_data_create(); cam.animation_data_create()
fmat=bpy.data.materials["face"]; FN=fmat.node_tree.nodes; ATE=FN["AT_eyes"].inputs["Location"]; ATM=FN["AT_mouth"].inputs["Location"]
def tileloc(i): return ((i%4)*0.25,(3-i//4)*0.25,0.0)
fan_b=bpy.data.objects["FAN_BLADES"]; fan_h=bpy.data.objects["FAN_HEAD"]
cars=[bpy.data.objects[f"CAR{i}"] for i in range(6)]; ojol=bpy.data.objects["OJOL"]
harga=bpy.data.materials["harga"].node_tree.nodes["HARGA"].inputs["Factor"]
lap=bpy.data.materials["layar_laptop"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
rcl=bpy.data.materials["lampu_rc"].node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
Lf=bpy.data.objects["L_kos_fill"]; Lw=bpy.data.objects["L_kos_window"]; Ld=bpy.data.objects["L_desklamp"]
phone=bpy.data.objects["phone"]; scr=bpy.data.objects["phone_screen"]
wS=W["W_SORE"].inputs["Factor"]; wM=W["W_MALAM"].inputs["Factor"]; wB=W["W_BG"].inputs[1]
def sundir(v,strength,col):
    sun.rotation_euler=Vector(v).normalized().to_track_quat('-Z','Y').to_euler(); sun.data.energy=strength; sun.data.color=col
LIGHT={
"kos_pagi":dict(w=(0,0,0.7),sun=((0.35,-1,-0.75),3.2,(1,0.92,0.8)),fill=(120,(1,0.97,0.92)),win=(260,(1,0.93,0.82)),desk=0,lap=1.0),
"kos_malam":dict(w=(0,1,0.3),sun=((0.35,-1,-0.75),0.0,(0.6,0.7,1)),fill=(70,(1.0,0.82,0.66)),win=(70,(0.55,0.65,1.0)),desk=180,lap=6.0),
"kampus":dict(w=(0,0,1.0),sun=((0.45,0.75,-0.9),4.5,(1,0.95,0.86)),fill=(0,(1,1,1)),win=(0,(1,1,1)),desk=0,lap=1.0),
"kota":dict(w=(1,0,0.65),sun=((0.85,0.45,-0.42),2.4,(1,0.68,0.42)),fill=(0,(1,1,1)),win=(0,(1,1,1)),desk=0,lap=1.0),
}
prev_tiles=(None,None)
def K(obj,path,f,idx=-1): obj.keyframe_insert(path,frame=f,index=idx)
rng2=random.Random(5)
for f in range(1,NF+1):
    t=T(f); s=shot_at(t); tl=t-s["start"]; n=s["n"]
    c=clip_at(t); speaking=c is not None
    # ---- Nayla root
    loc,rz,seat=path(s,tl); P,dz=pose_for(s,tl,t,speaking,c)
    if seat: loc.z=SEAT[seat]-0.92+0.02
    loc.z+=dz; rig.location=loc; rig.rotation_euler=(0,0,math.radians(rz))
    K(rig,"location",f); K(rig,"rotation_euler",f,2)
    for b in ["spine","head","arm.L","arm.R","hand.L","hand.R","leg.L","leg.R","hips","foot.L","foot.R"]:
        v=P.get(b,(0,0,0)); pbn=pb[b]; pbn.rotation_mode='XYZ'; pbn.rotation_euler=[math.radians(a) for a in v]
        pbn.keyframe_insert("rotation_euler",frame=f)
    # ---- face
    emo=emo_at(t); et,mt=EMO[emo]
    if f in blinks and et not in (1,3,12,15): et=1
    if speaking:
        v=viseme_at(t,c); mt=VIS.get(v,mt)
    if (et,mt)!=prev_tiles or f==1:
        ATE.default_value=tileloc(et); ATE.keyframe_insert("default_value",frame=f)
        ATM.default_value=tileloc(mt); ATM.keyframe_insert("default_value",frame=f); prev_tiles=(et,mt)
    # ---- camera
    spec=CAM[s["cam"]]; ox,oy=SET_O[s["set"]]; O=Vector((ox,oy,0)); d=s["end"]-s["start"]; g=ss(tl/d)
    if s["cam"]=="track_side": cl=Vector((loc.x-0.5,-5.6,2.4)); ct=Vector((loc.x+0.4,0.6,2.2))
    elif s["cam"]=="track_front": cl=Vector((loc.x-3.6,-0.9,2.3)); ct=Vector((loc.x,loc.y,2.45))
    else:
        l0,t0=Vector(spec[0])+O,Vector(spec[1])+O
        if spec[3]:
            gg=ss(min(1,tl/0.35)) if s["cam"]=="cu_zoom" else g
            l1,t1=Vector(spec[3])+O,Vector(spec[4])+O; cl=l0.lerp(l1,gg); ct=t0.lerp(t1,gg)
        else: cl,ct=l0,t0
    sh=spec[6]
    if sh: cl=cl+Vector((rng2.gauss(0,0.012*sh),rng2.gauss(0,0.006*sh),rng2.gauss(0,0.012*sh)))
    cam.location=cl; tgt.location=ct; cam.data.lens=spec[2]; cam.data.dof.aperture_fstop=spec[5]
    K(cam,"location",f); K(tgt,"location",f); cam.data.keyframe_insert("lens",frame=f); cam.data.dof.keyframe_insert("aperture_fstop",frame=f)
    # ---- lights / world (key on shot change)
    if tl < 1.0/FPS-1e-6 or f==1:
        L=LIGHT[s["set"]]
        wS.default_value,wM.default_value,wB.default_value=L["w"]
        for inp in (wS,wM,wB): inp.keyframe_insert("default_value",frame=f)
        sv=L["sun"]; dirv=sv[0]
        if s["cam"]=="crane_sunset": dirv=(0.3,-1,-0.32)
        sundir(dirv,sv[1],sv[2]); K(sun,"rotation_euler",f); sun.data.keyframe_insert("energy",frame=f); sun.data.keyframe_insert("color",frame=f)
        Lf.data.energy,Lf.data.color=L["fill"]; Lw.data.energy,Lw.data.color=L["win"]; Ld.data.energy=L["desk"]
        for o in (Lf,Lw): o.data.keyframe_insert("energy",frame=f); o.data.keyframe_insert("color",frame=f)
        Ld.data.keyframe_insert("energy",frame=f)
        lap.default_value=L["lap"]; lap.keyframe_insert("default_value",frame=f)
        on=s["act"] in("sit_phone","phone_buzz")
        for o in (phone,scr): o.hide_render=not on; o.hide_viewport=not on; o.keyframe_insert("hide_render",frame=f); o.keyframe_insert("hide_viewport",frame=f)
    # ---- props
    fan_b.rotation_euler=(0,(t*14)%(2*math.pi),0); K(fan_b,"rotation_euler",f,1)
    fz=math.radians(26.6) if n==32 else math.radians(32)*math.sin(2*math.pi*t/7)
    fan_h.rotation_euler=(0,0,fz); K(fan_h,"rotation_euler",f,2)
    spd=3.0 if n==24 else 1.0
    for i,cr in enumerate(cars):
        lane=i%2; v=4.2*spd*(1 if lane==0 else -1); x=((t*v+i*8.5)%50)-25
        cr.location=(120+x,4.0 if lane==0 else 8.2,0); cr.rotation_euler=(0,0,0 if lane==0 else math.pi)
        K(cr,"location",f); K(cr,"rotation_euler",f,2)
    if n==22: ojol.location=(108+26*(tl/(s["end"]-s["start"])),3.3,0)
    else: ojol.location=(300,0,0)
    K(ojol,"location",f)
    hv=1.0 if (n==23 and tl>1.0) or n>23 else 0.0
    if harga.default_value!=hv or f==1: harga.default_value=hv; harga.keyframe_insert("default_value",frame=f)
    after_ting = t>=SH[33]["start"]+0.25
    rc=(1.0,0.62,0.12,1) if after_ting else (1.0,0.12,0.05,1)
    if tuple(rcl.default_value)!=rc or f==1: rcl.default_value=rc; rcl.keyframe_insert("default_value",frame=f)
# constant interpolation everywhere
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
    const(idb.animation_data)
    nt=getattr(idb,"node_tree",None)
    if nt: const(nt.animation_data)
sc.frame_set(1)
sc.render.filepath="//frames/"; sc.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/ep01/ep01.blend")
print("ANIM OK frames",NF)
