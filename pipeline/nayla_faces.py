from PIL import Image, ImageDraw
S=2048; OUT=1024
INK=(28,20,16,255); BROW=(122,82,48,255); RED=(190,40,40,255); TONGUE=(230,110,110,255); WHITE=(255,255,255,255)
def P(x,y): return (S/2+x*S, S/2-y*S)          # x,y in head units (-0.5..0.5), y up
def eyes(d, look=0, squint=False, wide=False):
    for sx in (-1,1):
        cx,cy=P(sx*0.155+look,0.03)
        rx,ry=(0.040*S,0.052*S) if not wide else (0.044*S,0.060*S)
        if squint: ry*=0.55
        d.ellipse([cx-rx,cy-ry,cx+rx,cy+ry],fill=INK)
        d.ellipse([cx-rx*0.15+rx*0.25,cy-ry*0.55,cx+rx*0.45+rx*0.25,cy-ry*0.05],fill=WHITE)
        # lashes on outer top
        ox=cx+sx*rx*0.75; oy=cy-ry*0.75
        d.line([ox,oy,ox+sx*0.035*S,oy-0.02*S],fill=INK,width=int(0.011*S))
        d.line([ox-sx*0.01*S,oy-0.012*S,ox+sx*0.02*S,oy-0.04*S],fill=INK,width=int(0.009*S))
def brows(d, inner=0.0, outer=0.0, y=0.155):
    for sx in (-1,1):
        a=P(sx*0.085,y+inner); m=P(sx*0.155,y+0.02+(inner+outer)/2); b=P(sx*0.225,y+outer)
        d.line([a,m,b],fill=BROW,width=int(0.018*S),joint="curve")
def arc(d,cx,cy,w,h,start,end,width,col=INK):
    x,y=P(cx,cy); d.arc([x-w*S,y-h*S,x+w*S,y+h*S],start,end,fill=col,width=int(width*S))
def make(name, fn):
    im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im); fn(d)
    im.resize((OUT,OUT),Image.LANCZOS).save(f"faces/{name}.png")
def senyum(d):
    eyes(d); brows(d); arc(d,0.02,-0.14,0.09,0.06,20,160,0.016)
    arc(d,0.115,-0.155,0.015,0.02,250,360,0.010)          # dimple tick
def tertawa(d):
    eyes(d,squint=False); brows(d,inner=0.02,outer=0.01,y=0.17)
    x0,y0=P(-0.11,-0.12); x1,y1=P(0.11,-0.27)
    d.chord([x0,y0-0.08*S,x1,y1],0,180,fill=INK)
    d.chord([x0+0.012*S,y0-0.07*S,x1-0.012*S,y1-0.012*S],0,180,fill=RED)
    d.rectangle([x0+0.02*S,y0+0.0*S,x1-0.02*S,y0+0.03*S],fill=WHITE)   # teeth
    d.ellipse([P(-0.05,-0.20)[0],P(-0.05,-0.20)[1],P(0.05,-0.255)[0],P(0.05,-0.255)[1]],fill=TONGUE)
def kaget(d):
    eyes(d,wide=True); brows(d,inner=0.04,outer=0.03,y=0.19)
    x,y=P(0,-0.19); r=0.04*S
    d.ellipse([x-r,y-r*1.25,x+r,y+r*1.25],fill=INK); d.ellipse([x-r*0.6,y-r*0.3,x+r*0.6,y+r*1.0],fill=RED)
def kesal(d):
    eyes(d); brows(d,inner=-0.04,outer=0.02,y=0.15)
    arc(d,0,-0.21,0.07,0.04,200,340,0.016)
def sedih(d):
    eyes(d); brows(d,inner=0.035,outer=-0.02,y=0.15)
    arc(d,0,-0.22,0.07,0.045,205,335,0.016)
for n,f in [("senyum",senyum),("tertawa",tertawa),("kaget",kaget),("kesal",kesal),("sedih",sedih)]: make(n,f)
# preview strip on yellow
strip=Image.new("RGB",(5*300,300),(242,197,31))
for i,n in enumerate(["senyum","tertawa","kaget","kesal","sedih"]):
    f=Image.open(f"faces/{n}.png").resize((300,300)); strip.paste(f,(i*300,0),f)
strip.save("faces_preview.png")
