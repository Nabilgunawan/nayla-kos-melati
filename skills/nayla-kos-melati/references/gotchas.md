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
