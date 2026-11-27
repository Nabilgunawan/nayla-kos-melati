#!/bin/sh
# Ep5 revisi: sets -> anim -> segprep 13 segmen -> bake ulang 2 env kamar Dimas -> mix. Bisa dilanjutkan.
cd /tmp/w/ep5; PY=/tmp/bv/bin/python; WEB=/home/claude/nayla-kos-melati-main/pipeline/web
[ -f v2.sets ] || { $PY sets5.py > sets5.log 2>&1 && touch v2.sets; }
[ -f v2.anim ] || { $PY anim5.py > anim5.log 2>&1 && touch v2.anim; }
export DYN_FORCE=KONSOL_,STIK_meja,k1_door,k1_doorknob,k_door,k_doorknob DYN_MATS=tv_layar
python3 -c "
import json
for s in json.load(open('segments.json')): print(s['id'],s['F0'],s['F1'],s['focus'][0],s['focus'][1],s['env'])" > seglist.txt
while read id f0 f1 fx fy env; do
  [ -f segv2_$id/dyn.glb ] || $PY $WEB/segprep.py -- ep05.blend $f0 $f1 segv2_$id $fx $fy > segv2_$id.prep.log 2>&1
done < seglist.txt
for env in E_k1sore E_k1malam; do
  id=$(grep " $env\$" seglist.txt | head -1 | cut -d' ' -f1); fx=$(grep " $env\$" seglist.txt | head -1 | cut -d' ' -f4); fy=$(grep " $env\$" seglist.txt | head -1 | cut -d' ' -f5)
  d=segv2_$id
  [ -f $d/env.glb ] || $PY $WEB/segbake.py -- /tmp/w/ep5/$d $fx $fy 2048 16 > $d.bake.log 2>&1
  [ -f $d/lm_A_c.exr ] || $PY $WEB/dncomp.py -- /tmp/w/ep5/$d > $d.dn.log 2>&1
  [ -f $d/sky.exr ] || $PY $WEB/segprobe.py -- /tmp/w/ep5/$d $fx $fy 1.4 > $d.probe.log 2>&1
  mkdir -p env_$env && cp $d/env.glb $d/env.json $d/lm_*_c.exr $d/al_*.jpg $d/probe.exr $d/sky.exr env_$env/
  echo "$env selesai $(date +%H:%M)" >> progress2.txt
done
[ -f v2.mix ] || { $PY mix5.py > mix5.log 2>&1 && touch v2.mix; }
echo ALL DONE >> progress2.txt
