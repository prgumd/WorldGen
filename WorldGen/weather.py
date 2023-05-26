import bpy

from .utils import new_plane, new_sphere, add_wind

def addWeather(self, sky_hdri='', lighting='midday', weather='clear', hdri_img=''):

    # Remove all worlds
    for i, world in enumerate(bpy.data.worlds):
        bpy.data.worlds.remove(bpy.data.worlds[i])
    if not sky_hdri == '':
        hdri_img = sky_hdri
    else:
        # three options : midday, sunset, night
        if lighting == "midday":
            if hdri_img == "":
                hdri_img = "https://polyhaven.com/a/sunflowers_puresky"
        
        elif lighting == 'sunset':
            if hdri_img == "":
                hdri_img = "https://polyhaven.com/a/the_sky_is_on_fire"
        
        else:
            # night
            if hdri_img == "":
                hdri_img = "https://polyhaven.com/a/moonlit_golf"
    
    bpy.ops.object.lily_world_import(url=hdri_img) # creates the world for us
    bpy.data.worlds[0].node_tree.nodes["Mapping"].inputs[1].default_value[2] = 1.0
    bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

    # three options : rain, cloudy, clear, fog
    # if weather == 'cloudy':
    # if weather == 'fog':
    # if weather == 'rain':
    # Add a plane
    if weather == 'rain':
        terrain_dim = bpy.data.objects["Terrain"].dimensions
        rain_plane = new_plane((0,0,200), 1.0, "rain_plane")
        # print('rain obj: ', rain)
        # bpy.data.objects["rain_plane"].dimensions = bpy.data.objects["Terrain"].dimensions
        rain_plane.dimensions = bpy.data.objects["Terrain"].dimensions
        bpy.context.view_layer.objects.active = rain_plane
        mat = bpy.data.materials.new(name='rain_surface_material')
        mat.use_nodes = True
        rain_plane.data.materials.append(mat)
        mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.0
        rain_plane.active_material = mat

        # adding a particle system
        bpy.ops.object.particle_system_add()
        particles = bpy.data.particles[0]
        particles.render_type = 'OBJECT'
        rain_drop = new_sphere(location=(0,0,-10), scale=(0.1, 0.1, 1.525), name="rain_drop")
        rain_drop.dimensions = (0.2, 0.2, 3.05)

        particles.instance_object = rain_drop
        particles.lifetime = 180
            
    if weather == 'fog':
        scene = bpy.context.scene
        scene.view_layers["ViewLayer"].use_pass_mist = True
        scene.use_nodes = True

        nodes = scene.node_tree.nodes

        mist = bpy.data.worlds[scene.world.name].mist_settings
        mist.use_mist = True
        mist.intensity = 0.4
        mist.depth = 40
        mist.start = 1

        file_output_node = nodes.get('Composite')
        render_layer_node = nodes.get('Render Layers')
        mix_rgb_node = nodes.new('CompositorNodeMixRGB')

        scene.node_tree.links.new(render_layer_node.outputs["Image"], mix_rgb_node.inputs["Image"])
        scene.node_tree.links.new(render_layer_node.outputs["Mist"], mix_rgb_node.inputs["Fac"])
        # scene.node_tree.links.new(mix_rgb_node.outputs["Image"], compositor_node.inputs["Image"])



    bpy.ops.wm.save_as_mainfile(filepath=self.filepath)



