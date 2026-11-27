# Menyusun satu file HTML render mandiri dari hasil segprep/segbake/segprobe/mkseg.
# Pemakaian: python buildseg.py <OUT> <slug> "<judul>" <font.ttf> [fokus_x] [exposure]
# Butuh node_modules: three@0.170.0 dan mp4-muxer@5.2.2 (npm i di /tmp/bench atau ubah B).
import base64,json,os,sys
OUT=sys.argv[1]; SLUG=sys.argv[2]; HEAD=sys.argv[3]; FONT=sys.argv[4]
FX=float(sys.argv[5]) if len(sys.argv)>5 else 0.0; EXPO=float(sys.argv[6]) if len(sys.argv)>6 else 1.55
B=os.environ.get('NODE_MODULES','/tmp/bench/node_modules/')
def du(data,mime): return f'data:{mime};base64,'+base64.b64encode(data).decode()
rd=lambda p:open(p,'rb').read()
def js(path,rep=()):
    s=open(path).read()
    for a,b in rep: s=s.replace(a,b)
    return du(s.encode(),'text/javascript')
meta=json.load(open(f'{OUT}/meta.json')); seg=json.load(open(f'{OUT}/seg.json')); envj=json.load(open(f'{OUT}/env.json')); dj=json.load(open(f'{OUT}/dyn.json'))
rigs=dj['dyn_rigs']
K={'meta':meta,'look':{'pow':1.15,'sat':1.15,'exposure':EXPO,'env':0.6},'slug':SLUG,'focus':[FX,0,2],
 'env':du(rd(f'{OUT}/env.glb'),'model/gltf-binary'),'dyn':du(rd(f'{OUT}/dyn.glb'),'model/gltf-binary'),
 'lm':{g:du(rd(f'{OUT}/lm_{g}_c.exr'),'image/x-exr') for g in envj['groups']},
 'al':{g:du(rd(f'{OUT}/al_{g}.jpg'),'image/jpeg') for g in envj['groups'] if os.path.exists(f'{OUT}/al_{g}.jpg')},
 'procedural':envj['procedural'],'probe':du(rd(f'{OUT}/probe.exr'),'image/x-exr'),'sky':du(rd(f'{OUT}/sky.exr'),'image/x-exr'),
 'eyes':{r:du(rd(f'{OUT}/{r}_eyes.png'),'image/png') for r in meta['faces']},'mouth':{r:du(rd(f'{OUT}/{r}_mouth.png'),'image/png') for r in meta['faces']},
 'rigs':rigs,'blush':{r+'_rig':v for r,v in {'Nayla':0.38,'Adel':0.30,'Ibu':0.22,'Melati':0.30,'MelatiK':0.30,'Darmi':0.22,'Rina':0.28}.items()},'audio':du(rd(f'{OUT}/audio.flac'),'audio/flac'),'duration':seg['duration'],'cuts':seg['cuts'],'subs':seg['subs'],'flash':seg['flash'],'end':seg['end'],'preview':5.0}
t=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'player.html')).read()
rep={'__THREE__':js(B+'three/build/three.module.min.js'),'__BGU__':js(B+'three/examples/jsm/utils/BufferGeometryUtils.js'),'__FFLATE__':js(B+'three/examples/jsm/libs/fflate.module.js'),
 '__GLTF__':js(B+'three/examples/jsm/loaders/GLTFLoader.js',[("'../utils/BufferGeometryUtils.js'","'bgu'")]),
 '__EXR__':js(B+'three/examples/jsm/loaders/EXRLoader.js',[("'../libs/fflate.module.js'","'fflate'")]),'__MUXER__':js(B+'mp4-muxer/build/mp4-muxer.mjs'),
 '__FONT__':du(rd(FONT),'font/ttf'),'__TITLE__':'Render — '+HEAD,'__HEADING__':HEAD,'__PKG__':json.dumps(K)}
for k,v in rep.items(): t=t.replace(k,v)
p=f'{OUT}/render_{SLUG}.html'; open(p,'w').write(t); print(round(len(t)/1e6,1),'MB')
