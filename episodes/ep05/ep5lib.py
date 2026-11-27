# Pose bantu Ep 5: duduk selonjor di lantai, memegang stik dengan dua tangan
import bpy, math
from mathutils import Vector, Matrix
D=math.radians
def part(rig,key):
    pre=rig.name[:-4]+'_'
    for c in rig.children_recursive:
        n=c.name[len(pre):] if c.name.startswith(pre) else c.name
        if n==key: return c
def sit_floor(rig,x,y,yaw,floor=0.02):
    rig.location=(x,y,floor-0.91+0.03); rig.rotation_euler=(0,0,D(yaw))
    pb=rig.pose.bones
    for b in pb: b.rotation_mode='XYZ'
    for s in ('L','R'): pb[f'leg.{s}'].rotation_euler=(D(-88),0,D(7 if s=='L' else -7))
    pb['spine'].rotation_euler=(D(6),0,0)
def hold(rig,ctrl,fwd=-62):
    """lengan maju dan merapat sampai kedua tangan menggenggam pegangan stik"""
    pb=rig.pose.bones; best=None
    for sgn in (1,-1):
        for inward in range(0,64,2):
            pb['arm.L'].rotation_euler=(D(fwd),0,D(sgn*inward)); pb['arm.R'].rotation_euler=(D(fwd),0,D(-sgn*inward))
            bpy.context.view_layer.update()
            hl=part(rig,'hand.L').matrix_world.translation; hr=part(rig,'hand.R').matrix_world.translation
            d=(hl-hr).length
            if best is None or abs(d-0.42)<abs(best[0]-0.42): best=(d,sgn,inward)
    d,sgn,inward=best
    pb['arm.L'].rotation_euler=(D(fwd),0,D(sgn*inward)); pb['arm.R'].rotation_euler=(D(fwd),0,D(-sgn*inward))
    for s in ('L','R'): pb[f'hand.{s}'].rotation_euler=(D(-20),0,0)
    bpy.context.view_layer.update()
    hl=part(rig,'hand.L').matrix_world.translation; hr=part(rig,'hand.R').matrix_world.translation
    mid=(hl+hr)/2; yaw=rig.rotation_euler.z
    fwdv=Vector((math.sin(yaw),-math.cos(yaw),0))
    ctrl.parent=None
    ctrl.matrix_world=Matrix.Translation(mid+fwdv*0.03+Vector((0,0,0.04)))@Matrix.Rotation(yaw,4,'Z')@Matrix.Rotation(D(35),4,'X')
    bpy.context.view_layer.update(); mw=ctrl.matrix_world.copy()
    ctrl.parent=rig; ctrl.parent_type='BONE'; ctrl.parent_bone='hand.R'; bpy.context.view_layer.update(); ctrl.matrix_world=mw
    return d,sgn,inward
