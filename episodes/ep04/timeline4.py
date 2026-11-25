import json
F=lambda s:f"audio/{s}.mp3"
RT={0:[0.0,4.89],1:[5.4,10.41],2:[10.92,14.56],3:[15.09,22.03],4:[22.52,26.08],5:[26.6,31.78],6:[32.25,38.18],7:[38.67,44.7],8:[45.16,50.11],9:[50.67,54.33],10:[54.78,57.65],11:[58.09,62.84],12:[63.32,66.08],13:[66.46,72.43]}
NA={0:[0.16,6.39],1:[7.17,9.78],2:[10.27,13.38],3:[13.88,15.18]}; DA={0:[0.16,7.44],1:[8.25,13.26]}
DT={0:[0.0,3.51],1:[3.96,11.82],2:[12.25,13.95],3:[14.3,18.87],4:[19.23,24.43],5:[24.82,28.6],6:[28.91,33.13]}; MK={0:[0.0,4.85],1:[5.47,11.52]}
def r(i,t,e,g): return (f"R{i+1}","pakrt",RT[i],t,e,g)
U=[("N1","nayla",NA[0],"Malam ini, kami semua kumpul di pos ronda. Pak RT janji mau cerita... semuanya.","cemas",0.6),
r(0,"Melati itu anak baik. Tiap pagi dia nyapa semua orang di gang ini.","tenang",0.8),
r(1,"Dia kerja di pabrik sepatu di kota. Pulangnya sering bawain gorengan buat yang ronda.","tenang",0.4),
r(2,"Kalau ada warga yang butuh bantuan, dia yang pertama datang.","tenang",0.4),
("W1","budarmi",DA[0],"Saya masih inget, beberapa hari sebelum hilang, Melati beli lilin di warung saya. Banyak banget.","cemas",3.0),
r(3,"Sampai suatu malam... lampu kamarnya kedip-kedip sendiri. Hijau. Nggak berhenti-berhenti.","serius",1.0),
r(4,"Kami ketuk, nggak ada jawaban. Akhirnya kami dobrak.","serius",0.4),
r(5,"Kamarnya berantakan. Kasurnya terbalik. Tapi Melati... nggak ada.","sedih",1.2),
r(6,"Tiga hari tiga malam, sekampung nyari. Sampai ke sawah, ke kebun, ke sungai.","serius",1.0),
r(7,"Di pinggir sungai, kami nemuin sepatu dan tasnya. Cuma itu. Nggak ada jejak lain.","sedih",0.6),
r(8,"Kami nggak percaya dia pergi begitu aja. Jadi kami minta tolong seorang detektif.","serius",0.8),
("T1","detektif",DT[0],"Saya mulai dari tempat terakhir dia terlihat. Kamarnya.","serius",0.8),
("T2","detektif",DT[1],"Pintu dikunci dari dalam. Jendela juga. Tapi lihat ini... bekas lilin, melingkar di lantai. Dan abu kemenyan di sudut.","serius",0.6),
("T3","detektif",DT[2],"Berikutnya, tempat kerjanya.","mikir",0.8),
("RN1","rina",[0.2,9.47],"Melati seneng banget waktu itu. Katanya ada yang ngasih sepatu merah, cantik banget. Tapi dia nggak tahu dari siapa.","sedih",0.8),
("T4","detektif",DT[3],"Sepatu yang ditemukan di sungai... bukan sepatu kerjanya. Itu sepatu hadiah itu.","kaget",0.5),
("W2","budarmi",DA[1],"Katanya dia disuruh beliin sama seseorang, Pak. Tapi dia nggak bilang siapa.","cemas",1.2),
("T5","detektif",DT[4],"Sepatu ini disusun rapi, berdampingan. Orang yang hanyut nggak melepas sepatunya serapi ini.","serius",1.2),
("T6","detektif",DT[5],"Sisa kemenyan dan bunga tujuh rupa. Ini bukan hilang biasa.","serius",0.4),
("T7","detektif",DT[6],"Kemenyan nggak dijual di warung kampung. Cuma ada satu lapak... di pasar.","mikir",0.6),
("S1","sarip",[0.0,7.69],"Yang beli kemenyan minggu itu orang kampung situ, Pak. Pakai sarung, mukanya ditutup. Jalannya... ke arah hutan bambu.","takut",1.6),
r(9,"Detektif itu nemuin sesuatu yang nggak pernah kami duga.","serius",4.6),
r(10,"Melati... diduga jadi tumbal pesugihan.","serius",0.4),
("N2","nayla",NA[1],"Tumbal...? Maksudnya... dikorbankan?","takut",0.4),
("D1","dimas",[0.2,2.9],"Pak... tumbal itu buat apa?","takut",0.3),
r(11,"Orang yang pengin kaya lewat jalan gelap. Gantinya... nyawa orang lain.","serius",0.4),
("A1","adel",[0.0,2.73],"Terus, Pak... dukunnya ketemu?","takut",0.5),
r(12,"Ketemu. Di gubuk, di ujung hutan bambu.","serius",0.4),
("M1","mbahkarto",MK[0],"Saya cuma perantara... Yang minta, bukan saya.","seram",2.4),
("M2","mbahkarto",MK[1],"Orangnya... selalu dekat dengan korbannya. Tiap tujuh tahun... dia butuh lagi.","seram",0.5),
r(13,"Dukunnya ketemu. Tapi orang yang minta pesugihan itu... sampai sekarang belum ketahuan.","serius",0.8),
("N3","nayla",NA[2],"Tiap tujuh tahun... berarti... tahun ini.","takut",5.6),
("N4","nayla",NA[3],"Dekat dengan korbannya...?","beku",0.8),
("K1","kunti",[4.98,5.58],"","",1.4)]
t=0; clips=[]
for uid,sp,(s,e),txt,emo,gap in U:
    t+=gap; clips.append(dict(id=uid,spk=sp,file=F(sp),src=[s,e],dst=round(t,3),dur=round(e-s,3),text=txt,emo=emo)); t+=e-s
TOTAL=round(t+1.6,1); C={c["id"]:c for c in clips}
st=lambda u,o=0: round(C[u]["dst"]+o,3); en=lambda u,o=0: round(C[u]["dst"]+C[u]["dur"]+o,3)
SH=[(0,"posronda","s1"),(st("N1",2.6),"posronda","s2"),(st("R1",-0.2),"fb_pagi","s3"),(st("R2",-0.1),"fb_sore","s4"),(st("R2",2.6),"pabrik","s5"),(st("R3",-0.1),"fb_pagi","s6"),
(en("R3",0.1),"posronda","s7"),(st("W1",-0.3),"posronda","s8"),(st("R4",-0.6),"fb_malam","s9"),(st("R5",-0.1),"fb_malam","s10"),(en("R5",0.0),"fb_k4","s11"),(st("R6",0.3),"fb_k4","s12"),
(st("R7",-0.3),"fb_sawah","s13"),(st("R8",-0.2),"fb_sungai_malam","s14"),(st("R8",3.0),"fb_sungai_malam","s15"),(st("R9",-0.2),"fb_siang","s16"),(st("T2",-0.2),"k4_siang","s17"),(st("T2",3.0),"k4_siang","s18"),(st("T2",5.6),"k4_siang","s19"),
(st("T3",-0.4),"pabrik","s20"),(st("RN1",-0.1),"pabrik","s21"),(st("RN1",5.0),"pabrik","s22"),(st("T4",-0.1),"pabrik","s23"),(st("W2",-0.6),"warung","s24"),(st("W2",1.6),"warung","s25"),
(st("T5",-0.6),"sungai_siang","s26"),(st("T5",2.4),"sungai_siang","s27"),(st("T6",-0.1),"sungai_siang","s28"),(st("T7",-0.3),"pasar","s29"),(st("S1",-0.2),"pasar","s30"),(st("S1",4.8),"pasar","s31"),(en("S1",0.3),"papan","s32"),
(st("R10",-0.3),"posronda","s33"),(st("N2",-0.1),"posronda","s34"),(st("D1",-0.1),"posronda","s35"),(st("R12",-0.1),"posronda","s36"),(st("A1",-0.1),"posronda","s37"),(st("R13",-0.1),"gubuk","s38"),
(st("M1",-1.2),"gubuk","s39"),(st("M2",-0.1),"gubuk","s40"),(st("R14",-0.2),"posronda","s41"),(en("R14",0.6),"posronda","s42"),(st("N3",-0.2),"posronda","s43b"),(st("N4",-0.2),"posronda","s43"),(st("K1",-0.6),"posronda","s44")]
shots=[]
for i,(s,setn,cam) in enumerate(SH):
    e=SH[i+1][0] if i+1<len(SH) else TOTAL; shots.append(dict(n=i+1,start=round(s,3),end=round(e,3),set=setn,cam=cam,act=cam))
for s in shots: assert s["end"]>s["start"]+0.5,s
S={x["cam"]:x for x in shots}
FX=[(0.2,"kentongan",-24,4.0),(S["s5"]["start"],"pabrik",-22,S["s6"]["start"]-S["s5"]["start"]),(S["s10"]["start"]+0.4,"ketuk",0,None),(S["s11"]["start"],"banting",-4,None),
(S["s13"]["start"],"angin",-24,S["s16"]["start"]-S["s13"]["start"]),(S["s14"]["start"],"sungai",-20,S["s16"]["start"]-S["s14"]["start"]),(S["s17"]["start"]+0.6,"k:switch_002",-10,None),
(S["s19"]["start"],"hum",-24,2.5),(S["s20"]["start"],"pabrik",-28,S["s24"]["start"]-S["s20"]["start"]),(S["s22"]["start"],"k:click_001",-10,None),(S["s23"]["start"]+0.1,"hit",-12,None),
(S["s26"]["start"],"sungai",-24,S["s29"]["start"]-S["s26"]["start"]),(S["s29"]["start"],"pasar_synth",-28,S["s32"]["start"]-S["s29"]["start"]),(S["s32"]["start"]+0.3,"halaman",-12,None),
(S["s38"]["start"],"daun",-14,S["s39"]["start"]-S["s38"]["start"]),(S["s38"]["start"]+0.8,"burunghantu",-18,None),(S["s42"]["start"],"jantung",-14,S["s43b"]["start"]-S["s42"]["start"]),(S["s44"]["start"]+0.3,"k:glitch_002",-12,None)]
PARTA_END=S["s17"]["start"]
json.dump(dict(total=TOTAL,clips=clips,shots=shots,sfx=FX,partA_end=PARTA_END),open("timeline.json","w"),indent=1,ensure_ascii=False)
print("TOTAL",TOTAL,"partA",PARTA_END)
for s in shots: print(f"{s['n']:2d} {s['start']:6.2f}-{s['end']:6.2f} {s['end']-s['start']:4.1f}s {s['set']:15s} {s['cam']}")
