import numpy as np, json, subprocess
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; rng=np.random.default_rng(4)
def load(p):
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",p,"-ac","1","-ar",str(SR),"/tmp/_ld4.wav"],check=True)
    sr,x=wavfile.read("/tmp/_ld4.wav"); x=x.astype(np.float32); return x/32768 if np.abs(x).max()>2 else x
def norm(x,db): return x/(np.abs(x).max()+1e-9)*10**(db/20)
def fade(x,a=0.01,b=0.3):
    x=x.copy(); n=len(x); A=min(n,int(a*SR)); B=min(n,int(b*SR))
    if A: x[:A]*=np.linspace(0,1,A)
    if B: x[-B:]*=np.linspace(1,0,B)
    return x
TL=json.load(open("timeline.json")); N=int(TL["total"]*SR)+SR
voice=np.zeros(N,np.float32); fx=np.zeros(N,np.float32); music=np.zeros(N,np.float32)
def put(buf,x,t,g=1.0):
    o=int(t*SR); L=min(len(x),N-o)
    if L>0: buf[o:o+L]+=x[:L]*g
VO={}
for c in TL["clips"]:
    if c["file"] not in VO: VO[c["file"]]=load(c["file"])
    v=VO[c["file"]]; a=int(c["src"][0]*SR); b=int(c["src"][1]*SR)+int(0.05*SR)
    put(voice,fade(v[a:b],0.008,0.04),c["dst"],0.75 if "kunti" in c["file"] else 1.0)
t_=lambda d:np.arange(int(d*SR))/SR
def boom(d=1.3): tt=t_(d); return np.sin(2*np.pi*(55-25*tt)*tt)*np.exp(-2.4*tt)+sosfilt(butter(2,[60,2500],btype='band',fs=SR,output='sos'),rng.standard_normal(len(tt)))*np.exp(-9*tt)*0.6
def hum(d): tt=t_(d); return (np.sin(2*np.pi*55*tt)+0.5*np.sin(2*np.pi*110*tt))*np.sin(np.pi*tt/tt[-1])
def heart(d):
    out=np.zeros(int(d*SR)); tt=t_(0.12); th=np.sin(2*np.pi*50*tt)*np.exp(-30*tt)
    for k in range(int(d/0.85)):
        for off in (0,0.22):
            o=int((k*0.85+off)*SR); out[o:o+len(th)]+=th[:max(0,min(len(th),len(out)-o))]*(1 if off==0 else 0.7)
    return out
def crowd(d):
    x=sosfilt(butter(2,[250,2500],btype='band',fs=SR,output='sos'),rng.standard_normal(int(d*SR)))*0.3
    env=np.convolve(np.abs(rng.standard_normal(int(d*SR))),np.ones(int(0.25*SR))/int(0.25*SR),'same'); return x*(0.5+env)
def birds(d):
    out=np.zeros(int(d*SR))
    for k in range(int(d*1.2)):
        o=int(rng.uniform(0,max(0.1,d-0.4))*SR); f0=rng.uniform(2800,4200); tt=t_(rng.uniform(0.08,0.18))
        ch=np.sin(2*np.pi*(f0+900*np.sin(2*np.pi*12*tt))*tt)*np.sin(np.pi*tt/tt[-1])*0.3; out[o:o+len(ch)]+=ch[:len(out)-o]
    return out
KEN="/home/claude/sfxlib/cc0/"
SF={n:load(f"sfx/{n}.wav") for n in ["angin","tegang","jangkrik","halaman","kentongan","ketuk","banting","daun","burunghantu","pabrik","sungai","trailer"]}
def loop(x,d,xf=0.4):
    X=int(xf*SR); out=x.copy()
    while len(out)<int(d*SR): out=np.concatenate([out[:-X],out[-X:]*np.linspace(1,0,X)+x[:X]*np.linspace(0,1,X),x[X:]])
    return out[:int(d*SR)]
NIGHT={"posronda","fb_malam","fb_sawah","fb_sungai_malam","gubuk"}; DAY={"fb_pagi","fb_siang","warung","sungai_siang","pasar","fb_sore"}
segs=[]
for s in TL["shots"]:
    k="malam" if s["set"] in NIGHT else ("siang" if s["set"] in DAY else "dalam")
    if segs and segs[-1][0]==k: segs[-1][2]=s["end"]
    else: segs.append([k,s["start"],s["end"]])
for k,a,b in segs:
    if k=="malam": put(fx,fade(norm(loop(SF["jangkrik"],b-a),-38),0.4,0.4),a)
    elif k=="siang": put(fx,fade(norm(birds(b-a),-32),0.3,0.3),a)
for tm,name,gain,md in TL["sfx"]:
    if name.startswith("k:"): x=load(KEN+name[2:]+".wav")
    elif name=="hum": x=hum(md or 3)
    elif name=="hit": x=boom()
    elif name=="pasar_synth": x=crowd(md or 5)
    elif name=="jantung": x=heart(md or 4)
    else: x=SF[name]
    if md: x=loop(x,md) if len(x)<int(md*SR) else x[:int(md*SR)]
    put(fx,fade(norm(x,gain),0.02,0.3 if md else 0.05),tm)
# music bed
tr=SF["trailer"]; TR=lambda a,b: tr[int(a*SR):int(b*SR)].copy()
SH={s["cam"]:s for s in TL["shots"]}
def bed(a,b,g,src=(17,31)):
    put(music,fade(loop(TR(*src),b-a,0.8),1.2,1.2),a,g)
bed(0,SH["s7"]["start"],0.35,(0,8.5))
bed(SH["s9"]["start"],SH["s11"]["start"]-0.3,0.7)
put(music,fade(TR(8,16),0.05,1.0)[:int((SH["s13"]["start"]-SH["s11"]["start"])*SR)],SH["s11"]["start"],1.0)
bed(SH["s13"]["start"],SH["s16"]["start"],0.6)
bed(SH["s16"]["start"],SH["s32"]["end"],0.35)
put(music,fade(TR(8,16),0.4,0.6),SH["s32"]["start"]-1.5,0.7)
bed(SH["s33"]["start"],SH["s38"]["start"],0.5)
m2=[c for c in TL["clips"] if c["id"]=="M2"][0]; peak0=m2["dst"]-6.0
bed(SH["s38"]["start"],peak0,0.6); put(music,fade(TR(2,16),0.3,1.0),peak0,1.0)
put(music,fade(TR(24,31),0.6,0.4)[:int((SH["s44"]["start"]+1.2-SH["s42"]["start"])*SR)],SH["s42"]["start"],0.8)
music[int((SH["s44"]["start"]+1.2)*SR):]=0
env=np.convolve(np.abs(voice),np.ones(int(0.25*SR))/int(0.25*SR),'same'); duck=1-0.5*np.clip(env/(env.max()*0.15+1e-9),0,1)
final=voice+(fx+norm(music,-9))*duck
wavfile.write("audio/mix_raw.wav",SR,np.clip(final,-1,1).astype(np.float32)); print("mixed",round(len(final)/SR,1))
