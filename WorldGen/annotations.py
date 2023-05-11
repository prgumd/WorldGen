import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import sys
import random
import logging
import bpy
import array

import cv2
import glob
import matplotlib.pyplot as plt
import numpy as np
from .camera import Camera
from .utils import select_objects, deselect_all_objects, get_obj_with_name, assign_pass_indexes


class Annotations : 
    def __init__(self, outputFolder, camera, is_fog:bool):
        """ 
        Args:
            outputFolder (string): File path to store generated images. 
            camera (Camera)
        """
        self.outputFilePath = outputFolder
        print("file path : ", os.path.exists(self.outputFilePath))
        if not os.path.exists(self.outputFilePath):
            os.makedirs(self.outputFilePath)


        if camera==None:
            camera_names = [cam.name for cam in bpy.data.cameras]
            camera = bpy.data.objects[camera_names[0]]
        self.camera = camera
        self.is_fog = is_fog
        self.view_layer = bpy.context.scene.view_layers[0]

        self.view_layer.use_pass_z = True
        bpy.context.view_layer.cycles.denoising_store_passes = True
        self.view_layer.use_pass_normal = True
        self.view_layer.use_pass_object_index = True

    def generateOutputs(self, arrOfOutputs, classNames):

        # classNames - if semantic segmentation, then must specify class names
        # if fog, every channel creates its own mix node

        bpy.context.scene.use_nodes = True #common
        self.tree = bpy.context.scene.node_tree

        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles.samples = 8
       
        self.rl = self.tree.nodes.new('CompositorNodeRLayers')
        
        if 'depth' in arrOfOutputs:
            self.generateDepth()
                 
        if 'stereo' in arrOfOutputs:
            self.generateStereo()

        if 'semantic_seg' in arrOfOutputs:
            self.generateSemanticSeg(classNames)

        if 'flow' in arrOfOutputs:
            self.generateFlow()

        bpy.ops.render.render(animation=True, write_still=True)
        if 'depth' in arrOfOutputs:
            self.convertDepthToPlasma()
        if 'flow' in arrOfOutputs:
            folder_dir = self.outputFilePath + "/flow/metric/"

        
    def generateDepth(self, renderEngine="CYCLES"):
        """ 
        Generates depth for selected camera
        """
            
        # create input render layer node
        normalize = self.tree.nodes.new("CompositorNodeNormalize")
        links = self.tree.links


        fileOutput = self.tree.nodes.new(type="CompositorNodeOutputFile")
        fileOutput.file_slots.clear()

        fileOutput.layer_slots.new("depth_metric")

        # create a file output node and set the path
        links.new(self.rl.outputs["Depth"], normalize.inputs[0])
        if self.is_fog:
            mix_node = self.tree.nodes.new('CompositorNodeMixRGB')
            links.new(self.rl.outputs["Mist"], mix_node.inputs["Fac"])
            links.new(normalize.outputs[0], mix_node.inputs["Image"])
            links.new(mix_node.outputs[0], fileOutput.inputs["depth_metric"])
        else:    
            links.new(normalize.outputs[0], fileOutput.inputs["depth_metric"])
        

        fileOutput.format.file_format = "OPEN_EXR"
        fileOutput.base_path = self.outputFilePath + "/depth/metric/"

    def generateStereo(self, baseline=0.5, renderEngine="CYCLES"):
        """ 
        Generates stereo for selected camera

        Args:
            baseline (int)
        """
        # bpy.ops.scene.new(type='FULL_COPY')
        # cloneScene = bpy.context.scene
        # cloneScene.name = 'clone'

        links = self.tree.links

        bpy.context.scene.render.use_multiview = True
        bpy.context.scene.render.views_format = 'STEREO_3D'


        fileOutput = self.tree.nodes.new(type="CompositorNodeOutputFile")
        fileOutput.file_slots.clear()

        # create input render layer node
        fileOutput.layer_slots.new("stereo")
        if self.is_fog:
            mix_node = self.tree.nodes.new('CompositorNodeMixRGB')
            links.new(self.rl.outputs["Mist"], mix_node.inputs["Fac"])
            links.new(self.rl.outputs[0], mix_node.inputs["Image"])
            links.new(mix_node.outputs[0], fileOutput.inputs["stereo"])
        else:    
            links.new(self.rl.outputs[0], fileOutput.inputs["stereo"])
        
        
        self.camera.obj.data.stereo.interocular_distance = baseline
        fileOutput.base_path = self.outputFilePath + "/stereo/"
        fileOutput.format.file_format = "PNG"

    
    def generateSemanticSeg(self, classNames):
        deselect_all_objects()

        colorRampColors = [
            ('pink', (0.55, 0.15, 0.347,1)),
            ('dark_pink', (.28,.25,.21,1)),
            ('green', (0.019, 0.5, 0.038, 1)),
            ('brown', (0.02, 0, 0.01, 1)),
            ('very_light_brown', (0.88, 0.61, 0.22, 1)),
            ('very_light_yellow', (0.55, 0.55, 0.23, 1)),
            ('very_light_yellow', (0.08, 0, 0.05, 1)),
        ]

        # Merge classes
        # for name in classNames:
        #     collection = bpy.data.collections[name]
        #     if len(collection.all_objects) > 3:
        #         select_objects(collection, True)
        #         bpy.context.view_layer.objects.active = collection.all_objects[0]
        #         bpy.ops.object.join()
        #         select_objects(collection, False)
        #         bpy.context.view_layer.objects.active = None
        
        # loop thru the classes and give each a pass index
        assign_pass_indexes(classNames)
        valueNode = self.tree.nodes.new(type="CompositorNodeValue")
        valueNode.outputs[0].default_value = len(classNames)

        divideNode = self.tree.nodes.new(type="CompositorNodeMath")
        divideNode.operation = "DIVIDE"
        colorRamp = self.tree.nodes.new(type="CompositorNodeValToRGB")
        
        for i in range(len(classNames)):
            colorRamp.color_ramp.elements.new(i/len(classNames))
            colorRamp.color_ramp.elements[i].color = colorRampColors[i][1]

        fileOutput = self.tree.nodes.new(type="CompositorNodeOutputFile")
        fileOutput.file_slots.clear()
        fileOutput.layer_slots.new("semantic_seg")
        fileOutput.format.file_format = "PNG"
        fileOutput.base_path = self.outputFilePath + "/semantic_seg/"

        links = self.tree.links
        links.new(self.rl.outputs["IndexOB"], divideNode.inputs[0])
        links.new(valueNode.outputs[0], divideNode.inputs[1])
        links.new(divideNode.outputs[0], colorRamp.inputs[0])

        if self.is_fog:
            mix_node = self.tree.nodes.new('CompositorNodeMixRGB')
            links.new(self.rl.outputs["Mist"], mix_node.inputs["Fac"])
            links.new(colorRamp.outputs[0], mix_node.inputs["Image"])
            links.new( mix_node.outputs[0], fileOutput.inputs["semantic_seg"])
        else:    
            links.new(colorRamp.outputs[0], fileOutput.inputs["semantic_seg"])

    def generateFlow(self):
        fileOutput = self.tree.nodes.new(type="CompositorNodeOutputFile")
        fileOutput.file_slots.clear()

        fileOutput.layer_slots.new("flow_metric")
        links = self.tree.links

        
        if self.is_fog:
            mix_node = self.tree.nodes.new('CompositorNodeMixRGB')
            links.new(self.rl.outputs["Mist"], mix_node.inputs["Fac"])
            links.new(self.rl.outputs["Normal"], mix_node.inputs["Image"])
            links.new(mix_node.outputs[0], fileOutput.inputs["flow_metric"])
        else:    
            links.new(self.rl.outputs["Normal"], fileOutput.inputs["flow_metric"])
        
        fileOutput.format.file_format = "OPEN_EXR"
        fileOutput.base_path = self.outputFilePath + "/flow/metric/"

    def convertDepthToPlasma(self):
        dir = self.outputFilePath + "/depth/metric/"
        save_dir = self.outputFilePath+"/depth/"

        # loop through images in the directory
        for filename in os.listdir(dir):
            img = self.get_exr_rgb(dir+filename)
            if not os.path.isdir(save_dir+"viz/"):
                os.mkdir(save_dir+"viz/")
            filename = os.path.splitext(os.path.basename(filename))[0]
            im = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img= cv2.applyColorMap(im, cv2.COLORMAP_PLASMA)
            cv2.imwrite(save_dir + "viz" +filename + ".png", img)

    def get_exr_rgb(self, path):
        img = cv2.imread(path,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        # convert colour to sRGB
        img = np.where(img<=0.0031308, 12.92*img, 1.055*np.power(img, 1/2.4) - 0.055)
        return (img*255).astype(np.uint8)

    def Exr2Flow(self, exrfile):
        file = OpenEXR.InputFile(exrfile)

        # Compute the size
        dw = file.header()['dataWindow']
        ImgSize = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        [Width, Height] = ImgSize


        # R and G channel stores the flow in (u,v) (Read Blender Notes)
        FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
        (R,G,B) = [array.array('f', file.channel(Chan, FLOAT)).tolist() for Chan in ("R", "G", "B")]
        
        Img = np.zeros((Height, Width, 3), np.float64)
        Img[:,:,0] = np.array(R).reshape(Img.shape[0], -1)
        Img[:,:,1] = -np.array(G).reshape(Img.shape[0], -1)
	
        return Img, Width, Height

    def WriteFloFile(self, exrfile, Img, TAG_STRING, Width, Height):
        # Write to a .flo file: 
        # Ref: https://github.com/Johswald/flow-code-python/blob/master/writeFlowFile.py
        f = open(exrfile[:-4]+'.flo','wb')
        f.write(TAG_STRING)
        np.array(Width).astype(np.int32).tofile(f)
        np.array(Height).astype(np.int32).tofile(f)
        nBands = 2
        tmp = np.zeros((Height, Width * nBands))
        tmp[:,np.arange(Width)*2] = Img[:,:,0]
        tmp[:,np.arange(Width)*2 + 1] = Img[:,:,1]
        tmp.astype(np.float32).tofile(f)
        print("img : ", f.shape)
        f.close()
    
    def convertFlowToFlo(self, folder_dir):
        for image in os.listdir(folder_dir):
            if "exr" in image:
                exrfile = folder_dir+image
                TAG_STRING = 'PIEH'
                Img, Width, Height = self.Exr2Flow(exrfile)
                self.WriteFloFile(exrfile, Img, TAG_STRING, Width, Height)
    