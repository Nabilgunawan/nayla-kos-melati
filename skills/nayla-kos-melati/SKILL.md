---
name: nayla-kos-melati
description: Production pipeline for the "Nayla — Kos Melati" 3D toy-figure animation series (Blender 5.x, EEVEE, 12 fps stop-motion, 1080x1920 vertical) — Nayla, Adel, Dimas, Ibu Kos (Bu Sari), Pak RT, Pak Ronda, Melati, kuntilanak, Detektif Bima, Mbah Karto and other NPCs at Kos Melati. Use this skill whenever the user mentions Nayla, Kos Melati, kamar 4, Melati, Pak RT, an episode number ("episode 5", "lanjut episode berikutnya"), ElevenLabs voice files for these characters, rendering/encoding an episode, render.py/encode.py errors, new characters or sets for this series, captions or profile assets for this TikTok/Instagram account — even if the skill is not named.
---

# Nayla — Kos Melati: production pipeline

Everything (characters, sets, animation, audio mix, subtitles) is built with Python in Blender inside the sandbox;
the user renders on their own laptop with `render.py` + `encode.py`. Read `references/world.md` for characters,
sets, coordinates and story so far; read `references/gotchas.md` before running anything heavy.

## 0. Restore the workspace (every new chat)
The sandbox starts empty. Assets live in a **public GitHub repo** (`Nabilgunawan/nayla-kos-melati`; ask the user for the
username if it is not in memory). Episode `.blend` zips are attached to the repo's **Releases**.
```bash
pip install uv --break-system-packages -q
uv venv -p 3.11 /tmp/bv -q && uv pip install -p /tmp/bv bpy==5.0.1 pillow numpy scipy -q    # Blender 5.0 as a module
uv venv -p 3.13 /tmp/b53 -q && uv pip install -p /tmp/b53 bpy -q                            # optional: user's Blender 5.3 for checks
curl -sL -o /tmp/rh.zip https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip && unzip -qo /tmp/rh.zip -d /tmp
curl -sL -o /tmp/repo.zip https://codeload.github.com/Nabilgunawan/nayla-kos-melati/zip/refs/heads/main && unzip -qo /tmp/repo.zip -d /home/claude
curl -s https://api.github.com/repos/Nabilgunawan/nayla-kos-melati/releases | grep browser_download_url   # then curl -L each zip you need
```
Scripts hard-code `/home/claude/epNN/...` and `/home/claude/sfxlib/cc0/`: recreate that layout
(e.g. copy `pipeline/*` + `episodes/epNN/*` into `/home/claude/epNN/`, `assets/tex` into `epNN/tex`,
`assets/sfx_cc0` into `/home/claude/sfxlib/cc0`). Latest base scene = `ep04_sets.blend` from the Ep 4 release zip
(`ep04.blend` has animation; rebuild sets from `sets4.py` if needed, which chains ep02→ep03 bases).

## 0b. GitHub sync rules (always follow)
Two repos: **public** `Nabilgunawan/nayla-kos-melati` (code, own assets, CC0, voices, skill) and **private**
`Nabilgunawan/nayla-kos-melati-private` (raw third-party SFX/music from Pixabay/Freesound — their licence forbids public
redistribution, so NEVER upload them to the public repo). Reading the public repo needs no token; any upload needs a
fine-grained token (Contents: read & write, both repos) that the user pastes **per session** — never save it to memory,
never echo it. Upload with `scripts/gh_sync.py --repo Nabilgunawan/<repo> --token $GH_TOKEN --src <local> --dst <repo path>`.
- When the user sends new assets (voices → `episodes/epNN/audio/`, own textures → `assets/tex/`, Pixabay/Freesound SFX
  or music → private repo `sfx/`), offer to sync them in the same turn if a token is available.
- After finishing an episode, sync `episodes/epNN/` (scripts, timeline.json, script txts, voices, lips) to the public repo.
  The episode zip (`Nayla_EpsN.zip`) goes to Releases — the user attaches it manually.
- **Whenever this skill changes** (new character, set, rule, gotcha, story recap): update the files under
  `skills/nayla-kos-melati/` in the public repo AND give the user a fresh `.skill` to reinstall. Keep the story recap
  in `references/world.md` current after every episode.
- Private repo download: `curl -sL -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/Nabilgunawan/nayla-kos-melati-private/zipball -o /tmp/priv.zip`.

## 1. Plan the episode (Claude Doc)
One doc per episode with sections: Konsep (logline, twist/peta misteri), Karakter, Struktur (per detik), Naskah VO
(ElevenLabs v4, **one file per character**, `[emotion]` tags in English, blank line between lines, an
"Urutan percakapan" table), Shot list (#, detik, lokasi, kamera, aksi, SFX), Kebutuhan produksi (sets, props, SFX list
with ElevenLabs prompts, what the user must supply), Caption TikTok/IG/YT, Benih episode berikutnya + keputusan.
Story: horror-comedy/mystery, unpredictable twists allowed; no gore. Never reproduce copyrighted meme audio;
the user adds viral sounds in CapCut.

## 2. Audio → timeline
1. Copy uploads to `epNN/audio/<speaker>.mp3`; make 16 kHz mono wavs.
2. `alignp.py audio/x16.wav s_x.txt <dur>` → paragraph (line) boundaries per file (DP on syllables vs silences).
3. Rhubarb: `rhubarb -r phonetic -f json -o audio/lips_x.json audio/x16.wav` (phonetic works for Indonesian).
4. `timelineN.py`: list of clips `(id, speaker, [src_start,src_end], subtitle_text, emotion, gap_before)` in story
   order → `dst` times; shots anchored with `st(id,offset)/en(id,offset)`; SFX cues `(time,name,gain_dB,max_dur)`.
   Episodes have run 120–195 s; long ones get `partA_end` and encode outputs UTUH + Part A + Part B.

## 3. Build & animate
- `setsN.py`: open previous `epXX_sets.blend`, add new chars (`charsN.py` → `make_char(name,cfg,origin)`), new sets at
  free X offsets, props, lights (**all non-sun lights `use_shadow=False`**). Save `epNN_sets.blend`.
- `animN.py`: per-frame keyframes at 12 fps for every rig (location, Z rotation, bone eulers), face atlas tiles
  (eyes/mouth Mapping Location), camera + `CAM_TGT`, light presets per set, props; set all fcurves CONSTANT; save `epNN.blend`.
- Preview with Cycles 270x480, 10–12 samples via `prevA.py -- f1,f2,... 270 12`; compose contact sheets; fix and rebake.

## 4. Mix & encode
- `mixN.py`: voices + ambience (crickets only outdoors at night, quiet) + user SFX + Kenney CC0 + horror-trailer music
  bed (user's file; silence right before jump scares) → duck under voice → loudnorm to **−14 LUFS**, TP ≈ −1.5.
- `encode.py` (Blender VSE): image sequence (each 12 fps frame twice → 24 fps), `audio/mix.wav`, bold subtitles with
  speaker labels for non-Nayla speakers, flashback ADJUSTMENT strips (saturation 0.2–0.35), black "BERSAMBUNG...?" end card.
  Test encode with dummy frames before packaging.

## 5. Package & hand off
Pack images into the blend (`image.pack()`), zip: `epNN.blend`, `render.py`, `encode.py`, `timeline.json`,
`audio/mix.wav`, `fonts/`, `source/`, `README.txt`. Deliver preview PNG sheet + preview mp3 + zip. User commands (PowerShell, Blender at D:\blender.exe):
```
cd "$HOME\Downloads\Nayla_EpsN\Nayla_EpsN"; $B = "D:\blender.exe"; & $B -b epNN.blend -P render.py -- gpu 7
& $B -b epNN.blend -P encode.py
```
