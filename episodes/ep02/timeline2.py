import json
SRC={"nayla":"audio/nayla.mp3","ibukos":"audio/ibukos.mp3","adel":"audio/adel.mp3","dimas":"audio/dimas.mp3","kunti":"audio/kunti.mp3"}
# (id, speaker, src_start, src_end, text, emo, gap_before)
U=[("N1","nayla",0.18,5.31,"Ssst... jangan berisik. Udah jam dua pagi... dan lampu itu nyala lagi.","cemas",0.3),
("N2","nayla",5.90,7.90,"Kalian harus tahu ceritanya dari awal.","cemas",0.5),
("N3","nayla",8.35,20.57,"Jadi, kos aku ini isinya empat kamar, nyambung sama rumah Ibu Kos. Kamar satu, Dimas. Kamar dua, Adel. Kamar tiga, aku. Kamar empat? Kosong dari zaman aku pertama masuk.","ceria",1.0),
("N4","nayla",21.06,24.24,"Sampai minggu lalu... tiba-tiba ada penghuni baru.","penasaran",0.5),
("N5","nayla",24.61,32.68,"Anehnya, dia nggak pernah keluar siang hari. Nggak pernah. Keluarnya cuma tengah malam, pas semua orang udah tidur.","curiga",1.2),
("N6","nayla",33.06,36.64,"Terus tiap malam, lampu kamarnya kedip-kedip... warna hijau.","cemas",0.6),
("N7","nayla",36.97,40.70,"Oke... mungkin dia kerja shift malam. Atau mungkin dia cuma pemalu banget.","mikir",0.7),
("N8","nayla",41.08,46.38,"Tapi jam tiga pagi, ada baju putih panjang dijemur. Siapa yang nyuci baju jam segitu?","bingung",1.0),
("N9","nayla",46.71,51.12,"Kamarnya juga wangi bunga melati. Ya... mungkin parfumnya emang melati.","penasaran",0.7),
("K1","kunti",0.0,1.24,"","",0.6),
("N10","nayla",51.42,57.06,"Dan tiap malam ada suara ketawa pelan. Mungkin dia lagi nonton video lucu. Mungkin.","cemas",0.4),
("N11","nayla",57.35,59.72,"Oke. Malam ini aku mau kenalan langsung.","tegas",0.7),
("N12","nayla",60.04,62.65,"Permisi... aku Nayla, dari kamar tiga. Mau kenalan aja...","cemas",3.6),
("N13","nayla",63.09,64.07,"Kok... nggak dikunci?","takut",2.3),
("K2","kunti",1.75,4.41,"","",0.7),
("N14","nayla",64.44,65.84,"Aaaaaaa!","takut",0.2),
("N15","nayla",66.08,71.44,"Bu! Bu! Penghuni kamar empat itu... dia bukan manusia, Bu!","panik",5.2),
("I1","ibukos",0.0,4.40,"Penghuni kamar empat? Kamar empat itu nggak pernah Ibu sewain, Nay.","tenang",0.5),
("N16","nayla",71.63,73.02,"Maksud Ibu... gimana?","bingung",0.4),
("I2","ibukos",4.75,9.87,"Dari kos ini dibangun, kamar itu kosong. Kuncinya aja udah hilang dari dulu.","tenang",0.4),
("A1","adel",0.11,4.03,"Kamar empat? Lho... aku kira itu gudang, Nay.","penasaran",0.5),
("D1","dimas",0.13,5.27,"Jadi... lampu hijau yang tiap malam itu... bukan kamu yang nyalain, Nay?","takut",0.4),
("N17","nayla",73.32,75.13,"Terus... yang tadi malam itu... siapa?","beku",3.6),
("K3","kunti",4.98,5.58,"","",0.5)]
t=0; clips=[]
for uid,sp,s,e,txt,emo,gap in U:
    t+=gap; clips.append(dict(id=uid,spk=sp,file=SRC[sp],src=[s,e],dst=round(t,3),dur=round(e-s,3),text=txt,emo=emo)); t+=e-s
C={c["id"]:c for c in clips}
def st(u,o=0): return round(C[u]["dst"]+o,3)
def en(u,o=0): return round(C[u]["dst"]+C[u]["dur"]+o,3)
TOTAL=120.0
print("last speech ends",round(t,2))
# shots: start, set, cam, act
SH=[(0,"kamar_malam","s1","phone_ecu"),(st("N2",-0.2),"kamar_malam","s2","window_back"),
(en("N2",0.35),"luar_siang","s3","none"),(st("N3",1.8),"luar_siang","s4","walk_teras"),(st("N3",9.0),"luar_siang","s5","none"),(st("N4",-0.1),"luar_siang","s6","talk"),
(en("N4",0.3),"luar_malam","s7","none"),(st("N5",3.6),"kamar_malam","s8","peek"),(st("N6",-0.1),"luar_malam","s9","none"),(st("N7",-0.1),"kamar_malam","s10","think"),
(st("N8",-0.2),"luar_malam","s11","look_jemuran"),(st("N8",3.2),"luar_malam","s12","bingung"),(st("N9",-0.1),"luar_malam","s13","sniff"),
(st("K1",-0.3),"kamar_malam","s14","sit_bed"),(st("N10",2.6),"kamar_malam","s15","ear_wall"),(st("N11",-0.1),"kamar_malam","s16","talk"),
(en("N11",0.25),"luar_malam","s17","tiptoe"),(en("N11",2.9),"luar_malam","s18","knock"),(en("N12",0.3),"kamar4","s19","door_reveal"),
(st("N13",-0.2),"kamar4","s20","pov"),(st("K2",-0.1),"kamar4","s21","none"),(st("N14",-0.05),"kamar4","s22","scream"),
(en("N14",0.25),"luar_malam","s23","run"),(en("N14",1.7),"kamar_malam","s24","lean_door"),
(en("N14",3.5),"luar_pagi","s25","none"),(st("N15",-0.2),"luar_pagi","s26","report"),(st("I1",-0.1),"luar_pagi","s27","ibu_talk"),
(st("N16",-0.1),"luar_pagi","s27b","confused"),(st("I2",-0.1),"luar_pagi","s27","ibu_talk"),(st("A1",-0.1),"luar_pagi","s28","friends"),(st("D1",-0.1),"luar_pagi","s28d","dimas_scared"),
(en("D1",0.15),"luar_pagi","s29","freeze"),(en("D1",1.3),"luar_pagi","s30","none"),(st("N17",-0.9),"kamar_malam","s31","whisper"),(st("K3",-0.8),"kamar_malam","s32","ending")]
shots=[]
for i,(s,setn,cam,act) in enumerate(SH):
    e=SH[i+1][0] if i+1<len(SH) else TOTAL
    shots.append(dict(n=i+1,start=round(s,3),end=round(e,3),set=setn,cam=cam,act=act))
for s in shots: assert s["end"]>s["start"]+0.4,(s)
# SFX: (time, file, gain dB, max_dur, loop)
FX=[(0.0,"amb:jangkrik",-24,None),(0.05,"neon",-20,7.5),
(en("N2",0.3),"k:maximize_006",-12,None),(en("N2",0.4),"amb:pagi_synth",-30,None),
(en("N4",0.25),"k:minimize_005",-12,None),(en("N4",0.3),"amb:jangkrik",-24,None),(en("N4",0.3),"angin",-26,22),
(st("N6",0),"neon",-16,4.5),(st("N7",1.8),"k:question_001",-6,None),(st("N8",3.3),"k:error_004",-8,None),
(st("N9",0.2),"angin",-24,6),(st("K1",0),"tegang",-26,12),(st("N11",1.6),"k:confirmation_002",-10,None),
(en("N11",0.3),"lari:slow",-30,None),(en("N11",3.0),"ketuk",0,None),(en("N12",0.4),"derit",-6,None),
(st("N13",0.1),"neon",-12,3.0),(st("K2",0),"jumpscare",-2,None),(st("K2",0),"neon",-10,3.2),(st("N14",0),"teriak",-18,None),
(en("N14",0.3),"lari",-6,None),(en("N14",1.7),"banting",-4,None),(en("N14",1.9),"napas",-12,1.6),
(en("N14",3.5),"ayam",-6,None),(en("N14",3.6),"amb:pagi_synth",-28,None),(st("I1",4.2),"hening",0,None),
(en("D1",0.1),"tegang",-24,4.0),(st("N17",-0.9),"amb:jangkrik",-26,None),(st("N17",-0.9),"neon",-18,5.0),(st("K3",0),"k:glitch_002",-10,None)]
json.dump(dict(total=TOTAL,clips=clips,shots=shots,sfx=FX),open("timeline.json","w"),indent=1,ensure_ascii=False)
for s in shots: print(f"{s['n']:2d} {s['start']:6.2f}-{s['end']:6.2f} {s['end']-s['start']:4.1f}s {s['set']:12s} {s['cam']:5s} {s['act']}")
