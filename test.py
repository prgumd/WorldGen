import sys
import bpy


sys.path.append(
    '/opt/homebrew/Caskroom/miniforge/base/lib/python3.9/site-packages')
sys.path.append('/opt/homebrew/bin/')
sys.path.append("./settings")
# sys.path.insert(1, '/path/to/application/app/folder')
sys.path.append("./")
import yaml
from yaml.loader import SafeLoader

from WorldGen import WorldGen

with open('config.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    RENDER_DIR = data["render-dir"]
    BLEND_FILEPATH = data["blend-filepath"]
    RENDER_ENGINE = data["render-engine"]
    SCENE_COORDS = data["scene-coordinates"]
    CLASS_NAMES = data["class-names"]
    WEATHER = data["weather"]
    IMAGE_RESOLUTION = data["image-resolution"]
    OUTPUTS = data["outputs"]
    TWO_WAY_STREETS = data["two_way_streets"]

with open('texturesAndObjectsConfig.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    TERRAIN_TEXTURES = data["terrain"]
    ROOF_TEXTURES = data["roof"]
    TREE_OBJECTS = data["tree_objects"]
    NUMBER_OF_TREES = data["num_of_trees"]
    TRAFFIC_LIGHT_OBJ = data["traffic_light_obj"]
    STREET_LIGHT_OBJ = data["street_lamp_obj"]
    BENCH_OBJS = data["bench_objs"]
    STREET_TEXTURES = data["street_textures"]
    BUILDING_TEXTURES = data["building_textures"]
    ROOF_OBJECTS = data["roof_objs"]
    
def main():
    # initialize settings
    WorldGen.set_render_engine(RENDER_ENGINE)
    WorldGen.set_metadata_properties()
    WorldGen.set_image_resolution(IMAGE_RESOLUTION[0], IMAGE_RESOLUTION[1], IMAGE_RESOLUTION[2])


    # create simulation
    simulation = WorldGen.Simulator(BLEND_FILEPATH, TWO_WAY_STREETS)
    simulation.createScene(SCENE_COORDS[0], SCENE_COORDS[1], SCENE_COORDS[2], SCENE_COORDS[3], terrainTexture=TERRAIN_TEXTURES, 
                           roofTextures=ROOF_TEXTURES, treeObjects=TREE_OBJECTS, numOfTrees=NUMBER_OF_TREES, trafficLightObject = TRAFFIC_LIGHT_OBJ, 
                           streetLampObjects=[STREET_LIGHT_OBJ], benchObjects=BENCH_OBJS, streetTextures=STREET_TEXTURES, buildingTextures=BUILDING_TEXTURES, roofObjects=ROOF_OBJECTS)
    
    # camera = simulation.addCamera() # doesn't work correctly yet

    # add hdri
    # simulation.addWeather(WEATHER[0], WEATHER[1])


    # add different lens to camera...

    # Can now run simulation and get annotations
    # camera.makeActive()
    # # output_folder = "/Users/riyakumari/Desktop/world-gen/renders" #make sure this is the entire file path, not relative
    camera = None
    annotations = WorldGen.Annotations(RENDER_DIR, camera, WEATHER[1] == "fog")
    annotations.generateOutputs(OUTPUTS, CLASS_NAMES)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILEPATH)
   
    


if __name__=="__main__":
    main()