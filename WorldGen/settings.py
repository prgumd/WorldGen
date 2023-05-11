import os
import sys
import random
import bpy



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

