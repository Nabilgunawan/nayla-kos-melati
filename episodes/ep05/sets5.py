# Ep 5: dari ep04.blend -> ep05_sets.blend
# kamar 1 Dimas (X=450), TV + konsol generik + stik, beanbag, poster, camilan, jam dinding, ponsel Dimas, karakter perempuan femme.py
import bpy, sys, math
from mathutils import Vector
sys.path.insert(0,'/home/claude/nayla-kos-melati-main/pipeline')
bpy.ops.wm.open_mainfile(filepath="/tmp/ep4/Nayla_Eps4/ep04.blend")
O=bpy.data.objects; D=math.radians; X0=450.0
def lin(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c)+(1,)
def mat(name,hexc,rough=0.5,coat=0.0,emis=None,es=0.0,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=lin(hexc); b.inputs['Roughness'].default_value=rough; b.inputs['Coat Weight'].default_value=coat; b.inputs['Metallic'].default_value=metal
    if emis: b.inputs['Emission Color'].default_value=lin(emis); b.inputs['Emission Strength'].default_value=es
    return m
def obj(name,me,loc,m,rot=(0,0,0),bev=None):
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); o.location=loc; o.rotation_euler=rot
    if m: me.materials.append(m)
    for p in me.polygons: p.use_smooth=True
    if bev: md=o.modifiers.new('bev','BEVEL'); md.width=bev; md.segments=4; md.limit_method='NONE'
    return o
def box(name,size,loc,m,rot=(0,0,0),bev=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1); t=bpy.context.object; me=t.data; bpy.data.objects.remove(t)
    for v in me.vertices: v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
    return obj(name,me,loc,m,rot,bev)
def sph(name,r,loc,m,sc=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,segments=32,ring_count=16); t=bpy.context.object; me=t.data; bpy.data.objects.remove(t)
    for v in me.vertices: v.co=(v.co.x*sc[0],v.co.y*sc[1],v.co.z*sc[2])
    return obj(name,me,loc,m)
def cyl(name,r,h,loc,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=h,vertices=32); t=bpy.context.object; me=t.data; bpy.data.objects.remove(t)
    return obj(name,me,loc,m,rot,0.01)
def plane(name,w,h,loc,m,rot):
    bpy.ops.mesh.primitive_plane_add(size=1); t=bpy.context.object; me=t.data; bpy.data.objects.remove(t)
    for v in me.vertices: v.co=(v.co.x*w,v.co.y*h,0)
    return obj(name,me,loc,m,rot)
def imgmat(name,path,rough=0.6):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value=rough
    t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(path); t.image.pack(); nt.links.new(t.outputs[0],b.inputs['Base Color']); return m
# ---- 1. bersihkan animasi lama
for o in O:
    if o.animation_data: o.animation_data_clear()
    if o.data and hasattr(o.data,'animation_data') and o.data.animation_data: o.data.animation_data_clear()
for m in bpy.data.materials:
    if m.node_tree and m.node_tree.animation_data: m.node_tree.animation_data_clear()
if bpy.context.scene.world.node_tree.animation_data: bpy.context.scene.world.node_tree.animation_data_clear()
# ---- 2. karakter perempuan
import femme; femme.run(femme.FEMALE)
# ---- 3. salin kamar Nayla -> kamar 1 Dimas
rigkids=set()
for r in [o for o in O if o.type=='ARMATURE']: rigkids|=set(r.children_recursive)|{r}
SKIP=('k_desk','k_dleg','k_shelf','k_book','k_globe','k_lamp','k_laptop','k_stool','k_poster','k_bear','mug')
src=[o for o in O if o.name.startswith('k_') or o.name in('FAN_BLADES','FAN_HEAD','L_kos_fill','L_kos_window')]
src=[o for o in src if o not in rigkids and not o.name.startswith(SKIP)]
wall=mat('k1_dinding','#C9D3DE',0.8); M={}
for o in src:
    if o.parent and o.parent in src: continue
    def dup(o,parent=None):
        c=o.copy()
        if o.data: c.data=o.data.copy() if o.type=='MESH' else o.data.copy()
        bpy.context.scene.collection.objects.link(c); c.name='k1'+o.name[1:] if o.name.startswith('k_') else o.name.replace('L_kos','L_k1').replace('FAN','K1FAN')
        if parent: c.parent=parent; c.matrix_parent_inverse=o.matrix_parent_inverse.copy()
        else: c.location.x+=X0
        for ch in o.children: dup(ch,c)
        return c
    dup(o)
for o in [o for o in O if o.name.startswith('k1_wall')]: o.data.materials.clear(); o.data.materials.append(wall)
for n in ('k1_bedframe','k1_mattress','k1_blanket','k1_pillow'):     # kasur pindah ke kanan-belakang
    o=O.get(n)
    if o: o.location.x=X0+(X0-o.location.x)*0+3.25 if False else X0+abs(o.location.x-X0)
bl=O.get('k1_blanket');  bl and (bl.data.materials.clear(), bl.data.materials.append(mat('k1_selimut','#2E3B55',0.8)))
# ---- 4. set gaming di dinding kiri, menghadap +X
WX=X0-4.65
cab=box('k1_tv_meja',(0.75,3.4,0.9),(WX+0.45,0.8,0.45),mat('k1_kayu_gelap','#3A2A22',0.55),bev=0.04)
tv=box('k1_tv',(0.12,2.7,1.56),(WX+0.35,0.8,1.95),mat('k1_tv_bingkai','#111114',0.35),bev=0.03)
box('k1_tv_kaki',(0.35,0.5,0.06),(WX+0.45,0.8,0.93),mat('k1_tv_bingkai','#111114',0.35))
scr=plane('TV_SCREEN',2.56,1.44,(WX+0.416,0.8,1.95),mat('tv_layar','#000000',0.25,emis='#FFFFFF',es=0.0),rot=(D(90),0,D(90)))
# konsol generik (berdiri): inti hitam + dua panel putih membulat
kc=Vector((WX+0.45,2.15,0.9))
box('KONSOL_inti',(0.42,0.16,0.62),kc+Vector((0,0,0.33)),mat('konsol_hitam','#151518',0.4),bev=0.03)
for s in (-1,1):
    p=sph('KONSOL_panel',0.33,kc+Vector((0,s*0.1,0.34)),mat('konsol_putih','#F2F2F4',0.3,coat=0.4),sc=(0.75,0.12,1.05)); p.name=f'KONSOL_panel{s}'
box('KONSOL_kaki',(0.3,0.3,0.03),kc+Vector((0,0,0.015)),mat('konsol_hitam','#151518',0.4))
cyl('KONSOL_kabel',0.015,0.5,kc+Vector((-0.2,0,0.25)),mat('kabel','#111111',0.6))
# stik di meja (2) : badan + dua pegangan
def stik(name,loc,col,yaw=0):
    m=mat(f'stik_{col}',{'putih':'#ECECEF','hitam':'#1C1C20'}[col],0.35,coat=0.3)
    b=box(name,(0.34,0.16,0.07),loc,m,bev=0.04); b.rotation_euler=(0,0,D(yaw))
    for s in (-1,1):
        g=sph(name+f'_grip{s}',0.07,Vector((s*0.13,0.07,-0.01)),m,sc=(1,1.6,0.8)); g.parent=b
    for s in (-1,1):
        k=cyl(name+f'_stik{s}',0.03,0.03,Vector((s*0.06,-0.02,0.045)),mat('stik_karet','#2A2A30',0.7)); k.parent=b
    return b
stik('STIK_meja1',Vector((WX+0.55,-0.3,0.94)),'putih',80); stik('STIK_meja2',Vector((WX+0.6,0.1,0.94)),'hitam',95)
# beanbag, poster, camilan, jam
for i,(y,c) in enumerate(((-0.1,'#C0392B'),(1.7,'#2C6E8F'))):
    b=sph(f'k1_beanbag{i}',0.75,(X0-1.3,y,0.42),mat(f'k1_bb{i}',c,0.85),sc=(1.0,1.0,0.55))
for i,(p,y) in enumerate((('poster_neon',-1.6),('poster_speed',1.2))):
    plane(f'k1_poster{i}',1.2,1.68,(X0+y,4.36,3.6),imgmat(f'k1_{p}',f'/tmp/w/ep5/tex/{p}.png'),rot=(D(90),0,D(180)))
box('k1_keripik',(0.4,0.12,0.5),(X0-2.3,0.75,0.27),mat('keripik','#F39C12',0.4,coat=0.5),rot=(D(70),0,D(20)))
for i,y in enumerate((0.35,1.15)):
    cyl(f'k1_gelas{i}',0.09,0.26,(X0-2.4,y,0.13),mat('esteh','#B5651D',0.15))
cl=cyl('JAM',0.32,0.05,(X0+2.6,4.48,4.4),mat('jam_muka','#FAFAF5',0.5),rot=(D(90),0,0))
cyl('JAM_bingkai',0.35,0.04,(X0+2.6,4.5,4.4),mat('jam_bingkai','#222222',0.4),rot=(D(90),0,0))
for n,L,w in (('JAM_jarum_j',0.18,0.035),('JAM_jarum_m',0.27,0.022)):
    j=box(n,(w,0.01,L),(0,0,L/2),mat('jam_jarum','#111111',0.5),bev=0.005)
    piv=bpy.data.objects.new(n+'_piv',None); bpy.context.scene.collection.objects.link(piv); piv.location=(X0+2.6,4.42,4.4)
    j.parent=piv
# pintu kamar 1 (interior) bisa dibuka: pivot di engsel
door=O.get('k1_door')
if door:
    piv=bpy.data.objects.new('K1DOOR_piv',None); bpy.context.scene.collection.objects.link(piv)
    bb=[door.matrix_world@Vector(c) for c in door.bound_box]; piv.location=(min(v.x for v in bb),min(v.y for v in bb),0)
    for n in ('k1_door','k1_doorknob'):
        o=O.get(n)
        if o: mw=o.matrix_world.copy(); o.parent=piv; o.matrix_world=mw
# lampu: lampu kamar (titik hangat) + cahaya TV (area, warna berubah)
def light(name,typ,loc,e,col,rot=None,size=None):
    l=bpy.data.lights.new(name,typ); l.energy=e; l.color=col; l.use_shadow=False
    if size: l.size=size
    o=bpy.data.objects.new(name,l); bpy.context.scene.collection.objects.link(o); o.location=loc
    if rot: o.rotation_euler=rot
    return o
light('L_k1_lampu','POINT',(X0,0.6,5.7),0,(1,0.85,0.65))
light('L_tv','AREA',(WX+0.6,0.8,1.95),0,(0.6,0.75,1.0),rot=(0,D(90),0),size=2.4)
# ---- 5. ponsel Dimas (salinan ponsel Nayla) + layar unik
for who,rig,hand,col in (('nayla','Nayla_rig','hand.R','#E8B4C8'),('dimas','Dimas_rig','Dimas_hand.R','#2C3E66')):
    if who=='nayla':
        ph=O['phone']; sc_=O['phone_screen']
    else:
        ph=O['phone'].copy(); ph.data=O['phone'].data.copy(); bpy.context.scene.collection.objects.link(ph); ph.name='phone_dimas'
        sc_=O['phone_screen'].copy(); sc_.data=O['phone_screen'].data.copy(); bpy.context.scene.collection.objects.link(sc_); sc_.name='phone_screen_dimas'; sc_.parent=ph
        hn=O[hand]; rel=O['hand.R'].matrix_world.inverted()@O['phone'].matrix_world
        ph.parent=O[rig]; ph.parent_type='BONE'; ph.parent_bone=hand.replace('Dimas_','') if False else 'hand.R'
        bpy.context.view_layer.update(); ph.matrix_world=hn.matrix_world@rel
    ph.data.materials.clear(); ph.data.materials.append(mat(f'hp_body_{who}',col,0.3,coat=0.5))
    sc_.data.materials.clear(); sc_.data.materials.append(mat(f'hp_layar_{who}','#000000',0.2,emis='#FFFFFF',es=1.0))
    ph.hide_render=False; sc_.hide_render=False; ph.scale=(0.001,0.001,0.001)       # disembunyikan lewat skala (bisa dianimasikan di glTF)
bpy.ops.wm.save_as_mainfile(filepath='/tmp/w/ep5/ep05_sets.blend'); print('SETS5 OK')
