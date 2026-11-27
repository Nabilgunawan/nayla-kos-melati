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
SEGS=json.load(open(f'{EP}/segments.json'))
ENVS={}
for s in SEGS: ENVS.setdefault(s['env'],s['id'])
only=[x for x in sys.argv[1:] if not x.startswith('--')]                     # opsional: hanya env tertentu (uji)
if only: ENVS={k:v for k,v in ENVS.items() if k in only}; SEGS=[s for s in SEGS if s['env'] in ENVS]
for k,sid in ENVS.items():
    d=f'{EP}/env_{k}'; envj=json.load(open(f'{d}/env.json')); meta=json.load(open(f'{EP}/segv2_{sid}/meta.json'))
    if not os.path.exists(f'{OUT}/data/env_{k}.js') or '--force' in sys.argv:
        wjs(f'env_{k}',f'ENV_{k}',{'env':du(rd(f'{d}/env.glb'),'model/gltf-binary'),'lm':{g:du(rd(f'{d}/lm_{g}_c.exr'),'image/x-exr') for g in envj['groups']},
            'al':{g:du(rd(f'{d}/al_{g}.jpg'),'image/jpeg') for g in envj['groups'] if os.path.exists(f'{d}/al_{g}.jpg')},'procedural':envj['procedural'],
            'probe':du(rd(f'{d}/probe.exr'),'image/x-exr'),'sky':du(rd(f'{d}/sky.exr'),'image/x-exr'),'emissive':{n:e for n,e in meta['emissive'].items()}})
cuts=set()
for s in TL['shots']: cuts.add(int(round(s['start']*12)))
for sg in SEGS:
    d=f'{EP}/segv2_{sg["id"]}'; meta=json.load(open(f'{d}/meta.json'))
    for i in range(1,len(meta['cam'])):
        a,b=meta['cam'][i-1],meta['cam'][i]
        if math.dist(a[:3],b[:3])>0.6 or math.dist(a[3:6],b[3:6])>1.5: cuts.add(sg['F0']-1+i)
    wjs(f'seg_{sg["id"]}',f'SEG_{sg["id"]}',{'dyn':du(rd(f'{d}/dyn.glb'),'model/gltf-binary'),'meta':meta,
        'eyes':{r:du(rd(f'{d}/{r}_eyes.png'),'image/png') for r in meta['faces']},'mouth':{r:du(rd(f'{d}/{r}_mouth.png'),'image/png') for r in meta['faces']}})
if not os.path.exists(f'{OUT}/data/media.js') or '--force' in sys.argv:
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f'{EP}/audio/mix.wav','-c:a','flac',f'{EP}/audio/mix.flac'],check=True)
    CL={'kejar':'Scene_kejar_kejaran_mobil','view':'View_Vice_City_-_Trim','lucia':'Lucia_Gameplay','mandy':'Mandy_game_-_Trim'}
    frames={}
    for a,b_,k,off in json.load(open(f'{EP}/tvsched.json')):
        if k not in CL: continue
        d=f'{EP}/tvframes/{k}'; os.makedirs(d,exist_ok=True)
        for f in glob.glob(f'{d}/*.jpg'): os.remove(f)
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(off),'-t',str(b_-a+0.2),'-i',f'/mnt/user-data/uploads/{CL[k]}.mp4','-vf','fps=30,scale=-2:360','-q:v','5',f'{d}/%04d.jpg'],check=True)
        frames[k]=[du(rd(f),'image/jpeg') for f in sorted(glob.glob(f'{d}/*.jpg'))]
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','4.4','-i','/mnt/user-data/uploads/Lucia_Gameplay.mp4','-frames:v','1','-vf','scale=1024:576','-q:v','3',f'{EP}/tvframes/pause.jpg'],check=True)
    wjs('media','MEDIA',{'frames':frames,'pause':du(rd(f'{EP}/tvframes/pause.jpg'),'image/jpeg'),'audio':du(rd(f'{EP}/audio/mix.flac'),'audio/flac'),
        'font':du(rd('/tmp/ep3/Nayla_Eps3/fonts/DejaVuSans-Bold.ttf'),'font/ttf'),'font2':du(rd('/tmp/w/Oswald.ttf'),'font/ttf')})
subprocess.run(['python3',f'{WEB}/mkseg.py',f'{EP}/timeline.json','1',str(NF),f'{EP}'],check=True)
seg=json.load(open(f'{EP}/seg.json')); SH={s['cam']:s for s in TL['shots']}; S6=SH['s6']; S10=SH['s10']
EXPO={'E_sore':1.4,'E_kamar':1.4,'E_k1sore':1.45,'E_senja':1.6,'E_k1malam':1.75,'E_malam':1.85,'E_pagi':1.35}
def short_subs():
    out=[]
    for c in TL['clips']:
        txt=c['text'].replace('"','').strip()
        if not txt: continue
        w=txt.upper().split(); chunks=[]; cur=[]
        for x in w:
            cur.append(x)
            if len(cur)>=3 or len(' '.join(cur))>=16 or x[-1] in '.?!,': chunks.append(' '.join(cur)); cur=[]
        if cur: chunks.append(' '.join(cur))
        tot=sum(len(x) for x in chunks); t=c['dst']
        for ch in chunks:
            d=c['dur']*len(ch)/tot; out.append({'t0':round(t,3),'t1':round(t+d+0.05,3),'text':ch,'spk':c['spk'],'narasi':c['id'] in NARASI}); t+=d
    return out
NARASI={'N1','N7','N13','N14'}
man={'slug':'nayla_ep05','total':TL['total'] if not only else max(s['F1'] for s in SEGS)/12,'nf':NF,'look':{'pow':1.15,'sat':1.15,'env':0.6},'exposure':EXPO,
     'rigs':['Nayla_rig','Dimas_rig'],'blush':{'Nayla_rig':0.38,'Dimas_rig':0.0},'envKeys':list(ENVS),'segments':SEGS,'cuts':sorted(cuts),
     'subs':short_subs(),'end':seg['end'] or {'t0':TL['total']-0.85,'text':'BERSAMBUNG...?'},'tv':json.load(open(f'{EP}/tvsched.json')),'phone':TL['phone'],'inserts':[[S6['start']+1.4,S6['end'],'dimas'],[S10['start'],S10['end'],'dimas']],'preview':2.5}
open(f'{OUT}/data/manifest.js','w').write('window.EP='+json.dumps(man)+';')
head=open(f'{EP}/ph_head.html').read(); body=open(f'{EP}/ph_body.js').read().replace('__TONE__',open(f'{EP}/ph_tone.js').read())
head=head.replace('@font-face{font-family:"DejaVuSub";src:url(__FONT__) format("truetype");font-weight:700}','')
PP=B+'three/examples/jsm/'
def ppjs(path):
    import re
    s=open(PP+path).read()
    s=re.sub(r"from '\./(\w+)\.js'",r"from 'pp/\1'",s); s=re.sub(r"from '\.\./shaders/(\w+)\.js'",r"from 'sh/\1'",s)
    return du(s.encode(),'text/javascript')
extra={f'pp/{n}':ppjs(f'postprocessing/{n}.js') for n in ('EffectComposer','RenderPass','BokehPass','UnrealBloomPass','OutputPass','ShaderPass','MaskPass','Pass')}
extra.update({f'sh/{n}':ppjs(f'shaders/{n}.js') for n in ('BokehShader','CopyShader','LuminosityHighPassShader','OutputShader')})
head=head.replace('"mp4muxer":"__MUXER__"','"mp4muxer":"__MUXER__",'+','.join(f'"{k}":"{v}"' for k,v in extra.items()))
rep={'__THREE__':js(B+'three/build/three.module.min.js'),'__BGU__':js(B+'three/examples/jsm/utils/BufferGeometryUtils.js'),'__FFLATE__':js(B+'three/examples/jsm/libs/fflate.module.js'),
 '__GLTF__':js(B+'three/examples/jsm/loaders/GLTFLoader.js',[("'../utils/BufferGeometryUtils.js'","'bgu'")]),'__EXR__':js(B+'three/examples/jsm/loaders/EXRLoader.js',[("'../libs/fflate.module.js'","'fflate'")]),
 '__MUXER__':js(B+'mp4-muxer/build/mp4-muxer.mjs'),'__TITLE__':'Render — Nayla Ep. 5: GTA 6 Rilis!','__HEADING__':'Ep. 5 · GTA 6 Rilis!'}
for k,v in rep.items(): head=head.replace(k,v)
open(f'{OUT}/render_ep05.html','w').write(head+'<script type="module">\n'+body+'\n</script></body></html>')
print('ok', {f:round(os.path.getsize(f'{OUT}/data/{f}')/1e6,1) for f in os.listdir(f'{OUT}/data')})
