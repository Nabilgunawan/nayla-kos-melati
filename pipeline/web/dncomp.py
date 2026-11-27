# denoise + kompres lightmap, kompres albedo
import bpy, sys, os
import sys
OUT=sys.argv[sys.argv.index('--')+1]; sc=bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
for g in ('A','B','G'):
    p=f'{OUT}/lm_{g}.exr'
    if not os.path.exists(p): continue
    img=bpy.data.images.load(p); sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x,sc.render.resolution_y=img.size; sc.render.resolution_percentage=100
    sc.render.use_compositing=True; ng=bpy.data.node_groups.new('C'+g,'CompositorNodeTree'); sc.compositing_node_group=ng
    i=ng.nodes.new('CompositorNodeImage'); i.image=img; d=ng.nodes.new('CompositorNodeDenoise')
    ng.interface.new_socket('Image',in_out='OUTPUT',socket_type='NodeSocketColor'); go=ng.nodes.new('NodeGroupOutput')
    ng.links.new(i.outputs[0],d.inputs['Image']); ng.links.new(d.outputs[0],go.inputs[0])
    sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
    s=sc.render.image_settings; s.file_format='OPEN_EXR'; s.color_depth='16'; s.exr_codec='DWAA'; s.color_mode='RGB'
    sc.render.filepath=f'{OUT}/lm_{g}_c.exr'; bpy.ops.render.render(write_still=True); print('dn',g,os.path.getsize(f'{OUT}/lm_{g}_c.exr')//1024,'KB')
try:
    from PIL import Image
    for g in ('A','B','G'):
        p=f'{OUT}/al_{g}.png'
        if os.path.exists(p): Image.open(p).convert('RGB').save(f'{OUT}/al_{g}.jpg',quality=88); print('jpg',g)
except ImportError: print('pasang pillow untuk mengubah albedo ke JPG')
