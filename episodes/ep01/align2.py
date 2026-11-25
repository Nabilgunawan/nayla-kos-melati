import re, json, subprocess, math
script=open("script.txt").read()
paras=[p.strip() for p in script.split("\n\n") if p.strip()]
def syl(w):
    w=re.sub(r'[^a-z]','',w.lower())
    if not w: return 0
    sp={"rice":1,"cooker":2,"hi":2,"chat":1,"grup":1}
    if w in sp: return sp[w]
    w=w.replace('ai','a').replace('au','a')
    return max(1,len(re.findall(r'[aeiou]',w)))
EXTRA={"laughs":0.9,"sighs":0.7,"awkward laugh":0.9,"gasps":0.4,"pauses":0.5}
sents=[]
for pi,p in enumerate(paras):
    parts=re.split(r'(?<=[.!?…])\s+(?=\[|[A-Z"])',p)
    for s in parts:
        tags=re.findall(r'\[([^\]]*)\]',s); clean=re.sub(r'\[[^\]]*\]','',s).strip()
        if not clean: continue
        sents.append(dict(p=pi,text=clean,tags=tags,syl=sum(syl(w) for w in clean.split()),extra=sum(EXTRA.get(t,0) for t in tags)))
out=subprocess.run("ffmpeg -hide_banner -i audio/vo16k.wav -af silencedetect=noise=-30dB:d=0.15 -f null -",shell=True,capture_output=True,text=True).stderr
st=[float(v) for v in re.findall(r'silence_start: ([\d.]+)',out)]; en=[float(v) for v in re.findall(r'silence_end: ([\d.]+)',out)]
gaps=[(a,b) for a,b in zip(st,en)]
END=84.85
if gaps and gaps[-1][1]>=END-0.05: gaps[-1]=(gaps[-1][0],END)
else: gaps.append((END,END))
start0=gaps[0][1] if gaps[0][0]<0.3 else 0.0
G=[g for g in gaps if g[0]>start0]   # boundaries
N=len(sents); M=len(G)
speech_total=sum(1 for _ in [0]); 
tot_syl=sum(s['syl'] for s in sents); tot_extra=sum(s['extra'] for s in sents)
rate=tot_syl/(END-start0-sum(b-a for a,b in G[:-1])-tot_extra)
print("sentences",N,"gaps",M,"rate syl/s",round(rate,2))
INF=1e18; dp=[[INF]*(M) for _ in range(N)]; bk=[[-1]*M for _ in range(N)]
def seg(i_prev,j):  # speech from end of gap i_prev to start of gap j
    s=start0 if i_prev<0 else G[i_prev][1]; return s, G[j][0]-s
for k in range(N):
    exp=sents[k]['syl']/rate+sents[k]['extra']
    last_in_para = (k==N-1) or sents[k+1]['p']!=sents[k]['p']
    for j in range(M):
        for i in ([-1] if k==0 else range(j)):
            if k>0 and dp[k-1][i]>=INF: continue
            s,d=seg(i,j)
            if d<=0.15: continue
            c=(math.log(d/exp))**2
            if last_in_para: c-= 0.6*min(1.0,(G[j][1]-G[j][0]))   # prefer longer gaps at scene ends
            tot=(0 if k==0 else dp[k-1][i])+c
            if tot<dp[k][j]: dp[k][j]=tot; bk[k][j]=i
j=M-1; res=[]
for k in range(N-1,-1,-1):
    i=bk[k][j]; s,d=seg(i,j); res.append((k,s,G[j][0])); j=i
res.reverse()
rows=[]
for k,s,e in res:
    S=sents[k]; exp=S['syl']/rate+S['extra']; d=e-s; flag="" if 0.7<d/exp<1.4 else "  <- periksa"
    rows.append(dict(**S,start=round(s,2),end=round(e,2)))
    print(f"P{S['p']+1}  {s:6.2f}-{e:6.2f} ({d:4.1f}s, exp {exp:4.1f}){flag}  {S['text'][:70]}")
json.dump(rows,open("align.json","w"),indent=1,ensure_ascii=False)
