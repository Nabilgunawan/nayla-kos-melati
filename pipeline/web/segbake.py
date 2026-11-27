# Bake lightmap (irradiance, tanpa warna) untuk set statis di frozen.blend
# Pemakaian: python segbake.py -- <outdir> <focus_x> <focus_y> <res> <samples>
import bpy, sys, math, time, json, os
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]
OUT=a[0]; FOC=Vector((float(a[1]),float(a[2]),0)); RES=int(a[3]); SMP=int(a[4])
bpy.ops.wm.open_mainfile(filepath=f'{OUT}/frozen.blend')
sc=bpy.context.scene; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
R_NEAR=16
stat=[o for o in O if o.type in('MESH','CURVE') and not o.hide_render and o.visible_get()]
for o in O: o.hide_set(False)
def info(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; c=sum(bb,Vector())/8
    ev=o.evaluated_get(dg); me=ev.to_mesh(); s=o.matrix_world.to_scale(); ar=sum(p.area for p in me.polygons)*abs(s.x*s.y) if me else 0; ev.to_mesh_clear()
    return (c.xy-FOC.xy).length, ar
groups={'A':[],'B':[],'G':[]}
PREV={}
with bpy.data.libraries.load(f'{OUT}/baked_v1.blend') as (src,dst): dst.objects=[n for n in src.objects if n.startswith('ENV_')]
for ob in dst.objects: PREV[ob.name[4:]]=ob
# tekstur prosedural: Generated/Object -> atribut per-vertex agar tidak berubah saat objek digabung
for m in bpy.data.materials:
    nt=m.node_tree
    if not nt: continue
    for n in list(nt.nodes):
        if n.type!='TEX_COORD' or n.object: continue
        for out,att in (('Generated','gen'),('Object','objco')):
            ls=list(n.outputs[out].links)
            if not ls: continue
            a=nt.nodes.new('ShaderNodeAttribute'); a.attribute_type='GEOMETRY'; a.attribute_name=att
            for l in ls: nt.links.new(a.outputs['Vector'],l.to_socket)
for o in stat:
    d,ar=info(o)
    groups['G' if ar>1000 else ('A' if d<R_NEAR else 'B')].append(o)
print({k:len(v) for k,v in groups.items()})
proc=set()
for o in stat:
    for m in (o.data.materials if hasattr(o.data,'materials') else []):
        b=m and m.node_tree and m.node_tree.nodes.get('Principled BSDF')
        if b and b.inputs['Base Color'].is_linked and b.inputs['Base Color'].links[0].from_node.type!='TEX_IMAGE': proc.add(m.name)
print('procedural base color:',sorted(proc))
joined={}
for k,objs in groups.items():
    if not objs: continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.make_single_user(object=True,obdata=True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for o in bpy.context.selected_objects:
        me=o.data; tl=Vector(me.texspace_location); ts=Vector(me.texspace_size)
        g=me.attributes.get('gen') or me.attributes.new('gen','FLOAT_VECTOR','POINT'); oc=me.attributes.get('objco') or me.attributes.new('objco','FLOAT_VECTOR','POINT')
        for i,v in enumerate(me.vertices):
            gv=Vector(((v.co.x-tl.x+ts.x)/(2*ts.x or 1),(v.co.y-tl.y+ts.y)/(2*ts.y or 1),(v.co.z-tl.z+ts.z)/(2*ts.z or 1)))
            g.data[i].vector=gv; oc.data[i].vector=v.co
    bpy.ops.object.join(); J=bpy.context.view_layer.objects.active; J.name=f'ENV_{k}'; joined[k]=J
    me=J.data
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    me.uv_layers[0].active_render=True; lm=me.uv_layers.new(name='LM'); me.uv_layers.active=lm
    if k=='G':   # tanah: proyeksi dari atas, hanya area sekitar fokus
        X0,X1,Y0,Y1=FOC.x-35,FOC.x+35,FOC.y-30,FOC.y+30
        for p in me.polygons:
            for li in p.loop_indices:
                w=J.matrix_world@me.vertices[me.loops[li].vertex_index].co
                lm.data[li].uv=((w.x-X0)/(X1-X0),(w.y-Y0)/(Y1-Y0))
    elif k in PREV:
        src=PREV[k].data.uv_layers['LM'].data; assert len(src)==len(lm.data), (k,len(src),len(lm.data))
        buf=[0.0]*(2*len(src)); src.foreach_get('uv',buf); lm.data.foreach_set('uv',buf); print('LM copied',k)
    else:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=0.003,area_weight=0.0,correct_aspect=True,scale_to_bounds=False)
        bpy.ops.uv.pack_islands(margin=0.003,rotate=True); bpy.ops.object.mode_set(mode='OBJECT')
    print(k,'faces',len(me.polygons))
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SMP; sc.cycles.max_bounces=6
for k,J in joined.items():
    have=os.path.exists(f'{OUT}/lm_{k}.exr')
    img=bpy.data.images.new(f'LM_{k}',RES,RES,float_buffer=True)
    for m in J.data.materials:
        if not m or not m.node_tree: continue
        nt=m.node_tree; n=nt.nodes.get('BAKE') or nt.nodes.new('ShaderNodeTexImage'); n.name='BAKE'; n.image=img
        for x in nt.nodes: x.select=False
        n.select=True; nt.nodes.active=n
    bpy.ops.object.select_all(action='DESELECT'); J.select_set(True); bpy.context.view_layer.objects.active=J
    if not have:
        t=time.time(); bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT','INDIRECT'},margin=6,use_clear=True)
        print('BAKE',k,round(time.time()-t),'s',flush=True)
        img.filepath_raw=f'{OUT}/lm_{k}.exr'; img.file_format='OPEN_EXR'; img.save()
    # albedo (warna dasar, termasuk tekstur prosedural) pada UV yang sama, resolusi lebih tinggi
    cres=RES*2 if k!='G' else RES
    ci=bpy.data.images.new(f'AL_{k}',cres,cres,float_buffer=False)
    bpy.ops.object.select_all(action='DESELECT'); J.select_set(True); bpy.context.view_layer.objects.active=J
    for m in J.data.materials:
        if not m or not m.node_tree: continue
        nt=m.node_tree; n=nt.nodes.get('BAKEC') or nt.nodes.new('ShaderNodeTexImage'); n.name='BAKEC'; n.image=ci
        for x in nt.nodes: x.select=False
        n.select=True; nt.nodes.active=n
    sc.cycles.samples=4; t=time.time()
    bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'},margin=6,use_clear=True)
    sc.cycles.samples=SMP; print('ALBEDO',k,round(time.time()-t),'s',flush=True)
    ci.filepath_raw=f'{OUT}/al_{k}.png'; ci.file_format='PNG'; ci.save()
for m in bpy.data.materials:
    for nn in ('BAKE','BAKEC'):
        if m.node_tree and nn in m.node_tree.nodes: m.node_tree.nodes.remove(m.node_tree.nodes[nn])
# ekspor lingkungan statis (UVMap + LM)
bpy.ops.object.select_all(action='DESELECT')
for J in joined.values(): J.select_set(True)
bpy.ops.export_scene.gltf(filepath=f'{OUT}/env.glb',export_format='GLB',use_selection=True,export_texcoords=True,export_materials='EXPORT',export_animations=False,export_cameras=False,export_lights=False,export_yup=True)
json.dump({'groups':list(joined),'procedural':sorted(proc)},open(f'{OUT}/env.json','w'))
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/baked.blend'); print('SEGBAKE OK')
