# Nayla — Kos Melati

Animasi 3D figur mainan (Blender 5.x, dirender EEVEE) tentang Nayla, mahasiswi HI penghuni kamar 3 Kos Melati.
Semua karakter, set, animasi, dan audio dibangun lewat script Python bersama Claude.

## Isi repo
| Folder | Isi |
| --- | --- |
| `pipeline/` | Modul bersama: `lib.py` (helper model & material), `char.py` (generator figur mainan), `chars*.py` (definisi karakter), `alignp.py` (penyelarasan naskah–audio), `render.py`, `encode.py`, script prototipe Nayla |
| `assets/tex/` | Atlas wajah (`eyes.png`, `mouth.png`), papan nama, buku warga, foto Melati, dll. |
| `assets/hdri/` | HDRI siang, sore, malam (Poly Haven, CC0) |
| `assets/sfx_cc0/` | 151 suara Kenney (CC0) |
| `skills/nayla-kos-melati/` | Salinan skill Claude untuk seri ini (selalu diperbarui bila skill berubah) |
| `episodes/epXX/` | Script set, timeline, animasi, mix, encode, naskah, rekaman suara, lip-sync |

## Releases
Zip siap render setiap episode (`Nayla_EpsN.zip`, berisi `.blend` lengkap dan audio final) disimpan sebagai lampiran di halaman **Releases**.

## Aset pihak ketiga (disimpan di repo PRIVATE `nayla-kos-melati-private`)
Sound effect dan musik dari Pixabay/Freesound (musik trailer horor, ketukan, langkah, sungai, pabrik, kentongan, dll.)
tidak boleh disebarkan ulang sebagai file mentah, jadi disimpan di repo private terpisah. Di video, suara-suara itu sudah
tergabung di `audio/mix.wav` pada zip setiap episode.

## Lisensi
- Kode dan desain karakter: milik pemilik akun.
- `assets/hdri`: CC0 (Poly Haven). `assets/sfx_cc0`: CC0 (Kenney). `assets/fonts`: DejaVu (Bitstream Vera License).
