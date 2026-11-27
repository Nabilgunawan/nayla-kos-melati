# Ep 5 animasi (12 fps, kunci per frame, interpolasi CONSTANT) -> ep05.blend
import bpy, json, math, random, sys
from mathutils import Vector, Matrix
sys.path.insert(0,'/tmp/w/ep5'); import ep5lib
bpy.ops.wm.open_mainfile(filepath='/tmp/w/ep5/ep05_sets.blend')
bpy.context.preferences.edit.keyframe_new_interpolation_type='CONSTANT'
sc=bpy.context.scene; O=bpy.data.objects; Mt=bpy.data.materials; D=math.radians; FPS=12
TL=json.load(open('/tmp/w/ep5/timeline.json')); TOTAL=TL['total']; NF=int(TOTAL*FPS)
sc.frame_start=1; sc.frame_end=NF; sc.render.fps=12; sc.render.resolution_x=1080; sc.render.resolution_y=1920
T=lambda f:(f-1)/FPS
S={s['cam']:s for s in TL['shots']}; C={c['id']:c for c in TL['clips']}
def shot_at(t):
    for s in TL['shots']:
        if s['start']<=t<s['end']: return s
    return TL['shots'][-1]
X0=450.0; PARK=Vector((0,-200,0))
NAY,DIM=O['Nayla_rig'],O['Dimas_rig']; RIGS={'Nayla':NAY,'Dimas':DIM}
for r in [o for o in O if o.type=='ARMATURE' and o not in (NAY,DIM)]:
    r.location=PARK; r.keyframe_insert('location',frame=1)
# ---- perbaikan posisi pintu kamar 1 (offset ganda dari sets5)
bpy.context.view_layer.update()
for n in ('k1_door','k1_doorknob'):
    o=O[n]; mw=o.matrix_world.copy(); mw.translation.x-=454.42; o.matrix_world=mw
# pintu kamar Nayla: pivot engsel
pv=bpy.data.objects.new('KDOOR_piv',None); sc.collection.objects.link(pv); pv.location=(4.48,-2.5,0)
bpy.context.view_layer.update()
for n in ('k_door','k_doorknob'):
    o=O[n]; mw=o.matrix_world.copy(); o.parent=pv; o.matrix_parent_inverse=pv.matrix_world.inverted(); o.matrix_world=mw
# rice cooker + lemari kecil pindah ke dinding kanan bagian belakang (tidak menghalangi pintu)
for o in O:
    if o.name.startswith(('k1_cabinet','k1_rc_')) and o.parent is None: o.location.y+=3.2
# latar di luar pintu kamar 1 (supaya tidak kosong saat pintu dibuka)
bpy.ops.mesh.primitive_plane_add(size=1); bg=bpy.context.object; bg.name='k1_luar'; bg.scale=(1,10,6); bg.location=(X0+7.5,-2,3); bg.rotation_euler=(0,D(90),0)
mb=Mt.new('k1_luar_m'); mb.use_nodes=True; b=mb.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.55,0.47,0.36,1); b.inputs['Roughness'].default_value=0.9; bg.data.materials.append(mb)
# ---- stik dipegang
ST={'Nayla':O['STIK_nayla'],'Dimas':O['STIK_dimas']}
ARM={}
for who,r in (('Nayla',NAY),('Dimas',DIM)):
    ep5lib.sit_floor(r,X0-1.9,-0.2 if who=='Nayla' else 1.5,-90); bpy.context.view_layer.update()
    dd,sg,inw=ep5lib.hold(r,ST[who]); ARM[who]=(sg*inw); print(who,'genggam',round(dd,2),sg*inw)
# ---- wajah & lip-sync
FACEM={'Nayla':NAY.children and [c for c in NAY.children_recursive if c.name=='head'][0].data.materials[0],
       'Dimas':[c for c in DIM.children_recursive if c.name=='Dimas_head'][0].data.materials[0]}
LIPS={s:json.load(open(f'/tmp/w/ep5/audio/lips_{s}.json'))['mouthCues'] for s in ('nayla','dimas')}
VIS={'X':0,'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8}
EMO={'senang':(3,9),'heboh':(2,10),'kesal':(5,12),'kaget':(2,11),'malu':(15,14),'mikir':(8,12),'tertawa':(3,10),'kagum':(2,11),'jahil':(13,14),
     'ngantuk':(4,12),'tenang':(0,0),'yakin':(7,14),'cemas':(6,13),'bingung':(9,15),'panik':(11,11)}
tile=lambda i:((i%4)*0.25,(3-i//4)*0.25,0.0)
def speaking(who,t):
    for c in TL['clips']:
        if c['spk']==who and c['dst']<=t<c['dst']+c['dur']: return c
def mouth_at(who,t):
    c=speaking(who,t)
    if not c: return None
    ts=c['src'][0]+(t-c['dst']); v='X'
    for q in LIPS[who]:
        if q['start']<=ts<q['end']: v=q['value']; break
    return VIS.get(v,0)
rng=random.Random(5); BLINK={k:set() for k in RIGS}
for k in RIGS:
    tb=rng.uniform(0.5,2.0)
    while tb<TOTAL: BLINK[k].add(int(tb*FPS)+1); tb+=rng.uniform(2.4,4.6)
# ---- helper pose
def reset(rig):
    for b in rig.pose.bones: b.rotation_mode='XYZ'; b.rotation_euler=(0,0,0)
def walk(rig,t,amp=24):
    pb=rig.pose.bones; s=math.sin(t*2*math.pi*1.8)
    pb['leg.L'].rotation_euler=(D(amp*s),0,0); pb['leg.R'].rotation_euler=(D(-amp*s),0,0)
    pb['arm.L'].rotation_euler=(D(-amp*0.8*s),0,D(-3)); pb['arm.R'].rotation_euler=(D(amp*0.8*s),0,D(3))
    return 0.04*abs(math.cos(t*2*math.pi*1.8))
def place(rig,loc,yaw,dz=0):
    rig.location=Vector(loc)+Vector((0,0,dz)); rig.rotation_euler=(0,0,D(yaw))
def phone(who,on):
    o=O['phone'] if who=='Nayla' else O['phone_dimas']; o.scale=(1,1,1) if on else (0.001,0.001,0.001)
def hold_phone(rig):        # ponsel di depan dada, layar miring ke arah wajah, kepala sedikit menunduk
    pb=rig.pose.bones; pb['arm.R'].rotation_euler=(D(-58),0,D(-26)); pb['hand.R'].rotation_euler=(D(-50),0,0); pb['head'].rotation_euler=(D(14),0,0)
def show_phone(rig):        # menyodorkan ponsel: lengan lurus ke depan, layar menghadap lawan bicara
    pb=rig.pose.bones; pb['arm.R'].rotation_euler=(D(-82),0,D(-6)); pb['hand.R'].rotation_euler=(D(10),D(180),0)
def lerp(a,b,u): return a+(b-a)*max(0,min(1,u))
def smooth(u): u=max(0,min(1,u)); return u*u*(3-2*u)
# ---- cahaya per set
W=sc.world.node_tree.nodes; sun=O['SUN']
LALL=[o for o in O if o.type=='LIGHT' and o.name!='SUN']
def world(a,b,c): W['W_SORE'].inputs['Factor'].default_value=a; W['W_MALAM'].inputs['Factor'].default_value=b; W['W_BG'].inputs[1].default_value=c
def setsun(d,e,col): sun.rotation_euler=Vector(d).normalized().to_track_quat('-Z','Y').to_euler(); sun.data.energy=e; sun.data.color=col
def es(name,v):
    m=Mt.get(name)
    if m: m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=v
NIGHT=dict(L_teras1=45,L_teras2=45,L_teras3=45,L_teras4=45,L_jalan=350,L_kamar3=60)
TVL=json.load(open('/tmp/w/ep5/tvlight.json'))     # warna rata-rata layar TV per frame 12 fps
def preset(st,f,t,s):
    v={}
    if st in ('luar_sore','teras3_sore','hp'): world(1,0,0.6); setsun((-0.85,0.55,-0.32),2.6,(1,0.74,0.48))
    elif st=='kamar_sore': world(1,0,0.5); setsun((0.35,-1,-0.42),2.4,(1,0.76,0.52)); v.update(L_kos_fill=60,L_kos_window=170)
    elif st in ('k1_sore','k1_sore2'): world(1,0,0.5); setsun((0.35,-1,-0.42),2.2,(1,0.76,0.52)); v.update(L_k1_fill=70,L_k1_window=150)
    elif st=='luar_senja':
        u=(t-s['start'])/(s['end']-s['start']); world(1-u*0.6,u*0.6,0.5-0.2*u); setsun((-0.9,0.5,-0.12),1.6*(1-u)+0.2,(1,0.55,0.35))
        for i in range(4):
            if u>0.25+i*0.15: v[f'L_teras{i+1}']=45
        if u>0.85: v['L_jalan']=350
    elif st=='k1_malam':
        world(0,1,0.12); setsun((-0.4,0.7,-0.6),0.25,(0.55,0.65,1.0)); v.update(L_k1_lampu=6)
        c=TVL[min(f-1,len(TVL)-1)]; v['L_tv']=c[3]; O['L_tv'].data.color=c[:3]
    elif st=='luar_malam': world(0,1,0.35); setsun((-0.4,0.7,-0.6),0.7,(0.55,0.65,1.0)); v.update(NIGHT)
    elif st=='luar_pagi': world(0,0,0.7); setsun((0.75,0.55,-0.38),3.2,(1,0.82,0.62))
    for l in LALL: l.data.energy=v.get(l.name,0)
    night=st in ('luar_malam',) or (st=='luar_senja' and (t-s['start'])/(s['end']-s['start'])>0.25)
    es('lampu_teras1',6 if night else 0); es('lampu_jalan',8 if (st=='luar_malam' or (st=='luar_senja' and v.get('L_jalan'))) else 0)
    es('kaca_rumah',1 if night else 0); es('nkaca0',1 if night else 0); es('kaca3',1.5 if night else 0)
    tvon=st in ('k1_sore','k1_malam') ; es('tv_layar',2.5 if tvon else 0)
# ---- kamera
cam=O['CAM']; cam.constraints.clear()
def look(pos,tgt,lens):
    cam.location=pos; cam.rotation_euler=(Vector(tgt)-Vector(pos)).to_track_quat('-Z','Y').to_euler(); cam.data.lens=lens
def V3(*a): return Vector(a)
# ---- per-shot
KC=92.5; K3=102.5; TZ=0.3
def stand_still(rig,loc,yaw,dz=0):
    reset(rig); place(rig,loc,yaw,dz)
for f in range(1,NF+1):
    t=T(f); s=shot_at(t); tl=t-s['start']; d=s['end']-s['start']; u=tl/d; cm=s['cam']
    preset(s['set'],f,t,s)
    for r in RIGS.values(): reset(r)
    place(NAY,PARK,0); place(DIM,PARK+V3(5,0,0),0); phone('Nayla',False); phone('Dimas',False)
    O['KONSOL_inti'].scale=O['KONSOL_panel-1'].scale=O['KONSOL_panel1'].scale=O['KONSOL_kaki'].scale=O['KONSOL_kabel'].scale=(1,1,1)
    for n in ('STIK_meja1','STIK_meja2'): O[n].scale=(1,1,1)
    O['KDOOR_piv'].rotation_euler=(0,0,0); O['K1DOOR_piv'].rotation_euler=(0,0,0)
    expr={'Nayla':'tenang','Dimas':'tenang'}
    if cm in ('m1','m7','m13','m14'):          # Nayla bercerita langsung ke kamera di kamarnya
        place(NAY,(0.8,0.4,0),0); c=speaking('nayla',t); expr['Nayla']=c['emo'] if c else 'senang'
        NAY.pose.bones['arm.L'].rotation_euler=(0,0,D(-4)); NAY.pose.bones['arm.R'].rotation_euler=(0,0,D(4))
        look(V3(0.8,-2.6,2.78),(0.8,0.4,2.62),42)
    elif cm=='s1':
        place(DIM,(KC+0.3,-1.3,TZ),-10); phone('Dimas',True); hold_phone(DIM)
        look(V3(lerp(97.5,95.5,smooth(u)),lerp(-10,-8.2,smooth(u)),3.3),(KC+0.3,-1.0,2.2),30)
    elif cm=='s2':
        place(DIM,(KC+0.3,-1.3,TZ),-10); phone('Dimas',True); hold_phone(DIM); expr['Dimas']='kaget'
        look(V3(KC+0.55,-3.6,3.05),(KC+0.3,-1.3,TZ+2.75),45)
    elif cm=='s3':
        place(DIM,(KC+0.3,-1.3,TZ),80); expr['Dimas']='heboh'; pb=DIM.pose.bones
        pb['arm.L'].rotation_euler=(D(-150),0,D(10)); pb['head'].rotation_euler=(D(-12),0,0); pb['spine'].rotation_euler=(D(-6),0,0)
        sh=0.04*math.sin(t*37) if tl<1.6 else 0
        look(V3(KC-2.4+sh,-6.2,2.6+sh),(KC+0.6,-1.2,TZ+2.0),32)
    elif cm=='s4':
        place(NAY,(2.1,1.6,0),35 if tl<1.2 else 120); expr['Nayla']='kesal' if speaking('nayla',t) else 'kaget'
        NAY.pose.bones['head'].rotation_euler=(0,D(25) if tl>=1.2 else 0,0)
        look(V3(-1.8,-3.8,2.9),(2.2,1.4,2.0),30)
    elif cm=='s5':
        O['KDOOR_piv'].rotation_euler=(0,0,D(-75))
        place(NAY,(1.8,-1.3,0),90); place(DIM,(3.7,-1.6,0),-90); phone('Dimas',True); show_phone(DIM); expr['Dimas']='heboh'; expr['Nayla']='kaget'
        look(V3(-0.5,1.4,3.0),(3.7,-1.7,2.4),28)
    elif cm=='s6':
        O['KDOOR_piv'].rotation_euler=(0,0,D(-75))
        place(NAY,(1.8,-1.3,0),90); place(DIM,(3.1,-1.4,0),-90); phone('Dimas',True); show_phone(DIM); expr={'Nayla':'kaget' if tl<3.2 else 'senang','Dimas':'heboh'}
        bpy.context.view_layer.update(); c=O['phone_screen_dimas'].matrix_world.translation.copy()
        look(V3(2.45,-4.8,2.75),(2.45,-1.35,2.35),34)
    elif cm=='s7':
        j=abs(math.sin(tl*2*math.pi*1.4))*0.35
        place(NAY,(1.9,-0.9,0),-30,j); place(DIM,(3.0,-1.2,0),-10,abs(math.sin(tl*2*math.pi*1.4+1.2))*0.35)
        for r in (NAY,DIM):
            r.pose.bones['arm.L'].rotation_euler=(D(-160),0,D(15)); r.pose.bones['arm.R'].rotation_euler=(D(-160),0,D(-15))
        expr={'Nayla':'senang','Dimas':'heboh'}
        look(V3(0.6,-5.6,2.7),(2.4,-1.0,2.0),26)
    elif cm in ('s8','s9','s10'):
        place(NAY,(K3-0.6,-1.4,TZ),60); place(DIM,(K3+0.7,-1.6,TZ),-65)
        if cm=='s8':
            look(V3(K3+1.6,-6.4,2.6),(K3+0.05,-1.5,TZ+1.9),30)
            if speaking('dimas',t) and speaking('dimas',t)['id']=='D3':
                DIM.pose.bones['arm.R'].rotation_euler=(D(-160),0,D(25)); expr['Dimas']='malu'
            if speaking('nayla',t) and speaking('nayla',t)['id']=='N5':
                NAY.pose.bones['arm.R'].rotation_euler=(D(-120),0,D(-35)); expr['Nayla']='mikir'
            if t>=C['D4']['dst']: expr={'Nayla':'senang','Dimas':'senang'}
        elif cm=='s9':
            k=smooth(tl/0.5)
            NAY.pose.bones['arm.R'].rotation_euler=(D(-150*k),0,D(-20)); DIM.pose.bones['arm.L'].rotation_euler=(D(-150*k),0,D(20))
            expr={'Nayla':'tertawa','Dimas':'tertawa'}; look(V3(K3+0.3,-4.8,2.9),(K3+0.05,-1.5,TZ+2.5),30)
        else:
            phone('Dimas',True); hold_phone(DIM); expr={'Nayla':'senang','Dimas':'senang'}
            bpy.context.view_layer.update(); c=O['phone_screen_dimas'].matrix_world.translation.copy(); hd=[x for x in DIM.children_recursive if x.name=='Dimas_head'][0].matrix_world.translation.copy(); fw=(c-hd); fw.z=0; fw.normalize(); sd=fw.cross(Vector((0,0,1)))
            look(hd-fw*0.9+Vector((0,0,0.7))-sd*0.75,c,35)
    elif cm in ('s11','s13','s14','s15','s16','s17','s18','s19','s20'):
        if cm=='s11':
            for n in ('STIK_meja1','STIK_meja2'): O[n].scale=(0.001,0.001,0.001)
        sitN=(X0-1.9,-0.2); sitD=(X0-1.9,1.5)
        ep5lib.sit_floor(NAY,sitN[0],sitN[1],-90); ep5lib.sit_floor(DIM,sitD[0],sitD[1],-90)
        stand_u=None
        if cm=='s20' and t>=C['N12']['dst']-0.3: stand_u=smooth((t-(C['N12']['dst']-0.3))/0.7)
        for who,r in RIGS.items():
            if stand_u is not None and who=='Nayla':
                r.location.z=lerp(r.location.z,0,stand_u)
                for sd in ('L','R'): r.pose.bones[f'leg.{sd}'].rotation_euler=(D(lerp(-88,0,stand_u)),0,0)
                r.pose.bones['spine'].rotation_euler=(0,0,0); continue
            pb=r.pose.bones; pb['arm.L'].rotation_euler=(D(-62),0,D(ARM[who])); pb['arm.R'].rotation_euler=(D(-62),0,D(-ARM[who])); pb['hand.L'].rotation_euler=pb['hand.R'].rotation_euler=(D(-20),0,0)
        if cm=='s11':
            DIM.pose.bones['spine'].rotation_euler=(D(6),D(4*math.sin(t*20)),0); expr={'Nayla':'ngantuk','Dimas':'kesal'}
            look(V3(X0+3.4,-3.0,3.7),(X0-3.4,0.8,1.6),20)
        elif cm=='s13':
            for r in (NAY,DIM): r.pose.bones['spine'].rotation_euler=(D(14),D(6*math.sin(t*5)),0)
            expr={'Nayla':'kagum','Dimas':'heboh'}; look(V3(lerp(X0+3.0,X0+2.2,u),-2.4,3.3),(X0-3.5,0.7,1.6),20)
        elif cm=='s14':
            expr={'Nayla':'kagum','Dimas':'senang'}; look(V3(X0-4.0,0.65,1.55),(X0-1.9,0.65,1.5),20)
        elif cm in ('s15','s16'):
            expr={'Nayla':'kagum','Dimas':'senang'}; look(V3(X0-0.4,0.75,2.05),(X0-4.4,0.8,1.95),30)
        elif cm=='s17':
            NAY.pose.bones['head'].rotation_euler=(0,D(-30),0); expr={'Nayla':'jahil','Dimas':'tenang'}
            look(V3(X0-4.0,-1.9,1.9),(X0-1.9,-0.2,1.5),28)
        elif cm=='s18':
            NAY.pose.bones['head'].rotation_euler=(0,D(-25),0); DIM.pose.bones['head'].rotation_euler=(0,D(25),0)
            expr={'Nayla':'jahil','Dimas':'malu' if t<C['D8']['dst'] else 'tertawa'}
            if t<C['N10']['dst']-0.2: look(V3(X0-4.0,2.9,1.9),(X0-1.9,1.5,1.5),28)
            else: look(V3(X0-4.0,0.65,2.0),(X0-1.9,0.65,1.4),22)
        elif cm=='s19':
            k=abs(math.sin(tl*2*math.pi*1.2)); NAY.pose.bones['arm.L'].rotation_euler=(D(-60),0,D(ARM['Nayla']-40*k))
            for r in (NAY,DIM): r.pose.bones['spine'].rotation_euler=(D(-10+8*k),0,0)
            expr={'Nayla':'tertawa','Dimas':'tertawa'}; look(V3(X0-4.0,0.65,2.0),(X0-1.9,0.65,1.4),22)
        elif cm=='s20':
            jam=O['JAM_jarum_m_piv']; jam.rotation_euler=(0,D(-(tl/2.2)*40),0) ; O['JAM_jarum_j_piv'].rotation_euler=(0,D(-2),0)
            expr={'Nayla':'ngantuk','Dimas':'ngantuk'}
            if tl<2.2: look(V3(X0+2.6,3.1,4.4),(X0+2.6,4.48,4.4),40)
            else: look(V3(X0+0.6,-2.8,2.5),(X0-1.6,0.6,1.6),24)
    elif cm=='s12':
        look(V3(97.5,-9.6,3.0),(99,0,3.2),24)
    elif cm=='s21':
        x=lerp(KC+1.2,K3-0.7,smooth(u)); dz=walk(NAY,t) if u<0.98 else 0
        place(NAY,(x,-1.5,TZ),90,dz); place(DIM,(KC-0.5,-0.8,TZ),20)
        DIM.pose.bones['arm.R'].rotation_euler=(D(-160),0,D(-20+25*math.sin(t*9))); expr={'Nayla':'ngantuk','Dimas':'ngantuk'}
        look(V3(lerp(95.5,98.5,u),-9.5,3.2),(lerp(95,99,u),-1.0,2.0),30)
    elif cm=='s22':
        tL=C['D11']['dst']-0.3; tW=C['D11']['dst']+C['D11']['dur']+0.4
        if t<tL:
            place(DIM,(KC-0.5,-0.9,TZ),180); DIM.pose.bones['arm.R'].rotation_euler=(D(-80),0,0)
            place(NAY,(KC+1.6,-1.5,TZ),-40); expr={'Nayla':'tenang','Dimas':'tenang'}
            look(V3(KC+0.5,-8.5,3.0),(KC+0.5,-1.0,2.1),28)
        elif t<tW:
            place(DIM,(KC-0.5,-0.9,TZ),180); DIM.pose.bones['arm.R'].rotation_euler=(D(-85+6*math.sin(tl*14)),0,0); place(NAY,(KC+1.6,-1.5,TZ),-40)
            expr={'Nayla':'tenang','Dimas':'yakin'}; look(V3(KC+1.5,-1.1,2.3),(KC-0.05,-0.2,1.9),40)
        else:
            w=(t-tW)/(s['end']-tW); y=lerp(-1.4,-7.5,w)
            place(DIM,(KC+0.2,y,TZ if y>-2.6 else 0),0,walk(DIM,t)); place(NAY,(KC+1.3,y-0.2,TZ if y>-2.8 else 0),0,walk(NAY,t+0.3))
            expr={'Nayla':'senang','Dimas':'senang'}; look(V3(KC+0.7,-12,2.6),(KC+0.7,-3,2.0),35)
    elif cm in ('s23','s24'):
        for n in ('KONSOL_inti','KONSOL_panel-1','KONSOL_panel1','KONSOL_kaki','KONSOL_kabel'): O[n].scale=(0.001,0.001,0.001)
        tOpen=C['D12']['dst']+C['D12']['dur']+0.3 if cm=='s23' else -1
        if cm=='s23':
            ang=0 if t<tOpen else -80*smooth((t-tOpen)/0.8)
            if t<tOpen: ang=2*math.sin(tl*30) if tl>0.8 else 0
            O['K1DOOR_piv'].rotation_euler=(0,0,D(ang))
            place(DIM,(X0+5.4,-1.7,0),90); place(NAY,(X0+6.0,-0.9,0),90)
            if t>=tOpen: place(DIM,(X0+lerp(5.4,3.6,smooth((t-tOpen)/1.2)),-1.7,0),90,walk(DIM,t)*(t<tOpen+1.2)); place(NAY,(X0+lerp(6.0,4.2,smooth((t-tOpen-0.3)/1.2)),-0.9,0),90)
            expr={'Nayla':'cemas','Dimas':'kaget'}; look(V3(X0-0.8,1.2,2.5),(X0+4.48,-1.6,2.1),28)
        else:
            O['K1DOOR_piv'].rotation_euler=(0,0,D(-80))
            place(DIM,(X0+2.6,-1.6,0),-90); place(NAY,(X0+3.2,-0.5,0),-80)
            expr={'Nayla':'bingung','Dimas':'panik' if t>=C['D13']['dst']-0.2 else 'kaget'}
            if t>=C['D13']['dst']-0.2:
                for sd,sg in (('L',1),('R',-1)): DIM.pose.bones[f'arm.{sd}'].rotation_euler=(D(-150),0,D(sg*30))
            if tl<3.2: look(V3(lerp(X0-1.2,X0-2.8,smooth(tl/3.2)),2.1,1.9),(X0-4.2,2.1,1.1),35)
            else: look(V3(lerp(X0-3.2,X0-3.9,smooth((tl-3.2)/3.0)),lerp(1.0,0.5,smooth((tl-3.2)/3.0)),2.6),(X0+2.8,-1.0,2.2),24)
    # ---- wajah: emosi + mulut bicara + kedip
    for who,r in RIGS.items():
        e=EMO[expr[who]]; eye,mo=e
        m=mouth_at(who.lower(),t)
        if m is not None: mo=m
        if f in BLINK[who] or f-1 in BLINK[who]: eye=1
        N=FACEM[who].node_tree.nodes
        N['AT_eyes'].inputs['Location'].default_value=tile(eye); N['AT_mouth'].inputs['Location'].default_value=tile(mo)
        N['AT_eyes'].inputs['Location'].keyframe_insert('default_value',frame=f); N['AT_mouth'].inputs['Location'].keyframe_insert('default_value',frame=f)
    # ---- kunci semua
    for r in RIGS.values():
        r.keyframe_insert('location',frame=f); r.keyframe_insert('rotation_euler',frame=f)
        for b in r.pose.bones: b.keyframe_insert('rotation_euler',frame=f)
    for o in [cam,O['phone'],O['phone_dimas'],O['KDOOR_piv'],O['K1DOOR_piv'],O['JAM_jarum_m_piv'],O['JAM_jarum_j_piv'],
              O['KONSOL_inti'],O['KONSOL_panel-1'],O['KONSOL_panel1'],O['KONSOL_kaki'],O['KONSOL_kabel'],O['STIK_meja1'],O['STIK_meja2']]:
        o.keyframe_insert('location',frame=f); o.keyframe_insert('rotation_euler',frame=f); o.keyframe_insert('scale',frame=f)
    cam.data.keyframe_insert('lens',frame=f)
    sun.keyframe_insert('rotation_euler',frame=f); sun.data.keyframe_insert('energy',frame=f); sun.data.keyframe_insert('color',frame=f)
    for l in LALL: l.data.keyframe_insert('energy',frame=f)
    O['L_tv'].data.keyframe_insert('color',frame=f)
    for nme in ('W_SORE','W_MALAM'): W[nme].inputs['Factor'].keyframe_insert('default_value',frame=f)
    W['W_BG'].inputs[1].keyframe_insert('default_value',frame=f)
    for mn in ('lampu_teras1','lampu_jalan','kaca_rumah','nkaca0','kaca3','tv_layar'):
        m=Mt.get(mn)
        if m: m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].keyframe_insert('default_value',frame=f)
    if f%200==0: print('frame',f,flush=True)
# stik tangan: tempelkan sekali (pose duduk) lalu parent ke tulang tangan
for who,r in RIGS.items():
    for f in range(1,NF+1):
        t=T(f); cm=shot_at(t)['cam']
        on=cm in ('s11','s13','s14','s15','s16','s17','s18','s19') or (cm=='s20' and (who=='Dimas' or t<C['N12']['dst']-0.3))
        ST[who].scale=(1,1,1) if on else (0.001,0.001,0.001); ST[who].keyframe_insert('scale',frame=f)
bpy.ops.wm.save_as_mainfile(filepath='/tmp/w/ep5/ep05.blend'); print('ANIM5 OK',NF)
