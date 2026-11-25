import json
F={"nayla":"audio/nayla.mp3","ibukos":"audio/ibukos.mp3","adel":"audio/adel.mp3","dimas":"audio/dimas.mp3","pakrt":"audio/pakrt.mp3","pakronda":"audio/pakronda.mp3","kunti":"audio/kunti.mp3"}
NA={0:[0.21,4.63],1:[5.25,11.94],2:[12.42,14.63],3:[15.19,18.88],4:[19.54,22.22],5:[22.69,26.98],6:[27.48,30.95],7:[31.43,32.85],8:[33.46,35.34]}
IB={0:[0.15,7.02],1:[7.64,13.57],2:[14.19,20.72],3:[21.4,27.72],4:[28.33,31.96],5:[32.53,37.21]}
AD={0:[0.0,3.3],1:[3.67,6.67]}; DM={0:[0.0,5.64],1:[6.13,7.71]}; RT={0:[0.0,4.54],1:[5.25,16.58],2:[17.37,21.56],3:[22.22,28.31],4:[28.92,30.75]}
U=[("N1","nayla",NA[0],"Setelah malam itu, nggak ada satu pun dari kami yang bisa tidur.","lelah",0.4),
("N2","nayla",NA[1],"Paginya, Ibu Kos manggil kami bertiga ke rumahnya. Katanya... ada yang harus dia ceritain.","cemas",0.4),
("I1","ibukos",IB[0],"Ibu minta maaf. Kemarin Ibu bohong. Ibu takut kalian pindah semua.","sedih",1.4),
("I2","ibukos",IB[1],"Tujuh tahun lalu, kamar empat ditempati seorang perempuan. Namanya Melati.","sedih",0.4),
("N3","nayla",NA[2],"Melati? Kayak nama kos ini?","kaget",0.3),
("I3","ibukos",IB[2],"Dia suka bunga melati. Suka jemur baju tengah malam. Dan lampu tidurnya... warna hijau.","sedih",0.4),
("I4","ibukos",IB[3],"Suatu malam, dia hilang. Yang tersisa cuma baju putihnya... masih tergantung di jemuran.","sedih",0.5),
("A1","adel",AD[0],"Bu, perempuan di foto ini... siapa?","penasaran",0.8),
("I5","ibukos",IB[4],"Itu Melati. Foto terakhirnya, di depan kamarnya.","sedih",0.3),
("N4","nayla",NA[3],"Lampu di jendela itu... udah hijau dari tujuh tahun lalu.","takut",1.6),
("I6","ibukos",IB[5],"Kalau mau tahu lebih banyak, tanya Pak RT. Dulu dia yang memimpin pencarian.","tenang",0.3),
("N5","nayla",NA[4],"Malamnya, kami nemuin Pak RT di pos ronda.","tegas",1.0),
("R1","pakrt",RT[0],"Tiga hari kami cari Melati. Sekampung ikut. Nggak ketemu.","serius",3.0),
("R2","pakrt",RT[1],"Malam ketiga, warga dengar suara ketawa dari kamar empat. Pintunya terkunci dari dalam. Kami dobrak... kosong. Cuma lampu hijau yang nyala sendiri.","serius",0.4),
("P1","pakronda",[0.0,7.0],"Sejak malam itu, tiap jam tiga pagi ada baju putih di jemuran. Padahal nggak ada yang jemur.","takut",0.6),
("N6","nayla",NA[5],"Terkunci dari dalam? Terus dia keluarnya lewat mana, Pak?","bingung",0.4),
("R3","pakrt",RT[2],"Nggak ada yang tahu, Nak. Tapi Melati bukan yang pertama.","serius",0.4),
("R4","pakrt",RT[3],"Ratna, dua ribu dua belas. Sinta, dua ribu lima. Semuanya penghuni kamar empat.","serius",1.0),
("N7","nayla",NA[6],"Ratna... Sinta... Melati... semuanya penghuni kamar empat?","takut",0.4),
("D1","dimas",DM[0],"Dua ribu lima... dua ribu dua belas... dua ribu sembilan belas... tiap tujuh tahun.","takut",0.5),
("D2","dimas",DM[1],"Berarti... tahun ini?","takut",0.3),
("A2","adel",AD[1],"Tinta di halaman ini... masih basah.","takut",2.6),
("N8","nayla",NA[7],"Itu... nama aku.","beku",2.2),
("R5","pakrt",RT[4],"Ini... bukan tulisan saya.","takut",0.8),
("N9","nayla",NA[8],"Aku tinggal di kamar tiga... kan?","beku",4.2),
("K1","kunti",[4.98,5.58],"","",1.4)]
t=0; clips=[]
for uid,sp,(s,e),txt,emo,gap in U:
    t+=gap; clips.append(dict(id=uid,spk=sp,file=F[sp],src=[s,e],dst=round(t,3),dur=round(e-s,3),text=txt,emo=emo)); t+=e-s
TOTAL=round(t+1.6,1); C={c["id"]:c for c in clips}
st=lambda u,o=0: round(C[u]["dst"]+o,3); en=lambda u,o=0: round(C[u]["dst"]+C[u]["dur"]+o,3)
SH=[(0,"kamar_pagi","s1"),(st("N2",1.5),"luar_pagi","s2"),(st("I1",-1.0),"ruangtamu","s3"),(st("I1",2.2),"ruangtamu","s4"),(st("I2",-0.1),"ruangtamu","s5"),
(st("N3",-0.1),"ruangtamu","s6"),(st("I3",-0.1),"flash_malam","s7"),(st("I4",2.6),"flash_malam","s8"),(st("A1",-0.4),"ruangtamu","s9"),(st("I5",-0.1),"ruangtamu","s10"),
(st("N4",-0.8),"ruangtamu","s11"),(st("I6",-0.1),"ruangtamu","s12"),(st("N5",-0.4),"luar_malam","s13"),(st("R1",-2.6),"posronda","s14"),(st("R1",-0.1),"posronda","s15"),
(st("R2",3.3),"flash_k4","s16"),(st("P1",-0.2),"posronda","s17"),(st("N6",-0.1),"posronda","s18"),(st("R3",-0.1),"posronda","s19"),(st("R4",-0.2),"posronda","s20"),
(st("N7",-0.1),"posronda","s21"),(st("D1",-0.1),"posronda","s22"),(en("D2",0.2),"posronda","s23"),(st("A2",-0.2),"posronda","s24"),(en("A2",0.1),"posronda","s25"),
(st("N8",-0.1),"posronda","s26"),(st("R5",-0.2),"posronda","s27"),(en("R5",0.5),"luar_malam","s28"),(st("N9",-0.2),"luar_malam","s29"),(st("K1",-0.6),"luar_malam","s30")]
shots=[]
for i,(s,setn,cam) in enumerate(SH):
    e=SH[i+1][0] if i+1<len(SH) else TOTAL; shots.append(dict(n=i+1,start=round(s,3),end=round(e,3),set=setn,cam=cam,act=cam))
for s in shots: assert s["end"]>s["start"]+0.5,s
S={x["cam"]:x for x in shots}
FX=[(0.2,"ayam",-8,None),(S["s3"]["start"],"jam",-24,S["s12"]["end"]-S["s3"]["start"]),(S["s7"]["start"],"angin",-22,S["s9"]["start"]-S["s7"]["start"]),
(S["s14"]["start"]+0.3,"catur",-12,1.2),(S["s16"]["start"],"banting",-6,None),(S["s16"]["start"]+0.6,"kunti_k1",-20,None),(S["s17"]["start"]+0.4,"kentongan",-20,4.0),
(S["s20"]["start"]+0.2,"halaman",-10,None),(S["s23"]["start"]+0.2,"halaman",-6,None),(S["s25"]["start"],"hum",-26,3.5),(S["s26"]["start"]+0.15,"jumpscare_kecil",-8,None),
(S["s28"]["start"]+1.8,"klotak",-8,None),(S["s29"]["start"],"neon",-30,3),(S["s30"]["start"]+0.3,"k:glitch_002",-12,None)]
json.dump(dict(total=TOTAL,clips=clips,shots=shots,sfx=FX),open("timeline.json","w"),indent=1,ensure_ascii=False)
print("TOTAL",TOTAL); [print(f"{s['n']:2d} {s['start']:6.2f}-{s['end']:6.2f} {s['end']-s['start']:4.1f}s {s['set']:11s} {s['cam']}") for s in shots]
