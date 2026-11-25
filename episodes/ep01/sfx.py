import numpy as np, json, subprocess
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; rng=np.random.default_rng(4)
def t(d): return np.arange(int(d*SR))/SR
def env(n,a=0.005,r=0.2):
    e=np.ones(n); A=int(a*SR); R=int(r*SR)
    if A: e[:A]=np.linspace(0,1,A)
    if R and R<n: e[-R:]*=np.exp(-np.linspace(0,6,R))
    return e
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,hi],btype='band',fs=SR,output='sos'),x)
def lp(x,f): return sosfilt(butter(2,f,btype='low',fs=SR,output='sos'),x)
def tone(f,d,dec=6,h=(1,)):
    tt=t(d); y=sum(a*np.sin(2*np.pi*f*(k+1)*tt) for k,a in enumerate(h)); return y*np.exp(-dec*tt)
def noise(d): return rng.standard_normal(int(d*SR))
FX={}
FX["rec_beep"]=np.concatenate([tone(1320,0.12,3)*env(int(0.12*SR),0.003,0.03),np.zeros(int(0.05*SR)),tone(1760,0.15,3)*env(int(0.15*SR),0.003,0.05)])*0.5
w=noise(0.6); sweep=np.linspace(0,1,len(w)); FX["whoosh"]=bp(w,300,3000)*np.sin(np.pi*sweep)**2*0.6
def step():
    d=0.09; return (bp(noise(d),1500,6000)*np.exp(-60*t(d))*0.5+tone(900,d,50)*0.4)
st=np.zeros(int(1.6*SR))
for i in range(5): s=step()*rng.uniform(0.7,1.0); o=int(i*0.3*SR); st[o:o+len(s)]+=s
FX["steps"]=st
p=t(0.12); FX["pop"]=np.sin(2*np.pi*(300+2200*p)*p)*np.exp(-30*p)*0.7
FX["tada"]=np.concatenate([tone(784,0.12,4,(1,.4)),tone(1046,0.45,3,(1,.4,.2))])*0.45
def ting(f,d=1.4): return tone(f,d,3,(1,0.5,0.25,0.12))*0.5+tone(f*2.76,d,8)*0.15
FX["ting_soft"]=ting(1568)*0.5; FX["ting"]=ting(1975)
n=noise(3.0); FX["fan_loud"]=(bp(n,80,600)*(1+0.6*np.sin(2*np.pi*14*t(3.0))))*0.35*env(len(n),0.2,0.6)
d=0.9; FX["door"]=np.concatenate([bp(noise(0.5),200,1200)*np.sin(np.pi*np.linspace(0,1,int(0.5*SR)))*0.3+tone(330,0.5,2,(1,.5))*0.1,
      (tone(90,0.4,12)+bp(noise(0.4),60,400)*np.exp(-15*t(0.4)))*0.8])
def amb(d,lo,hi,g):
    x=bp(noise(d),lo,hi)*g; return x*env(len(x),0.8,0.8)
c=amb(10,300,2500,0.08)
for i in range(14):
    o=int(rng.uniform(0,9.4)*SR); ch=tone(rng.uniform(2800,4200),0.12,15)*0.08; c[o:o+len(ch)]+=ch
FX["campus_amb"]=c
sc=t(0.55); FX["scratch"]=bp(noise(0.55),400,4000)*np.abs(np.sin(2*np.pi*3.5*sc))*np.exp(-2*sc)*0.8+np.sin(2*np.pi*(700-500*sc)*sc)*0.25*np.exp(-3*sc)
sp=np.zeros(int(1.2*SR))
for i,f in enumerate([1568,2093,2637,3136,4186]): s=tone(f,0.6,7)*0.25; o=int(i*0.07*SR); sp[o:o+len(s)]+=s
ch=t(1.0); sp[:len(ch)]+= (np.sin(2*np.pi*523*ch)+np.sin(2*np.pi*659*ch)+np.sin(2*np.pi*784*ch))*0.07*np.sin(np.pi*ch)
FX["sparkle"]=sp
nt=np.zeros(int(1.6*SR))
for i in range(4): s=np.concatenate([tone(1047,0.09,10),tone(1568,0.18,10)])*0.45; o=int(i*0.35*SR); nt[o:o+len(s)]+=s
FX["notif3"]=nt
ca=amb(36,60,900,0.12)
for i in range(6):
    o=int(rng.uniform(1,34)*SR); hn=(np.sign(np.sin(2*np.pi*420*t(0.35)))*0.5+np.sign(np.sin(2*np.pi*530*t(0.35)))*0.5)*0.05*env(int(0.35*SR),0.01,0.08)
    ca[o:o+len(hn)]+=lp(hn,2500)
FX["city_amb"]=ca
m=t(2.4); FX["moto"]=lp(np.sign(np.sin(2*np.pi*(55+25*np.sin(np.pi*m/2.4))*m)),1500)*0.25*np.sin(np.pi*m/2.4)**2
FX["kaching"]=np.concatenate([bp(noise(0.08),2000,8000)*0.4*np.exp(-40*t(0.08)),ting(2637,0.9)*0.9])
FX["traffic"]=amb(3.5,80,1200,0.3)
cr=np.zeros(int(32*SR)); tt=t(0.06)
chirp=np.sin(2*np.pi*4300*tt)*np.sin(np.pi*tt/0.06)*0.08
for k in range(int(32/0.45)):
    if rng.random()<0.8:
        o=int((k*0.45+rng.uniform(0,0.05))*SR)
        for j in range(3):
            oo=o+int(j*0.07*SR)
            if oo+len(chirp)<len(cr): cr[oo:oo+len(chirp)]+=chirp
FX["crickets"]=cr
ty=np.zeros(int(3.0*SR))
for i in range(22): s=bp(noise(0.03),1500,7000)*np.exp(-120*t(0.03))*0.4; o=int(rng.uniform(0,2.9)*SR); ty[o:o+len(s)]+=s
FX["typing"]=ty
h=t(1.2); FX["hit"]=(np.sin(2*np.pi*(120-60*h)*h)*np.exp(-3*h)*0.9+bp(noise(1.2),100,3000)*np.exp(-12*h)*0.3+np.sin(2*np.pi*233*h)*np.exp(-2*h)*0.2)
for k,v in FX.items(): FX[k]=v.astype(np.float32)
# ---------------- MIX ----------------
TL=json.load(open("timeline.json")); N=int(TL["total"]*SR)+SR//2; mix=np.zeros(N,np.float32)
sr,vo=wavfile.read("audio/vo.wav"); vo=vo.astype(np.float32)/32768
if sr!=SR:
    from scipy.signal import resample_poly; vo=resample_poly(vo,SR,sr).astype(np.float32)
for c in TL["clips"]:
    a=int((c["src"][0])*SR); b=int(c["src"][1]*SR)+int(0.06*SR); seg=vo[a:b].copy()
    fl=int(0.008*SR); seg[:fl]*=np.linspace(0,1,fl); seg[-fl:]*=np.linspace(1,0,fl)
    o=int(c["dst"]*SR); mix[o:o+len(seg)]+=seg*1.0
sfxtrack=np.zeros(N,np.float32)
for ev in TL["sfx"]:
    tm,name,gain=ev[0],ev[1],ev[2]; x=FX[name]
    if len(ev)>3: x=x[:int(ev[3]*SR)]
    x=x/ (np.max(np.abs(x))+1e-9) * 10**(gain/20)
    o=int(tm*SR); L=min(len(x),N-o); sfxtrack[o:o+L]+=x[:L]
mix=mix+sfxtrack*0.9
wavfile.write("audio/mix_raw.wav",SR,np.clip(mix,-1,1))
print("mixed",len(mix)/SR)
