
class WorldGen:
    def __init__(self, filepath, isTwoWay = True):
        self.filepath = filepath
        self.isTwoWay = isTwoWay
    
    from .settings import set_image_resolution, set_metadata_properties, set_render_engine, set_camera, set_render
    from .simulator import Simulator
    from .annotations import Annotations
    from .camera import Camera

    # from .weather import Weather
    # blender-gpt
    
    

    