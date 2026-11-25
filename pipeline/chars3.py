import bpy, math, sys
sys.path.insert(0,"/home/claude/ep04")
from lib import *; from char import *
from mathutils import Vector
def batik(hexc="#7A4A25"):
    m=bpy.data.materials.new("batik"); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N["Principled BSDF"]
    tc=N.new("ShaderNodeTexCoord"); v=N.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value=7; v.feature='DISTANCE_TO_EDGE'; L.new(tc.outputs["Object"],v.inputs["Vector"])
    w=N.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value=9; w.inputs["Distortion"].default_value=4; L.new(tc.outputs["Object"],w.inputs["Vector"])
    r=N.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].color=lin("#3A2212"); r.color_ramp.elements[1].position=0.08; r.color_ramp.elements[1].color=lin(hexc); L.new(v.outputs["Distance"],r.inputs[0])
    mx=N.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.inputs["Factor"].default_value=0.25; L.new(r.outputs[0],mx.inputs[6]); mx.inputs[7].default_value=lin("#D9A441"); L.new(w.outputs["Fac"],mx.inputs["Factor"])
    L.new(mx.outputs[2],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.6; return m
def sarung():
    m=bpy.data.materials.new("sarung"); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N["Principled BSDF"]
    tc=N.new("ShaderNodeTexCoord"); ch=N.new("ShaderNodeTexChecker"); ch.inputs["Scale"].default_value=9; L.new(tc.outputs["Object"],ch.inputs["Vector"])
    ch.inputs["Color1"].default_value=lin("#1F5E3A"); ch.inputs["Color2"].default_value=lin("#2E7D4F"); L.new(ch.outputs["Color"],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.7; return m
def loreng():
    m=bpy.data.materials.new("loreng"); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links; b=N["Principled BSDF"]
    tc=N.new("ShaderNodeTexCoord"); n=N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value=6; n.inputs["Detail"].default_value=2; L.new(tc.outputs["Object"],n.inputs["Vector"])
    r=N.new("ShaderNodeValToRGB"); r.color_ramp.interpolation='CONSTANT'; e=r.color_ramp.elements; e[0].color=lin("#2F3B23"); e[1].position=0.62; e[1].color=lin("#6B6A3C")
    e2=e.new(0.45); e2.color=lin("#4A5530"); L.new(n.outputs["Fac"],r.inputs[0]); L.new(r.outputs[0],b.inputs["Base Color"]); b.inputs["Roughness"].default_value=0.75; return m
def rt_extras(O,HC,add):
    g=mat("#111111",0.25,0.3)
    for sx in (1,-1): add(torus(f"RT_glass{sx}",0.085,0.012,HC+Vector((sx*0.155,-0.405,0.03)),g,rot=(math.radians(90),0,0)))
    add(box("RT_glassbridge",(0.07,0.02,0.02),HC+Vector((0,-0.41,0.05)),g,0.005))
    add(box("RT_kumis",(0.34,0.06,0.07),HC+Vector((0,-0.405,-0.11)),mat("#161616",0.6,0.1),0.03))
    for z in (1.95,1.7,1.45): add(sph("RT_band_btn",0.025,O+Vector((0,-0.33,z)),mat("#E9D8B4",0.3,0.2)))
    add(box("RT_band_collar",(0.5,0.08,0.1),O+Vector((0,-0.29,2.12)),batik(),0.03))
def ronda_extras(O,HC,add):
    t=torus("Ronda_band_sarung",0.36,0.1,O+Vector((0,0.0,2.12)),sarung()); t.scale=(1.05,0.95,0.8); add(t)
    add(box("Ronda_zip",(0.04,0.02,0.95),O+Vector((0,-0.318,1.66)),mat("#222222",0.4,0.3),0.01))
    add(box("Ronda_kumis",(0.22,0.05,0.05),HC+Vector((0,-0.405,-0.12)),mat("#161616",0.6,0.1),0.02))
CH3={
 "RT":dict(skin="#F2C51F",top="#7A4A25",bottom="#1F5E3A",shoes="#3A2A1E",hair=dict(type="peci",color="#9A9A9A"),extras=[rt_extras]),
 "Ronda":dict(skin="#F2C51F",top="#4A5530",bottom="#2A2A2E",shoes="#1C1C1C",hair=dict(type="kupluk",color="#2B3324"),extras=[ronda_extras]),
 "Melati":dict(skin="#F2C51F",top="#F4F2EC",bottom="#F4F2EC",ghost=True,grounded=True,hair=dict(type="longback",color="#121212")),
}
def build3(base):
    rigs={}
    for i,(n,cfg) in enumerate(CH3.items()):
        r=make_char(n,cfg,(base[0]+i*2.2,base[1],0)); rigs[n]=r
    bpy.data.objects["RT_torso"].data.materials[0]=batik(); 
    for o in ("RT_leg.L","RT_leg.R","RT_hips"): bpy.data.objects[o].data.materials[0]=sarung()
    for o in ("Ronda_torso","Ronda_arm.L","Ronda_arm.R"): bpy.data.objects[o].data.materials[0]=loreng()
    return rigs
