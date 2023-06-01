"""
Copyright 2023 Perception and Robotics Group, University of Maryland.

This code is part of the project to fragment objects in a 3D environment.
All rights reserved.

This software is provided "as is", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose and noninfringement. In no event shall the
authors or copyright holders be liable for any claim, damages or other
liability, whether in an action of contract, tort or otherwise, arising from,
out of or in connection with the software or the use or other dealings in
the software.
"""

import bpy
import yaml


def load_config(config_file):
    """Load configuration from a YAML file.
    
    Args:
        config_file (str): Path to the YAML configuration file.

    Returns:
        dict: Configuration dictionary.
    """
    
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def enable_addon(addon):
    """Enable a specific addon in Blender.
    
    Args:
        addon (str): The name of the addon to enable.
    """
    bpy.ops.preferences.addon_enable(module=addon)


def delete_all_mesh_objects():
    """Delete all mesh objects in the scene"""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

def import_object(filepath, scale):
    """Import an object from a file and scale it.
    
    Args:
        filepath (str): Path to the .obj file.
        scale (float): Scale factor for the object.

    Returns:
        bpy.types.Object: The imported object.
    """
    bpy.ops.import_scene.obj(filepath=filepath)
    bpy.ops.transform.resize(value=(scale, scale, scale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                             orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, 
                             proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False,
                             use_proportional_projected=False)

    return bpy.context.object
    
def fracture_object(obj, mesh_name, nObjects):
    """Fracture a given object using the cell fracture addon.
    
    Args:
        obj (bpy.types.Object): The object to fracture.
    """
    bpy.ops.object.add_fracture_cell_objects(source={'PARTICLE_OWN'},
                                             source_limit=nObjects,
                                             recursion=0, source_noise=0)

    # bpy.ops.object.add_fracture_cell_objects(source={'PARTICLE_OWN'},
    #         source_limit=100,
    #         source_noise=0,
    #         cell_scale=(1, 1, 1),
    #         recursion=0,
    #         recursion_source_limit=8,
    #         recursion_clamp=250,
    #         recursion_chance=0.25,
    #         recursion_chance_select='SIZE_MIN',
    #         use_smooth_faces=False,
    #         use_sharp_edges=True,
    #         use_sharp_edges_apply=True,
    #         use_data_match=True,
    #         use_island_split=True,
    #         margin=1e-6,
    #         material_index=0,
    #         use_interior_vgroup=False,
    #         mass_mode='VOLUME',
    #         mass=1,
    #         use_recenter=True,
    #         use_remove_original=True,
    #         collection_name="",
    #         use_debug_points=False,
    #         use_debug_redraw=True,
    #         use_debug_bool=False)
    bpy.ops.object.select_all(action='DESELECT')
    object_to_delete = bpy.data.objects[mesh_name[0]]
    bpy.data.objects.remove(object_to_delete, do_unlink=True)


def add_rigid_body_to_all_mesh_objects():
    """Add an active rigid body to all mesh objects in the scene.
    This will allow the objects to be affected by physics.
    """
    bpy.ops.object.select_all(action='SELECT')
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_add()
            obj.rigid_body.type = 'ACTIVE'


def create_ground(size=20, location=(0, 0, -1)):
    """Create a ground plane and add a passive rigid body to it.
    
    Args:
        size (float): The size of the ground plane.
        location (tuple): The coordinates of the ground plane in the scene.
    """
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
    ground = bpy.context.object
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = 'PASSIVE'  # Set the ground to passive, it will not move


def play_animation():
    """Start the animation"""
    bpy.ops.screen.animation_play()


def render_frames(output_path, frame_start, frame_end):
    """Render and save the frames as RGB images from frame_start to frame_end.
    
    Args:
        output_path (str): Directory where the rendered frames will be saved.
        frame_start (int): The start of the frame range.
        frame_end (int): The end of the frame range.
    """
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    # Load configuration from YAML file
    config = load_config('FragConfig.yaml')
    
    # Enable necessary addon
    enable_addon(config['addon'])
    
    # Delete all existing mesh objects in the scene
    delete_all_mesh_objects()
    
    # Import and fracture the object
    obj = import_object(config['filepath'], config['scale'])
    mesh_name = [obj.name for obj in bpy.data.objects if obj.type == 'MESH']
    mesh = mesh_name[0]
    fracture_object(obj, mesh_name, config['nObjects'])
    
    # Add rigid body physics to all mesh objects
    add_rigid_body_to_all_mesh_objects()
    
    # Create a ground plane
    create_ground(config['ground_size'], tuple(config['ground_location']))
    
    # Save Current Blender File
    bpy.ops.wm.save_as_mainfile(filepath=config['output_blend_path'])

    # Render the animation frames
    for frame in range(config['frame_start'], config['frame_end'] + 1):
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = f"{config['output_path']}/frame_{str(frame).zfill(3)}"
        bpy.ops.render.render(write_still=True)
