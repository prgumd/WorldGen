import os
import sys
import random
import logging
import bpy

sys.path.append(
    '/opt/homebrew/Caskroom/miniforge/base/lib/python3.9/site-packages')
sys.path.append('/opt/homebrew/bin/')

import cv2
import matplotlib.pyplot as plt
import numpy as np
from .camera import Camera

# depth, flow, normal, stereo
class Annotations : 
    def __init__(self, outputFolder, camera:Camera):
        """ 
        Args:
            outputFolder (string): File path to store generated images. 
            camera (Camera)
        """
        self.outputFilePath = outputFolder
        self.camera = camera
        
    def generateDepth(self, renderEngine="CYCLES"):
        """ 
        Generates depth for selected camera
        """
        bpy.context.scene.render.engine = renderEngine
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear default nodes
        for n in tree.nodes:
            tree.nodes.remove(n)
            
        # create input render layer node
        rl = tree.nodes.new('CompositorNodeRLayers')
        normalize = tree.nodes.new("CompositorNodeNormalize")
    
        links.new(rl.outputs[2], normalize.inputs[0])
        
        # create a file output node and set the path
        fileOutput1 = tree.nodes.new(type="CompositorNodeOutputFile")
        fileOutput2 = tree.nodes.new(type="CompositorNodeOutputFile")
        links.new(normalize.outputs[0], fileOutput1.inputs[0])
        links.new(normalize.outputs[0], fileOutput2.inputs[0])

        # render jpeg
        fileOutput1.format.file_format = 'JPEG'
        fileOutput2.base_path = os.path.join(self.outputFilePath, "depth/jpeg/")
        bpy.ops.render.render(write_still=True)

        # render openexr
        fileOutput2.format.file_format = 'OPEN_EXR'
        fileOutput2.base_path = os.path.join(self.outputFilePath, "depth/open-exr/")
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
    
    def generateSurfaceNormals(self, renderEngine="CYCLES"):
        """ 
        Generates surface normals for selected camera
        """

        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear existing nodes
        for n in tree.nodes:
            tree.nodes.remove(n)
        
        # create input render layer node
        rl = tree.nodes.new('CompositorNodeRLayers')
        fileOutput1 = tree.nodes.new(type="CompositorNodeOutputFile")
        links.new(rl.outputs[0], fileOutput1.inputs[0])

        bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
        shading = bpy.context.scene.display.shading
        shading.light = 'MATCAP'
        shading.color_type = 'OBJECT'
        shading.studio_light = 'check_normal+y.exr'
        
        bpy.context.scene.view_settings.view_transform = 'Standard'
     
    def generateStereo(self, baseline=0.5, renderEngine="CYCLES"):
        """ 
        Generates stereo for selected camera

        Args:
            baseline (int)
        """
        bpy.context.scene.render.engine = renderEngine
        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear existing nodes
        for n in tree.nodes:
            tree.nodes.remove(n)

        bpy.context.scene.render.use_multiview = True
        bpy.context.scene.render.views_format = 'STEREO_3D'

        # create input render layer node
        rl = tree.nodes.new('CompositorNodeRLayers')
        fileOutput1 = tree.nodes.new(type="CompositorNodeOutputFile")
        links.new(rl.outputs[0], fileOutput1.inputs[0])
        
        
        self.camera.obj.data.stereo.interocular_distance = baseline
        fileOutput1.base_path = os.path.join(self.outputFilePath, "stereo/")
        # bpy.ops.render.render(animation=True)
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)

        
        
# def generateDepth(path_dir):
#     """ Generates depth maps of format jpeg or openexr for the animation.

#     Args:
#         path_dir (str): The file path to store generated depth maps. A jpeg and open-exr folder is created here.

#     Returns:
#         None
#     """
    
#     # Set up rendering of depth map:
#     bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True

#     bpy.context.scene.use_nodes = True
#     tree = bpy.context.scene.node_tree
#     links = tree.links

#     # clear default nodes
#     for n in tree.nodes:
#         tree.nodes.remove(n)

#     # create input render layer node
#     rl = tree.nodes.new('CompositorNodeRLayers')

#     map = tree.nodes.new(type="CompositorNodeMapRange")

#     map.inputs[1].default_value = 0
#     map.inputs[2].default_value = 20
#     map.inputs[3].default_value = 0
#     map.inputs[4].default_value = 1

#     links.new(rl.outputs[2], map.inputs[0])
#     invert = tree.nodes.new(type="CompositorNodeInvert")
#     links.new(map.outputs[0], invert.inputs[1])

#     # create a file output node and set the path
#     fileOutput1 = tree.nodes.new(type="CompositorNodeOutputFile")
#     fileOutput2 = tree.nodes.new(type="CompositorNodeOutputFile")
#     links.new(invert.outputs[0], fileOutput1.inputs[0])
#     links.new(invert.outputs[0], fileOutput2.inputs[0])

#     # render jpeg
#     fileOutput1.format.file_format = 'JPEG'
#     fileOutput1.base_path = path_dir + "/depth/jpeg/a"
#     bpy.ops.render.render(write_still=True)

# #    # render openexr
#     fileOutput2.format.file_format = 'OPEN_EXR'
#     fileOutput2.base_path = path_dir + "/depth/open-exr/a"
#     bpy.ops.render.render(write_still=True)
    
#     bpy.ops.wm.save_as_mainfile(filepath="/Users/riyakumari/blender_project/blender-prm-riya/src/scene2depth.blend")




# def generateSurfaceNormals(path_dir):
#     """ Generates surface normal map of the animation.

#     Args:
#         path_dir (str): The file path to store generated depth map. Subfolders jpeg and open-exr are created as well.

#     Returns:
#         None
#     """
#     bpy.context.scene.use_nodes = True
#     tree = bpy.context.scene.node_tree
#     links = tree.links

#     bpy.context.scene.view_layers["ViewLayer"].use_pass_normal = True

#     # create nodes
#     rl2 = tree.nodes.new("CompositorNodeRLayers")
#     multiply = tree.nodes.new(type="CompositorNodeMixRGB")
#     multiply.blend_type = "MULTIPLY"
#     add = tree.nodes.new(type="CompositorNodeMixRGB")
#     add.blend_type = "ADD"
#     invert = tree.nodes.new(type="CompositorNodeInvert")
#     fileOutput3 = tree.nodes.new(type="CompositorNodeOutputFile")
#     fileOutput4 = tree.nodes.new(type="CompositorNodeOutputFile")
        
#     # create links
#     links.new(rl2.outputs[3], multiply.inputs[1])
#     links.new(multiply.outputs[0], add.inputs[1])
#     links.new(add.outputs[0], invert.inputs[1])
#     links.new(invert.outputs[0], fileOutput3.inputs[0])
#     links.new(invert.outputs[0], fileOutput4.inputs[0])


#     # render it
#     fileOutput3.format.file_format = 'JPEG'
#     fileOutput3.base_path = path_dir + "/surface_normal/jpeg"
    
#     fileOutput4.format.file_format = 'OPEN_EXR'
#     fileOutput4.base_path = path_dir + "/surface_normal/open-exr"
    
    

# def generateOpticalFlow(path_dir):
#     """ Generates optical flow map of the animation.

#     Args:
#         path_dir (str): File path to store generated images. A folder named /optical_flow/open-exr is created with the generated png images.

#     Returns:
#         None
#     """
    
#     settings.set_render_engine('CYCLES')
    
#     bpy.context.scene.use_nodes = True
#     tree = bpy.context.scene.node_tree
#     links = tree.links
#     print("tree: ", tree)

        
#     bpy.context.scene.view_layers["ViewLayer"].use_pass_vector = True
#     r3 = tree.nodes.new("CompositorNodeRLayers")
#     fileOutput5 = tree.nodes.new(type="CompositorNodeOutputFile")
#     links.new(r3.outputs["Vector"], fileOutput5.inputs[0])
    
#     fileOutput5.format.file_format = 'OPEN_EXR'
#     fileOutput5.base_path = path_dir + "/optical_flow/open-exr"
#     print("optical flow ..., ", path_dir)
# #    bpy.context.scene.render.filepath = path_dir + "/optical_flow/"
# #    bpy.ops.render.render(animation=True)
    
# #    bpy.ops.wm.save_as_mainfile(filepath="/Users/riyakumari/blender_project/blender-prm-riya/src/opticalFlow.blend")
    
    
    
# def generate360(path_dir, cam):
#     """ Generates 360 image for each frame of the animation.

#     Args:
#         path_dir (str): File path to store generated images. A folder named /360 is created with png images.
#         cam (bpy_types.Object): the camera that captures the 360 image.
        
#     Returns:
#         None
#     """
    
#     settings.set_render_engine('CYCLES')
#     cam.data.type = 'PANO'
#     cam.data.cycles.panorama_type = "EQUIRECTANGULAR"
    
#     bpy.context.scene.render.filepath = path_dir + "/360/frame"
#     bpy.context.scene.render.image_settings.file_format = "PNG"
#     bpy.ops.render.render(animation=True)



# def generateImageSeg(path_dir):
#     """ Generates segmentation map for each frame of  animation.

#     Args:
#         path_dir (str): File path to store generated images. A folder named /image_seg is created with png images.
        
#     Returns:
#         None
#     """
    
#     settings.set_render_engine('CYCLES')
#     bpy.context.scene.view_layers["ViewLayer"].use_pass_object_index = True
    
#     num_of_obj = len(bpy.data.objects)
#     print("numOfObj", num_of_obj)
# #    print("c", c)
#     c = int(255/num_of_obj)
#     pass_index = c
    
    
#     for object in bpy.data.objects:
#         object.pass_index = pass_index
#         pass_index = pass_index + c
#         print("object_passIndex", object.pass_index)
    
#     bpy.context.scene.use_nodes = True
#     tree = bpy.context.scene.node_tree
#     links = tree.links
    
#     r1 = tree.nodes.new("CompositorNodeRLayers")
    
#     divide = tree.nodes.new(type="CompositorNodeMath")
#     divide.operation = "DIVIDE"
#     divide.inputs[1].default_value= 255
    
#     fileOutput = tree.nodes.new(type="CompositorNodeOutputFile")
    
#     links.new(r1.outputs[2], divide.inputs[0])
#     links.new(divide.outputs[0], fileOutput.inputs[0])
    
#     fileOutput.format.file_format = 'PNG'
#     fileOutput.base_path = path_dir + "/image_seg/"
# #    bpy.ops.render.render(animation=True)
    
    
    
    

# def generateStereo(path_dir, cam, baseline):
#     """ Generates stereo images for the animation

#     Args:
#         path_dir (str) : File path to store all generated outputs.
#         cam (bpy_types.Object): the camera that captures the 360 and stereo iamges
#         baseline (float) : Distance between two stereo cameras.
        
#     Returns:
#         None
#     """
#     # Enable stereoscopy
#     bpy.context.scene.render.use_multiview = True
#     bpy.context.scene.render.views_format = 'STEREO_3D'
    
#     cam.data.stereo.interocular_distance = baseline
#     bpy.context.scene.render.filepath = path_dir + "/stereo/"
#     bpy.ops.render.render(animation=True)
    
    
    
# def generateDisparity(path_dir, cam, baseline):
#     """ Generates disparity map for each frame of the animation

#     Args:
#         path_dir_left (str): File path to store generated images. A folder named /360 is created with png images.
#         cam (bpy_types.Object): the camera that captures the 360 image.
        
#     Returns:
#         None
#     """
#     stereo_dir = path_dir + "/stereo/"
    
#     # Assumption: if stereo directory exists then the stereo images have been generated already
#     if not (os.path.isdir(stereo_dir)):
#         generateStereo(path_dir, cam, baseline)
    
    
    
#     _, _, files = next(os.walk(stereo_dir))
#     file_count = len(files)/2
#     # Make sure to delete the stereo folder before running again
#     # blender -b ball.blend -P main.py
#     for i in range(1,int(file_count + 1)):
#         left_img_path = stereo_dir + "{:04d}".format(i) + "_L.png"
#         right_img_path = stereo_dir + "{:04d}".format(i) + "_R.png"
        
#         left_img = cv2.imread(left_img_path,0)
#         right_img = cv2.imread(right_img_path,0)
        
# #        stereo = cv2.StereoBM_create(numDisparities=int(baseline), blockSize=15)
#         stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
#         disparity = stereo.compute(left_img ,right_img)
#         plt.imshow(disparity, cmap='magma')
# #        plt.show()
#         plt.pause(1)
#         plt.close()
# #        color = cv2.cvtColor(disparity,cv2.COLOR_GRAY2RGB)
# #        break
# #        cv2.imshow(disparity)
# #        key = cv2.waitKey(3000)#pauses for 3 seconds before fetching next image
# #        if key == 27:#if ESC is pressed, exit loop
# #            cv2.destroyAllWindows()
# #            break
        
        
        
# #        print(left_img)
# #    print("filecount : ", file_count)
    
    
# def generateAllOutputs(path, cam=None, baseline=0.5):
#     """ Calls the respective functions to create all possible outputs.

#     Args:
#         path_dir (str) : File path to store all generated outputs.
#         cam (bpy_types.Object): the camera that captures the 360 and stereo images
#         baseline (float) : optional; Distance between two stereo cameras. Default is 0.5.
        
#     Returns:
#         None
#     """
#     generateDepth(path)
#     generateSurfaceNormals(path)
#     generateOpticalFlow(path)
    
#     bpy.ops.render.render(animation=True)
    
# #    generateStereo(path, cam, baseline)
#     generateDisparity(path, cam, baseline)
    
#     generateImageSeg(path)
#     generate360(path, cam)
    
    
    
# def generateOutputs(path, output_arr, cam=None, baseline=0.5):
#     """ Calls the respective functions to render the type of outputs passed in.

#     Args:
#         path_dir (str) : File path to store all generated outputs.
#         outputArr (list<string>): List of outputs, can either be depth, normal, flow, 360, or stereo
#         cam (båpy_types.Object): the camera that captures the 360 image, only required if creating 360 or stereo images.
#         baseline (float) : optional; Distance between two stereo cameras. Default is 0.5.
    
#     Returns:
#         None
#     """
    
#     if 'depth' in output_arr:
#         generateDepth2(path)
#     if 'normal' in output_arr:
#         generateSurfaceNormals(path)
#     if 'flow' in output_arr:
#         print("path: ", path)
#         generateOpticalFlow(path)
        
#     if 'depth' in output_arr or 'normal' in output_arr or 'flow' in output_arr:
#         bpy.ops.render.render(animation=True)
        
#     if 'disparity' in output_arr:
#         generateDisparity(path, cam, baseline)
    
#     if 'stereo' in output_arr:
#         generateStereo(path, cam, baseline)
        
#     if 'image_seg' in output_arr:
#         generateImageSeg(path)
        
#     if '360' in output_arr:
#         generate360(path)
    
    
        

    

