# Menyusun folder render Ep 5: render_ep05/render_ep05.html + data/*.js  (bisa dibuka langsung dari file://)
import base64,json,os,sys,subprocess,glob,math
EP='/tmp/w/ep5'; OUT=f'{EP}/render_ep05'; B='/tmp/bench/node_modules/'; WEB='/home/claude/nayla-kos-melati-main/pipeline/web'
os.makedirs(f'{OUT}/data',exist_ok=True)
du=lambda b,m:f'data:{m};base64,'+base64.b64encode(b).decode(); rd=lambda p:open(p,'rb').read()
def js(path,rep=()):
    s=open(path).read()
    for a,b in rep: s=s.replace(a,b)
    return du(s.encode(),'text/javascript')
def wjs(name,var,obj): open(f'{OUT}/data/{name}.js','w').write(f'window.{var}='+json.dumps(obj)+';')
TL=json.load(open(f'{EP}/timeline.json')); NF=int(TL['total']*12)
ENVS={'E_sore':'A','E_kamar':'B','E_k1sore':'D','E_senja':'E','E_k1malam':'F','E_malam':'G','E_pagi':'H'}
SEGS=json.load(open(f'{EP}/segments.json'))
only=[x for x in sys.argv[1:] if not x.startswith('--')]                     # opsional: hanya env tertentu (uji)
if only: ENVS={k:v for k,v in ENVS.items() if k in only}; SEGS=[s for s in SEGS if s['env'] in ENVS]
for k,sid in ENVS.items():
    d=f'{EP}/seg_{sid}'; envj=json.load(open(f'{d}/env.json')); meta=json.load(open(f'{d}/meta.json'))
    if not os.path.exists(f'{OUT}/data/env_{k}.js') or '--force' in sys.argv:
        wjs(f'env_{k}',f'ENV_{k}',{'env':du(rd(f'{d}/env.glb'),'model/gltf-binary'),'lm':{g:du(rd(f'{d}/lm_{g}_c.exr'),'image/x-exr') for g in envj['groups']},
            'al':{g:du(rd(f'{d}/al_{g}.jpg'),'image/jpeg') for g in envj['groups'] if os.path.exists(f'{d}/al_{g}.jpg')},'procedural':envj['procedural'],
            'probe':du(rd(f'{d}/probe.exr'),'image/x-exr'),'sky':du(rd(f'{d}/sky.exr'),'image/x-exr'),'emissive':{n:e for n,e in meta['emissive'].items()}})
cuts=set()
for s in TL['shots']: cuts.add(int(round(s['start']*12)))
for sg in SEGS:
    d=f'{EP}/seg_{sg["id"]}'; meta=json.load(open(f'{d}/meta.json'))
    for i in range(1,len(meta['cam'])):
        a,b=meta['cam'][i-1],meta['cam'][i]
        if math.dist(a[:3],b[:3])>0.6 or math.dist(a[3:6],b[3:6])>1.5: cuts.add(sg['F0']-1+i)
    wjs(f'seg_{sg["id"]}',f'SEG_{sg["id"]}',{'dyn':du(rd(f'{d}/dyn.glb'),'model/gltf-binary'),'meta':meta,
        'eyes':{r:du(rd(f'{d}/{r}_eyes.png'),'image/png') for r in meta['faces']},'mouth':{r:du(rd(f'{d}/{r}_mouth.png'),'image/png') for r in meta['faces']}})
if not os.path.exists(f'{OUT}/data/media.js') or '--force' in sys.argv:
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f'{EP}/audio/mix.wav','-c:a','flac',f'{EP}/audio/mix.flac'],check=True)
    CL={'kejar':'Scene_kejar_kejaran_mobil','view':'View_Vice_City_-_Trim','lucia':'Lucia_Gameplay','mandy':'Mandy_game_-_Trim'}
    wjs('media','MEDIA',{'clips':{k:du(rd(f'/mnt/user-data/uploads/{f}.mp4'),'video/mp4') for k,f in CL.items()},'audio':du(rd(f'{EP}/audio/mix.flac'),'audio/flac'),
        'font':du(rd('/tmp/ep3/Nayla_Eps3/fonts/DejaVuSans-Bold.ttf'),'font/ttf')})
subprocess.run(['python3',f'{WEB}/mkseg.py',f'{EP}/timeline.json','1',str(NF),f'{EP}'],check=True)
seg=json.load(open(f'{EP}/seg.json')); SH={s['cam']:s for s in TL['shots']}; S6=SH['s6']; S10=SH['s10']
EXPO={'E_sore':1.25,'E_kamar':1.2,'E_k1sore':1.2,'E_senja':1.4,'E_k1malam':1.5,'E_malam':1.55,'E_pagi':1.2}
man={'slug':'nayla_ep05','total':TL['total'] if not only else max(s['F1'] for s in SEGS)/12,'nf':NF,'look':{'pow':1.15,'sat':1.15,'env':0.6},'exposure':EXPO,
     'rigs':['Nayla_rig','Dimas_rig'],'blush':{'Nayla_rig':0.38,'Dimas_rig':0.0},'envKeys':list(ENVS),'segments':SEGS,'cuts':sorted(cuts),
     'subs':seg['subs'],'end':seg['end'] or {'t0':TL['total']-0.85,'text':'BERSAMBUNG...?'},'tv':json.load(open(f'{EP}/tvsched.json')),'phone':TL['phone'],'inserts':[[S6['start'],S6['end'],'nayla'],[S10['start'],S10['end'],'dimas']],'preview':60.0}
open(f'{OUT}/data/manifest.js','w').write('window.EP='+json.dumps(man)+';')
head=open(f'{EP}/ph_head.html').read(); body=open(f'{EP}/ph_body.js').read().replace('__TONE__',open(f'{EP}/ph_tone.js').read())
head=head.replace('@font-face{font-family:"DejaVuSub";src:url(__FONT__) format("truetype");font-weight:700}','')
rep={'__THREE__':js(B+'three/build/three.module.min.js'),'__BGU__':js(B+'three/examples/jsm/utils/BufferGeometryUtils.js'),'__FFLATE__':js(B+'three/examples/jsm/libs/fflate.module.js'),
 '__GLTF__':js(B+'three/examples/jsm/loaders/GLTFLoader.js',[("'../utils/BufferGeometryUtils.js'","'bgu'")]),'__EXR__':js(B+'three/examples/jsm/loaders/EXRLoader.js',[("'../libs/fflate.module.js'","'fflate'")]),
 '__MUXER__':js(B+'mp4-muxer/build/mp4-muxer.mjs'),'__TITLE__':'Render — Nayla Ep. 5: GTA 6 Rilis!','__HEADING__':'Ep. 5 · GTA 6 Rilis!'}
for k,v in rep.items(): head=head.replace(k,v)
open(f'{OUT}/render_ep05.html','w').write(head+'<script type="module">\n'+body+'\n</script></body></html>')
print('ok', {f:round(os.path.getsize(f'{OUT}/data/{f}')/1e6,1) for f in os.listdir(f'{OUT}/data')})
