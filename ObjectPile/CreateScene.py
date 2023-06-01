#!/usr/bin/python3
# blender -b -P CreateSceneFromTemplate.py empty_scene.blend


import bpy, sys, random
from math import pi
import numpy as np

CamLocX, CamLocY, CamLocZ = (7.8049, 3.54512, 10.87)
CamRotX, CamRotY, CamRotZ = (45, 0, 90)

CubeLocX, CubeLocY, CubeLocZ = (-13.48, 1.84, -2)
CubeRotX, CubeRotY, CubeRotZ = (0, 0, 0)

CubeScaleX, CubeScaleY, CubeScaleZ = (35.4021, 46.0721, 1.19088)



"""
Import Libraries for Volume Estimation
"""
import bmesh  
from object_print3d_utils import (
    mesh_helpers,
    report,
)

# Remove All Meshes before the code starts
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()


# Paths
PATH_TO_GROUNDTEXTURE = "../textures/2.jpg"
PATH_TO_TEXTURE = "../textures/1.jpg"
PATH_TO_OBJECT_LIST = "OBJList.txt"
PATH_TO_TEXTURE_LIST = "/home/chahatdeep/git_cloned/blender-script/scripts/TextureList.txt"
TEXTURE_LIST_BASE_PATH = "/mnt/21DCE94650615B1A/Datasets"
BASE_PATH_FOR_SAVED_FRAMES = "/home/chahatdeep/Blender-Data/"
PATH_TO_SAVED_FRAMES = "Set2"
print(BASE_PATH_FOR_SAVED_FRAMES + PATH_TO_SAVED_FRAMES)

# Motion Parameters
bpy.context.scene.use_gravity = True

# Variable List:
GroundPlaneSize = 25
CollisionMargin = 0.5
RigidBodyFriciton = 0.5
nObjects = random.randint(6, 10) # Number of objects to be added
nFrames = 1


# import bpy


# Create Ground Plane (Passive):
def CreatePlane(GroundPlaneSize, CollisionMargin, PATH_TO_TEXTURE_LIST):
    UseCubeAsPlane = 1
    ## Not using Plane because a few objects goes through the plane. Known bug!
    if (UseCubeAsPlane == 0):
        # Create Passive Plane as the ground level
        bpy.ops.mesh.primitive_plane_add(size=GroundPlaneSize, enter_editmode=False, align='WORLD', location=(0,0,0))
        bpy.ops.rigidbody.object_add(type='PASSIVE') # Make it passive so it does not move!
        bpy.context.object.rigid_body.use_margin = True
        bpy.context.object.rigid_body.collision_margin = CollisionMargin
    
    elif (UseCubeAsPlane == 1):
        # Add a Cube
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        bpy.context.object.scale = [25, 25, 1]
        bpy.ops.rigidbody.object_add(type='PASSIVE') # Make it passive so it does not move!
        bpy.context.object.rigid_body.use_margin = True
        bpy.context.object.rigid_body.collision_margin = CollisionMargin
        bpy.context.object.location[2] = -2


    # Import and Create Material for the Texture:
    PassiveObject = bpy.context.view_layer.objects.active
    mat = bpy.data.materials.new(name='Texture')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    lines = open(PATH_TO_TEXTURE_LIST).read().splitlines()
    RandomTexture = random.choice(lines)
    RandomTexture = TEXTURE_LIST_BASE_PATH + RandomTexture # RandomTexture[26:]
    texImage.image = bpy.data.images.load(filepath=RandomTexture)
    # texImage.image = bpy.data.images.load(filepath=PATH_TO_GROUNDTEXTURE) 
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    return PassiveObject, mat


# Assign Texture to Ground Plane
def ApplyTextureToPlane(PassiveObject, mat):
    if PassiveObject.data.materials:
        PassiveObject.data.materials[0] = mat
    else:
        PassiveObject.data.materials.append(mat)

# Import Active Objects to the Scene
def ImportObj(PATH_TO_OBJECT_LIST, CurrObjIdx):
    # Import a Random Object File to the scene
    lines = open(PATH_TO_OBJECT_LIST).read().splitlines()
    RandomModel = random.choice(lines)
    bpy.ops.import_scene.obj(filepath=RandomModel)
    bpy.context.selected_objects[0].name = 'model_normalized'+'.'+'00'+str(CurrObjIdx)
    print(CurrObjIdx)

    
    # Remove if object is high poly:    
    bpy.ops.object.mode_set(mode='EDIT')
    print('vert')
    print(CurrObjIdx + len(bpy.context.object.data.vertices))
    if len(bpy.context.object.data.vertices) > 1e3:
        bpy.ops.object.delete(use_global=False, confirm=False)
        ImportObj(PATH_TO_OBJECT_LIST, CurrObjIdx)
        bpy.ops.object.mode_set(mode='OBJECT')

    else:        
        # Object Physics:
        CurrObj = bpy.data.objects['model_normalized'+'.'+'00'+str(CurrObjIdx)]
        CurrObj.select_set(True)
        print("dance", str(CurrObj))
        CurrObj.rigid_body.use_margin = True
        CurrObj.rigid_body.collision_margin = 0.25
        CurrObj.rigid_body.collision_shape = 'BOX'
        CurrObj.rigid_body.angular_damping = 0.8
        CurrObj.rigid_body.linear_damping = 0.2
        
        # Recalculate Surface Normals
        # https://blender.stackexchange.com/questions/190853/how-do-i-keep-the-two-objects-from-penetrating-each-other-in-blender
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.object.mode_set(mode='OBJECT')



def GetVolume(CurrObject):
    scene = bpy.context.scene
    unit = scene.unit_settings
    scale = 1.0 if unit.system == 'NONE' else unit.scale_length
    # obj = bpy.context.active_object
    obj = CurrObject

    bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
    volume = bm.calc_volume()
    bm.free()

    # Assuming unit.system == 'METRIC'
    volume = volume * (scale ** 3.0) / (0.01 ** 3.0)  # cm3
    volume = volume / 1000000.0 # in Meter cube (m3)

    # Bounding Box Volume:
    BBVolume = np.prod(obj.dimensions)

    # Percentage Volume Occupied 
    occupancy = volume / BBVolume * 100 # Defined between 0 to 100

    return volume, BBVolume, occupancy
# def LightSettings():



# Object Transformations:
def ObjTransform(CurrObject):
    [Roll, Pitch, Yaw] = [(random.randint(-180, 180)) * pi / 180 for x in range(3)]
    [PositionX, PositionY] = [(random.randint(-5, 5)) for x in range(2)]
    PositionZ = random.randint(4,16)
    # PositionZ = 2
    print('PosZ: ' + str(PositionZ))
    # bpy.ops.transform.translate(value=(PositionX, PositionY, PositionZ), orient_type='GLOBAL',
                                # orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                # mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
                                # proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    # bpy.context.active_object.rigid_body.collision_shape = 'BOX'
    CurrObject.location[0], CurrObject.location[1], CurrObject.location[2] = (PositionX, PositionY, PositionZ)
    CurrObject.rotation_euler[0] = Roll
    CurrObject.rotation_euler[1] = Pitch
    CurrObject.rotation_euler[2] = Yaw


    # bpy.ops.transform.rotate(value=Roll, orient_axis='X')
    # bpy.ops.transform.rotate(value=Pitch, orient_axis='Y')
    # bpy.ops.transform.rotate(value=Yaw, orient_axis='Z')

# Object Dimensions Normalization:
def ObjSizeNormalization(dim):
    # Normalized objects so there are of similar size:
    size = 4  /max(dim)
    bpy.ops.transform.resize(value=(size, size, size), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                             orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, 
                             proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False,
                             use_proportional_projected=False)
                             



"""
Apply Random Texture to the active Objects
"""


def ApplyTextureToObject2(CurrObject, CurrObjIdx):
    mat = bpy.data.materials.new(name="MaterialName") #set new material to variable
    activeObject = bpy.context.active_object #Set active object to variable
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    lines = open(PATH_TO_TEXTURE_LIST).read().splitlines()
    RandomTexture = TEXTURE_LIST_BASE_PATH + random.choice(lines)
    texImage.image = bpy.data.images.load(filepath=RandomTexture)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project(cube_size=1)
    bpy.ops.object.mode_set(mode='OBJECT')


def ApplyTextureToObject(CurrObject, CurrObjIdx):
    bpy.data.materials.new(name="MaterialName")
    activeObject = bpy.context.active_object #Set active object to variable
    mat = bpy.data.materials.new(name="MaterialName") #set new material to variable
    activeObject.data.materials.append(mat) #add the material to the object
    bpy.data.objects['model_normalized'+'.'+'00'+str(CurrObjIdx)].select_set(True)
    Mat_Name = 'material'+'.'+'00'+str(CurrObjIdx)
    mat = bpy.data.materials.new(name=Mat_Name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    lines = open(PATH_TO_TEXTURE_LIST).read().splitlines()
    RandomTexture = random.choice(lines) 
    # RandomTexture = TEXTURE_LIST_BASE_PATH + RandomTexture[26:]
    RandomTexture = TEXTURE_LIST_BASE_PATH + random.choice(lines)
    texImage.image = bpy.data.images.load(RandomTexture)
    # texImage.image = bpy.data.images.load("/home/chahatdeep/git_cloned/blender-script/scripts/1.jpg")
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

    bpy.ops.view3d.materialutilities_assign_material_object(material_name=Mat_Name, override_type='OVERRIDE_ALL', \
                                                            new_material=False, show_dialog=False)
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.cube_project(cube_size=1)
    bpy.ops.object.editmode_toggle()

# Add a force field in the center
def CreateForceField():
    bpy.ops.object.effector_add(type='FORCE', enter_editmode=False, align='WORLD', location=(0,0,10))
    ForceField = bpy.data.objects['Field']
    ForceField.select_set(True)
    bpy.ops.transform.resize(value=(10, 10, 10), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                             orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False,
                             proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False,
                             use_proportional_projected=False)
    # Add a force field which pulls objects towards the center for a few frames:
    ForceField.field.strength=-20
    ForceField.keyframe_insert(data_path="field.strength", frame=150.0)
    # Remove the force field after few frames:
    ForceField.field.strength=0
    ForceField.keyframe_insert(data_path="field.strength", frame=200.0)

def Compositing():
    bpy.context.scene.use_nodes = True
    bpy.ops.node.add_node(type="CompositorNodeOutputFile", use_transform=True)
    
    
def RenderSettings(nFrames):
    FIELD_OF_VIEW = 70
    bpy.data.cameras['Camera'].lens_unit = 'FOV'
    bpy.data.cameras['Camera'].angle = FIELD_OF_VIEW * (np.pi / 180)
    bpy.context.scene.render.resolution_x = 640
    bpy.context.scene.render.resolution_y = 480
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    # bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.frame_end = nFrames

    # Turn on Optical Flow:
    bpy.context.scene.view_layers["ViewLayer"].use_pass_vector = True

    # Define Gravity:
    bpy.context.scene.gravity[0] = 0 # random.randint(-5,5)
    bpy.context.scene.gravity[1] = 0 # random.randint(-5,5)
    bpy.context.scene.gravity[2] = -9.8 # random.randint(-5,2)



def SaveScene():
    bpy.ops.wm.save_as_mainfile(filepath= BASE_PATH_FOR_SAVED_FRAMES + "Blender-Scenes/" +  PATH_TO_SAVED_FRAMES + ".blend")
    print("Saving in: ", BASE_PATH_FOR_SAVED_FRAMES + "Blender-Scenes/" +  PATH_TO_SAVED_FRAMES + ".blend")
    # Save Rendered Images:
    # bpy.context.scene.render.filepath = "~/Blender-Data/Test/Frames/"
    # Save Frames, Depth and Optical Flow
    # bpy.data.scenes["Scene"].node_tree.nodes["File Output"].active_input_index = 0
    bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = BASE_PATH_FOR_SAVED_FRAMES + PATH_TO_SAVED_FRAMES
    # bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = BASE_PATH_FOR_SAVED_FRAMES + 
    

def RenderScene():
    bpy.ops.render.view_show()
    bpy.ops.render.render(animation=True)

def LightSettings():
    # Remove Shadow
    # bpy.data.objects['Light'].data.cycles.cast_shadow = False
    bpy.data.lights['Light'].use_shadow = False
    bpy.data.lights['Light'].energy = 1e4
    bpy.data.objects['Light'].location[0] = 0
    bpy.data.objects['Light'].location[1] = 0
    bpy.data.objects['Light'].location[2] = 20

def main():
    # Create a Passive Ground Plane and Apply Texture to it:
    PassiveObject, mat = CreatePlane(GroundPlaneSize, CollisionMargin, PATH_TO_TEXTURE_LIST)
    ApplyTextureToPlane(PassiveObject, mat)
    RenderSettings(nFrames)
    
    ## Importing new objects and applying textures to the active objects in the scene:
    for CurrObjIdx in range(0, nObjects):
        # Import Objects
        ImportObj(PATH_TO_OBJECT_LIST, CurrObjIdx)
        CurrObject = bpy.data.objects['model_normalized'+'.'+'00'+str(CurrObjIdx)]
        
        CurrObject.select_set(True)

        # CurrObject = bpy.context.selected_objects[0]
        print("c",CurrObject.rigid_body)
        # Set Collision Type:
        CurrObject.rigid_body.collision_shape = 'BOX'
        
        [Volume, BBVolume, Occupancy] = GetVolume(CurrObject)
        print(Volume, BBVolume, Occupancy)

        # Change Size of Objects so all objects are of similar scale
        ObjSizeNormalization(CurrObject.dimensions)

        # Change Position and Orientation of Objects randomly        
        ObjTransform(CurrObject)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.object.mode_set(mode='OBJECT')
                
        # Add max friction to the objects so they don't move much after falling
        bpy.context.object.rigid_body.friction = RigidBodyFriciton
        bpy.context.scene.rigidbody_world.collection = bpy.data.collections["Collection"]
        bpy.context.scene.rigidbody_world.constraints = bpy.data.collections["Collection"]

        # Remove Rigid Body Constraint
        # bpy.ops.rigidbody.constraint_remove()

        # https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8?rq=1
        CurrObject = bpy.data.objects['model_normalized'+'.'+'00'+str(CurrObjIdx)]
        
        # Apply Different Textures to the Active Objects:
        ApplyTextureToObject(CurrObject, CurrObjIdx)
        #   # Always start the filepath with '..'; It's a Blender bug (No fix)
        #   # Note: The code works without '..' in Blender Python Environment but
        #   #       not from command line terminal blender.
        #   texImage.image = bpy.data.images.load(filepath="../textures/1.jpg")
        #   mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
        

# Function Calls go here
if __name__ == "__main__":
    for i in range(0, 1):
        print("----------------- Set Number ----------------", i)
#        bpy.data.scenes['Scene'].frame_set(16)
        

        # Clear Previous Data:
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        try:
            bpy.data.objects['Field'].select_set(True)
            bpy.ops.object.delete()
        except:
            print('Previous Force Field deleted')
        main()
        # CreateForceField()
        LightSettings()
        bpy.context.scene.render.image_settings.file_format='PNG'
        bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = "/mnt/ddb5152f-7808-4a33-9f27-ba0a0d7f3164/CodedApertureBlenderData/" + str(i)
        for j in range(0, nFrames):
            bpy.data.scenes['Scene'].frame_set(j)
            bpy.ops.render.render(write_still=True, animation=False)
    #    SaveScene()
    #   RenderScene()

    # bpy.ops.wm.open_mainfile(filepath="../TemplateScenes/TemplateDepth-FlowNoObject.blend")

bpy.context.scene.frame_end = 100
