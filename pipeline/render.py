# Render semua frame Nayla Episode 1. Bisa dihentikan dan dilanjutkan kapan saja.
# Pemakaian (PowerShell):  & $B -b ep01.blend -P render.py -- <mode>
#   GPU (EEVEE):  tesgpu [nomor varian...] -> tes varian GPU, misalnya: tesgpu 4 5 6
#                 gpu N          -> render penuh dengan varian N (1-9)
#   CPU (Cycles): tescpu / cpu   -> cadangan tanpa GPU
#   Lama:         tes / final / cepat (EEVEE bawaan)
import bpy, os, glob, sys, time
def png_ok(p):
    try:
        if os.path.getsize(p)<60: return False
        with open(p,"rb") as f:
            if f.read(8)!=b"\x89PNG\r\n\x1a\n": return False
            f.seek(-12,2); return b"IEND" in f.read(12)
    except OSError: return False

sc=bpy.context.scene
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
mode=args[0] if args else "final"
var=int(args[1]) if len(args)>1 and args[1].isdigit() else 1
LIGHTS=[o for o in bpy.data.objects if o.type=='LIGHT']
SHADOW_ON={o.name:o.data.use_shadow for o in LIGHTS}
# varian: (memori bayangan MB, skala resolusi bayangan); 3 = tanpa bayangan
VARIAN={1:('64',1.0),2:('16',0.5),4:('128',1.0),5:('256',1.0),6:('128',0.5),7:('64',0.5),8:('64',1.0),9:('32',0.5)}
SUN_ONLY={7,8,9}   # hanya matahari yang membuat bayangan (hemat memori GPU)
def gpu_variant(v):
    e=sc.eevee; sc.render.engine='BLENDER_EEVEE'; e.taa_render_samples=24
    if hasattr(e,"use_raytracing"): e.use_raytracing=False
    cfg=VARIAN.get(v)
    if cfg: e.use_shadows=True; e.shadow_pool_size=cfg[0]; e.shadow_resolution_scale=cfg[1]
    else:   e.use_shadows=False
    for o in LIGHTS:
        if not cfg: o.data.use_shadow=False
        elif v in SUN_ONLY: o.data.use_shadow = (o.data.type=='SUN')
        else: o.data.use_shadow = SHADOW_ON[o.name]
def cpu_setup():
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
    sc.cycles.use_adaptive_sampling=True; sc.cycles.max_bounces=4
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
def outdir(name):
    d=bpy.path.abspath(f"//{name}/"); os.makedirs(d,exist_ok=True)
    rusak=[f for f in glob.glob(os.path.join(d,"*.png")) if not png_ok(f)]
    for f in rusak: os.remove(f)                      # frame kosong/terpotong dirender ulang
    if rusak: print(f"\n{len(rusak)} frame rusak dihapus dan akan dirender ulang: "+", ".join(os.path.basename(x) for x in sorted(rusak)[:20])+("..." if len(rusak)>20 else "")+"\n")
    return d
def still(path):
    sc.render.filepath=path; t=time.time(); bpy.ops.render.render(write_still=True); return time.time()-t
def animate(d):
    sc.render.filepath=os.path.join(d,""); sc.render.use_overwrite=False; sc.render.use_placeholder=True
    bpy.ops.render.render(animation=True); print("\nRENDER SELESAI. Lanjutkan dengan encode.py\n")
if mode=="tesgpu":
    d=outdir("frames_tes"); lines=[]
    pilih=[int(a) for a in args[1:] if a.isdigit()] or [1,2,3]
    for v in pilih:
        gpu_variant(v); ts=[]
        for f in (62,1132):
            sc.frame_set(f); ts.append(still(os.path.join(d,f"varian{v}_{f:04d}.png")))
        lines.append(f"Varian {v} {VARIAN.get(v,('tanpa bayangan',))[0]}{' MB' if v in VARIAN else ''}: {ts[-1]:.1f} detik per frame -> render penuh sekitar {ts[-1]*sc.frame_end/3600:.1f} jam")
    msg="\n".join(lines); open(os.path.join(d,"hasil_tes_gpu.txt"),"w").write(msg)
    print("\nTES GPU SELESAI: lihat folder frames_tes\n"+msg+"\n")
elif mode=="gpu":
    gpu_variant(var); print(f"Render GPU varian {var}"); animate(outdir("frames"))
elif mode in ("tes","tescpu"):
    cpu_setup() if mode=="tescpu" else gpu_variant(0)
    if mode=="tes": sc.eevee.use_shadows=True
    d=outdir("frames_tes"); ts=[]
    for f in (62,426,841,1132):
        sc.frame_set(f); ts.append(still(os.path.join(d,f"tes_{f:04d}.png")))
    avg=sum(ts[1:])/3; msg=f"Rata-rata {avg:.1f} detik per frame. Perkiraan render penuh ({sc.frame_end} frame): {avg*sc.frame_end/3600:.1f} jam."
    open(os.path.join(d,"hasil_tes.txt"),"w").write(msg); print("\nTES SELESAI: lihat folder frames_tes\n"+msg+"\n")
elif mode=="cpu":
    cpu_setup(); animate(outdir("frames"))
else:
    sc.render.engine='BLENDER_EEVEE'; sc.eevee.taa_render_samples=12 if mode=="cepat" else 24; animate(outdir("frames"))
