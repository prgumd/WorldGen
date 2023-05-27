
import bpy
# from .simulator import Simulator


class Camera:
    def __init__(self, name):
        self.name = name
        self.obj = bpy.data.objects[name]

    def makeActive(self):
        """ 
        Sets this camera as active
        """
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj
        bpy.context.scene.camera = self.obj
        
