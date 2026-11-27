# Ekspor satu segmen episode (rentang frame) untuk render Three.js.
# Pemakaian: python segprep.py -- <blend> <F0> <F1> <outdir> <focus_x> <focus_y>
import bpy, sys, json, math, os
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
BLEND,F0,F1,OUT=a[0],int(a[1]),int(a[2]),a[3]; FOC=Vector((float(a[4]),float(a[5]),0))
os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc=bpy.context.scene; O=bpy.data.objects; FR=list(range(F0,F1+1))
cv=lambda v:[v.x,v.z,-v.y]                      # Blender Z-up -> three Y-up
R_NEAR,R_FAR=16,45
def dist(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; c=sum(bb,Vector())/8; return (c.xy-FOC.xy).length, c
# ---------- sample per frame
meshes=[o for o in O if o.type=='MESH']
first={}; moving=set(); cam=[]; lights={}; matv={}
rigs=[o for o in O if o.type=='ARMATURE']; rig_seen=set()
def principled(m):
    return m and m.node_tree and m.node_tree.nodes.get('Principled BSDF')
face_mats={}
for r in rigs:
    for c in r.children_recursive:
        if c.type=='MESH' and c.data.materials and c.data.materials[0] and 'AT_eyes' in c.data.materials[0].node_tree.nodes:
            face_mats[r.name]=c.data.materials[0]
faces={r:[] for r in face_mats}
tile=lambda loc:int(round(loc[0]/0.25))+4*(3-int(round(loc[1]/0.25)))
for f in FR:
    sc.frame_set(f)
    for o in meshes:
        m=o.matrix_world
        if o.name not in first: first[o.name]=m.copy()
        elif o.name not in moving:
            p=first[o.name]
            if (m.translation-p.translation).length>1e-4 or m.to_quaternion().rotation_difference(p.to_quaternion()).angle>1e-4: moving.add(o.name)
    for r in rigs:
        if (r.matrix_world.translation.xy-FOC.xy).length<R_FAR and r.matrix_world.translation.y>-150: rig_seen.add(r.name)
    c=sc.camera; mw=c.matrix_world; fwd=mw.to_quaternion()@Vector((0,0,-1)); up=mw.to_quaternion()@Vector((0,1,0))
    sens=c.data.sensor_width if c.data.sensor_fit!='VERTICAL' else c.data.sensor_height
    vfov=2*math.atan(sens/2/c.data.lens)          # potret + sensor AUTO -> sensor mengikuti sisi tinggi
    cam.append([*cv(mw.translation),*cv(mw.translation+fwd),*cv(up),math.degrees(vfov)])
    for l in O:
        if l.type!='LIGHT': continue
        d=l.matrix_world.to_quaternion()@Vector((0,0,-1))
        lights.setdefault(l.name,[]).append([round(l.data.energy,4),*[round(x,4) for x in l.data.color],*[round(x,4) for x in cv(l.matrix_world.translation)],*[round(x,4) for x in cv(d)]])
    for m in bpy.data.materials:
        b=principled(m)
        if b: matv.setdefault(m.name,[]).append([round(x,4) for x in list(b.inputs['Emission Color'].default_value)[:3]]+[round(b.inputs['Emission Strength'].default_value,4)])
    for r,m in face_mats.items():
        N=m.node_tree.nodes; faces[r].append([tile(N['AT_eyes'].inputs['Location'].default_value),tile(N['AT_mouth'].inputs['Location'].default_value)])
const=lambda arr:all(x==arr[0] for x in arr)
# karakter yang benar-benar muncul + benda bergerak di dekat fokus
dyn_rigs=sorted(rig_seen)
dyn_objs=set()
for r in dyn_rigs: dyn_objs|={c.name for c in O[r].children_recursive if c.type=='MESH' and not c.hide_render}
for n in moving:
    o=O[n]
    if dist(o)[0]<R_FAR and not any(n in {c.name for c in O[r].children_recursive} for r in [x.name for x in rigs]): dyn_objs.add(n)
import os
for pat in [p for p in os.environ.get('DYN_FORCE','').split(',') if p]:
    for o in O:
        if o.type=='MESH' and (o.name==pat or o.name.startswith(pat)) and dist(o)[0]<R_FAR: dyn_objs.add(o.name)
dyn_objs={n for n in dyn_objs if not O[n].hide_render}
print('rigs',dyn_rigs,'dyn props',[n for n in dyn_objs if not any(n in {c.name for c in O[r].children_recursive} for r in dyn_rigs)])
# lampu
LI={}
for n,arr in lights.items():
    l=O[n]
    if max(x[0] for x in arr)<=0: continue
    if l.data.type!='SUN' and (Vector((arr[0][4],-arr[0][6],arr[0][5])).xy-FOC.xy).length>R_FAR: continue
    e={'type':l.data.type,'static':const(arr)}
    if l.data.type=='SPOT': e['size']=l.data.spot_size; e['blend']=l.data.spot_blend
    if l.data.type=='SUN': e['angle']=l.data.angle
    if l.data.type=='AREA': e['area']=[l.data.size,getattr(l.data,'size_y',l.data.size)]
    e['frames']=arr if not e['static'] else [arr[0]]
    LI[n]=e
dyn_lights=[n for n,e in LI.items() if not e['static']]
print('lights',{n:(e['type'],e['static']) for n,e in LI.items()})
MATS={n:{'static':const(v),'frames':(v if not const(v) else [v[0]])} for n,v in matv.items() if max(x[3] for x in v)>0}
dyn_mats=[n for n,e in MATS.items() if not e['static']]+[m for m in os.environ.get('DYN_MATS','').split(',') if m and m in MATS]
for m in dyn_mats: MATS[m]['static']=False
print('emissive',{n:e['static'] for n,e in MATS.items()})
meta={'F0':F0,'F1':F1,'fps':sc.render.fps,'cam':cam,'lights':LI,'emissive':MATS,'faces':{r:faces[r] for r in dyn_rigs if r in faces},
      'skin':{r:list(face_mats[r].node_tree.nodes['Mix'].inputs[6].default_value)[:3] for r in dyn_rigs if r in face_mats},
      'mask':{r:face_mats[r].node_tree.nodes['Math'].inputs[1].default_value for r in dyn_rigs if r in face_mats},
      'face_names':{r:face_mats[r].name for r in dyn_rigs if r in face_mats}}
json.dump(meta,open(f'{OUT}/meta.json','w'))
# atlas wajah
for r,m in face_mats.items():
    if r not in dyn_rigs: continue
    for nm in ('eyes','mouth'):
        im=m.node_tree.nodes['TX_'+nm].image; p=f'{OUT}/{r}_{nm}.png'
        if not os.path.exists(p): im2=im.copy(); im2.scale(2048,2048); im2.filepath_raw=p; im2.file_format='PNG'; im2.save()
# ---------- glTF benda dinamis (animasi dipanggang per frame, mulai dari 0)
sc.frame_start=F0; sc.frame_end=F1; sc.frame_set(F0)
bpy.ops.object.select_all(action='DESELECT')
for n in list(dyn_objs)+dyn_rigs:
    o=O[n]; o.hide_set(False); o.select_set(True)
bpy.ops.export_scene.gltf(filepath=f'{OUT}/dyn.glb',export_format='GLB',use_selection=True,export_apply=True,export_animations=True,
    export_animation_mode='SCENE',export_bake_animation=True,export_force_sampling=True,export_frame_range=True,export_anim_slide_to_zero=True,
    export_optimize_animation_size=False,export_cameras=False,export_lights=False,export_yup=True)
# ---------- adegan beku untuk bake: frame F0, tanpa karakter/benda dinamis/lampu & emisi dinamis
sc.frame_set(F0)
for o in list(O):
    if o.type in ('MESH','CURVE','EMPTY','ARMATURE'):
        if o.name in dyn_objs or o.name in dyn_rigs: o.hide_render=True; continue
        if o.type in('MESH','CURVE') and dist(o)[0]>R_FAR: bpy.data.objects.remove(o,do_unlink=True)
for o in O:
    if o.animation_data: o.animation_data_clear()
    if o.type=='LIGHT':
        if o.data.animation_data: o.data.animation_data_clear()
        if o.name in dyn_lights or o.name not in LI: o.data.energy=0
for m in bpy.data.materials:
    if m.node_tree and m.node_tree.animation_data: m.node_tree.animation_data_clear()
    b=principled(m)
    if m.name in dyn_mats and b: b.inputs['Emission Strength'].default_value=0
if sc.world.node_tree.animation_data: sc.world.node_tree.animation_data_clear()
for o in O:
    if o.type=='LIGHT' and o.name in LI and not LI[o.name]['static']: pass
json.dump({'dyn_objs':sorted(dyn_objs),'dyn_rigs':dyn_rigs},open(f'{OUT}/dyn.json','w'))
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/frozen.blend'); print('SEGPREP OK')
