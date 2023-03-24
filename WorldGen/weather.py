import bpy
    #     self.weather = weather

def addWeather(self, lighting='midday', weather='clear', hdri_img=''):

    # Remove all worlds
    for i, world in enumerate(bpy.data.worlds):
        bpy.data.worlds.remove(bpy.data.worlds[i])

    # # Create a new world
    # new_world_name = lighting + " " + weather
    # new_world = bpy.data.worlds.new(new_world_name)
    
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

