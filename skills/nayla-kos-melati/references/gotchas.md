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
