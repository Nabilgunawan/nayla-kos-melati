# Upgrade badan figur perempuan (lebih lembut, pinggang, dada sedikit menonjol) dan jilbab model khimar.
# Bekerja pada .blend yang sudah berisi karakter: mesh diganti di tempat, nama/bone/material/animasi tetap.
# Pemakaian: blender -b file.blend -P femme.py -- [Nayla Adel Ibu ...]   (tanpa nama = semua perempuan)
import bpy, bmesh, math, sys
from mathutils import Vector
FEMALE=["Nayla","Adel","Ibu","Melati","MelatiK","Darmi","Rina"]
HIJAB=["Adel","Darmi"]
import os
BUST=float(os.environ.get('FEMME_BUST','0.14'))   # seberapa maju dada (unit Blender); 0 = rata
BLUSH={'Nayla':0.38,'Adel':0.30,'Ibu':0.22,'Melati':0.30,'MelatiK':0.30,'Darmi':0.22,'Rina':0.28}   # kekuatan rona pipi

def part(rig,key):
    pre=rig.name[:-4]+'_'
    for c in rig.children_recursive:
        n=c.name[len(pre):] if c.name.startswith(pre) else c.name
        if n==key: return c
    return None
def sgn(x): return (x>0)-(x<0)
def superq(nu=64,nv=40,e=0.45):
    """mesh 'superellipsoid' satuan (kotak membulat), tutup atas-bawah"""
    bm=bmesh.new(); rows=[]
    for j in range(nv+1):
        ph=-math.pi/2+math.pi*j/nv; ring=[]
        for i in range(nu):
            th=2*math.pi*i/nu; cp,sp,ct,st=math.cos(ph),math.sin(ph),math.cos(th),math.sin(th)
            x=sgn(cp*ct)*abs(cp)**e*abs(ct)**e; y=sgn(cp*st)*abs(cp)**e*abs(st)**e; z=sgn(sp)*abs(sp)**e
            ring.append(bm.verts.new((x,y,z)))
        rows.append(ring)
    for j in range(nv):
        for i in range(nu):
            a,b,c,d=rows[j][i],rows[j][(i+1)%nu],rows[j+1][(i+1)%nu],rows[j+1][i]
            try: bm.faces.new((a,b,c,d))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5); return bm
def tapered_capsule(r0,r1,L,nu=32,nv=24):
    """kapsul meruncing sepanjang sumbu z (r0 atas, r1 bawah), pusat di 0"""
    bm=bmesh.new(); rows=[]
    for j in range(nv+1):
        t=j/nv; ph=math.pi*t                 # 0 atas .. pi bawah
        z=math.cos(ph); r=math.sin(ph)
        zz=(L/2+r0*z) if z>0 else (-L/2+r1*z); rr=(r0 if z>0 else r1)*r
        if 0.35<t<0.65: pass
        ring=[bm.verts.new((rr*math.cos(2*math.pi*i/nu),rr*math.sin(2*math.pi*i/nu),zz)) for i in range(nu)]; rows.append(ring)
    # bagian tengah (silinder meruncing)
    for j in range(nv):
        for i in range(nu):
            try: bm.faces.new((rows[j][i],rows[j][(i+1)%nu],rows[j+1][(i+1)%nu],rows[j+1][i]))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5); return bm
def swap(o,bm,keep_mods=()):
    me=bpy.data.meshes.new(o.data.name+"_f"); bm.to_mesh(me); bm.free()
    for m in o.data.materials: me.materials.append(m)
    for p in me.polygons: p.use_smooth=True
    o.data=me
    for md in list(o.modifiers):
        if md.type not in keep_mods: o.modifiers.remove(md)
def torso_f(o,bust):
    bm=superq(112,80,0.42); W,D,H=0.47,0.28,0.51     # resolusi tinggi agar lengkung dada mulus
    for v in bm.verts:
        x,y,z=v.co; h=(z+1)/2                                          # 0 bawah .. 1 atas
        wsc=0.86+0.10*h-0.10*math.exp(-((h-0.28)/0.16)**2)              # pinggang ramping, bahu sedikit lebih lebar
        wsc*=1-0.10*max(0,h-0.82)/0.18                                   # bahu membulat
        dsc=0.95-0.08*math.exp(-((h-0.28)/0.18)**2)
        X=x*W*wsc; Y=y*D*dsc; Z=z*H
        if y<0 and bust>0:                                               # depan = -Y: dua kubah bulat
            d=0.0; ds=[]
            for cx in (-0.18,0.18):
                rx=0.19; rz=0.19*(1.15 if h>0.63 else 1.0)                       # hampir lingkaran: bulat penuh
                r=math.sqrt(((X-cx)/rx)**2+((h-0.63)/rz)**2)
                sq=max(0.0,1.0-r*r); ds.append(3*sq*sq-2*sq*sq*sq)             # kubah bulat penuh, tepi tetap menyatu halus
            d=max(ds)+0.30*min(ds)                                               # dua sisi menyatu lembut di tengah
            Y-=bust*min(1.0,d)*min(1,-y*1.6)
        if y>0: Y+=0.02*math.exp(-((h-0.15)/0.2)**2)*y                  # lekuk punggung bawah halus
        v.co=(X,Y,Z)
    swap(o,bm)
def hips_f(o):
    bm=superq(64,32,0.5)
    for v in bm.verts:
        x,y,z=v.co; h=(z+1)/2; v.co=(x*0.47*(0.92+0.08*(1-h)),y*0.285,z*0.17)
    swap(o,bm)
def limb(o,r0,r1,L,ysc=1.0):
    bm=tapered_capsule(r0,r1,L)
    for v in bm.verts: v.co.y*=ysc
    swap(o,bm)
def apply_body(rig,bust=BUST):
    P=lambda k:part(rig,k)
    t=P('torso'); 
    if t: torso_f(t,bust)
    h=P('hips')
    if h and h.data.polygons and len(h.data.vertices)<5000: hips_f(h)
    for s in ('L','R'):
        a=P(f'arm.{s}')
        if a: limb(a,0.125,0.10,0.50); a.location.x-=(1 if a.matrix_world.translation.x>rig.matrix_world.translation.x else -1)*0.0
        sgnx=1 if s=='L' else -1
        for k in (f'arm.{s}',f'hand.{s}'):
            o=P(k)
            if o: mw=o.matrix_world.copy(); mw.translation.x-=sgnx*0.085; o.matrix_world=mw
        l=P(f'leg.{s}'); l and limb(l,0.175,0.135,0.60,1.08)
        hd=P(f'hand.{s}');
        if hd: hd.scale=(hd.scale[0]*0.88,hd.scale[1]*0.88,hd.scale[2]*0.9)
        for k in (f'shoe.{s}',f'sole.{s}'):
            sh=P(k)
            if sh: sh.scale=(sh.scale[0]*0.86,sh.scale[1]*0.92,sh.scale[2])
    n=P('neck')
    if n: n.scale=(n.scale[0]*0.85,n.scale[1]*0.85,n.scale[2]*1.25)
    # detail baju menempel ke permukaan badan baru
    t=P('torso')
    if t:
        for c in rig.children_recursive:
            if c==t or c.type not in('MESH','CURVE') or c.parent_bone!='spine': continue
            base=c.name.split('_',1)[-1]
            if base.startswith(('torso','neck','hood','drape','hijab')): continue
            if c.type=='CURVE':
                bpy.context.view_layer.objects.active=c
                for o in bpy.context.selected_objects: o.select_set(False)
                c.select_set(True); bpy.ops.object.convert(target='MESH')
            bb=[c.matrix_world@Vector(v) for v in c.bound_box]; zs=[v.z for v in bb]; cen=sum(bb,Vector())/8
            if max(zs)-min(zs)>0.3:
                if 'wrap' not in c.modifiers:
                    m=c.modifiers.new('wrap','SHRINKWRAP'); m.target=t; m.wrap_method='NEAREST_SURFACEPOINT'; m.wrap_mode='OUTSIDE_SURFACE'; m.offset=0.012
                    c.modifiers.move(len(c.modifiers)-1,0)
            else:
                tl=t.matrix_world; inv=tl.inverted(); dg=bpy.context.evaluated_depsgraph_get(); te=t.evaluated_get(dg)
                front=cen.y<t.matrix_world.translation.y
                o_=inv@Vector((cen.x,cen.y-3 if front else cen.y+3,cen.z)); d_=(inv.to_3x3()@Vector((0,1 if front else -1,0))).normalized()
                ok,loc,nrm,idx=te.ray_cast(o_,d_)
                if ok:
                    hit=tl@loc; ymin=min(v.y for v in bb); ymax=max(v.y for v in bb)
                    dy=(hit.y-0.004-ymax) if front else (hit.y+0.004-ymin)
                    if abs(dy)<0.45: mw=c.matrix_world.copy(); mw.translation.y+=dy; c.matrix_world=mw
def hijab(rig,color):
    """khimar: penutup kepala + kain jatuh menutupi bahu & dada dengan lipatan lembut"""
    pre=rig.name[:-4]; head=part(rig,'head')
    mats=[]
    for k in ('hijab','drape'):
        o=bpy.data.objects.get(f'{pre}_{k}')
        if o: mats+=list(o.data.materials); bpy.data.objects.remove(o,do_unlink=True)
    mat=mats[0] if mats else None
    O=rig.matrix_world.translation.copy()
    HC=head.matrix_world@Vector((0,0,0)) if head else O+Vector((0,0,2.72))
    # ---- penutup kepala: mengikuti bentuk kepala (kotak membulat), bukaan wajah oval, turun menutup leher
    bm=superq(96,64,0.62); kill=[]
    for v in bm.verts:
        x,y,z=v.co
        p=Vector((x*0.50,y*0.445,z*0.475))
        if z<-0.2: p.x*=1-0.18*min(1,(-0.2-z)/0.8); p.y*=1-0.12*min(1,(-0.2-z)/0.8)   # menyempit di bawah dagu
        if z<-0.55: p.z=-0.475*0.55-(-0.55-z)*0.9                                       # memanjang ke leher
        v.co=p
        if p.y<-0.18 and (p.x/0.345)**2+((p.z+0.0)/0.355)**2<1: kill.append(v)
    bmesh.ops.delete(bm,geom=kill,context='VERTS')
    me=bpy.data.meshes.new(f'{pre}_hijab'); bm.to_mesh(me); bm.free()
    cap=bpy.data.objects.new(f'{pre}_hijab',me); rig.users_collection[0].objects.link(cap); cap.location=HC+Vector((0,0.015,0.01))
    # ---- kain khimar: dari bawah dagu jatuh menutupi bahu, lengan atas, dan dada; depan paling panjang
    nu,nv=160,40; bm=bmesh.new(); rows=[]; top_z=HC.z-0.40
    for j in range(nv+1):
        v=j/nv; ring=[]
        for i in range(nu):
            th=2*math.pi*i/nu; s_,c_=math.sin(th),math.cos(th)              # th=0 depan (-Y)
            hem=1.40+0.26*abs(s_)**1.3 if c_>=0 else 1.52+0.14*abs(s_)**1.3
            hem+=0.025*math.sin(7*th)                                       # ujung kain sedikit bergelombang
            z=top_z+(hem-top_z)*v
            sh=min(1,v/0.32); sm=sh*sh*(3-2*sh)
            rx=0.30+(0.70-0.30)*sm+0.04*max(0,v-0.32)
            ry=0.27+(0.36-0.27)*sm+0.02*max(0,v-0.32)
            ry+=(0.09*BUST/0.10)*max(0,c_)*min(1,max(0,(v-0.2)/0.35))                   # ruang untuk dada
            fold=(0.006+0.045*max(0,v-0.25)**1.2)*math.sin(15*th+2.1*math.sin(2*th))
            p=Vector((rx*s_*(1+fold),-ry*c_*(1+fold),z-top_z))
            p.z+=0.10*(1-sm)*0                                              
            ring.append(bm.verts.new(p))
        rows.append(ring)
    for j in range(nv):
        for i in range(nu): bm.faces.new((rows[j][i],rows[j][(i+1)%nu],rows[j+1][(i+1)%nu],rows[j+1][i]))
    me=bpy.data.meshes.new(f'{pre}_drape'); bm.to_mesh(me); bm.free()
    dr=bpy.data.objects.new(f'{pre}_drape',me); rig.users_collection[0].objects.link(dr); dr.location=Vector((HC.x,HC.y+0.02,top_z))
    if mat and mat.node_tree:
        b=mat.node_tree.nodes.get('Principled BSDF')
        if b: b.inputs['Coat Weight'].default_value=0.0; b.inputs['Roughness'].default_value=0.85; b.inputs['Sheen Weight'].default_value=0.4
    for o in (cap,dr):
        for p in o.data.polygons: p.use_smooth=True
        if mat: o.data.materials.append(mat)
        s=o.modifiers.new('sol','SOLIDIFY'); s.thickness=0.022; s.offset=1 if o==cap else 0
        sub=o.modifiers.new('sub','SUBSURF'); sub.levels=1; sub.render_levels=2
    # parent ke tulang
    bpy.context.view_layer.update()
    for o,bn in ((cap,'head'),(dr,'spine')):
        mw=o.matrix_world.copy(); o.parent=rig; o.parent_type='BONE'; o.parent_bone=bn; bpy.context.view_layer.update(); o.matrix_world=mw
    # tepi ciput di sekeliling wajah (warna sedikit berbeda)
    return cap,dr
def blush(rig,k):
    """rona pipi lembut di material wajah (koordinat objek kepala, sama dengan atlas mata/mulut)"""
    head=part(rig,'head')
    if not head or not head.data.materials: return
    m=head.data.materials[0]; nt=m.node_tree; N=nt.nodes; Lk=nt.links
    if 'BLUSH' in N or 'Mix.001' not in N: return
    sep=[n for n in N if n.type=='SEPXYZ'][0]; front=N['Math']; last=N['Mix.001']; bsdf=N['Principled BSDF']
    def mth(op,a,b=None):
        n=N.new('ShaderNodeMath'); n.operation=op
        for i,x in enumerate((a,b)):
            if x is None: continue
            if isinstance(x,(int,float)): n.inputs[i].default_value=x
            else: Lk.new(x,n.inputs[i])
        return n.outputs[0]
    dx=mth('DIVIDE',mth('SUBTRACT',mth('ABSOLUTE',sep.outputs['X']),0.23),0.085)
    dz=mth('DIVIDE',mth('ADD',sep.outputs['Z'],0.09),0.05)
    d=mth('ADD',mth('POWER',dx,2.0),mth('POWER',dz,2.0))
    msk=mth('MULTIPLY',mth('MULTIPLY',mth('POWER',mth('MAXIMUM',mth('SUBTRACT',1.0,d),0.0),1.5),k),front.outputs[0])
    mx=N.new('ShaderNodeMix'); mx.name='BLUSH'; mx.data_type='RGBA'; mx.blend_type='MIX'
    Lk.new(msk,mx.inputs['Factor']); Lk.new(last.outputs[2],mx.inputs[6]); mx.inputs[7].default_value=(1.0,0.32,0.38,1)
    Lk.new(mx.outputs[2],bsdf.inputs['Base Color'])
def hairclip(rig):
    """jepit rambut bunga kecil di sisi kiri (khusus Nayla)"""
    head=part(rig,'head'); cap=part(rig,'hair_cap')
    if not head or not cap or bpy.data.objects.get('clip_center'): return
    HC=head.matrix_world.translation; d=Vector((0.62,-0.42,0.66)).normalized()
    c=HC+Vector((0,0.03,0.05))+Vector((d.x*0.53*1.06,d.y*0.47*1.06,d.z*0.50*1.06))
    pet=bpy.data.materials.new('clip_kelopak'); pet.use_nodes=True; b=pet.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.98,0.45,0.55,1); b.inputs['Roughness'].default_value=0.35; b.inputs['Coat Weight'].default_value=0.4
    mid=bpy.data.materials.new('clip_tengah'); mid.use_nodes=True; b=mid.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(1.0,0.80,0.30,1); b.inputs['Roughness'].default_value=0.3
    nrm=d; t1=nrm.cross(Vector((0,0,1))).normalized(); t2=nrm.cross(t1)
    objs=[]
    for i in range(5):
        a=2*math.pi*i/5; p=c+(t1*math.cos(a)+t2*math.sin(a))*0.055
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045,segments=16,ring_count=10,location=p); o=bpy.context.object; o.name=f'clip_petal{i}'
        o.scale=(1.0,1.0,0.45); o.rotation_euler=nrm.to_track_quat('Z','Y').to_euler(); o.data.materials.append(pet); objs.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03,segments=16,ring_count=10,location=c+nrm*0.012); o=bpy.context.object; o.name='clip_center'; o.data.materials.append(mid); objs.append(o)
    for o in objs:
        for p in o.data.polygons: p.use_smooth=True
        for col in list(o.users_collection): col.objects.unlink(o)
        rig.users_collection[0].objects.link(o)
    bpy.context.view_layer.update()
    for o in objs:
        mw=o.matrix_world.copy(); o.parent=rig; o.parent_type='BONE'; o.parent_bone='head'; bpy.context.view_layer.update(); o.matrix_world=mw
def run(names):
    O=bpy.data.objects; sc=bpy.context.scene
    for n in names:
        rig=O.get(f'{n}_rig')
        if not rig: continue
        # kerjakan di pose istirahat agar posisi tulang konsisten
        act=rig.animation_data.action if rig.animation_data else None
        if rig.animation_data: rig.animation_data.action=None
        for b in rig.pose.bones: b.rotation_mode='XYZ'; b.rotation_euler=(0,0,0); b.location=(0,0,0)
        loc,rot=rig.location.copy(),rig.rotation_euler.copy(); rig.location=(0,0,0); rig.rotation_euler=(0,0,0)
        bpy.context.view_layer.update()
        apply_body(rig)
        if n in HIJAB: hijab(rig,None)
        if n in BLUSH: blush(rig,BLUSH[n])
        if n=='Nayla': hairclip(rig)
        rig.location,rig.rotation_euler=loc,rot
        if act: rig.animation_data.action=act
        bpy.context.view_layer.update(); print('upgraded',n)
if __name__=="__main__":
    a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    out=[x for x in a if x.endswith('.blend')]; names=[x for x in a if not x.endswith('.blend')] or FEMALE
    run(names)
    if out: bpy.ops.wm.save_as_mainfile(filepath=out[0]); print('saved',out[0])
