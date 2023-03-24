
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
        

    # def addCameraToScene():
    #     """ Generates 360 image for each frame of the animation.
    #     Args:
    #         path_dir (str): File path to store generated images. A folder named /360 is created with png images.
    #         cam (bpy_types.Object): the camera that captures the 360 image.
            
    #     Returns:
    #         None
    #     """
    #     print("hi")
    
    # def setCameraPath(self, seconds):
    #     """ Generates 360 image for each frame of the animation.
    #     Args:
    #         seconds (int) : length of video
            
    #     Returns:
    #         None
    #     """
    #     print("hi")
    
    # def cameraDistortion(self):
    #     print("hi")
    