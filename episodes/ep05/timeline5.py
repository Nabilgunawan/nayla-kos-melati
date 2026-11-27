import json
F=lambda s:f"audio/{s}.mp3"
NA={1:[0.0,4.04],2:[4.37,7.21],3:[7.45,10.92],4:[11.18,13.38],5:[13.71,16.66],6:[16.86,19.72],7:[19.99,23.29],8:[23.63,25.82],9:[26.11,29.36],10:[29.58,32.90],11:[33.0,33.97],12:[34.30,37.80],13:[38.10,41.03],14:[41.39,43.24],15:[43.50,45.36]}
DM={1:[0.0,1.81],2:[2.09,4.34],3:[4.78,8.72],4:[8.93,10.0],5:[10.22,13.12],6:[13.40,15.23],7:[15.65,18.58],8:[18.86,21.82],9:[21.88,23.47],10:[23.76,26.48],11:[26.83,28.67],12:[29.0,31.14],13:[31.65,32.75]}
TX_N={1:"Sore itu kos lagi sepi. Sampai Dimas teriak dari kamar satu.",2:"Apaan sih, Dim? Teriak-teriak kayak ada maling.",3:"Hah? Serius? GTA 6 resmi rilis di PS5?",4:"Ya ampun, beneran udah keluar!",
5:"Lo kan punya PS5... gimana kalau kita patungan?",6:"Deal! Tapi gue yang main duluan.",7:"Dan sore itu... pelan-pelan berubah jadi malam.",8:"Dim, grafiknya kayak film beneran!",
9:"Eh, Dim. Tipe cewek lo yang kayak Lucia atau Mandy?",10:"Ahh, masa? Bukannya cowok rata-rata tim Mandy?",11:"Hahaha!",12:"Udah lewat tengah malam. Gue balik ke kamar ya.",
13:"Besoknya, kami berangkat kuliah seperti biasa.",14:"Dan waktu kami pulang...",15:"Dim... PS5 lo mana?"}
TX_D={1:"NAYLAAA! Sini cepetan!",2:"GTA 6 udah rilis, Nay! Lihat nih!",3:"PS gue ada... tapi duit gue cuma cukup buat setengahnya.",4:"Deal! Patungan!",5:"Ayo dong... 99 persen dari tadi...",
6:"Kejar, kejar! Belok kiri, Nay!",7:"Lucia lah. Dia setia sama Jason dari awal.",8:"Serius! Cowok yang bener tuh nyarinya yang setia!",9:"Hahaha!",10:"Oke, besok lanjut ya. Jangan main duluan!",
11:"Pintu udah dikunci. Aman.",12:"Nggak mungkin... pintunya masih kekunci...",13:"PS GUE MANA?!"}
EMO={'N1':'senang','D1':'heboh','N2':'kesal','D2':'heboh','N3':'kaget','N4':'senang','D3':'malu','N5':'mikir','D4':'senang','N6':'tertawa','D5':'kesal','N7':'senang',
'D6':'heboh','N8':'kagum','N9':'jahil','D7':'malu','N10':'jahil','D8':'tertawa','D9':'tertawa','N11':'tertawa','N12':'ngantuk','D10':'ngantuk','N13':'tenang','D11':'yakin','N14':'cemas','D12':'kaget','N15':'bingung','D13':'panik'}
def n(i,g): return (f"N{i}","nayla",NA[i],TX_N[i],EMO[f'N{i}'],g)
def d(i,g): return (f"D{i}","dimas",DM[i],TX_D[i],EMO[f'D{i}'],g)
U=[n(1,0.8),d(1,2.8),n(2,1.2),d(2,0.8),n(3,2.2),n(4,0.3),d(3,1.8),n(5,0.4),d(4,0.3),n(6,0.2),d(5,4.2),n(7,1.6),
   d(6,3.4),n(8,1.6),n(9,8.4),d(7,0.4),n(10,0.4),d(8,0.3),d(9,0.0),("N11","nayla",NA[11],"","tertawa",-1.4),
   n(12,4.0),d(10,0.3),n(13,6.0),d(11,1.8),n(14,4.4),d(12,2.6),n(15,0.8),d(13,0.6)]
t=0; clips=[]
for uid,sp,(s,e),txt,emo,gap in U:
    t+=gap; clips.append(dict(id=uid,spk=sp,file=F(sp),src=[s,e],dst=round(t,3),dur=round(e-s,3),text=txt,emo=emo))
    if gap>=0: t+=e-s
    else: t=max(t+e-s, t)            # tawa tumpang tindih
TOTAL=round(max(c['dst']+c['dur'] for c in clips)+2.6,1); C={c["id"]:c for c in clips}
st=lambda u,o=0: round(C[u]["dst"]+o,3); en=lambda u,o=0: round(C[u]["dst"]+C[u]["dur"]+o,3)
SH=[(0,"luar_sore","s1"),(en("N1",0.1),"luar_sore","s2"),(st("D1",-0.1),"luar_sore","s3"),(st("N2",-0.3),"kamar_sore","s4"),(st("D2",-0.3),"kamar_sore","s5"),
(st("N3",-1.0),"kamar_sore","s6"),(st("N4",-0.1),"kamar_sore","s7"),(st("D3",-0.4),"teras3_sore","s8"),(en("N6",-0.6),"teras3_sore","s9"),(en("N6",0.4),"hp","s10"),
(st("D5",-1.2),"k1_sore","s11"),(st("N7",-0.2),"luar_senja","s12"),(en("N7",0.4),"k1_malam","s13"),(st("N8",-0.2),"k1_malam","s14"),(en("N8",0.5),"k1_malam","s15"),
(en("N8",4.4),"k1_malam","s16"),(st("N9",-0.6),"k1_malam","s17"),(st("D7",-0.2),"k1_malam","s18"),(st("D9",-0.1),"k1_malam","s19"),(en("D9",0.6),"k1_malam","s20"),
(en("D10",0.4),"luar_malam","s21"),(st("N13",-1.6),"luar_pagi","s22"),(st("N14",-0.6),"k1_sore2","s23"),(st("N15",-0.8),"k1_sore2","s24")]
shots=[]
for i,(s,setn,cam) in enumerate(SH):
    e=SH[i+1][0] if i+1<len(SH) else TOTAL; shots.append(dict(n=i+1,start=round(s,3),end=round(e,3),set=setn,cam=cam,act=cam))
for s in shots: assert s["end"]>s["start"]+0.8,s
S={x["cam"]:x for x in shots}
TV=[(S["s11"]["start"],S["s13"]["start"],"unduh",0),(S["s13"]["start"],S["s15"]["start"],"kejar",0.0),(S["s15"]["start"],S["s16"]["start"],"lucia",0.5),
    (S["s16"]["start"],S["s17"]["start"],"mandy",0.0),(S["s17"]["start"],S["s20"]["start"],"pause",0),(S["s20"]["start"],S["s21"]["start"],"pause",0)]
PHONE=[(0,S["s2"]["start"],"dimas","home"),(S["s2"]["start"],S["s4"]["start"],"dimas","notif"),(S["s5"]["start"],S["s6"]["start"],"dimas","berita"),
       (S["s6"]["start"],S["s7"]["start"],"nayla","berita"),(S["s10"]["start"],S["s11"]["start"],"dimas","beli")]
FX=[(0.0,"burung_sore",-26,S["s4"]["start"]),(S["s2"]["start"]+0.2,"notif",-8,None),(S["s5"]["start"]+0.1,"langkah_lari",-14,None),(S["s6"]["start"]+0.6,"tap",-14,None),
    (S["s9"]["start"]+0.5,"tos",-8,None),(S["s10"]["start"]+0.2,"ding",-10,None),(S["s11"]["start"],"jam_cepat",-20,S["s12"]["start"]-S["s11"]["start"]),
    (S["s12"]["start"],"jangkrik",-30,S["s13"]["start"]-S["s12"]["start"]+1),(S["s17"]["start"]+0.2,"pause",-12,None),(S["s20"]["start"],"jam_detik",-22,3.0),
    (S["s21"]["start"],"jangkrik",-28,S["s22"]["start"]-S["s21"]["start"]),(S["s22"]["start"],"ayam",-20,None),(S["s22"]["start"]+0.6,"kunci",-8,None),
    (S["s23"]["start"]+0.8,"gagang",-8,None),(S["s24"]["start"]+0.3,"sting",-6,None)]
json.dump(dict(total=TOTAL,clips=clips,shots=shots,sfx=FX,tv=TV,phone=PHONE),open("timeline.json","w"),indent=1,ensure_ascii=False)
print("TOTAL",TOTAL)
for s in shots: print(f"{s['n']:2d} {s['start']:6.2f}-{s['end']:6.2f} {s['end']-s['start']:4.1f}s {s['set']:12s} {s['cam']}")
