import json, subprocess, numpy as np
SR=48000; TL=json.load(open('timeline.json')); N=int((TL['total'])*SR)
P='/tmp/priv/Nabilgunawan-nayla-kos-melati-private-6c32c0054f0558ecc95fddf4f796a065883ee9b5'; K='/home/claude/nayla-kos-melati-main/assets/sfx_cc0'
def load(path,ss=None,dur=None):
    cmd=['ffmpeg','-loglevel','error']+(['-ss',str(ss)] if ss is not None else [])+(['-t',str(dur)] if dur else [])+['-i',path,'-ac','2','-ar',str(SR),'-f','f32le','-']
    a=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32); return a.reshape(-1,2)
def find(name):
    import glob
    for d in (P+'/sfx',P,K):
        g=glob.glob(f'{d}/{name}*')
        if g: return g[0]
voice=np.zeros((N,2),np.float32); fx=np.zeros((N,2),np.float32)
def put(buf,a,t,db=0,fade=0.02):
    i=int(t*SR); a=a[:max(0,N-i)].copy()*10**(db/20)
    if len(a)==0: return
    f=min(len(a)//2,int(fade*SR))
    if f: a[:f]*=np.linspace(0,1,f)[:,None]; a[-f:]*=np.linspace(1,0,f)[:,None]
    buf[i:i+len(a)]+=a
for c in TL['clips']:
    put(voice,load(f"audio/{c['spk']}.mp3",c['src'][0],c['dur']),c['dst'],0)
MAP={'burung_sore':'angin','notif':'confirmation_001','langkah_lari':'lari','tap':'click_002','tos':'drop_003','ding':'confirmation_004','jam_cepat':'jam','jangkrik':'jangkrik',
     'pause':'click_004','jam_detik':'jam','ayam':'ayam','kunci':'click_005','gagang':'buka-pintu','sting':'banting'}
for t,name,db,dur in TL['sfx']:
    p=find(MAP.get(name,name))
    if not p: print('tidak ada',name); continue
    put(fx,load(p,0,dur),t,db,0.15 if dur else 0.01)
# audio footage di TV (game)
CL={'kejar':'Scene_kejar_kejaran_mobil','view':'View_Vice_City_-_Trim','lucia':'Lucia_Gameplay','mandy':'Mandy_game_-_Trim'}
for a,b,k,off in json.load(open('tvsched.json')):
    if k in CL: put(fx,load(f'/mnt/user-data/uploads/{CL[k]}.mp4',off,b-a),a,-14,0.2)
# musik tegang di babak akhir, hening sejenak sebelum teriakan
S={s['cam']:s for s in TL['shots']}; C={c['id']:c for c in TL['clips']}
mus=find('tegang'); t0=S['s23']['start']; t1=C['D13']['dst']-0.6
if mus: put(fx,load(mus,0,t1-t0),t0,-16,0.5)
tr=find('trailer')
if tr: put(fx,load(tr,0,TL['total']-C['D13']['dst']),C['D13']['dst'],-10,0.05)
# duck: efek turun 8 dB saat ada suara
env=np.abs(voice).max(1); k=int(0.15*SR); env=np.convolve(env,np.ones(k)/k,'same'); g=np.where(env>0.02,10**(-8/20),1.0)
g=np.convolve(g,np.ones(k)/k,'same').astype(np.float32)
mix=voice+fx*g[:,None]
open('mix_raw.f32','wb').write(mix.astype(np.float32).tobytes())
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','mix_raw.f32','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'audio/mix.wav'],check=True)
print('mix ok',TL['total'])
