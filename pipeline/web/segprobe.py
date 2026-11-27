import bpy, sys, math
a=sys.argv[sys.argv.index('--')+1:]; OUT=a[0]; P=(float(a[1]),float(a[2]),float(a[3]))
bpy.ops.wm.open_mainfile(filepath=f'{OUT}/frozen.blend')
sc=bpy.context.scene
cd=bpy.data.cameras.new('PANO'); cd.type='PANO'; cd.panorama_type='EQUIRECTANGULAR'
c=bpy.data.objects.new('PANO',cd); sc.collection.objects.link(c); sc.camera=c; c.rotation_euler=(math.pi/2,0,-math.pi/2)
sc.render.engine='CYCLES'; sc.cycles.use_denoising=True; sc.cycles.max_bounces=6
sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'; sc.view_settings.exposure=0
s=sc.render.image_settings; s.file_format='OPEN_EXR'; s.color_depth='16'; s.exr_codec='DWAA'; s.color_mode='RGB'
sc.render.resolution_percentage=100
c.location=P; sc.render.resolution_x=512; sc.render.resolution_y=256; sc.cycles.samples=128
sc.render.filepath=f'{OUT}/probe.exr'; bpy.ops.render.render(write_still=True); print('PROBE OK',flush=True)
for o in bpy.data.objects:
    if o.type in('MESH','CURVE'): o.hide_render=True
sc.render.resolution_x=2048; sc.render.resolution_y=1024; sc.cycles.samples=8; sc.cycles.use_denoising=False
sc.render.filepath=f'{OUT}/sky.exr'; bpy.ops.render.render(write_still=True); print('SKY OK')
