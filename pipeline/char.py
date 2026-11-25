# Generator karakter figur mainan (badan sama dengan Nayla), dipakai untuk Adel, Dimas, Ibu Kos, Kuntilanak
import bpy, bmesh, math
from mathutils import Vector, Matrix
from lib import lin, mat, sph, cyl, torus, box
C=bpy.context
def _fin(o,m,bev=None,seg=6):
    if bev: md=o.modifiers.new("bev","BEVEL"); md.width=bev; md.segments=seg; md.limit_method='NONE'
    for p in o.data.polygons: p.use_smooth=True
    o.data.materials.append(m); return o
def rbox(n,size,loc,m,bev,seg=6,taper=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=C.object; o.name=n
    for v in o.data.vertices: v.co.x*=size[0]*(taper if v.co.z>0 else 1); v.co.y*=size[1]; v.co.z*=size[2]
    return _fin(o,m,bev,seg)
def caps(n,r,L,loc,m,rot=(0,0,0),sc=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=32,ring_count=16); o=C.object; o.name=n
    for v in o.data.vertices:
        v.co.z+= L/2 if v.co.z>0 else -L/2; v.co.x*=sc[0]; v.co.y*=sc[1]
    o.location=loc; o.rotation_euler=rot; return _fin(o,m)
def fabric(hexc,rough=0.55,bumpk=0.15,scale=60):
    m=mat(hexc,rough,0.15,name=f"kain_{hexc}"); nt=m.node_tree; N=nt.nodes
    if "Bump" in N: return m
    t=N.new("ShaderNodeTexNoise"); t.inputs["Scale"].default_value=scale; b=N.new("ShaderNodeBump"); b.name="Bump"; b.inputs["Strength"].default_value=bumpk
    nt.links.new(t.outputs["Fac"],b.inputs["Height"]); nt.links.new(b.outputs[0],N["Principled BSDF"].inputs["Normal"]); return m
def face_mat(name,head,skin):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N["Principled BSDF"]
    b.inputs["Roughness"].default_value=0.28; b.inputs["Coat Weight"].default_value=0.35
    tc=N.new("ShaderNodeTexCoord"); tc.object=head; sep=N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"],sep.inputs[0])
    m1=N.new("ShaderNodeMapping"); m1.inputs["Location"].default_value=(0.5,0.5,0); m1.inputs["Rotation"].default_value=(math.radians(-90),0,0); L.new(tc.outputs["Object"],m1.inputs[0])
    fr=N.new("ShaderNodeMath"); fr.operation='LESS_THAN'; fr.inputs[1].default_value=-0.1; L.new(sep.outputs[1],fr.inputs[0])
    prev=None
    for layer in ("eyes","mouth"):
        mp=N.new("ShaderNodeMapping"); mp.name=f"AT_{layer}"; mp.inputs["Scale"].default_value=(0.25,0.25,1); L.new(m1.outputs[0],mp.inputs[0])
        t=N.new("ShaderNodeTexImage"); t.name=f"TX_{layer}"; t.image=bpy.data.images.load(f"/home/claude/ep04/tex/{layer}.png",check_existing=True); t.extension='CLIP'
        L.new(mp.outputs[0],t.inputs[0]); mu=N.new("ShaderNodeMath"); mu.operation='MULTIPLY'; L.new(t.outputs["Alpha"],mu.inputs[0]); L.new(fr.outputs[0],mu.inputs[1])
        mx=N.new("ShaderNodeMix"); mx.data_type='RGBA'; L.new(mu.outputs[0],mx.inputs["Factor"])
        if prev is None: mx.inputs[6].default_value=lin(skin)
        else: L.new(prev.outputs[2],mx.inputs[6])
        L.new(t.outputs["Color"],mx.inputs[7]); prev=mx
    L.new(prev.outputs[2],b.inputs["Base Color"]); return m
def strand_cap(n,HC,scale,cut_front,mhair,depth_down=-0.30,seg=30,amp=0.022,yoff=0.03):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1,segments=96,ring_count=56); o=C.object; o.name=n
    bm=bmesh.new(); bm.from_mesh(o.data)
    for v in bm.verts:
        th=math.atan2(v.co.x,v.co.z); g=1+amp*math.sin(seg*th)*min(1,max(0,(v.co.z+0.5)))
        v.co.x*=scale[0]*g; v.co.y*=scale[1]*g; v.co.z*=scale[2]*g
    kill=[v for v in bm.verts if v.co.z<depth_down*scale[2]*2 or (cut_front and v.co.y<-0.12 and v.co.z<0.17-0.25*(abs(v.co.x)/scale[0])**2)]
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free()
    o.location=HC+Vector((0,yoff,0.05)); _fin(o,mhair)
    s=o.modifiers.new("sol","SOLIDIFY"); s.thickness=0.05; s.offset=1
    return o
def make_char(name, cfg, origin=(0,0,0)):
    """cfg: skin, top, bottom, shoes, hair dict, extras"""
    objs=[]; O=Vector(origin); HC=O+Vector((0,0,2.72))
    skin=mat(cfg["skin"],0.28,0.35,name=f"skin_{name}")
    top=fabric(cfg["top"]); bot=fabric(cfg["bottom"],0.45,0.08); shoe=mat(cfg.get("shoes","#1E1E22"),0.35,0.3)
    def add(o): objs.append(o); return o
    ghost=cfg.get("ghost",False)
    if not ghost:
        for sx,n in ((1,"L"),(-1,"R")):
            add(caps(f"{name}_leg.{n}",0.19,0.62,O+Vector((sx*0.24,0,0.62)),bot,sc=(1,1.15,1)))
            add(rbox(f"{name}_shoe.{n}",(0.40,0.56,0.20),O+Vector((sx*0.24,-0.06,0.10)),shoe,0.09))
            add(rbox(f"{name}_sole.{n}",(0.42,0.58,0.06),O+Vector((sx*0.24,-0.06,0.03)),mat("#EDEDED",0.5,0.1),0.03))
        add(rbox(f"{name}_hips",(0.98,0.56,0.32),O+Vector((0,0,1.08)),bot,0.13))
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=0.85,radius2=0.42,depth=2.3 if not cfg.get("grounded") else 2.0,location=O+Vector((0,0,0.85 if not cfg.get("grounded") else 1.0)),vertices=48); d=C.object; d.name=f"{name}_dress"
        wv=d.modifiers.new("w","WAVE"); wv.height=0.05; wv.width=0.35; wv.use_normal=True; sub=d.modifiers.new("s","SUBSURF"); sub.levels=2; sub.render_levels=2; d.modifiers.move(1,0)
        add(_fin(d,fabric("#F2F0EA",0.7,0.25,30)))
    add(rbox(f"{name}_torso",(1.06,0.62,1.02),O+Vector((0,0,1.66)),top,0.24,8,taper=0.86))
    add(caps(f"{name}_neck",0.13,0.06,O+Vector((0,0,2.22)),skin))
    head=add(rbox(f"{name}_head",(0.92,0.80,0.84),HC,skin,0.30,10))
    if not cfg.get("noface"): head.data.materials[0]=face_mat(f"face_{name}",head,cfg["skin"])
    for sx,n in ((1,"L"),(-1,"R")):
        add(caps(f"{name}_arm.{n}",0.15,0.52,O+Vector((sx*0.66,0,1.82)),top,rot=(0,math.radians(sx*12),0)))
        h=sph(f"{name}_hand.{n}",0.16,O+Vector((sx*0.73,-0.02,1.37)),skin,scale=(0.9,1,1.1)); add(h)
    hair=cfg.get("hair",{}); ht=hair.get("type")
    hm=mat(hair.get("color","#222222"),0.38,0.2,name=f"hair_{name}")
    if ht=="bob":
        add(strand_cap(f"{name}_hair",HC,(0.54,0.49,0.52),True,hm,seg=26))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.5,depth=0.55,location=HC+Vector((0,0.06,-0.12)),vertices=48); bb=C.object; bb.name=f"{name}_bob"
        bm=bmesh.new(); bm.from_mesh(bb.data); kill=[v for v in bm.verts if v.co.y<-0.05 and abs(v.co.x)<0.36]; bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(bb.data); bm.free()
        bb.scale=(1.12,1.0,1.0); s=bb.modifiers.new("sol","SOLIDIFY"); s.thickness=0.06; add(_fin(bb,hm,0.02,2))
    elif ht=="curly":
        add(strand_cap(f"{name}_hair",HC,(0.52,0.47,0.46),True,hm,amp=0.0))
        import random; rnd=random.Random(3)
        for i in range(70):
            th=rnd.uniform(0,2*math.pi); ph=rnd.uniform(0.15,1.45)
            p=Vector((math.sin(ph)*math.cos(th)*0.52, math.sin(ph)*math.sin(th)*0.47, math.cos(ph)*0.5))
            if p.y<-0.2 and p.z<0.25: continue
            add(sph(f"{name}_curl",rnd.uniform(0.09,0.13),HC+Vector((0,0.03,0.12))+p,hm,seg=12))
    elif ht=="hijab":
        hj=fabric(hair.get("color","#CDB79A"),0.75,0.12,40)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,segments=64,ring_count=40); hb=C.object; hb.name=f"{name}_hijab"
        bm=bmesh.new(); bm.from_mesh(hb.data)
        for v in bm.verts: v.co.x*=0.545; v.co.y*=0.49; v.co.z*=0.54
        kill=[v for v in bm.verts if v.co.y<-0.12 and (v.co.x/0.37)**2+((v.co.z+0.03)/0.36)**2<1.0]
        bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(hb.data); bm.free()
        hb.location=HC+Vector((0,0.03,0.02)); s=hb.modifiers.new("sol","SOLIDIFY"); s.thickness=0.05; sub=hb.modifiers.new("sub","SUBSURF"); sub.levels=1; add(_fin(hb,hj))
        bpy.ops.mesh.primitive_cone_add(radius1=0.70,radius2=0.36,depth=0.50,location=O+Vector((0,0.02,2.06)),vertices=48); dr=C.object; dr.name=f"{name}_drape"
        wv=dr.modifiers.new("w","WAVE"); wv.height=0.025; wv.width=0.25; wv.use_normal=True; add(_fin(dr,hj))
    elif ht=="peci":
        add(strand_cap(f"{name}_hair",HC,(0.50,0.45,0.44),True,hm,amp=0.01,depth_down=-0.2))
        add(cyl(f"{name}_peci",0.47,0.32,HC+Vector((0,0.02,0.36)),mat("#151515",0.6,0.1,name="peci"),bev=0.03))
    elif ht=="kupluk":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1,segments=48,ring_count=24); k=C.object; k.name=f"{name}_kupluk"
        bm=bmesh.new(); bm.from_mesh(k.data)
        for v in bm.verts: v.co.x*=0.52; v.co.y*=0.47; v.co.z*=0.50
        kill=[v for v in bm.verts if v.co.z<0.08]; bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(k.data); bm.free()
        k.location=HC+Vector((0,0.02,0.1)); s=k.modifiers.new("sol","SOLIDIFY"); s.thickness=0.06; add(_fin(k,fabric(hair.get("color","#2F3B2A"),0.8,0.4,120)))
        t=torus(f"{name}_kupluk_rim",0.5,0.06,HC+Vector((0,0.02,0.13)),fabric(hair.get("color","#2F3B2A"),0.8,0.4,120)); t.scale=(1.03,0.94,1); add(t)
    elif ht=="longback":
        add(strand_cap(f"{name}_hair",HC,(0.54,0.49,0.51),True,hm,seg=34))
        for i,x in enumerate([-0.42,-0.25,-0.08,0.08,0.25,0.42]):
            add(caps(f"{name}_long{i}",0.12,1.0,HC+Vector((x,0.22,-0.55)),hm,sc=(1,0.7,1)))
    elif ht=="short":
        add(strand_cap(f"{name}_hair",HC,(0.50,0.45,0.45),True,hm,amp=0.012,depth_down=-0.18))
    elif ht=="ponytail":
        add(strand_cap(f"{name}_hair",HC,(0.53,0.48,0.5),True,hm,seg=30))
        add(sph(f"{name}_tie",0.07,HC+Vector((0,0.47,0.05)),mat("#C0392B",0.4,0.2)))
        add(caps(f"{name}_tail",0.13,0.55,HC+Vector((0,0.55,-0.3)),hm,rot=(math.radians(-20),0,0)))
    elif ht in ("fedora","kopiah","blangkon"):
        if ht!="kopiah": add(strand_cap(f"{name}_hair",HC,(0.50,0.45,0.44),True,hm,amp=0.01,depth_down=-0.2))
        hc=mat(hair.get("hat","#8A7A5A"),0.6,0.1,name=f"topi_{name}")
        if ht=="fedora":
            add(cyl(f"{name}_brim",0.72,0.05,HC+Vector((0,0,0.36)),hc,bev=0.02)); add(cyl(f"{name}_crown",0.44,0.42,HC+Vector((0,0,0.58)),hc,bev=0.08))
            add(cyl(f"{name}_band",0.445,0.08,HC+Vector((0,0,0.43)),mat("#2B2B2B",0.5,0.1),bev=0.01))
        elif ht=="kopiah": add(strand_cap(f"{name}_hair",HC,(0.50,0.45,0.44),True,mat("#B8B8B8",0.6,0.1),amp=0.0,depth_down=-0.2)); add(cyl(f"{name}_kopiah",0.47,0.3,HC+Vector((0,0.02,0.35)),hc,bev=0.03))
        else:
            add(cyl(f"{name}_blangkon",0.49,0.3,HC+Vector((0,0.02,0.33)),hc,bev=0.06)); add(sph(f"{name}_mondolan",0.17,HC+Vector((0,0.47,0.25)),hc,scale=(1.3,1,0.8)))
    elif ht=="ghost":
        gh=mat("#0D0D0F",0.6,0.05,name="rambut_kunti")
        add(strand_cap(f"{name}_hair",HC,(0.55,0.50,0.52),False,gh,seg=40,amp=0.03))
        for i,x in enumerate([-0.36,-0.22,-0.08,0.08,0.22,0.36]):   # rambut panjang menutupi wajah sampai pinggang
            hc=caps(f"{name}_strand{i}",0.11,1.6,HC+Vector((x,-0.36+abs(x)*0.25,-0.75)),gh,sc=(1,0.6,1))
            wv=hc.modifiers.new("w","WAVE"); wv.height=0.03; wv.width=0.4; add(hc)
        for i,x in enumerate([-0.5,0.5]): add(caps(f"{name}_side{i}",0.13,1.7,HC+Vector((x,0.05,-0.8)),gh,sc=(0.8,1,1)))
    for ex in cfg.get("extras",[]): ex(O,HC,add)
    # rig
    bpy.ops.object.armature_add(location=O); rig=C.object; rig.name=f"{name}_rig"; ad=rig.data; ad.name=f"{name}_rig"
    bpy.ops.object.mode_set(mode='EDIT'); eb=ad.edit_bones; eb.remove(eb[0])
    def bone(n,h,t,p=None):
        b=eb.new(n); b.head=Vector(h); b.tail=Vector(t)
        if p: b.parent=eb[p]
    bone("root",(0,0,0),(0,0.6,0)); bone("hips",(0,0,0.95),(0,0,1.15),"root"); bone("spine",(0,0,1.15),(0,0,2.15),"hips"); bone("head",(0,0,2.20),(0,0,3.1),"spine")
    for sx,n in ((1,"L"),(-1,"R")):
        bone(f"arm.{n}",(sx*0.62,0,2.08),(sx*0.71,0,1.45),"spine"); bone(f"hand.{n}",(sx*0.71,0,1.45),(sx*0.75,0,1.25),f"arm.{n}")
        bone(f"leg.{n}",(sx*0.24,0,1.0),(sx*0.24,0,0.1),"hips"); bone(f"foot.{n}",(sx*0.24,0,0.18),(sx*0.24,-0.35,0.18),f"leg.{n}")
    bpy.ops.object.mode_set(mode='OBJECT'); C.view_layer.update()
    def bn(o):
        n=o.name.split("_",1)[1]
        for k in ("hand.L","hand.R","arm.L","arm.R","leg.L","leg.R"):
            if n.startswith(k): return k
        if n.startswith(("shoe.","sole.")): return "foot."+n.split(".")[1][0]
        if n in ("hips","dress"): return "hips"
        if n in ("torso","neck","drape") or n.startswith(("seam","zip","lapel","necklace","bag","band")): return "spine"
        return "head"
    for o in objs:
        mw=o.matrix_world.copy(); o.parent=rig; o.parent_type='BONE'; o.parent_bone=bn(o); C.view_layer.update(); o.matrix_world=mw
    col=bpy.data.collections.new(f"char_{name}"); C.scene.collection.children.link(col)
    for o in objs+[rig]:
        for c in o.users_collection: c.objects.unlink(o)
        col.objects.link(o)
    return rig
