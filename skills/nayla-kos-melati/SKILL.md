---
name: "storyboard"
description: Production pipeline for the "Nayla — Kos Melati" 3D toy-figure animation series (Blender 5.x build/animate/bake, Three.js browser render, 12 fps keys → 24 fps Halus, 1080x1920 vertical) — Nayla, Adel, Dimas, Ibu Kos (Bu Sari), Pak RT, Pak Ronda, Melati, kuntilanak, Detektif Bima, Mbah Karto and other NPCs at Kos Melati. Use this skill whenever the user mentions Nayla, Kos Melati, kamar 4, Melati, Pak RT, an episode number ("episode 5", "lanjut episode berikutnya"), ElevenLabs voice files for these characters, rendering/encoding an episode (Three.js render page, WebCodecs MP4, light baking), render.py/encode.py errors, character looks (femme.py, hijab, blush), new characters or sets for this series, captions or profile assets for this TikTok/Instagram account — even if the skill is not named.
---

# Nayla — Kos Melati: production pipeline

Characters, sets, animation and light baking are built with Python in Blender inside the sandbox; the user renders on their own
laptop in Chrome with a self-contained Three.js HTML page (section 4) that writes the MP4 directly. Read `references/world.md` for characters,
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
- **Female characters: always run `pipeline/femme.py` after building/adding them** (`blender -b epNN_sets.blend -P femme.py -- [names] out.blend`):
  softer rounded torso with waist, bust (`BUST`, default 0.30 — chosen by the user; override with env FEMME_BUST), tapered limbs, arms closer to the body, khimar-style hijab
  (Adel, Bu Darmi: cap on `head` bone + drape on `spine` bone), cheek blush (`BLUSH` per character), flower hair clip on Nayla.
  It edits meshes in place (names, bones, materials, actions kept) and is idempotent for blush/clip. Female list: Nayla, Adel, Ibu, Melati, MelatiK, Darmi, Rina.
- `animN.py`: per-frame keyframes at 12 fps for every rig (location, Z rotation, bone eulers), face atlas tiles
  (eyes/mouth Mapping Location), camera + `CAM_TGT`, light presets per set, props; set all fcurves CONSTANT; save `epNN.blend`.
  Bone axes: bones point along their local Y, so **turning the head = local Y rotation**, nodding = local X, local Z = sideways tilt.
- Preview with Cycles 270x480, 10–12 samples via `prevA.py -- f1,f2,... 270 12`; compose contact sheets; fix and rebake.

## 4. Render with Three.js (default since Ep 5) — `pipeline/web/`
The user renders in Chrome/Edge on the laptop GPU (AMD Radeon iGPU, D3D11): ~18 ms/frame, a 190 s episode in ~1.5 min at 24 fps.
Blender stays for building, animating and **baking light**; frames are drawn by Three.js r170 and encoded to MP4 in the browser
(WebCodecs H.264 + AAC, mp4-muxer 5.2.2). Default output: **24 fps, style "Halus"** (12 fps keys interpolated; never across shot cuts),
1080x1920. Per segment (a run of shots, usually per set):
1. `segprep.py -- epNN.blend F0 F1 OUT fx fy` — samples every frame: camera, lights (static vs dynamic), emissive materials, face tiles;
   exports moving things (rigs + props that move) to `dyn.glb` (baked, slide-to-zero); writes `meta.json` and a frozen `frozen.blend`.
2. `segbake.py -- OUT fx fy 2048 32` — joins static meshes in groups A (near), B (far), G (huge ground, planar UV), bakes
   DIFFUSE irradiance (no colour) to `lm_X.exr` + albedo (`COLOR`, 4096) to `al_X.png`; exports `env.glb` (UV0 + LM). ~25 min for the kos exterior.
   One bake per set+light preset; reuse it for every shot in that combination.
3. `dncomp.py -- OUT` (denoise + DWAA EXR + albedo JPG), `segprobe.py -- OUT x y z` (512x256 light probe at the characters + world-only sky).
4. `mkseg.py timeline.json F0 F1 OUT mix.wav` — subtitles (encode.py style), cuts, flashback ranges, end card, FLAC audio slice.
5. `buildseg.py OUT slug "Judul" fonts/DejaVuSans-Bold.ttf fx [exposure]` → one self-contained `render_<slug>.html` (~30 MB per
   exterior segment). Test in the sandbox with Playwright + SwiftShader (`--use-angle=swiftshader`): `window.__snap(t,540)` returns a PNG.
Look: AgX + "Punchy"-like look (pow 1.15, sat 1.15), exposure 1.55 at night (1.2 day); light probe IBL 0.6 on characters; moon/sun is the
only real-time shadow; dynamic lights (flicker, senter) also light baked surfaces via a shader term; contact-shadow blob per rig;
automatic idle layer (breathing, hip sway, head drift, braid swing, relaxed arms); cheek blush per rig from `K.blush`.
Verify against 2–3 Cycles reference frames (540x960, 32 spp) before handing over.

## 5. Package & hand off
Deliver the HTML render page(s) + a sandbox-rendered 540p check MP4 + comparison sheet. The user opens the HTML in Chrome, picks
24 fps / Halus / 1080x1920, presses **Mulai render**, downloads the MP4 and the `_statistik.txt`, then adds viral sounds in CapCut.
Legacy path (EEVEE `render.py -- gpu 7` + `encode.py`) still works for old episodes but is no longer the default.
