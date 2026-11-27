# Ep5: memperkaya isi kamar Nayla dan kamar Dimas (properti rapi, bukan berantakan)
import bpy, math, random
from mathutils import Vector
_src=open('/tmp/w/ep5/sets5.py').read(); exec(_src[_src.index('def lin'):_src.index('# ---- 1. bersihkan animasi lama')])
bpy.ops.wm.open_mainfile(filepath='/tmp/w/ep5/ep05_sets.blend')
O=bpy.data.objects; D=math.radians; X0=450.0; rnd=random.Random(7)
def plant(name,loc,s=1.0):
    cyl(name+'_pot',0.22*s,0.35*s,(loc[0],loc[1],loc[2]+0.175*s),mat('pot_tanah','#B5653A',0.7))
    for i in range(7):
        a=i/7*6.283; l=sph(name+f'_daun{i}',0.16*s,(loc[0]+math.cos(a)*0.12*s,loc[1]+math.sin(a)*0.12*s,loc[2]+(0.5+0.12*(i%3))*s),mat('daun_hijau','#3E8E41',0.6),sc=(0.7,0.7,1.5))
def shelf(name,loc,w,rot=0,books=True,col='#E8D3B0'):
    b=box(name,(w,0.32,0.06),loc,mat('rak_kayu',col,0.6)); b.rotation_euler=(0,0,D(rot))
    if books:
        x=-w/2+0.12; cols=['#E85D75','#4D96FF','#6BCB77','#FFD93D','#845EC2','#FF9671','#2EC4B6']
        while x<w/2-0.3:
            h=rnd.uniform(0.3,0.45); t=rnd.uniform(0.07,0.11)
            o=box(name+'_buku',(t,0.24,h),(0,0,0),mat('buku'+cols[int(x*10)%7],cols[int(x*10)%7],0.6)); o.parent=b; o.location=(x,0,0.03+h/2); x+=t+0.01
        plant(name+'_tanaman',(loc[0]+(w/2-0.25)*math.cos(D(rot)),loc[1]+(w/2-0.25)*math.sin(D(rot)),loc[2]+0.03),0.55)
def frame(name,loc,w,h,col,rot):
    box(name,(w,0.04,h),loc,mat('bingkai','#3A2A22',0.5),rot=rot); box(name+'_isi',(w*0.82,0.05,h*0.82),loc,mat('foto_'+col,col,0.4),rot=rot)
# ---------- kamar Nayla (pusat 0,0)
for i in range(16):                                   # lampu tumbler di atas jendela dan dinding belakang
    x=-3.6+i*0.42; z=5.05-0.12*math.sin(i*0.9)**2
    sph(f'k_tumbler{i}',0.05,(x,4.36,z),mat('tumbler','#FFD9A0',0.3,emis='#FFC873',es=6))
shelf('k_rak2',(1.6,4.38,3.0),1.6)
plant('k_tanaman_lantai',(2.3,3.9,0.0),1.2)
for i,(x,c) in enumerate(((0.75,'#F4B6C2'),(1.25,'#A0C4FF'),(0.95,'#FDFFB6'))): frame(f'k_foto{i}',(x,4.42,2.0+i*0.55 if i<2 else 3.9),0.38,0.46,c,(D(90),0,0))
sph('k_boneka',0.32,(-3.6,3.6,1.35),mat('boneka','#C8A27A',0.8),sc=(1,0.9,1)); sph('k_boneka_kepala',0.22,(-3.6,3.55,1.8),mat('boneka','#C8A27A',0.8))
cyl('k_keranjang',0.32,0.6,(-4.0,-1.8,0.3),mat('keranjang','#D9C29A',0.8))
# ---------- kamar Dimas (X0=450): LED di belakang TV, rak figur, gitar, tempat sampah, tanaman
WX=X0-4.65
box('k1_led',(0.05,2.9,0.06),(WX+0.08,0.8,2.85),mat('led_ungu','#9B5DE5',0.3,emis='#9B5DE5',es=8)); box('k1_led2',(0.05,2.9,0.06),(WX+0.08,0.8,1.05),mat('led_ungu','#9B5DE5',0.3,emis='#9B5DE5',es=8))
shelf('k1_rak',(WX+0.2,3.3,3.1),1.4,90,books=False,col='#2B2B30')
for i,c in enumerate(('#E63946','#F1FAEE','#FFD166','#06D6A0')):
    o=box(f'k1_figur{i}',(0.14,0.14,0.32),(WX+0.2,2.8+i*0.32,3.3),mat('figur'+c,c,0.4,coat=0.4))
shelf('k1_rak_buku',(X0-1.0,4.38,2.8),1.8)
g=sph('k1_gitar_badan',0.42,(X0+1.7,4.15,0.75),mat('gitar','#B5651D',0.35,coat=0.5),sc=(1,0.35,1.25)); box('k1_gitar_leher',(0.12,0.08,1.2),(X0+1.7,4.15,1.9),mat('gitar_leher','#3A2A22',0.5)); g.rotation_euler=(D(-8),0,0)
cyl('k1_sampah',0.22,0.5,(X0+4.2,3.6,0.25),mat('sampah','#5C677D',0.6))
plant('k1_tanaman',(X0-3.9,3.9,0.0),1.1)
for i,(y,c) in enumerate(((-2.4,'#FF6B6B'),(2.6,'#4D96FF'))): frame(f'k1_foto{i}',(X0+4.58,y,3.4),0.5,0.62,c,(D(90),0,D(90)))
bpy.ops.wm.save_as_mainfile(filepath='/tmp/w/ep5/ep05_sets.blend'); print('PROPS OK')
