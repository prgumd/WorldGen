import os
import sys
import random
import bpy
import numpy as np

sys.path.append(
    '/opt/homebrew/Caskroom/miniforge/base/lib/python3.9/site-packages')
sys.path.append('/opt/homebrew/bin/')


def set_image_resolution(x, y, percent):
    bpy.context.scene.render.resolution_x = x
    bpy.context.scene.render.resolution_y = y
    bpy.context.scene.render.resolution_percentage = percent


def set_metadata_properties():
    bpy.context.scene.render.use_stamp_date = True
    bpy.context.scene.render.use_stamp_time = True
    bpy.context.scene.render.use_stamp_render_time = True
    bpy.context.scene.render.use_stamp_frame = True
    bpy.context.scene.render.use_stamp_frame_range = False
    bpy.context.scene.render.use_stamp_memory = False
    bpy.context.scene.render.use_stamp_hostname = False
    bpy.context.scene.render.use_stamp_camera = True
    bpy.context.scene.render.use_stamp_lens = True
    bpy.context.scene.render.use_stamp_scene = True
    bpy.context.scene.render.use_stamp_marker = False
    bpy.context.scene.render.use_stamp_filename = True
    bpy.context.scene.render.use_stamp_render_time = True
    bpy.context.scene.render.use_stamp_scene = True
    bpy.context.scene.render.use_stamp_sequencer_strip = False

def set_render_engine(type):
    bpy.context.scene.render.engine = type

def deselect_all_objects():
    for obj in bpy.data.objects:
        obj.select_set(False)

def set_camera(camera_settings):
    # setting field of view
    FIELD_OF_VIEW = camera_settings[0]['field_of_view']
    bpy.data.cameras['Camera'].lens_unit = 'FOV'
    bpy.data.cameras['Camera'].angle = FIELD_OF_VIEW * (np.pi / 180)
    bpy.context.scene.render.resolution_x = 640
    bpy.context.scene.render.resolution_y = 480
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.frame_end = camera_settings[3]['end_frame']

    bpy.context.scene.render.frame_map_new = camera_settings[5]['time_stretching']


    # #setting lens property
    # bpy.context.object.data.dof.focus_distance = camera_settings[8]['lens_focus_distance']
    # bpy.context.object.data.dof.aperture_fstop = camera_settings[9]['lens_aperture_fstop']
    # bpy.context.object.data.dof.aperture_ratio = camera_settings[10]['lens_aperture_ratio']

    bpy.context.scene.render.use_motion_blur = camera_settings[6]["motion_blur"] == "on"


def set_render(render_settings):
    bpy.context.scene.render.use_border = render_settings[0]['enable_render_region']
    bpy.context.scene.render.use_crop_to_border = render_settings[1]['enable_crop_to_render_region']
    bpy.context.scene.cycles.use_adaptive_sampling = render_settings[2]['render_noise_threshold']

    bpy.context.scene.cycles.samples = render_settings[3]['render_max_samples']
    bpy.context.scene.cycles.time_limit = render_settings[4]['render_time_limit']
    bpy.context.scene.cycles.use_denoising = render_settings[5]['render_denoiser']

    if render_settings[6]['enable_fast_GI']:
        bpy.context.scene.cycles.max_bounces = 8
        bpy.context.scene.cycles.diffuse_bounces = 1
        bpy.context.scene.cycles.glossy_bounces = 4
        bpy.context.scene.cycles.transmission_bounces = 8
        bpy.context.scene.cycles.volume_bounces = 2
        bpy.context.scene.cycles.transparent_max_bounces = 8
        bpy.context.scene.cycles.sample_clamp_direct = 0
        bpy.context.scene.cycles.sample_clamp_indirect = 10
        bpy.context.scene.cycles.blur_glossy = 1
        bpy.context.scene.cycles.use_fast_gi = True

    # bpy.context.object.data.clip_start = render_settings[7]['enable_camera_clipping'][0]
    # bpy.context.object.data.clip_end = render_settings[7]['enable_camera_clipping'][1]

    








