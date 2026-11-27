# Waktu subtitle, potongan shot, flashback, dan kartu akhir untuk satu segmen (meniru encode.py).
# Pemakaian: python mkseg.py <timeline.json> <F0> <F1> <OUT> [mix.wav]   (fps animasi 12, frame f = waktu (f-1)/12)
import json,re,sys,subprocess
TLP,F0,F1,OUT=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]; MIX=sys.argv[5] if len(sys.argv)>5 else None
TL=json.load(open(TLP)); T=lambda f:(f-1)/12; t0=T(F0); dur=(F1-F0+1)/12
def shot(t):
    for s in TL['shots']:
        if s['start']<=t<s['end']+1e-9: return s['n']
    return TL['shots'][-1]['n']
cuts=[k for k in range(1,F1-F0+1) if shot(T(F0+k))!=shot(T(F0+k-1))]
NAMA={"ibukos":"Ibu Kos","adel":"Adel","dimas":"Dimas","pakrt":"Pak RT","pakronda":"Pak Ronda","budarmi":"Bu Darmi","detektif":"Detektif Bima","mbahkarto":"Mbah Karto","rina":"Mbak Rina","sarip":"Pak Sarip"}
subs=[]
for c in TL['clips']:
    txt=c['text'].replace('"','')
    if not txt or c['dst']+c['dur']<t0 or c['dst']>t0+dur: continue
    pre=NAMA.get(c.get('spk'),''); parts=[p.strip() for p in re.split(r'(?<=[,.!?])\s+',txt) if p.strip()]; chunks=[]; cur=''
    for p in parts:
        if len(cur)+len(p)<=44: cur=(cur+' '+p).strip()
        else:
            if cur: chunks.append(cur)
            cur=p
    if cur: chunks.append(cur)
    tot=sum(len(x) for x in chunks); t=c['dst']
    for ch in chunks:
        d=c['dur']*len(ch)/tot; subs.append({'t0':round(t-t0,3),'t1':round(t+d+0.15-t0,3),'text':(pre+': ' if pre else '')+ch}); t+=d
flash=[[max(0,s['start']-t0),s['end']-t0] for s in TL['shots'] if s.get('flashback') or s['set'].startswith('flash')] 
flash=[f for f in flash if f[1]>0 and f[0]<dur]
end={'t0':round(TL['total']-0.85-t0,3),'text':'BERSAMBUNG...?'} if F1>=int(TL['total']*12)-1 else None
json.dump({'t0':t0,'duration':dur,'cuts':cuts,'subs':subs,'flash':flash,'end':end},open(f'{OUT}/seg.json','w'),indent=1)
if MIX: subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t0),'-t',str(dur),'-i',MIX,'-ar','48000','-ac','2','-c:a','flac',f'{OUT}/audio.flac'],check=True)
print('seg.json',len(subs),'subtitle',len(cuts),'potongan')
