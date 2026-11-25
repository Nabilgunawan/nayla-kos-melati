import bpy, math, random
from mathutils import Vector
C=bpy.context
def lin(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c)+(1,)
_M={}
def mat(hexc,rough=0.35,coat=0.25,metal=0.0,emit=None,es=0.0,name=None):
    k=(hexc,rough,coat,metal,emit,es)
    if k in _M: return _M[k]
    m=bpy.data.materials.new(name or f"m_{hexc}"); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value=lin(hexc); b.inputs["Roughness"].default_value=rough
    b.inputs["Coat Weight"].default_value=coat; b.inputs["Metallic"].default_value=metal
    if emit: b.inputs["Emission Color"].default_value=lin(emit); b.inputs["Emission Strength"].default_value=es
    _M[k]=m; return m
def _fin(o,m,bev=None,seg=3,col=None,smooth=True):
    if bev:
        md=o.modifiers.new("bev","BEVEL"); md.width=bev; md.segments=seg; md.limit_method='ANGLE'
    if smooth:
        for p in o.data.polygons: p.use_smooth=True
    o.data.materials.append(m)
    if col: link(o,col)
    return o
def link(o,col):
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
def box(name,size,loc,m,bev=0.04,col=None,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=C.object; o.name=name
    for v in o.data.vertices: v.co.x*=size[0]; v.co.y*=size[1]; v.co.z*=size[2]
    return _fin(o,m,bev,3,col)
def cyl(name,r,d,loc,m,rot=(0,0,0),bev=0.02,col=None,v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,location=loc,rotation=rot,vertices=v); o=C.object; o.name=name
    return _fin(o,m,bev,2,col)
def sph(name,r,loc,m,scale=(1,1,1),col=None,seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,location=loc,segments=seg,ring_count=seg//2); o=C.object; o.name=name; o.scale=scale
    return _fin(o,m,None,0,col)
def cone(name,r1,r2,d,loc,m,col=None,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1,radius2=r2,depth=d,location=loc,rotation=rot,vertices=32); o=C.object; o.name=name
    return _fin(o,m,0.02,2,col)
def torus(name,R,r,loc,m,rot=(0,0,0),col=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R,minor_radius=r,location=loc,rotation=rot); o=C.object; o.name=name
    return _fin(o,m,None,0,col)
def plane(name,size,loc,m,rot=(0,0,0),col=None):
    bpy.ops.mesh.primitive_plane_add(size=1,location=loc,rotation=rot); o=C.object; o.name=name
    o.scale=(size[0],size[1],1); return _fin(o,m,None,0,col,False)
def newcol(name):
    c=bpy.data.collections.new(name); C.scene.collection.children.link(c); return c
