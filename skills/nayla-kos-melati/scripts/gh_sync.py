"""Upload files/folders to a GitHub repo via the REST Contents API (no git needed).
Usage:
  python gh_sync.py --repo USER/REPO --token TOKEN --src LOCAL_PATH --dst REPO_PATH [--msg "pesan commit"]
- LOCAL_PATH can be a file or a folder (uploaded recursively, same structure under REPO_PATH).
- Existing files are updated (their sha is fetched first); unchanged files are skipped.
- Practical limit per file is a few tens of MB; put big episode zips in Releases manually.
Never print or store the token."""
import argparse, base64, hashlib, json, os, sys, time, urllib.request, urllib.error
def api(method,url,token,data=None):
    for attempt in range(6):
        st,res,hdr=_api(method,url,token,data)
        if st in (403,429) or st>=500:
            wait=int(hdr.get("Retry-After") or 60)*(1 if attempt<2 else 2); print(f"  tunggu {wait}s (status {st})",flush=True); time.sleep(wait); continue
        return st,res
    return st,res
def _api(method,url,token,data=None):
    req=urllib.request.Request(url,method=method,data=None if data is None else json.dumps(data).encode(),
        headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","User-Agent":"nayla-sync","X-GitHub-Api-Version":"2022-11-28"})
    try:
        with urllib.request.urlopen(req,timeout=180) as r: return r.status, json.loads(r.read() or b"{}"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), dict(e.headers)
    except Exception as e:
        return 599, {"message":str(e)}, {}
def git_blob_sha(raw): return hashlib.sha1(b"blob %d\0"%len(raw)+raw).hexdigest()
def put(repo,token,local,remote,msg):
    raw=open(local,"rb").read(); url=f"https://api.github.com/repos/{repo}/contents/{remote}"
    st,info=api("GET",url,token); sha=info.get("sha") if st==200 else None
    if sha and sha==git_blob_sha(raw): return "skip"
    body={"message":msg,"content":base64.b64encode(raw).decode()}
    if sha: body["sha"]=sha
    st,res=api("PUT",url,token,body); time.sleep(1.0)
    return "ok" if st in (200,201) else f"GAGAL {st}: {res.get('message')}"
if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("--repo",required=True); a.add_argument("--token",default=os.environ.get("GH_TOKEN"))
    a.add_argument("--src",required=True); a.add_argument("--dst",default=""); a.add_argument("--msg",default="Sinkronisasi aset Nayla")
    o=a.parse_args()
    if not o.token: sys.exit("Butuh token (--token atau env GH_TOKEN)")
    files=[]
    if os.path.isdir(o.src):
        for root,_,fs in os.walk(o.src):
            for f in fs: p=os.path.join(root,f); files.append((p,os.path.join(o.dst,os.path.relpath(p,o.src)).replace("\\","/")))
    else: files=[(o.src,(o.dst or os.path.basename(o.src)).replace("\\","/"))]
    counts={}
    for l,r in sorted(files):
        res=put(o.repo,o.token,l,r,o.msg); counts[res[:4]]=counts.get(res[:4],0)+1
        print(r,res,flush=True)
    print("Selesai:",counts)
