import bpy, math, sys
sys.path.insert(0,"/home/claude/ep04")
from lib import *; from char import *; from chars3 import batik, sarung
from mathutils import Vector
def lurik():
    m=bpy.data.materials.new("lurik"); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N["Principled BSDF"]
    tc=N.new("ShaderNodeTexCoord"); w=N.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value=14; w.bands_direction='X'; L.new(tc.outputs["Object"],w.inputs["Vector"])
    r=N.new("ShaderNodeValToRGB"); r.color_ramp.interpolation='CONSTANT'; r.color_ramp.elements[0].color=lin("#1E1A17"); r.color_ramp.elements[1].position=0.75; r.color_ramp.elements[1].color=lin("#4A3B2C")
    L.new(w.outputs["Fac"],r.inputs[0]); L.new(r.outputs[0],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.8; return m
def darmi_x(O,HC,add): add(rbox("Darmi_band_apron",(0.8,0.06,0.9),O+Vector((0,-0.32,1.45)),mat("#E8E2D0",0.7,0),0.04))
def joko_x(O,HC,add):
    t=torus("Joko_band_handuk",0.34,0.08,O+Vector((0,0.0,2.13)),mat("#F2F2F2",0.9,0)); t.scale=(1.05,0.95,0.8); add(t)
def bima_x(O,HC,add):
    for sx in (1,-1): l=rbox(f"Bima_lapel{sx}",(0.14,0.05,0.6),O+Vector((sx*0.18,-0.32,1.85)),mat("#B8A57A",0.6,0.1),0.03); l.rotation_euler=(0,math.radians(sx*15),0); add(l)
    add(rbox("Bima_band_belt",(1.0,0.64,0.1),O+Vector((0,0,1.3)),mat("#6B5233",0.5,0.2),0.03))
    t=torus("Bima_hand.R_lens",0.12,0.02,O+Vector((-0.73,-0.2,1.37)),mat("#333333",0.3,0.3,0.7),rot=(math.radians(90),0,0)); add(t)
    add(box("Bima_hand.R_handle",(0.04,0.04,0.25),O+Vector((-0.73,-0.2,1.2)),mat("#5A3A22",0.4,0.2),0.01))
def rina_x(O,HC,add): add(box("Rina_band_id",(0.18,0.03,0.24),O+Vector((0.22,-0.33,1.85)),mat("#FFFFFF",0.4,0.1),0.01))
def karto_x(O,HC,add):
    add(caps("Karto_jenggot",0.16,0.18,HC+Vector((0,-0.36,-0.32)),mat("#EDEDED",0.8,0),sc=(1.3,0.8,1)))
    add(box("Karto_kumis",(0.3,0.05,0.05),HC+Vector((0,-0.405,-0.12)),mat("#EDEDED",0.8,0),0.02))
def sarip_x(O,HC,add): pass
CH4={
 "Darmi":dict(skin="#F2C51F",top="#9A5A2E",bottom="#9A5A2E",shoes="#5A3A22",hair=dict(type="hijab",color="#6B4A2E"),extras=[darmi_x]),
 "Joko":dict(skin="#F2C51F",top="#8E9196",bottom="#3D4A5C",shoes="#222222",hair=dict(type="short",color="#1A1A1A"),extras=[joko_x]),
 "Bima":dict(skin="#F2C51F",top="#CDBB8E",bottom="#5B4A36",shoes="#2A1E14",hair=dict(type="fedora",color="#2A2018",hat="#7A6A4E"),extras=[bima_x]),
 "Rina":dict(skin="#F2C51F",top="#2E5C9A",bottom="#1E2A4A",shoes="#1A1A1A",hair=dict(type="ponytail",color="#2A1A10"),extras=[rina_x]),
 "Sarip":dict(skin="#F2C51F",top="#EDEDE6",bottom="#6B4A2E",shoes="#4A3A2A",hair=dict(type="kopiah",hat="#F2F2EE"),extras=[sarip_x]),
 "Karto":dict(skin="#E0B84A",top="#2E2620",bottom="#151515",shoes="#2A1E14",hair=dict(type="blangkon",color="#BFBFBF",hat="#4A2E1A"),extras=[karto_x]),
 "MelatiK":dict(skin="#F2C51F",top="#2E5C9A",bottom="#1E2A4A",shoes="#B71C1C",hair=dict(type="longback",color="#121212")),
}
def build4(base):
    rigs={}
    for i,(n,cfg) in enumerate(CH4.items()): rigs[n]=make_char(n,cfg,(base[0]+i*2.2,base[1],0))
    D=bpy.data.objects
    for o in ("Darmi_torso","Darmi_hips","Darmi_leg.L","Darmi_leg.R","Darmi_arm.L","Darmi_arm.R"): D[o].data.materials[0]=batik("#8A4A22")
    for o in ("Sarip_leg.L","Sarip_leg.R","Sarip_hips"): D[o].data.materials[0]=sarung()
    for o in ("Sarip_arm.L","Sarip_arm.R"): D[o].data.materials[0]=D["Sarip_hand.L"].data.materials[0]
    for o in ("Joko_arm.L","Joko_arm.R"): D[o].data.materials[0]=D["Joko_hand.L"].data.materials[0]
    D["Karto_torso"].data.materials[0]=lurik()
    return rigs
