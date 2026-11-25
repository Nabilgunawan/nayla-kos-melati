import json
U=[ # id, src_start, src_end, text, emotion(eyes idx, rest mouth idx), extra_gap_after
("u1",0.00,1.26,"Eh... udah ngerekam?","kaget",0),
("u2",1.53,2.23,"Bentar, bentar!","panik",1.3),
("u3",2.57,3.55,"Halo semuanya!","ceria",0),
("u4",3.81,5.04,"Kenalin, aku Nayla.","ceria",0),
("u5",5.42,10.65,"Umur dua puluh tahun, mahasiswi Hubungan Internasional, dan sekarang aku ngekos di dekat kampus.","ceria",1.2),
("u6",11.04,12.98,"Nah, ini dia istana aku.","bangga",0),
("u7",13.24,14.44,"Tiga kali tiga meter.","jahil",0),
("u8",14.77,18.94,"Ada kasur, meja belajar, kipas angin yang bunyinya kayak helikopter...","jahil",1.4),
("u9",19.14,19.78,"dan ini.","lembut",0),
("u10",20.14,20.82,"Rice cooker.","lembut",0.2),
("u11",21.15,22.55,"Sahabat sejati anak kos.","lembut",5.0),
("u12",23.02,24.53,"Nah, ini kampus aku.","ceria",0),
("u13",24.93,28.87,"Setiap kali aku bilang kuliah di HI, pertanyaannya pasti sama.","pasrah",0.4),
("u14",29.28,30.30,"\"HI itu apa?","bingung",0),
("u15",30.59,31.52,"Hotel Indonesia?\"","bingung",1.3),
("u16",31.89,32.64,"Bukan, Om.","deadpan",0),
("u17",32.93,34.35,"Hubungan Internasional.","deadpan",1.0),
("u18",34.72,35.69,"Terus lanjut lagi.","pasrah",0),
("u19",36.03,37.48,"\"Nanti kerjanya jadi apa?\"","bingung",0),
("u20",37.78,39.36,"Diplomat, Tante.","bangga",0.6),
("u21",39.51,40.77,"Aamiin dulu aja.","tawa",0.3),
("u22",41.18,45.86,"Sehari-hari aku belajar kenapa negara-negara bisa akur, dan kenapa bisa ribut.","merenung",0),
("u23",46.13,48.30,"Padahal grup chat kelas aja kadang ribut.","kesal",5.6),
("u24",48.61,50.19,"Tapi belajarnya nggak cuma di kelas.","jahil",0),
("u25",50.62,52.14,"Kota ini juga guru aku.","lembut",0),
("u26",52.36,58.38,"Dari obrolan sama abang ojol, harga cilok yang naik pelan-pelan, sampai orang-orang yang buru-buru tiap pagi.","jahil",1.6),
("u27",58.66,60.58,"Buat aku, semua itu cerita.","lembut",0),
("u28",60.91,62.12,"Dunia itu besar banget...","merenung",0.6),
("u29",62.60,65.82,"tapi ceritanya sering dimulai dari hal kecil di sekitar kita.","lembut",6.6),
("u30",66.15,67.74,"Makanya aku bikin akun ini.","ceria",0),
("u31",67.95,73.98,"Di sini aku bakal cerita kehidupan anak kos, drama kuliah, dan barang-barang kecil yang bikin hidup aku lebih gampang.","ceria",1.2),
("u32",74.31,76.24,"Kadang lucu, kadang curhat...","jahil",0),
("u33",76.39,79.00,"kadang aku cuma ngobrol sama kipas angin.","canggung",2.2),
("u34",79.32,82.55,"Jadi, kalau kalian mau nemenin perjalanan aku, follow ya!","ceria",1.0),
("u35",82.85,83.37,"Eh...","kaget",0.2),
("u36",83.69,84.41,"nasi aku!","panik",0),
]
EMO={ # eyes tile, rest-mouth tile
"kaget":(2,11),"panik":(11,11),"ceria":(0,9),"bangga":(7,14),"jahil":(8,14),"lembut":(12,9),"pasrah":(6,12),
"bingung":(9,15),"deadpan":(4,12),"tawa":(3,10),"merenung":(10,0),"kesal":(5,13),"canggung":(3,15),"malu":(15,9)}
t=0.25; clips=[]
for i,(uid,s,e,txt,emo,extra) in enumerate(U):
    clips.append(dict(id=uid,src=[s,e],dst=round(t,3),dur=round(e-s,3),text=txt,emo=emo))
    nat=(U[i+1][1]-e) if i+1<len(U) else 0
    t+= (e-s)+nat+extra
TOTAL=120.0
end_speech=clips[-1]['dst']+clips[-1]['dur']
print("speech ends at",round(end_speech,2),"tail",round(TOTAL-end_speech,2))
C={c['id']:c for c in clips}
def st(u,o=0): return round(C[u]['dst']+o,3)
def en(u,o=0): return round(C[u]['dst']+C[u]['dur']+o,3)
# shots: start, set, cam, action
SH=[
(0,"kos_pagi","ecu_hand","too_close"),
(st("u2",-0.1),"kos_pagi","ms_pullback","step_back"),
(st("u3",-0.2),"kos_pagi","ms_eye","wave"),
(st("u5"),"kos_pagi","mcu_push","talk"),
(st("u6",-1.1),"kos_pagi","wide_high","present"),
(st("u7"),"kos_pagi","wide_pan","arms_open"),
(st("u8"),"kos_pagi","ins_desk","walk_desk"),
(st("u8",2.2),"kos_pagi","ins_fan","fan_gag"),
(st("u9",-0.2),"kos_pagi","cu_rice","hug_rice"),
(en("u11",1.2),"kampus","est_low","walk_in"),
(st("u12",-0.4),"kampus","track_side","walk"),
(st("u13"),"kampus","ms_k","talk"),
(st("u14",-0.1),"kampus","cu_zoom","silly"),
(st("u16",-0.15),"kampus","cu_static","deadpan"),
(st("u18",-0.1),"kampus","ms_k2","talk_shrug"),
(st("u20",-0.1),"kampus","low_hero","hero"),
(st("u22",-0.1),"kampus","mw_bench","sit_phone"),
(st("u23",-0.1),"kampus","cu_phone","phone_buzz"),
(en("u23",2.0),"kota","est_tilt","none"),
(st("u24",-0.6),"kota","track_front","walk_city"),
(st("u25"),"kota","ms_c","talk"),
(st("u26"),"kota","ins_ojol","watch_ojol"),
(st("u26",2.4),"kota","ins_cilok","point_cilok"),
(st("u26",4.4),"kota","wide_traffic","stand"),
(st("u27"),"kota","cu_gaze","gaze"),
(st("u29"),"kota","crane_sunset","gaze_far"),
(en("u29",3.6),"kos_malam","est_night","sit_desk_idle"),
(st("u30",-0.2),"kos_malam","ms_desk","sit_talk"),
(st("u31"),"kos_malam","cu_desk","sit_talk"),
(st("u31",3.6),"kos_malam","ins_items","sit_talk"),
(st("u32",-0.2),"kos_malam","ms_desk2","sit_talk"),
(st("u33"),"kos_malam","wide_fan","talk_fan"),
(st("u34",-0.2),"kos_malam","mcu_follow","wave"),
(en("u34",0.15),"kos_malam","ins_rice2","none"),
(st("u35",-0.1),"kos_malam","cu_shock","shock"),
(st("u36",-0.05),"kos_malam","run_ecu","run_cam"),
]
shots=[]
for i,(s,setn,cam,act) in enumerate(SH):
    e=SH[i+1][0] if i+1<len(SH) else TOTAL
    shots.append(dict(n=i+1,start=round(s,3),end=round(e,3),set=setn,cam=cam,act=act))
for s in shots: assert s['end']>s['start']+0.3, s
# SFX events (time, name, gain dB)
FX=[(0.05,"rec_beep",-6),(st("u2",0.6),"whoosh",-8),(st("u2",0.9),"steps",-10),(st("u4",0.3),"pop",-8),
(st("u7",-0.2),"tada",-10),(st("u8",2.3),"fan_loud",-12),(st("u10",0.1),"ting_soft",-10),
(en("u11",1.1),"door",-8),(en("u11",1.4),"campus_amb",-20,9),(st("u12",-0.4),"steps",-12),
(en("u15",0.05),"scratch",-8),(en("u17",0.2),"",0),(st("u21",-0.2),"sparkle",-10),
(en("u23",0.2),"notif3",-8),(en("u23",2.0),"city_amb",-20,34),(st("u24",-0.6),"steps",-12),
(st("u26",0.3),"moto",-14),(st("u26",2.6),"kaching",-10),(st("u26",4.4),"traffic",-16),
(en("u29",3.6),"crickets",-24,32),(st("u30",0.3),"typing",-18),(st("u33",0.2),"fan_loud",-16),
(st("u34",-0.2),"pop",-10),(en("u34",0.3),"ting",-6),(st("u35",0),"hit",-6),(st("u36",0.3),"whoosh",-6)]
FX=[f for f in FX if f[1]]
json.dump(dict(total=TOTAL,clips=clips,shots=shots,emo=EMO,sfx=FX),open("timeline.json","w"),indent=1,ensure_ascii=False)
for s in shots: print(f"{s['n']:2d} {s['start']:6.2f}-{s['end']:6.2f} {s['end']-s['start']:4.1f}s {s['set']:10s} {s['cam']:13s} {s['act']}")
