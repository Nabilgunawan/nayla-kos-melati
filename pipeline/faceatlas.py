from PIL import Image, ImageDraw
T=1024; SS=2; S=T*SS
INK=(28,20,16,255); BROW=(122,82,48,255); RED=(178,38,38,255); TONGUE=(232,112,112,255); WHITE=(255,255,255,255); BLUSH=(255,120,90,110)
def P(x,y): return (S/2+x*S, S/2-y*S)
def W(v): return int(v*S)
def eye(d,sx,mode="open",look=(0,0),sc=1.0):
    cx,cy=P(sx*0.155,0.03); rx,ry=0.040*S*sc,0.052*S*sc
    if mode in("open","half","wide"):
        if mode=="wide": rx,ry=rx*1.12,ry*1.18
        d.ellipse([cx-rx,cy-ry,cx+rx,cy+ry],fill=INK)
        hx,hy=cx+rx*0.25+look[0]*S,cy-ry*0.35-look[1]*S
        d.ellipse([hx-rx*0.32,hy-ry*0.25,hx+rx*0.32,hy+ry*0.25],fill=WHITE)
        if mode=="half":   # lid: cover top half with skin-coloured? use transparent cut: draw lid line + erase top
            d.rectangle([cx-rx*1.3,cy-ry*1.3,cx+rx*1.3,cy-ry*0.05],fill=(0,0,0,0))
            d.line([cx-rx*1.15,cy-ry*0.05,cx+rx*1.15,cy-ry*0.05],fill=INK,width=W(0.012))
        ox=cx+sx*rx*0.75; oy=cy-ry*(0.75 if mode!="half" else 0.05)
        d.line([ox,oy,ox+sx*0.035*S,oy-0.02*S],fill=INK,width=W(0.011))
    elif mode=="closed":
        d.arc([cx-rx,cy-ry*0.5,cx+rx,cy+ry*0.9],200,340,fill=INK,width=W(0.013))
        d.line([cx+sx*rx*0.9,cy,cx+sx*(rx+0.03*S),cy-0.015*S],fill=INK,width=W(0.010))
    elif mode=="happy":
        d.arc([cx-rx,cy-ry*0.6,cx+rx,cy+ry*1.2],195,345,fill=INK,width=W(0.016))
    elif mode=="squint":
        d.line([cx-rx,cy-ry*0.2,cx+rx*0.2,cy,cx-rx,cy+ry*0.25],fill=INK,width=W(0.014),joint="curve")
def eyes(d,mode="open",look=(0,0),l=None,r=None):
    eye(d,-1,l or mode,look); eye(d,1,r or mode,look)
def brows(d,inner=0.0,outer=0.0,y=0.155,only=None,lift=None):
    for sx in (-1,1):
        if only and sx!=only: continue
        i,o=inner,outer
        if lift and sx==lift: i+=0.045; o+=0.05
        a=P(sx*0.085,y+i); m=P(sx*0.155,y+0.02+(i+o)/2); b=P(sx*0.225,y+o)
        d.line([a,m,b],fill=BROW,width=W(0.018),joint="curve")
def blush(d):
    for sx in(-1,1):
        x,y=P(sx*0.2,-0.08); d.ellipse([x-0.05*S,y-0.025*S,x+0.05*S,y+0.025*S],fill=BLUSH)
EYES=[
 lambda d:(eyes(d),brows(d)),                                  #0 normal
 lambda d:(eyes(d,"closed"),brows(d)),                         #1 blink
 lambda d:(eyes(d,"wide"),brows(d,0.04,0.03,0.19)),            #2 wide/kaget
 lambda d:(eyes(d,"happy"),brows(d,0.02,0.01,0.17)),           #3 happy
 lambda d:(eyes(d,"half"),brows(d,-0.005,-0.005,0.14)),        #4 deadpan
 lambda d:(eyes(d),brows(d,-0.04,0.02,0.15)),                  #5 kesal
 lambda d:(eyes(d,look=(0,-0.01)),brows(d,0.035,-0.02,0.15)),  #6 sedih/pasrah
 lambda d:(eyes(d,"half"),brows(d,-0.01,0.02,0.16)),           #7 bangga
 lambda d:(eyes(d),brows(d,lift=1)),                           #8 jahil (alis naik)
 lambda d:(eyes(d,l="squint",r="wide"),brows(d,-0.02,0.0,0.15,only=-1),brows(d,0.04,0.04,0.17,only=1)), #9 bingung lucu
 lambda d:(eyes(d,look=(0.012,0.022)),brows(d,0.02,0.02,0.17)),#10 merenung (lihat atas)
 lambda d:(eyes(d,"wide"),brows(d,0.06,-0.01,0.19)),           #11 panik
 lambda d:(eyes(d,"happy"),brows(d,0.01,0.0,0.155)),           #12 lembut
 lambda d:(eyes(d,look=(-0.02,0)),brows(d)),                   #13 lirik kiri
 lambda d:(eyes(d,look=(0.02,0)),brows(d)),                    #14 lirik kanan
 lambda d:(eyes(d,"happy"),brows(d,0.02,0.0,0.16),blush(d)),   #15 malu
]
def arc(d,cx,cy,w,h,a0,a1,wd=0.016,col=INK):
    x,y=P(cx,cy); d.arc([x-w*S,y-h*S,x+w*S,y+h*S],a0,a1,fill=col,width=W(wd))
def opening(d,w,h,cy=-0.2,teeth=False,tongue=False,round_=False):
    x,y=P(0,cy)
    box=[x-w*S,y-h*S,x+w*S,y+h*S]
    d.ellipse(box,fill=INK) if round_ else d.rounded_rectangle(box,radius=min(w,h)*S*0.9,fill=INK)
    inner=[box[0]+0.01*S,box[1]+0.01*S,box[2]-0.01*S,box[3]-0.01*S]
    (d.ellipse if round_ else (lambda b,fill:d.rounded_rectangle(b,radius=min(w,h)*S*0.8,fill=fill)))(inner,fill=RED)
    if teeth: d.rectangle([inner[0]+0.01*S,inner[1],inner[2]-0.01*S,inner[1]+min(0.025*S,(inner[3]-inner[1])*0.35)],fill=WHITE)
    if tongue: d.ellipse([x-w*S*0.5,y+h*S*0.1,x+w*S*0.5,inner[3]],fill=TONGUE)
MOUTH=[
 lambda d:arc(d,0,-0.17,0.06,0.03,20,160),                               #0 X rest (soft smile)
 lambda d:d.line([P(-0.055,-0.2),P(0.055,-0.2)],fill=INK,width=W(0.016)),#1 A closed MBP
 lambda d:opening(d,0.06,0.018,teeth=True),                              #2 B slightly open teeth
 lambda d:opening(d,0.065,0.035,teeth=True),                             #3 C open
 lambda d:opening(d,0.07,0.06,teeth=True,tongue=True),                   #4 D wide
 lambda d:opening(d,0.04,0.045,round_=True),                             #5 E round
 lambda d:opening(d,0.025,0.03,round_=True),                             #6 F pucker
 lambda d:(opening(d,0.055,0.02),d.rectangle([P(-0.04,-0.185)[0],P(-0.04,-0.185)[1],P(0.04,-0.2)[0],P(0.04,-0.2)[1]],fill=WHITE)), #7 G f/v
 lambda d:opening(d,0.06,0.04,tongue=True),                              #8 H L
 lambda d:arc(d,0.0,-0.14,0.09,0.06,20,160),                             #9 smile
 None,                                                                   #10 laugh (special)
 lambda d:opening(d,0.035,0.045,round_=True),                            #11 O kaget
 lambda d:d.line([P(-0.06,-0.21),P(0.06,-0.21)],fill=INK,width=W(0.016)),#12 flat
 lambda d:arc(d,0,-0.22,0.07,0.045,205,335),                             #13 frown
 lambda d:arc(d,0.03,-0.17,0.06,0.03,10,120),                            #14 smirk
 lambda d:d.line([P(-0.07,-0.2),P(-0.035,-0.19),P(0,-0.205),P(0.035,-0.19),P(0.07,-0.2)],fill=INK,width=W(0.014),joint="curve"), #15 wavy
]
def laugh(d):
    x0,y0=P(-0.11,-0.12); x1,y1=P(0.11,-0.27)
    d.chord([x0,y0-0.08*S,x1,y1],0,180,fill=INK); d.chord([x0+0.012*S,y0-0.07*S,x1-0.012*S,y1-0.012*S],0,180,fill=RED)
    d.rectangle([x0+0.02*S,y0,x1-0.02*S,y0+0.03*S],fill=WHITE)
    d.ellipse([P(-0.05,-0.20)[0],P(-0.05,-0.20)[1],P(0.05,-0.255)[0],P(0.05,-0.255)[1]],fill=TONGUE)
MOUTH[10]=laugh
def atlas(fns,name):
    A=Image.new("RGBA",(4*T,4*T),(0,0,0,0)); prev=Image.new("RGB",(4*256,4*256),(242,197,31))
    for i,f in enumerate(fns):
        im=Image.new("RGBA",(S,S),(0,0,0,0)); f(ImageDraw.Draw(im)); im=im.resize((T,T),Image.LANCZOS)
        A.paste(im,((i%4)*T,(i//4)*T)); sm=im.resize((256,256)); prev.paste(sm,((i%4)*256,(i//4)*256),sm)
    A.save(f"tex/{name}.png"); prev.save(f"tex/{name}_preview.png")
atlas(EYES,"eyes"); atlas(MOUTH,"mouth")
a=Image.open("tex/eyes_preview.png"); b=Image.open("tex/mouth_preview.png")
c=Image.new("RGB",(2048+20,1024),"white"); c.paste(a,(0,0)); c.paste(b,(1044,0)); c.save("tex/atlas_preview.png")
