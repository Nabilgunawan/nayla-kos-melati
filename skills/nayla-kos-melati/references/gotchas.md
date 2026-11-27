# Gotchas learned in production

- **User laptop**: Lenovo IdeaPad Slim 3, Ryzen 3, AMD integrated GPU, Blender 5.3 at D:\blender.exe, Windows PowerShell.
  EEVEE shadow pool >64 MB or <32 MB makes all lamps go dark; Vulkan/OpenGL driver crashes happened before a driver update.
  Use `render.py -- gpu 7` (pool 64 MB, resolution 0.5, **only the sun casts shadows**). Design lighting so the key light is a sun/moon.
  Cycles CPU fallback (`tescpu`/`cpu`) is ~26 h per 2 min — avoid.
- render.py deletes corrupt/partial PNGs (IEND check) and resumes; encode.py refuses missing/corrupt frames. Tell user to disable sleep.
- Sandbox: 1 CPU, no GPU, **300 s per command** → run bakes/renders with `nohup … &` then `sleep` and poll. EEVEE in sandbox cannot do shadows (looks dark) → preview with Cycles.
- `lib.mat()` caches by colour/params, so the `name=` argument may not be the real material name; look materials up via objects (e.g. `O["Sarip_hand.L"].data.materials[0]`).
- `/bin/sh` has no brace expansion — loop over filenames.
- Seated characters' legs stick forward and can block inserts (move props away from legs); hide the `phone` objects unless needed; set ceilings `visible_camera=True` when the camera looks up.
- Sign planes on back walls: rot=(90°,0,0) faces −Y; (90°,0,180°) faces +Y (else mirrored text).
- Flashbacks are desaturated in encode (ADJUSTMENT strips), not in render.
- ElevenLabs: Eleven v4, English tags in [brackets]; the user's files are named loosely (e.g. `Nayla_eps_3__2_.mp3`) — map by speaker.
- Never put Pixabay/Freesound raw files or the user's trailer music in the public repo.
- GitHub sync: run `gh_sync.py` in the FOREGROUND with `timeout 270` and simply re-run until it prints `Selesai` (it skips files already uploaded). Background jobs can be killed between tool calls.
- Never use `pkill -f <pattern>` or awk/grep kill loops whose pattern also matches your own command line — it kills the tool shell. Kill by explicit PID.
- The user's GitHub token must never be written into the skill, memory, or any repo file; ask for it per session.

## Three.js pipeline (learned Nov 2026)
- Sandbox has no GPU: Playwright Chromium + SwiftShader works for WebGL2 tests (~1–4 s/frame); Blender module = `bpy==5.0.1` in a uv venv (py3.11).
  Background jobs: `setsid nohup … &` survives between tool calls only within a session; the container can restart — make bakes resumable (segbake skips groups whose `lm_X.exr` exists).
- glTF exporter splits object animation into several clips even with `export_animation_mode='SCENE'` → play **all** `gltf.animations`.
- Procedural textures using Generated/Object coordinates change when objects are joined → segbake stores them as per-vertex attributes `gen`/`objco` before joining.
- Cycles DIFFUSE bake (no colour) = irradiance; Three.js MeshBasicMaterial lightMap already multiplies by 1/π, matching Cycles. Point/spot lights: three intensity = Blender W / (4π).
- Lightmap EXR (DataTexture) needs `repeat(1,-1), offset(0,1)`; albedo PNG/JPG needs `flipY=false`; both on `channel=1` (LM UV).
- Blender world/probe equirect == Three.js equirect with no rotation when the pano camera rotation is (90°,0,−90°).
- Chromium in the sandbox has no AAC encoder → Opus fallback; Chrome on Windows uses AAC + hardware H.264.
- Exposure: Three.js reads ~15 % darker than Cycles at night → exposure 1.55 (day 1.2).

## Episode render (learned on Ep 5, Nov 2026)
- Package = folder `render_epNN/` with `render_epNN.html` + `data/manifest.js`, `data/media.js`, one `data/env_<key>.js` per baked environment and one `data/seg_<id>.js` per segment (plain `<script>` files work from file://; fetch of local files does not). Built by `pipeline/web/episode/buildep.py`; player code = `ph_head.html` + `ph_tone.js` + `ph_body.js`.
- The player loads an environment/segment only when the render reaches it, disposes the previous one, and prefetches the next segment's scripts in the background (a 226 MB package fits a laptop and even the 3 GB sandbox).
- **Never seek a <video> per frame** (50–200 ms per frame). TV/monitor footage is pre-extracted as JPEG frames at 30 fps (`scale=-2:360`, q 5) for only the time ranges used, decoded with createImageBitmap (~2.5 ms/frame).
- glTF exporter does NOT export the armature OBJECT's own motion (only bone tracks) → segprep stores each rig's world transform per frame in `meta.rigpos` and the player applies it to the `<rig>_pos` node. Without this, characters stay where they were at the segment's first frame.
- Phone/screen inserts look better as a 2D overlay (device mock-up drawn on the composite canvas over a cheap downscaled blur of the scene) than a 3D camera over the shoulder, which always clips into the hair.
- Canvas textures applied to glTF materials need `flipY=false`.
- Sandbox: background processes are killed when a reply ends → keep the chain resumable (`run_epNN.sh` skips finished outputs) and poll with `sleep` inside the turn. Never run a Playwright test while a bake runs (OOM kills the bake). 16 spp + OIDN denoise is enough: ~13 min per exterior environment, ~4 min per room.
- Exposure per environment lives in the manifest (`exposure`): rooms 1.2, dusk 1.4, TV-lit room 1.5, night exterior 1.55.
- Floor sitting (no knee bones): root z = floor − 0.88, legs −88°, spine +6°; holding a controller = `ep5lib.hold()` (searches the arm angle until both hands reach the grips, parents the pad to `hand.R`).

## Quality bar (user feedback on Ep 5, reference: Kacaurus)
- No automatic idle wobble: only slow breathing (spine 0.35°) and tiny braid sway. Cameras static within a shot.
- Narration (Nayla's monologue lines) = Nayla to camera in her room, medium close-up (cam (0.8,-2.6,2.78) → (0.8,0.4,2.62), 42 mm).
- Phones: hold in front of the chest, screen toward the face (arm.R -58°/z -26°, hand.R -50°); showing a phone = arm straight (-82°), hand.R Y 180°. Screen content = 2D insert (device mock-up) for readable, stable screens.
- Visibility by scale must also go into `meta.objscale` (constant scale tracks are dropped by the glTF exporter); player applies it per frame.
- Look: DOF (BokehPass, focus = camera→target distance, aperture 0.0012) + soft bloom (0.28), brighter exposure (rooms 1.4–1.45, night 1.75–1.85).
- Captions: 1–3 words, CAPS, Oswald 700 with a coloured speaker pill (Nayla pink, Dimas blue); narration in yellow without pill.
- Rooms must be closed (front wall) and tidy; avoid clutter props.
- Bust default 0.11 (user choice).
