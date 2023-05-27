import sys
import bpy

sys.path.append("./settings")
sys.path.append("./")

import yaml
from yaml.loader import SafeLoader

from WorldGen import WorldGen



with open('config.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    RENDER_DIR = data["render_dir"]
    BLEND_FILEPATH = data["blend_filepath"]
    RENDER_ENGINE = data["render_engine"]
    SCENE_COORDS = data["scene_coordinates"]
    CLASS_NAMES = data["class_names"]
    WEATHER = data["weather"]
    IMAGE_RESOLUTION = data["image_resolution"]
    OUTPUTS = data["outputs"]
    TWO_WAY_STREETS = data["two_way_streets"]
    ONLY_RENDER_ANNOTATIONS = data["only_render_annotations"]
    IS_SUBURBS = data['is_suburbs']
    SYSTEM_PATH = data["python_system_path"]
    CAMERA_SETTINGS = data["camera_settings"]
    RENDER_SETTINGS = data["render_settings"]


sys.path.append(SYSTEM_PATH)
    

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
    CAR_OBJECTS = data["car_objs"]
    NUM_OF_CARS = data["num_of_cars"]
    NUM_OF_BENCHES = data["num_of_benches"]
    NUM_OF_STREET_LAMPS = data["num_of_street_lamps"]
    BUILDING_SCALE = data["building_scale"]
    MAX_NUM_OF_ROOF_OBJS = data["max_number_of_roof_obj"]
    ROOF_OBJ_SCALE = data["roof_obj_scale"]
    SKY_HDRI = data["sky_hdri"]

    
def main():
    if not ONLY_RENDER_ANNOTATIONS:
        # initialize settings
        WorldGen.set_render_engine(RENDER_ENGINE)
        
        WorldGen.set_camera(CAMERA_SETTINGS)
        WorldGen.set_render(RENDER_SETTINGS)
        WorldGen.set_metadata_properties()
        WorldGen.set_image_resolution(IMAGE_RESOLUTION[0], IMAGE_RESOLUTION[1], IMAGE_RESOLUTION[2])
   

        # create simulation
        simulation = WorldGen.Simulator(BLEND_FILEPATH, TWO_WAY_STREETS)
        simulation.createScene(SCENE_COORDS[0], SCENE_COORDS[1], SCENE_COORDS[2], SCENE_COORDS[3], terrainTexture=TERRAIN_TEXTURES, isSuburbs=IS_SUBURBS,
                            roofTextures=ROOF_TEXTURES, treeObjects=TREE_OBJECTS, numOfTrees=NUMBER_OF_TREES, trafficLightObject = TRAFFIC_LIGHT_OBJ, 
                            streetLampObjects=[STREET_LIGHT_OBJ], benchObjects=BENCH_OBJS, streetTextures=STREET_TEXTURES, buildingTextures=BUILDING_TEXTURES, 
                            roofObjects=ROOF_OBJECTS, carObjs=CAR_OBJECTS, numOfCars=2, numOfBenches=20, numOfStreetLamps=20, buildingScale = BUILDING_SCALE,
                            maxNumRoofObj=MAX_NUM_OF_ROOF_OBJS, roofObjScale=ROOF_OBJ_SCALE)
        
        camera = simulation.addCamera() # doesn't work correctly yet
    

        # add hdri
        simulation.addWeather(SKY_HDRI,WEATHER[0], WEATHER[1])


    # add different lens to camera...

    # Can now run simulation and get annotations
    # camera.makeActive()
    # # output_folder = "/Users/riyakumari/Desktop/world-gen/renders" #make sure this is the entire file path, not relative
    if ONLY_RENDER_ANNOTATIONS:
        camera = None
    if not len(OUTPUTS) == 0:
        annotations = WorldGen.Annotations(RENDER_DIR, camera, WEATHER[1] == "fog")
        annotations.generateOutputs(OUTPUTS, CLASS_NAMES, CAMERA_SETTINGS)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILEPATH)
   
    


if __name__=="__main__":
    main()