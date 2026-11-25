import bpy, bmesh, math
from mathutils import Vector, Matrix
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; C=bpy.context
def lin(h):  # hex sRGB -> linear
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c)+(1,)
def plastic(name,hexc,rough=0.28,coat=0.35):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value=lin(hexc); b.inputs["Roughness"].default_value=rough
    b.inputs["Coat Weight"].default_value=coat; b.inputs["Coat Roughness"].default_value=0.15
    return m
M={k:plastic(k,v) for k,v in dict(skin="#F2C51F",black="#1B1B1E",sole="#EDEDED",tie="#F4F4F4",mug="#E7DCC0").items()}
M["gold"]=plastic("gold","#D9A441",rough=0.2,coat=0.0); M["gold"].node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=1.0
M["gem"]=plastic("gem","#FFFFFF",rough=0.05,coat=0.0)

def finish(o,mat,bev=None,seg=6,smooth=True):
    if bev: md=o.modifiers.new("bev","BEVEL"); md.width=bev; md.segments=seg; md.limit_method='NONE'
    if smooth:
        for p in o.data.polygons: p.use_smooth=True
    o.data.materials.append(mat); return o
def rbox(name,size,loc,mat,bev,seg=6,taper_top=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=C.object; o.name=name
    for v in o.data.vertices:
        v.co.x*=size[0]*(taper_top if v.co.z>0 else 1); v.co.y*=size[1]; v.co.z*=size[2]
    return finish(o,mat,bev,seg)
def capsule(name,r,length,loc,mat,rot=(0,0,0),scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=32,ring_count=16,location=(0,0,0)); o=C.object; o.name=name
    for v in o.data.vertices:
        v.co.z+= length/2 if v.co.z>0 else -length/2
        v.co.x*=scale[0]; v.co.y*=scale[1]
    o.location=loc; o.rotation_euler=rot; return finish(o,mat)
def sphere(name,r,loc,mat,scale=(1,1,1),rot=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=32,ring_count=16,location=loc); o=C.object; o.name=name
    o.scale=scale; o.rotation_euler=rot; return finish(o,mat)

# ---------- BODY (original toy figure) ----------
HC=Vector((0,0,2.72))   # head centre
legs=[]
for sx,n in ((1,"L"),(-1,"R")):
    legs.append(capsule(f"leg.{n}",0.19,0.62,(sx*0.24,0,0.62),M["black"],scale=(1.0,1.15,1)))
    legs.append(rbox(f"shoe.{n}",(0.40,0.56,0.20),(sx*0.24,-0.06,0.10),M["black"],0.09))
    legs.append(rbox(f"sole.{n}",(0.42,0.58,0.06),(sx*0.24,-0.06,0.03),M["sole"],0.03))
hips=rbox("hips",(0.98,0.56,0.32),(0,0,1.08),M["black"],0.13)
torso=rbox("torso",(1.06,0.62,1.02),(0,0,1.66),M["black"],0.24,8,taper_top=0.86)
neck=capsule("neck",0.13,0.06,(0,0,2.22),M["skin"])
head=rbox("head",(0.92,0.80,0.84),tuple(HC),M["skin"],0.30,10)
arms=[]
for sx,n in ((1,"L"),(-1,"R")):
    a=capsule(f"arm.{n}",0.15,0.52,(sx*0.66,0,1.82),M["black"],rot=(0,math.radians(sx*12),0))
    h=sphere(f"hand.{n}",0.16,(sx*0.73,-0.02,1.37),M["skin"],scale=(0.9,1,1.1))
    arms.append((n,a,h))

# ---------- FACE material (projected decal) ----------
fm=M["skin"].copy(); fm.name="face"; head.data.materials[0]=fm
nt=fm.node_tree; N=nt.nodes; L=nt.links; bsdf=N["Principled BSDF"]
tc=N.new("ShaderNodeTexCoord"); tc.object=head
sep=N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"],sep.inputs[0])
mp=N.new("ShaderNodeMapping"); mp.inputs["Location"].default_value=(0.5,0.5,0); mp.inputs["Rotation"].default_value=(math.radians(-90),0,0)
L.new(tc.outputs["Object"],mp.inputs[0])
img=N.new("ShaderNodeTexImage"); img.name="FACE"; img.extension='CLIP'; img.interpolation='Cubic'
for e in ["senyum","tertawa","kaget","kesal","sedih"]:
    im=bpy.data.images.load(f"//faces/{e}.png" if bpy.data.filepath else f"/home/claude/nayla/faces/{e}.png"); im.name=e; im.use_fake_user=True; im.pack()
img.image=bpy.data.images["senyum"]
L.new(mp.outputs[0],img.inputs[0])
front=N.new("ShaderNodeMath"); front.operation='LESS_THAN'; front.inputs[1].default_value=-0.1; L.new(sep.outputs[1],front.inputs[0])
mul=N.new("ShaderNodeMath"); mul.operation='MULTIPLY'; L.new(img.outputs["Alpha"],mul.inputs[0]); L.new(front.outputs[0],mul.inputs[1])
mix=N.new("ShaderNodeMix"); mix.data_type='RGBA'; L.new(mul.outputs[0],mix.inputs["Factor"])
mix.inputs[6].default_value=lin("#F2C51F"); L.new(img.outputs["Color"],mix.inputs[7])
L.new(mix.outputs[2],bsdf.inputs["Base Color"])

# ---------- HAIR ----------
hair_m=plastic("hair","#7C6347",rough=0.38,coat=0.2); hn=hair_m.node_tree.nodes; hl=hair_m.node_tree.links
w=hn.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value=16; w.inputs["Distortion"].default_value=1.5; w.bands_direction='X'
bump=hn.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.7; hl.new(w.outputs[1],bump.inputs["Height"])
hl.new(bump.outputs[0],hn["Principled BSDF"].inputs["Normal"])
bpy.ops.mesh.primitive_uv_sphere_add(radius=1,segments=128,ring_count=72,location=(0,0,0)); cap=C.object; cap.name="hair_cap"
bm=bmesh.new(); bm.from_mesh(cap.data)
for v in bm.verts:
    th=math.atan2(v.co.x,v.co.z); g=1+0.022*math.sin(30*th)*min(1,max(0,(v.co.z+0.5)))
    if v.co.y<0.2 and abs(th)<0.07: g-=0.035*(1-abs(th)/0.07)
    v.co.x*=0.53*g; v.co.y*=0.47*g; v.co.z*=0.50*g
kill=[v for v in bm.verts if v.co.z<-0.30 or (v.co.y<-0.12 and v.co.z< 0.17-0.25*(abs(v.co.x)/0.53)**2) ]
bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(cap.data); bm.free()
cap.location=HC+Vector((0,0.03,0.05)); finish(cap,hair_m)
sol=cap.modifiers.new("sol","SOLIDIFY"); sol.thickness=0.05; sol.offset=1
sub=cap.modifiers.new("sub","SUBSURF"); sub.levels=1; sub.render_levels=2
# centre parting groove
#part=capsule("hair_part",0.012,0.30,HC+Vector((0,-0.30,0.43)),plastic("part","#5E4A35"),rot=(math.radians(-55),0,0))
# back bun volume
hb=sphere("hair_back",0.40,HC+Vector((0,0.18,-0.05)),hair_m,scale=(1.25,0.9,1.15))
for v in hb.data.vertices:
    th=math.atan2(v.co.x,v.co.z); v.co*= 1+0.03*math.sin(22*th)
# braids
braid_objs=[]
def bez(p0,p1,p2,t): return p0*(1-t)**2+p1*2*t*(1-t)+p2*t*t
for sx,n in ((1,"L"),(-1,"R")):
    p0=Vector((sx*0.44,-0.04,2.50)); p1=Vector((sx*0.62,-0.50,2.30)); p2=Vector((sx*0.50,-0.44,1.52))
    k=17
    for i in range(k):
        t=i/(k-1); p=bez(p0,p1,p2,t); tan=(bez(p0,p1,p2,min(1,t+0.02))-bez(p0,p1,p2,max(0,t-0.02))).normalized()
        view=Vector((0,-1,0)); view=(view-tan*view.dot(tan)).normalized(); side=tan.cross(view)
        base=Matrix((side,view,tan)).transposed()
        tilt=Matrix.Rotation(math.radians(38 if i%2 else -38),3,'Y')
        s=sphere(f"braid.{n}.{i}",0.072*(1-0.22*t),p,hair_m)
        s.rotation_mode='QUATERNION'; s.rotation_quaternion=(base@tilt).to_quaternion(); s.scale=(1.05,0.8,1.75)
        braid_objs.append(s)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.062,minor_radius=0.022,location=p2+Vector((0,0,-0.03)))
    tie=C.object; tie.name=f"tie.{n}"; finish(tie,M["tie"]); braid_objs.append(tie)
    bpy.ops.mesh.primitive_cone_add(radius1=0.10,radius2=0.05,depth=0.22,location=p2+Vector((0,0,-0.15)))
    tuft=C.object; tuft.name=f"tuft.{n}"; finish(tuft,hair_m,0.03,3); braid_objs.append(tuft)

# ---------- HOODIE details ----------
seam_m=plastic("seam","#55565C",rough=0.5,coat=0)
for sx in (1,-1):
    capsule(f"seam.{sx}",0.012,0.80,(sx*0.17,-0.312,1.62),seam_m,scale=(1,0.5,1))
    capsule(f"pocket.{sx}",0.010,0.22,(sx*0.30,-0.313,1.30),seam_m,rot=(0,math.radians(-sx*35),0),scale=(1,0.5,1))
bpy.ops.mesh.primitive_torus_add(major_radius=0.27,minor_radius=0.075,location=(0,0.02,2.16)); hood=C.object; hood.name="hood_rim"
hood.scale=(1.05,0.95,0.8); finish(hood,M["black"])
sphere("hood_back",0.40,(0,0.29,1.98),M["black"],scale=(0.95,0.22,0.85))
# necklace
cd=bpy.data.curves.new("neck_chain","CURVE"); cd.dimensions='3D'; cd.bevel_depth=0.007; cd.bevel_resolution=2
sp=cd.splines.new('BEZIER'); sp.bezier_points.add(2)
for bp,co in zip(sp.bezier_points,[(-0.20,-0.18,2.14),(0,-0.318,1.80),(0.20,-0.18,2.14)]):
    bp.co=co; bp.handle_left_type=bp.handle_right_type='AUTO'
chain=bpy.data.objects.new("chain",cd); sc.collection.objects.link(chain); cd.materials.append(M["gold"])
bpy.ops.mesh.primitive_cylinder_add(radius=0.045,depth=0.02,location=(0,-0.322,1.75),rotation=(math.radians(90),0,0)); pend=C.object; pend.name="pendant"; finish(pend,M["gold"],0.006,2)
sphere("gem",0.025,(0,-0.335,1.75),M["gem"])

# ---------- PROP: mug ----------
bpy.ops.mesh.primitive_cylinder_add(radius=0.13,depth=0.28,location=(0,0,0)); mug=C.object; mug.name="mug"; finish(mug,M["mug"],0.03,3)
bpy.ops.mesh.primitive_torus_add(major_radius=0.07,minor_radius=0.022,location=(0.15,0,0),rotation=(math.radians(90),0,0)); mh=C.object; mh.name="mug_handle"; finish(mh,M["mug"])
mh.parent=mug; mug.hide_render=True; mh.hide_render=True

# ---------- RIG ----------
bpy.ops.object.armature_add(location=(0,0,0)); rig=C.object; rig.name="Nayla_rig"; ad=rig.data; ad.name="Nayla_rig"
bpy.ops.object.mode_set(mode='EDIT'); eb=ad.edit_bones; eb.remove(eb[0])
def bone(n,h,t,par=None):
    b=eb.new(n); b.head=h; b.tail=t
    if par: b.parent=eb[par]
bone("root",(0,0,0),(0,0.6,0)); bone("hips",(0,0,0.95),(0,0,1.15),"root"); bone("spine",(0,0,1.15),(0,0,2.15),"hips")
bone("head",(0,0,2.20),(0,0,3.1),"spine")
for sx,n in ((1,"L"),(-1,"R")):
    bone(f"arm.{n}",(sx*0.62,0,2.08),(sx*0.71,0,1.45),"spine"); bone(f"hand.{n}",(sx*0.71,0,1.45),(sx*0.75,0,1.25),f"arm.{n}")
    bone(f"leg.{n}",(sx*0.24,0,1.0),(sx*0.24,0,0.1),"hips")
bone("braid.L",(0.44,-0.04,2.5),(0.5,-0.44,1.52),"head"); bone("braid.R",(-0.44,-0.04,2.5),(-0.5,-0.44,1.52),"head")
bpy.ops.object.mode_set(mode='OBJECT')
def parent(obj,bn):
    mw=obj.matrix_world.copy(); obj.parent=rig; obj.parent_type='BONE'; obj.parent_bone=bn
    obj.matrix_world=mw
C.view_layer.update()
groups={"head":["head","hair_cap","hair_back"],"spine":["torso","neck","hood_rim","hood_back","chain","pendant","gem","seam.1","seam.-1","pocket.1","pocket.-1"],"hips":["hips"]}
for sx,n in (("L","L"),("R","R")):
    groups[f"leg.{n}"]=[f"leg.{n}",f"shoe.{n}",f"sole.{n}"]; groups[f"arm.{n}"]=[f"arm.{n}"]; groups[f"hand.{n}"]=[f"hand.{n}"]
    groups[f"braid.{n}"]=[o.name for o in braid_objs if f".{n}" in o.name]
for bn,names in groups.items():
    for nm in names: parent(bpy.data.objects[nm],bn); C.view_layer.update()
for o in bpy.data.objects:
    if o.type=='MESH' and o.parent is None and not o.name.startswith("mug"): print("UNPARENTED",o.name)

# ---------- STUDIO ----------
w=bpy.data.worlds.new("studio"); sc.world=w; w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(1,1,1,1); w.node_tree.nodes["Background"].inputs[1].default_value=0.35
bpy.ops.mesh.primitive_plane_add(size=40,location=(0,0,0)); fl=C.object; fl.name="floor"; fl.is_shadow_catcher=True
def area(n,loc,energy,size,col=(1,1,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); l=C.object; l.name=n; l.data.energy=energy; l.data.size=size; l.data.color=col
    d=Vector((0,0,1.7))-l.location; l.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); return l
area("key",(-3.5,-4.5,5),650,3,(1,0.96,0.9)); area("fill",(4.5,-3,2.5),220,4,(0.9,0.95,1)); area("rim",(1,5,5),600,2.5)
bpy.ops.object.camera_add(location=(0,-14,1.62)); cam=C.object; cam.name="cam_ortho"; cam.rotation_euler=(math.radians(90),0,0)
cam.data.type='ORTHO'; cam.data.ortho_scale=3.6; sc.camera=cam
r=sc.render; r.engine='CYCLES'; sc.cycles.samples=24; sc.cycles.use_denoising=True; sc.cycles.device='CPU'
r.resolution_x=560; r.resolution_y=720; sc.view_settings.view_transform='Standard'; r.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/nayla/nayla_v1.blend")
print("saved")
