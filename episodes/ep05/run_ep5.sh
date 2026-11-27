#!/bin/sh
# Pipeline Ep5: anim -> segprep (9 segmen) -> bake/denoise/probe (7 env). Bisa dilanjutkan (lewati yang sudah ada).
cd /tmp/w/ep5; PY=/tmp/bv/bin/python; WEB=/home/claude/nayla-kos-melati-main/pipeline/web
[ -f anim.done ] || { $PY anim5.py > anim5.log 2>&1 && touch anim.done; }
export DYN_FORCE=KONSOL_,STIK_meja,k1_door,k1_doorknob,k_door,k_doorknob DYN_MATS=tv_layar
for row in A:1:124:95.5:-1.5 B:125:313:1.8:0.0 C:314:495:102.5:-1.5 D:496:561:448.5:0.5 E:562:608:98.5:-2.0 F:609:1119:448.5:0.6 G:1120:1167:97.5:-1.5 H:1168:1311:93.0:-2.5 I:1312:1480:450.5:0.0; do
  id=$(echo $row|cut -d: -f1); f0=$(echo $row|cut -d: -f2); f1=$(echo $row|cut -d: -f3); fx=$(echo $row|cut -d: -f4); fy=$(echo $row|cut -d: -f5)
  [ -f seg_$id/dyn.glb ] || $PY $WEB/segprep.py -- ep05.blend $f0 $f1 seg_$id $fx $fy > seg_$id.prep.log 2>&1
done
for row in B:1.8:0.0:1.5 D:448.5:0.5:1.4 F:448.5:0.6:1.4 A:95.5:-1.5:2.2 E:98.5:-2.0:2.2 G:97.5:-1.5:2.2 H:93.0:-2.5:2.2; do
  id=$(echo $row|cut -d: -f1); fx=$(echo $row|cut -d: -f2); fy=$(echo $row|cut -d: -f3); fz=$(echo $row|cut -d: -f4)
  [ -f seg_$id/env.glb ] || $PY $WEB/segbake.py -- /tmp/w/ep5/seg_$id $fx $fy 2048 32 > seg_$id.bake.log 2>&1
  [ -f seg_$id/lm_A_c.exr ] || $PY $WEB/dncomp.py -- /tmp/w/ep5/seg_$id > seg_$id.dn.log 2>&1
  [ -f seg_$id/sky.exr ] || $PY $WEB/segprobe.py -- /tmp/w/ep5/seg_$id $fx $fy $fz > seg_$id.probe.log 2>&1
  echo "$id selesai $(date +%H:%M)" >> progress.txt
done
echo ALL DONE >> progress.txt
