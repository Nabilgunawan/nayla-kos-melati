import re, json, subprocess, math, sys
wav,scr,END=sys.argv[1],sys.argv[2],float(sys.argv[3])
paras=[p.strip() for p in open(scr).read().split("\n\n") if p.strip()]
def syl(w):
    w=re.sub(r'[^a-z]','',w.lower()); 
    if not w: return 0
    w=w.replace('ai','a').replace('au','a'); return max(1,len(re.findall(r'[aeiou]',w)))
EX={"laughs":0.9,"sighs":0.7,"pauses":0.5}
S=[]
for pi,p in enumerate(paras):
    for s in re.split(r'(?<=[.!?])\s+(?=\[|[A-Z"])',p):
        tags=re.findall(r'\[([^\]]*)\]',s); cl=re.sub(r'\[[^\]]*\]','',s).strip()
        if cl: S.append(dict(p=pi,syl=sum(syl(w) for w in cl.split()),extra=sum(EX.get(t,0) for t in tags)))
out=subprocess.run(f"ffmpeg -hide_banner -i {wav} -af silencedetect=noise=-30dB:d=0.15 -f null -",shell=True,capture_output=True,text=True).stderr
st=[float(v) for v in re.findall(r'silence_start: ([\d.]+)',out)]; en=[float(v) for v in re.findall(r'silence_end: ([\d.]+)',out)]
G=list(zip(st,en))
start0=G[0][1] if G and G[0][0]<0.05 else 0.0
G=[g for g in G if g[0]>start0+0.05]
if not G or G[-1][1]<END-0.05: G.append((END,END))
N=len(S); M=len(G); tot=sum(s['syl'] for s in S); ex=sum(s['extra'] for s in S)
rate=tot/max(1,(END-start0-sum(b-a for a,b in G[:-1])-ex))
INF=1e18; dp=[[INF]*M for _ in range(N)]; bk=[[-1]*M for _ in range(N)]
def seg(i,j): s=start0 if i<0 else G[i][1]; return s,G[j][0]-s
for k in range(N):
    e=S[k]['syl']/rate+S[k]['extra']; last=(k==N-1) or S[k+1]['p']!=S[k]['p']
    for j in range(M):
        for i in ([-1] if k==0 else range(j)):
            if k>0 and dp[k-1][i]>=INF: continue
            s,d=seg(i,j)
            if d<=0.15: continue
            c=(math.log(d/e))**2 - (0.8*min(1,G[j][1]-G[j][0]) if last else 0)
            v=(0 if k==0 else dp[k-1][i])+c
            if v<dp[k][j]: dp[k][j]=v; bk[k][j]=i
j=M-1; res=[]
for k in range(N-1,-1,-1):
    i=bk[k][j]; s,d=seg(i,j); res.append((S[k]['p'],s,G[j][0])); j=i
res.reverse(); P={}
for p,s,e in res: P.setdefault(p,[s,e]); P[p][1]=e
print(json.dumps({k:[round(v[0],2),round(v[1],2)] for k,v in P.items()}))
