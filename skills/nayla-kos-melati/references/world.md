# World reference

## Characters (toy-figure body from char.py; NOT a LEGO minifigure shape). Female rigs get the softer body from femme.py:
waist, modest bust (BUST 0.10), tapered limbs, cheek blush; Adel & Bu Darmi wear a khimar-style hijab; Nayla has a pink flower hair clip (left side).
| Rig | Who | Look |
| --- | --- | --- |
| Nayla_rig | Nayla, 20, HI student, kamar 3 | ash-brown double braids, black hoodie, gold necklace; face material `face` |
| Adel_rig | Adel, kamar 2, cheerful | beige hijab, white shirt, tan pants, brown sling bag |
| Dimas_rig | Dimas, kamar 1, scared easily | curly brown hair, blue puffer hoodie, black pants |
| Ibu_rig | Ibu Kos = Bu Sari | black bob, round glasses, purple blazer, navy pants |
| Kunti_rig | kuntilanak (Melati's spirit) | long black hair over face, white floating dress |
| RT_rig | Pak RT (Pak Darto) | peci, glasses, thick moustache, brown batik, green check sarung |
| Ronda_rig | Pak Ronda | green beanie, camo jacket, sarung around neck |
| Melati_rig / MelatiK_rig | Melati (white dress / blue factory uniform + red shoes) | long black hair |
| Darmi_rig, Joko_rig, Bima_rig, Rina_rig, Sarip_rig, Karto_rig | Bu Darmi (warung), Mas Joko, Detektif Bima (fedora), Mbak Rina (factory), Pak Sarip (kemenyan seller), Mbah Karto (dukun, blangkon, white beard) | see chars4.py |
Faces: atlas 4x4 tiles. Eyes: 0 normal,1 blink,2 wide,3 happy,4 deadpan,5 annoyed,6 sad,7 proud,8 brow-up,9 confused,10 look-up,11 panic,12 soft,13/14 glance,15 blush.
Mouth: 0 rest,1 A(MBP),2 B,3 C,4 D,5 E,6 F,7 G,8 H (Rhubarb visemes),9 smile,10 laugh,11 O,12 flat,13 frown,14 smirk,15 wavy.
Rotation convention: rig front = (sin θ, −cos θ) for rotation_z θ → 0 faces −Y, 90 faces +X, −90 faces −X, 180 faces +Y.

## Set coordinates (Blender units; figure ≈ 3.2 tall)
| Set | Where |
| --- | --- |
| Nayla's room (kamar 3 interior) | origin; window x=−1 on back wall y=4.55; door right wall x=4.48 |
| Kos exterior | X≈100: units cx = 92.5/97.5/102.5/107.5 (kamar 1–4), doors at cx−1.0, windows cx+1.2, teras z=0.3 y −2.6..0; Ibu Kos house x 110–120 (teras z 0.35); jemuran x=87; gang y −10..−3; neighbour houses y≈−15.5 |
| Kamar 4 interior | X=50 (front wall + door pivot PIV_k4door at x 49.6, y −3.05; neon L_neon) |
| Pos ronda | (80, −7.2); bale top z≈0.93; book BUKU at (78.6,−8.05) |
| Ruang tamu Ibu Kos | X=150 |
| Pabrik sepatu 200 · Sungai & sawah 250 · Pasar 300 · Gubuk dukun 350 · Papan petunjuk 400 · Warung Bu Darmi (86,−10.6) |

## Story so far
1. Ep1 Perkenalan — Nayla, HI student, kos/kampus/kota.
2. Ep2 Tetangga Baru di Kamar 4 — mysterious occupant, green flickering light, white dress, jasmine, laughter → kuntilanak; twist: Ibu Kos never rented kamar 4.
3. Ep3 Penghuni Kamar 4 — Ibu Kos admits Melati lived there and vanished 7 years ago; Pak RT's register: Sinta 2005, Ratna 2012, Melati 2019 all vanished from kamar 4 (every 7 years); last page in wet ink "Kamar 4 — Nayla — 2026"; Nayla's door plate 3 falls revealing 4.
4. Ep4 Hilangnya Melati — Pak RT narrates: Melati kind, worked at shoe factory; green flicker, break-in, shoes & bag by river; Detektif Bima: candle ring + incense in room, red shoes were an anonymous gift (Mbak Rina), Melati bought candles "for someone" (Bu Darmi), incense bought at market by a masked villager (Pak Sarip) → dukun Mbah Karto: "the one who asked is always close to the victim; every 7 years". Culprit unknown; suspicion seeded on Ibu Kos, Bu Darmi, Pak Ronda, Mas Joko, Pak RT.
