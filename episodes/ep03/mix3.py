import numpy as np, json, subprocess, os
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, resample_poly
SR=48000; rng=np.random.default_rng(2)
def load(p):
    tmp="/tmp/_ld.wav"; subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",p,"-ac","1","-ar",str(SR),tmp],check=True)
    sr,x=wavfile.read(tmp); x=x.astype(np.float32); return x/(np.abs(x).max()+1e-9) if x.dtype!=np.int16 else x/32768
def norm(x,db): return x/(np.abs(x).max()+1e-9)*10**(db/20)
def fade(x,a=0.01,b=0.3):
    n=len(x); A=min(n,int(a*SR)); B=min(n,int(b*SR)); x=x.copy()
    if A: x[:A]*=np.linspace(0,1,A)
    if B: x[-B:]*=np.linspace(1,0,B)
    return x
TL=json.load(open("timeline.json")); N=int(TL["total"]*SR)+SR; mix=np.zeros(N,np.float32)
def put(x,t):
    o=int(t*SR); L=min(len(x),N-o)
    if L>0: mix[o:o+L]+=x[:L]
# ---- voices
VO={}
for c in TL["clips"]:
    if c["file"] not in VO: VO[c["file"]]=load(c["file"])
    v=VO[c["file"]]; a=int(c["src"][0]*SR); b=int(c["src"][1]*SR)+int(0.05*SR)
    g={"audio/kunti.mp3":0.75}.get(c["file"],1.0)
    put(fade(v[a:b]*g,0.008,0.04),c["dst"])
voice=mix.copy(); mix[:]=0
# ---- synth helpers
t_=lambda d:np.arange(int(d*SR))/SR
def neon(d):
    tt=t_(d); hum=(np.sin(2*np.pi*100*tt)+0.5*np.sin(2*np.pi*200*tt)+0.3*np.sin(2*np.pi*300*tt))*0.3
    buzz=0
    env=np.ones(len(tt))
    for k in range(int(d*6)):
        if rng.random()<0.45:
            o=int(rng.uniform(0,d)*SR); env[o:o+int(0.06*SR)]*=0.1
            cl=rng.standard_normal(int(0.01*SR))*0.8; mix_o=o; hum[mix_o:mix_o+len(cl)]+=cl[:max(0,min(len(cl),len(hum)-mix_o))]
    return (hum+buzz)*env
def boom(d=1.6):
    tt=t_(d); return (np.sin(2*np.pi*(55-25*tt)*tt)*np.exp(-2.2*tt)+sosfilt(butter(2,[60,2500],btype='band',fs=SR,output='sos'),rng.standard_normal(len(tt)))*np.exp(-9*tt)*0.6)
def birds(d):
    out=np.zeros(int(d*SR))
    for k in range(int(d*1.2)):
        o=int(rng.uniform(0,d-0.4)*SR); f0=rng.uniform(2800,4200); tt=t_(rng.uniform(0.08,0.18))
        ch=np.sin(2*np.pi*(f0+900*np.sin(2*np.pi*12*tt))*tt)*np.sin(np.pi*tt/tt[-1])*0.3; out[o:o+len(ch)]+=ch
    return out
KEN="/home/claude/sfxlib/cc0/"
SFXF={n:load(f"sfx/{n}.wav") for n in ["angin","tegang","ayam","jangkrik","jam","catur","halaman","kentongan"]}
SFXF["banting"]=load("/home/claude/ep02/sfx/banting.wav"); SFXF["teriak"]=load("/home/claude/ep02/sfx/teriak.wav")
KUN=load("audio/kunti.mp3")
# ---- ambience by set
segs=[]
for s_ in TL["shots"]:
    kind="malam" if s_["set"] in ("luar_malam","posronda") else ("pagi" if s_["set"] in ("kamar_pagi","luar_pagi") else "dalam")
    if segs and segs[-1][0]==kind and abs(segs[-1][2]-s_["start"])<1e-3: segs[-1][2]=s_["end"]
    else: segs.append([kind,s_["start"],s_["end"]])
for kind,a,b in segs:
    d=b-a
    if kind=="malam":
        j=SFXF["jangkrik"]; reps=int(d/(len(j)/SR))+2; xf=int(0.4*SR); out=np.zeros(0,np.float32)
        for r in range(reps):
            seg=j.copy()
            if len(out)>xf: out[-xf:]=out[-xf:]*np.linspace(1,0,xf)+seg[:xf]*np.linspace(0,1,xf); out=np.concatenate([out,seg[xf:]])
            else: out=np.concatenate([out,seg])
        put(fade(norm(out[:int(d*SR)],-38),0.4,0.4),a)
    elif kind=="pagi": put(fade(norm(birds(d),-32),0.3,0.3),a)
# ---- events
for ev in TL["sfx"]:
    tm,name,gain,md=ev[0],ev[1],ev[2],ev[3]
    if name.startswith("amb:") or name=="hening": continue
    if name.startswith("k:"): x=load(KEN+name[2:]+".wav")
    elif name=="neon": x=neon(md or 3)
    elif name=="hum": tt=t_(md or 3); x=(np.sin(2*np.pi*55*tt)+0.5*np.sin(2*np.pi*110*tt))*np.sin(np.pi*tt/tt[-1])
    elif name=="kunti_k1": x=KUN[int(0.0*SR):int(1.24*SR)]
    elif name=="jumpscare_kecil": b=boom(1.2); g=load(KEN+"glitch_002.wav"); x=b.copy(); x[:len(g)]+=g[:len(x)]*0.6
    elif name=="klotak": x=load(KEN+"drop_002.wav")
    else: x=SFXF[name]
    if name=="tegang" and tm<80: pass
    if md: x=x[:int(md*SR)]
    put(fade(norm(x,gain),0.01,0.25 if md else 0.05),tm)
# ---- horror trailer music bed (ep3)
tr=load("sfx/trailer.wav"); TRS=lambda a,b: tr[int(a*SR):int(b*SR)].copy()
def xcat(parts,xf=0.8):
    out=parts[0]; X=int(xf*SR)
    for p in parts[1:]: out=np.concatenate([out[:-X], out[-X:]*np.linspace(1,0,X)+p[:X]*np.linspace(0,1,X), p[X:]])
    return out
SHT={x["cam"]:x for x in TL["shots"]}; CLP={c["id"]:c for c in TL["clips"]}
music=np.zeros(N,np.float32)
def mput(x,t,g=1.0):
    o=int(t*SR); L=min(len(x),N-o); music[o:o+L]+=x[:L]*g
# soft under the confession + flashback
a0=SHT["s5"]["start"]; a1=SHT["s9"]["start"]; mput(fade(xcat([TRS(0,8.5),TRS(0,8.5),TRS(0,8.5)])[:int((a1-a0)*SR)],1.5,1.5),a0,0.55)
# pos ronda: steady bed, intense part lands on the book reveal, silence on the page turn, hit on the name
p0=SHT["s14"]["start"]; turn=SHT["s23"]["start"]; reveal=CLP["N8"]["dst"]
peak=turn-8.0; L1=peak-p0; parts=[]; tot=0
while tot<L1+1: parts.append(TRS(17,31)); tot+=13.2
bed=xcat(parts)[:int(L1*SR)]; bed=xcat([bed,TRS(0,16)]); mput(fade(bed,1.5,0.4),p0)
music[int((turn+0.1)*SR):int(reveal*SR)]=0
mput(fade(TRS(24,31),0.05,1.0)[:int((SHT["s28"]["start"]-reveal)*SR)],reveal,1.0)
# ending
e0=SHT["s29"]["start"]; black=TL["total"]-0.85; mput(fade(TRS(25,25+(black-e0)),0.4,0.05),e0); music[int(black*SR):]=0
mix+=norm(music,-9)
sfx=mix.copy()
# duck SFX/ambience under voice
env=np.convolve(np.abs(voice),np.ones(int(0.25*SR))/int(0.25*SR),'same'); duck=1-0.45*np.clip(env/ (env.max()*0.15+1e-9),0,1)
final=voice*1.0+sfx*duck
wavfile.write("audio/mix_raw.wav",SR,np.clip(final,-1,1).astype(np.float32)); print("mixed")
