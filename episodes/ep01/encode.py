# Menggabungkan frame + audio + subtitle menjadi MP4 1080x1920. Jalankan setelah render selesai.
import bpy, os, json, glob
def png_ok(p):
    try:
        if os.path.getsize(p)<60: return False
        with open(p,"rb") as f:
            if f.read(8)!=b"\x89PNG\r\n\x1a\n": return False
            f.seek(-12,2); return b"IEND" in f.read(12)
    except OSError: return False

base=bpy.path.abspath("//"); TL=json.load(open(os.path.join(base,"timeline.json"),encoding="utf-8"))
frames=sorted(glob.glob(os.path.join(base,"frames","*.png")))
src=bpy.data.scenes[0]; NF=src.frame_end
rusak=[f for f in frames if not png_ok(f)]
for f in rusak: os.remove(f)
if rusak:
    raise SystemExit(f"\n{len(rusak)} frame rusak sudah dihapus: "+", ".join(os.path.basename(x) for x in rusak[:20])+"\nJalankan render.py lagi (perintah yang sama), lalu encode.py.\n")
frames=[f for f in frames if f not in rusak]
missing=NF-len(frames)
if missing>0: raise SystemExit(f"Masih ada {missing} frame yang belum dirender. Jalankan render.py lagi.")
sc=bpy.data.scenes.new("ENCODE")
sc.render.fps=24; sc.render.resolution_x=1080; sc.render.resolution_y=1920; sc.frame_start=1; sc.frame_end=NF*2
se=sc.sequence_editor_create()
strips=se.strips if hasattr(se,"strips") else se.sequences
im=strips.new_image("frames",frames[0],1,1)
FONT=bpy.data.fonts.load(os.path.join(base,"fonts","DejaVuSans-Bold.ttf"))
_i=bpy.data.images.load(frames[0]); _w=_i.size[0]
if _w and _w!=1080: im.transform.scale_x=im.transform.scale_y=1080/_w
im.elements.append(os.path.basename(frames[0]))          # 12 fps -> 24 fps: setiap frame tampil dua kali
for f in frames[1:]:
    im.elements.append(os.path.basename(f)); im.elements.append(os.path.basename(f))
snd=strips.new_sound("audio",os.path.join(base,"audio","mix.wav"),2,1)
def text(t0,t1,txt,y,size,ch):
    s=strips.new_effect(f"sub{ch}_{int(t0*100)}",'TEXT',ch,frame_start=int(t0*24)+1,length=max(2,int((t1-t0)*24)))
    s.text=txt; s.font=FONT; s.font_size=size; s.location=(0.5,y); s.use_outline=True; s.outline_width=0.12; s.color=(1,1,1,1)
    s.anchor_x='CENTER'; s.anchor_y='CENTER'; s.wrap_width=0.86
    return s
import re
for c in TL["clips"]:
    txt=c["text"].replace('"',''); t0=c["dst"]; dur=c["dur"]
    parts=[p.strip() for p in re.split(r'(?<=[,.!?])\s+',txt) if p.strip()]
    chunks=[]; cur=""
    for p in parts:
        if len(cur)+len(p)<=44: cur=(cur+" "+p).strip()
        else:
            if cur: chunks.append(cur)
            cur=p
    if cur: chunks.append(cur)
    tot=sum(len(x) for x in chunks); t=t0
    for ch in chunks:
        d=dur*len(ch)/tot; text(t,t+d+0.15,ch,0.30,68,3); t+=d
u4=[c for c in TL["clips"] if c["id"]=="u4"][0]; text(u4["dst"],u4["dst"]+4.0,"NAYLA  ·  20  ·  Hubungan Internasional",0.80,48,4)
u34=[c for c in TL["clips"] if c["id"]=="u34"][0]; text(u34["dst"]+2.0,u34["dst"]+u34["dur"]+0.6,"FOLLOW",0.62,110,4)
r=sc.render
if hasattr(r.image_settings,'media_type'): r.image_settings.media_type='VIDEO'
r.image_settings.file_format='FFMPEG'; r.ffmpeg.format='MPEG4'; r.ffmpeg.codec='H264'; r.ffmpeg.constant_rate_factor='HIGH'
r.ffmpeg.audio_codec='AAC'; r.ffmpeg.audio_bitrate=192; r.ffmpeg.audio_channels='STEREO'; r.ffmpeg.audio_mixrate=48000
r.filepath=os.path.join(base,"Nayla_Episode1.mp4"); r.use_file_extension=False
bpy.ops.render.render(animation=True, scene=sc.name)
print("\nSELESAI: Nayla_Episode1.mp4\n")
