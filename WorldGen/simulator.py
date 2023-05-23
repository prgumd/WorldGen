
import bpy
import os
import random
import bmesh
import mathutils
import math
from .camera import Camera
from mathutils import geometry
from .utils import checkOverlap, getListofBuildings, pokeStreet
from scipy import spatial


class Simulator:
    
    def __init__(self, blendFilePath, isTwoWay=True):
        """
        Args:
            blendFilePath (string): file path to blend file
            isTwoWay (boolean) : If this is true then two streets are created, 
                                else single streets are kept with two graphs, 
                                each representing the two directions of traffic flow
        """
        self.filepath = blendFilePath
        self.pokedFaces = False
        self.isTwoWay = isTwoWay
        self.pokeLeftStreet = False
        self.pokeRightStreet = False
        self.pokeLeftStreetVerts = []
        self.pokeRightStreetVerts = []
        self.cameras = []
        self.active_camera = None
        self.object_names = []
        self.pass_indexes = []

    def createScene(self, minLong, minLat, maxLong, maxLat, isSuburbs=False, terrainTexture={'material_url': '', "material_name": ''}, 
                    roofTextures=[], streetTextures={}, treeObjects=[], numOfTrees = 2, benchObjects=[], streetLampObjects=[], trafficLightObject='', buildingTextures={}, roofObjects=[]):
        '''
        Creates scene given latitude and longitude, flat roofs are imported by default

        Args:
            minLong, minLat, maxLong, maxLat (int): longitudes and latitudes of region
            isSuburbs (boolean) : Must specify whether scene created is of a suburb/rural area. If true, then slanted/gabled roofs will be enabled
        
        Returns:
            None
        '''
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        self.importScene(minLong, minLat, maxLong, maxLat, isSuburbs)
        
        self.separateRoofs()
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addTextureToBuildings(buildingTextures["building_texture_urls"], buildingTextures["building_texture_names"])
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)
        
        self.addTextureToTerrain(terrainTexture["material_url"], terrainTexture["material_name"])
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addTextureToRoofs(roof_textures_url=roofTextures["roof_textures_url"], roof_textures_name=roofTextures["roof_textures_name"])
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)
        
        main_collection = bpy.context.scene.collection
        rooftop_objects_collection = bpy.data.collections.new("RooftopObjects")
        rooftopObjects = self.addRooftopObjects(roofObjects=roofObjects, collection=rooftop_objects_collection)
        self.moveToCollection(rooftopObjects, rooftop_objects_collection)
        main_collection.children.link(rooftop_objects_collection)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)


        self.addStreets()
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        
       
        # Adding traffic lights
        # main_collection = bpy.context.scene.collection
        traffic_lights_collection = bpy.data.collections.new("TrafficLights")
        self.addTrafficLights(street_name='secondary_roads.000', collection=traffic_lights_collection, traffic_light_obj=trafficLightObject)
        main_collection.children.link(traffic_lights_collection)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        # Addging trees
        tree_collection = bpy.data.collections.new("Trees")
        main_collection.children.link(tree_collection)
        self.addTrees(treeObjects, tree_collection, numOfTrees=numOfTrees)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        intersections = self.getIntersections("secondary_roads.000")
        # self.addTrafficLights(collection, traffic_light_obj=trafficLightObject)
        
        street_lamp_collection = bpy.data.collections.new("StreetLamps")
        main_collection.children.link(street_lamp_collection)
        self.addingToSidewalks("street_lamps", streetLampObjects, street_lamp_collection, 2, intersections)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        twin_bench_collection = bpy.data.collections.new("TwinBenches")
        main_collection.children.link(twin_bench_collection)
        self.addingToSidewalks("benches", benchObjects, twin_bench_collection, 2, intersections)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addTextureToStreets(streetTextures["street_texture_url"], streetTextures["street_texture_name"])

        self.hide_center_road()
        self.hide_path()
        self.extrude_roads()
        

        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)


    
    def extrude_roads(self):
        self.deselectObjects()
        roads = [o for o in bpy.data.objects if "roads" in o.name]
        for road in roads:
            road.select_set(True)
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(4.65661e-10, 4.65661e-10, -0.425891), "orient_axis_ortho":'X', "orient_type":'NORMAL', "orient_matrix":((0.999904, -0.000133084, -0.0138799), (1.25411e-06, 0.999955, -0.00949752), (0.0138805, 0.00949659, 0.999859)), "orient_matrix_type":'NORMAL', "constraint_axis":(False, False, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            road.select_set(False)
            
    def moveToCollection(self, rooftopObj, collection):
        self.deselectObjects()
        for obj in rooftopObj:
            obj.select_set(True)
            collection.objects.link(obj)
            obj.users_collection[0].objects.unlink(obj)
            obj.select_set(False)
        
    def addCamera(self):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()

        if self.isTwoWay:
            # left and right street
            streets = ["secondary_roads.001", "secondary_roads.002"]

            street = bpy.data.objects[streets[0]] #picking the left street for now
            
            # poke faces
            poked = self.pokeLeftStreetVerts
            # ****** Can use these vertices to construct any kind of curve you want *****

            poked_tree = spatial.KDTree(poked)
            start_vertex = poked[random.randint(0, len(poked)-1)]

            distances, indexes = poked_tree.query(start_vertex, k = 2)
            coords = []
            count = 0
            while(count < 20):
                count+=1
                for i in indexes:
                    v = poked[i]
                    vertex_world_coords = street.matrix_world @ mathutils.Vector((v[0], v[1], v[2]))
                    if not vertex_world_coords in coords:
                        coords.append(vertex_world_coords)
                        start_vertex = vertex_world_coords
                        break
                
                distances, indexes = poked_tree.query(start_vertex, k = 2)

            # https://blender.stackexchange.com/questions/6750/poly-bezier-curve-from-a-list-of-coordinates
            # create the Curve Datablock
            curveData = bpy.data.curves.new('cameraCurve', type='CURVE')
            curveData.dimensions = '3D'
            curveData.resolution_u = 2

            # map coords to spline
            polyline = curveData.splines.new('NURBS')
            polyline.points.add(len(coords))
            for i, coord in enumerate(coords):
                x = coord.x
                y = coord.y
                z = coord.z
                polyline.points[i].co = (x, y, z, 1)

            # create Object
            curveOB = bpy.data.objects.new('CameraCurve', curveData)
            bpy.data.scenes[0].collection.objects.link(curveOB)

            bpy.ops.object.mode_set(mode = 'OBJECT')
            self.deselectObjects()

            cam_location = polyline.points[len(coords)].co
            bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(cam_location.x, cam_location.y, cam_location.z), rotation=(1.38569, -8.8702e-07, -1.53589), scale=(1, 1, 1))
            camera = bpy.context.active_object
            cam_name = bpy.context.active_object.name
            bpy.ops.object.constraint_add(type='FOLLOW_PATH')
            bpy.context.object.constraints["Follow Path"].target = bpy.data.objects["CameraCurve"]
            bpy.ops.constraint.followpath_path_animate(constraint="Follow Path", owner='OBJECT')
            bpy.context.object.constraints["Follow Path"].use_curve_follow = True
            camera.location = (cam_location.x, cam_location.y, cam_location.z + 5)
            camera.constraints["Follow Path"].forward_axis = 'FORWARD_X'


            self.deselectObjects()

            bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

            camera_obj = Camera(cam_name)
            return camera_obj
        
    def importScene(self, minLong, minLat, maxLong, maxLat, isSuburbs):
        '''
        Imports scene given latitude and longitude
        '''
        bpy.context.scene.blosm.maxLat = maxLat
        bpy.context.scene.blosm.minLat = minLat
        bpy.context.scene.blosm.minLon = minLong
        bpy.context.scene.blosm.maxLon = maxLong
        
        # Import the terrain and building models 
        bpy.context.scene.blosm.dataType = 'terrain'
        bpy.ops.blosm.import_data()

        # Importing the buildings ********************
        bpy.context.scene.blosm.dataType = 'osm'
        bpy.context.scene.blosm.singleObject = False
        bpy.context.scene.blosm.buildings = True
        bpy.context.scene.blosm.water = True # for suburbs
        bpy.context.scene.blosm.forests = True # for suburbs
        bpy.context.scene.blosm.vegetation = True # for suburbs
        bpy.context.scene.blosm.highways = False
        # bpy.context.scene.blosm.highways = True
        # bpy.context.scene.blosm.railways = True

        if isSuburbs:
            bpy.context.scene.blosm.defaultRoofShape = 'gabled' # select this if you know its a suburb area

        bpy.ops.blosm.import_data()

        # import roads as single object
        bpy.context.scene.blosm.buildings = False
        bpy.context.scene.blosm.water = False
        bpy.context.scene.blosm.forests = False
        bpy.context.scene.blosm.vegetation = False
        bpy.context.scene.blosm.singleObject = True
        bpy.context.scene.blosm.highways = True
        bpy.ops.blosm.import_data()

    def separateRoofs(self):
        '''
        Separates the roofs from the buildings. Assumes buildings are under a collection with the name osm_buildings in it
        '''
        # bpy.ops.object.mode_set(mode = 'OBJECT')
        
        self.deselectObjects()

        # Selects all the buildings under osm_buildings
        buildings = None
        for collection in bpy.data.collections:
            if "osm_buildings" in collection.name:
                bpy.context.view_layer.objects.active = bpy.data.objects[collection.name]
                myObj = bpy.context.active_object
                myObj.children[0].select_set(True)
                bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
                bpy.context.view_layer.objects.active = myObj.children[0]
                buildings = collection.name

        # Separating roof from walls in edit mode
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.context.object.active_material = bpy.data.materials['roof']
        bpy.ops.object.material_slot_select()
        bpy.context.object.active_material = bpy.data.materials['wall']
        bpy.ops.object.material_slot_deselect()
        bpy.ops.mesh.separate(type = 'SELECTED')

        # Translate the roof down
        bpy.ops.object.mode_set(mode = 'OBJECT')

        for obj in bpy.data.objects:
            obj.select_set(False)

        active_obj = bpy.data.objects[buildings]
        bpy.context.view_layer.objects.active = active_obj
        myObjs = bpy.context.active_object
        for o in myObjs.children:
            if "001" in o.name:
                o.select_set(True)
                o.name = o.name.replace("001", "roof")

        bpy.ops.transform.translate(value=(-0, -0, -0.48044), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

        self.deselectObjects()

        # if buildings have element in their name
        # bpy.ops.object.mode_set(mode = 'EDIT')
        for collection in bpy.data.collections:
            if "osm_buildings" in collection.name:
                bpy.context.view_layer.objects.active = bpy.data.objects[collection.name]
                myObj = bpy.context.active_object

                for childObj in myObj.children:
                    bpy.context.view_layer.objects.active = childObj
                    childObj.select_set(True)
                    if "element" in childObj.name:
                        bpy.ops.object.mode_set(mode = 'EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        ob = bpy.context.object
                        me = ob.data
                        if len(me.polygons) == 1:
                            childObj.name = childObj.name + ".roof"
                    childObj.select_set(False)
                            

        self.deselectObjects()

    def chunks(self, lst, n):
        '''
        Divide a list into multiple sublists
            lst -> is number of 
        '''
        chunk = []
        for i in range(0, len(lst), n):
            chunk.append(lst[i:i + n])
        return chunk

    def addTextureToBuildings(self, list_of_building_urls, list_of_building_materials):
        
        self.deselectObjects()

        # creating list of buildings
        buildings = None
        list_of_buildings = []
        for collection in bpy.data.collections:
            if "osm_buildings" in collection.name:
                buildings = collection.name
                active_obj = bpy.data.objects[buildings]
                bpy.context.view_layer.objects.active = active_obj
                myObjs = bpy.context.active_object
                for o in myObjs.children:
                    if "roof" not in o.name:
                        list_of_buildings.append(o.name)

        
        # shuffle the list of buildings
        random.shuffle(list_of_buildings)
        grouped_buildings = self.chunks(list_of_buildings, round(len(list_of_buildings)/(len(list_of_building_urls))+1))

        for idx, group in enumerate(grouped_buildings):

            material_url = list_of_building_urls[idx]
            material = list_of_building_materials[idx]
            # select all buildings in a group
            for building in group:
                bpy.data.objects[building].select_set(True)

                # bpy.context.view_layer.objects.active = bpy.data.objects[group[0]]
                bpy.context.view_layer.objects.active = bpy.data.objects[building]
                bpy.data.objects[building].select_set(True)
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                # pick material    
                if len(bpy.context.object.material_slots) == 0:
                    continue
                bpy.context.object.active_material = bpy.data.materials['wall']
                
                
                bpy.ops.material.new()
                bpy.ops.object.lily_surface_import(url=material_url)
                
                # bpy.data.materials[material].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 20
                # bpy.data.materials[material].node_tree.nodes["Mapping"].inputs[3].default_value[1] = 20
                # bpy.data.objects[building].active_material = bpy.data.materials[material]
            
                # apply material to buildings in the group
                bpy.ops.uv.smart_project()
                bpy.data.objects[building].select_set(False)

            # print("materials :", bpy.data.materials)
            # material = set(material)
            for mat in bpy.data.materials:  
                mat2 = mat.name.split('.')
            
                if material in mat2:
                    bpy.data.materials[mat.name].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 15
                    bpy.data.materials[mat.name].node_tree.nodes["Mapping"].inputs[3].default_value[1] = 15
                    bpy.ops.object.mode_set(mode = 'OBJECT')
            
            self.deselectObjects()

    def addTextureToTerrain(self, material_url, material_name):
        '''
        Adds texture to the ground terrain. Using textures from https://ambientcg.com/

        Args:
            None
        Returns:
            None
        '''
        self.deselectObjects()


        bpy.context.view_layer.objects.active = bpy.data.objects["Terrain"]
        obj = bpy.context.active_object
        obj.select_set(True)

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        bpy.ops.material.new()
        bpy.ops.object.lily_surface_import(url=material_url)
        # bpy.ops.uv.smart_project()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)


        bpy.data.materials[material_name].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 110
        bpy.data.materials[material_name].node_tree.nodes["Mapping"].inputs[3].default_value[1] = 110

    def addStreets(self, ):
        '''
        The street itself is actually created in importScene. 

        Args: None
        Returns: None
        '''

        self.deselectObjects()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        roads = ["residential", "secondary", "tertiary"]
        

        # selecting the roads
        for collection in bpy.data.collections:
            if "osm" in collection.name:
                for obj in collection.all_objects:
                    for road in roads:
                        if road in obj.name:
                            obj.select_set(True)
                            bpy.context.view_layer.objects.active = obj
                            if obj != "MESH":
                                bpy.ops.object.convert(target='MESH') # convert curve to mesh
        bpy.ops.object.join()

        if self.isTwoWay:

            # rename the joined road
            obj = bpy.context.view_layer.objects.active
            obj.name = 'secondary_roads.000' # will use this joined road to create two new roads which will be translated left and right to create two different flows of traffic

            bpy.ops.object.duplicate(linked=False)
            bpy.ops.transform.translate(value=(-1.59264, -3.9816, 0), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            # bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.816367, 10.3733, 1.72802), "orient_axis_ortho":'X', "orient_type":'LOCAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'LOCAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.816367, 10.3733, 0), "orient_axis_ortho":'X', "orient_type":'LOCAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'LOCAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            # selecting the roads
            for collection in bpy.data.collections:
                if "osm" in collection.name:
                    for obj in collection.all_objects:
                        if "road" in obj.name:
                            obj.select_set(True)
                            bpy.context.view_layer.objects.active = obj

            # translate the roads to be higher than the plane
            # bpy.ops.transform.translate(value=(0, 0, 1.24545), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            
            bpy.data.objects['secondary_roads.000'].hide_render = True # hiding this road as two streets will be created from this
            bpy.data.objects['secondary_roads.000'].hide_viewport = True
            
            streets = ["secondary_roads.001", "secondary_roads.002"]
        
            # poke faces
            self.pokeLeftStreetVerts = pokeStreet(streets[0])
            self.pokeRightStreetVerts = pokeStreet(streets[1])
            self.pokeLeftStreet = True
            self.pokeRightStreet = True

    def addTextureToStreets(self, roadTextureUrl, roadTextureName):
        '''
        Adding texture to roads. 

        Args:
            None

        Returns:
            None
        '''

        self.deselectObjects()
        # roads = None
        # if "road" in or "path" in

        
        view_layer = bpy.context.view_layer

        roadObjects = []

        
        nonMeshObjExists = False
        for collection in bpy.data.collections:
            if "osm" in collection.name:
                for obj in collection.all_objects:
                    if ("road" in obj.name) or ("path" in obj.name):
                        # roads.append(obj)
                        obj.select_set(True)
                        roadObjects.append(obj)
                        view_layer.objects.active = obj
                        if obj != "MESH":
                            nonMeshObjExists = True
        print("roadObjects",roadObjects)
     

        if nonMeshObjExists:
            bpy.ops.object.convert(target='MESH') # convert curve to mesh
            

        self.deselectObjects()
        material_index = None
        for obj in roadObjects:
            obj.select_set(True)
            view_layer.objects.active = obj     
            obj.hide_set(False)     
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            
            bpy.ops.object.lily_surface_import(url=roadTextureUrl)
            bpy.data.materials[roadTextureName].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 4.6
            if material_index == None:
                for i in range(len(obj.material_slots)):
                    if roadTextureName in obj.material_slots[i].name:
                        bpy.context.object.active_material_index = i
                        material_index = i
                        break
            
            
            bpy.context.object.active_material_index = material_index
            bpy.ops.object.material_slot_assign()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            obj.select_set(False)

        #making sure all parts of the road is assigned textures

    def hideFootways(self):
        for collection in bpy.data.collections:
                if "osm" in collection.name:
                    for obj in collection.all_objects:
                        if "osm_paths_footway" in obj.name:
                            obj.hide_render = True
                            obj.hide_viewport = True

    def addTrees(self, treeFilePaths, collection, numOfTrees):
        '''
        Adding trees to the scene

        Args:
            treeFilePaths (string[]): list of tree object paths to import from
            numOfTrees (int) : the number of trees to import into the scene

        Returns:
            None
        '''
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()
        object = None
        # pass_index = random.randint(0,50)
        # while(pass_index in self.pass_indexes):
        #     pass_index = random.randint(0,50)
        # self.pass_indexes.append(pass_index)
        for collection in bpy.data.collections:
                if "osm" in collection.name:
                    # if (len(collection.all_objects)) > 0:
                    for obj in collection.all_objects:
                        if "paths_footway" in obj.name:
                            obj.hide_viewport = False
                            obj.select_set(True)
                            bpy.context.view_layer.objects.active = obj
                            if obj.type != "MESH":
                                bpy.ops.object.convert(target='MESH')
                            object = obj
                            break

        # z_pos = object.dimensions[2]
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        vertices = [v for v in bm.verts]
        random.shuffle(vertices) # we want to place trees randomly

        count = 0
        
        for v in vertices:
            v.select = len(v.link_edges) == 3
            if v.select:
                coords = (object.matrix_world @ v.co)
                randIndex = random.randint(0, len(treeFilePaths)-1)
                bpy.ops.import_scene.obj(filepath=treeFilePaths[randIndex], axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")

                pos = coords
                obj = bpy.context.selected_objects

                randNum = random.randint(1,3)
                if randNum == 1:
                    obj[0].scale = [0.5, 0.5, 0.5]
                elif randNum == 2:
                    obj[0].scale = [0.25, 0.25, 0.25]
                else:
                    obj[0].scale = [0.2, 0.2, 0.2]

                obj[0].location = [pos.x, pos.y, pos.z]

                if count == numOfTrees:
                    break
                else:
                    count = count + 1

                obj[0].name = "tree" + str(count)
                obj[0].select_set(False)
                obj[0].users_collection[0].objects.unlink(obj[0])
                # obj[0].pass_index = pass_index

                collection.objects.link(obj[0])

        self.object_names.append("tree")
        object.hide_viewport = False
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()
        

    def getIntersections(self, street):
        '''
        Finding intersections in a street

        Args:
            street (string) 

        Returns:
            list array<(x,y)> coordinates
        '''
        self.deselectObjects()
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # unhide the street if its hidden
        street = bpy.data.objects[street]
        visibility = street.hide_viewport
        street.hide_viewport = False

        # select the street
        street.select_set(True)
        bpy.context.view_layer.objects.active = street

        bpy.ops.object.mode_set(mode = 'EDIT')
        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Check if there are any intersecting lines, if not then intersect the street lines
        intersectingLines_flag = False
        for v in bm.verts:
            if len(v.link_edges) == 4:
                intersectingLines_flag = True

        # intersect the street lines
        if not intersectingLines_flag:
            bpy.ops.tinycad.intersectall()


        # adding traffic lights and plane to intersections
        context = bpy.context
        me = context.edit_object.data
        bm = bmesh.from_edit_mesh(me)
        vertices = []

        for v in bm.verts:
            if len(v.link_edges) == 4:
                coords = (street.matrix_world @ v.co)
                vertices.append(coords)
                

        
        street.hide_viewport = visibility

        

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[0]
        
        self.deselectObjects()

        return vertices

    def deselectObjects(self):
        for obj in bpy.data.objects:
            obj.select_set(False)

    def addingToSidewalks(self, nameOfObj, objectFilePaths, collection, numOfObjects, intersections):
        '''
        Adding objects to the scene by placing them on the center street

        Args:
            nameOfObj (string)
            objectFilePaths (string[]): list of bench object paths to import from
            numOfObjects (int) : the number of benches to import into the scene
            intersections (Vector[]) : points/vertices to stay away from

        Returns:
            None
        '''        

        self.deselectObjects()
        bpy.context.view_layer.objects.active = bpy.data.objects[0]
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()

        # pass_index = random.randint(0,50)
        # while(pass_index in self.pass_indexes):
        #     pass_index = random.randint(0,50)
        # self.pass_indexes.append(pass_index)
        
        object = bpy.data.objects["secondary_roads.000"]

        visibility_render = object.hide_render
        visibility_viewport = object.hide_viewport

        object.hide_viewport = False
        object.select_set(True)

        bpy.context.view_layer.objects.active = object
        if object.type != "MESH":
            bpy.ops.object.convert(target='MESH')


        z_pos = object.dimensions[2]
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        
        obj = bpy.context.edit_object # getting the context
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        faces = [f for f in bm.faces if f.select] # getting all the selected faces
        
        # https://blender.stackexchange.com/questions/222669/python-how-to-select-new-center-vertices-after-using-poke-face
        # Getting center of each road block
        # pokedFaces = False
        # for v in bm.verts:
        #     if len(v.link_edges) == 4:
        #         pokedFaces = True
        if not self.pokedFaces:
            poked = bmesh.ops.poke( bm, faces=faces)
            bmesh.update_edit_mesh(me)
            # bm = bmesh.from_edit_mesh(me)

            obj = bpy.context.object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            self.pokedFaces = True
        
        vertices = [v for v in bm.verts]
        # random.shuffle(vertices) # we want to place objects randomly
        
        

        count = 0
        
        set_of_objects = []
        self.object_names.append(nameOfObj)
        list_of_buildings = getListofBuildings("osm_buildings")

        # bpy.ops.object.mode_set(mode = 'OBJECT')
        # self.deselectObjects()

        for i, v in enumerate(vertices):
            # select the side vertex of each square
            v.select = len(v.link_edges) == 5
            
            if v.select:
                # picking an object from the list of filepaths
                randIndex = random.randint(0, len(objectFilePaths)-1)
                coords = (object.matrix_world @ v.co)
                
                # checks to see if a vertex falls in an intersection, in that case don't place the object there
                nearIntersection = False
                for intersection in intersections:
                    if math.sqrt((coords.x - intersection.x)**2 + (coords.y - intersection.y)**2 + (coords.z - intersection.z)**2) < 10:
                        nearIntersection = True
                        break
                if nearIntersection:
                    continue

                # getting the largest edge connected to vertex
                largest_edge = v.link_edges[0]
                shortest_edge = v.link_edges[0]
                vertex_coords = None

                # get other vertex of shorter edge, this should ideally be the center of the street squares
                # also finding largest edge for rotation calculation
                for e in v.link_edges:
                    v1, v2 = e.verts
                    if len(v1.link_edges) == 4:
                        vertex_coords = v1.co
                    if len(v2.link_edges) == 4:
                        vertex_coords = v2.co

                    if e.calc_length() > largest_edge.calc_length():
                        largest_edge = e

                if vertex_coords == None:
                    continue

                # importing the object    
                bpy.ops.import_scene.obj(filepath=objectFilePaths[randIndex], axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")

                obj = bpy.context.selected_objects

                # placing object
                obj_deleted = False # this flag is true if object is too close to the others, if it overlaps with another, and if it can't be oriented correctly
                
                obj[0].location = [vertex_coords.x, vertex_coords.y, coords.z - 0.45]
                obj[0].scale = [0.462, 0.462, 0.462]
                for o in set_of_objects:
                    distance = math.sqrt((vertex_coords.x - o.location.x)**2 + (vertex_coords.y - o.location.y)**2)
                    if distance  < 5:
                        obj_deleted = True
                


                # calculating rotation of object so its perpendicular to the street
                v1, v2 = largest_edge.verts # getting vector of largest edge of vertex the obj is on
                v3 = mathutils.Vector((-5.1466, -0.0000, 2.5466)) # rotation of imported obj is always same
                v4 = mathutils.Vector((5.1466, -0.0000, 2.5466))

                vec1 = v1.co-v2.co
                vec2 = v3-v4
                a=vec1
                b = vec2
                angle = math.atan2( a.x*b.y - a.y*b.x, a.x*b.x + a.y*b.y )
                # angle = vec1.angle(vec2) # get angle between both vectors

                obj[0].rotation_euler[2] = angle + math.pi/2
                bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

                # if object is placed such that it is parallel to the roads
                if checkOverlap(object.name, obj[0].name): 
                    obj[0].rotation_euler[2] = -obj[0].rotation_euler[2]
                    if checkOverlap(obj[0].name, object.name):
                        obj_deleted = True

                for building_name in list_of_buildings:
                    if checkOverlap(building_name, obj[0].name):
                        obj_deleted = True
                        # break
                # break

                if obj_deleted:
                    bpy.data.objects.remove(obj[0], do_unlink=True)
                else:
                
                    if count == numOfObjects:
                        break
                    else:
                        count = count + 1
                    obj[0].select_set(False)
                    obj[0].name = nameOfObj + str(i)
                    collection.objects.link(obj[0])
                    obj[0].users_collection[0].objects.unlink(obj[0])
                # obj[0].pass_index = pass_index
                
                    set_of_objects.append(obj[0])
        
        
        self.deselectObjects()

        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        object = bpy.data.objects["secondary_roads.000"]
        object.hide_viewport = visibility_viewport
        object.hide_render = visibility_render
        
        self.deselectObjects()
        
        
    def addTextureToRoofs(self, roof_textures_url, roof_textures_name):
        '''
        Adds texture to the roofs. Using textures from https://ambientcg.com/

        Args:
            None
        Returns:
            None
        '''

        self.deselectObjects()

        # creating list of buildings
        buildings = None
        list_of_roofs = []
        for collection in bpy.data.collections:
            if "osm_buildings" in collection.name:
                buildings = collection.name
                active_obj = bpy.data.objects[buildings]
                bpy.context.view_layer.objects.active = active_obj
                myObjs = bpy.context.active_object
                for o in myObjs.children:
                    if "roof" in o.name:
                        list_of_roofs.append(o.name)

        
        # shuffle the list of buildings
        random.shuffle(list_of_roofs)
        grouped_roofs = self.chunks(list_of_roofs, round(len(list_of_roofs)/len(roof_textures_name)))

        
        for idx, group in enumerate(grouped_roofs):
            # select all buildings in a group
            for roof in group:
                bpy.data.objects[roof].select_set(True)
                obj = bpy.data.objects[roof]

                # bpy.context.view_layer.objects.active = bpy.data.objects[group[0]]
                bpy.context.view_layer.objects.active = bpy.data.objects[roof]
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                # pick material    
                # if len(bpy.context.object.material_slots) == 0:
                #     continue
                # bpy.context.object.active_material = bpy.data.materials['roof']
                material_url = roof_textures_url[idx]
                material = roof_textures_name[idx]
                # bpy.ops.material.new()

                bpy.ops.object.lily_surface_import(url=material_url)
            
                # apply material to buildings in the group
                bpy.ops.uv.smart_project()
                for i in range(len(obj.material_slots)):
                    if material in obj.material_slots[i].name:
                        bpy.context.object.active_material_index = i
                        break
            
                bpy.context.object.active_material_index = i
                bpy.ops.object.material_slot_assign()

                bpy.ops.object.mode_set(mode = 'OBJECT')
            
                bpy.data.objects[roof].select_set(False)
            self.deselectObjects()

    
    def addTrafficLights(self, street_name, collection, traffic_light_obj):
        #https://blender.stackexchange.com/questions/2976/how-can-i-add-vertices-to-intersection-of-two-edges
        # https://docs.blender.org/manual/en/latest/addons/mesh/tinycad.html
            # object mode
        bpy.ops.object.mode_set(mode = 'OBJECT')


        width = 10 # will later use this to place traffic lights; hardcoded as 2 by looking at difference in adjacent vertices locations
        view_layer = bpy.context.view_layer
        
        # selecting the center road
        street_obj = bpy.data.objects[street_name] 
        sidewalk_obj = None
        for obj in bpy.data.objects:
            if "osm_paths_footway" in obj.name:
                sidewalk_obj = obj
                break

        self.deselectObjects()

        # add intersections to sidewalks

        # select the sidewalk and unhide it if hidden
        sidewalk_obj.select_set(True)
        view_layer.objects.active = sidewalk_obj
        sidewalk_obj.hide_viewport = False
        bpy.ops.object.convert(target='MESH')
        

        # in edit mode, intersect all edges
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        # create the sidewalk intersections
        bpy.ops.tinycad.intersectall()
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)
        
        
        # append sidewalk intersections to an array
        sidewalk_intersections = []
        for v in bm.verts:
            if len(v.link_edges) == 4:
                world_coords = (sidewalk_obj.matrix_world @ v.co)
                sidewalk_intersections.append([world_coords.x, world_coords.y, world_coords.z])
            
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()
     

        # create intersections for street
        street_obj.hide_viewport = False
        street_obj.select_set(True)
        view_layer.objects.active = street_obj
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        # look for intersecting edges and place a box on top of point of intersection
        obj = bpy.context.object
        me = obj.data
        bpy.ops.mesh.select_all(action='SELECT')
        bm = bmesh.from_edit_mesh(me)


        edges = [e for e in bm.edges if e.select]
        bpy.ops.tinycad.intersectall()

        path = traffic_light_obj
        
        i = 1
        vertices = []
        traffic_light_objs = []
        
        for v in bm.verts: 
            v.select = len(v.link_edges) > 4
        
            if v.select:
            
                coords = (street_obj.matrix_world @ v.co)
                vertices.append(v)
                i += 1

                traffic_lights_at_intersection = []
                for count in range(4):
                    bpy.ops.import_scene.obj(filepath=path, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")
            


                    obj = bpy.context.selected_objects
                    obj[0].location = [coords.x, coords.y, coords.z ]
                    obj[0].scale = [0.6, 0.6, 0.6]
                    obj[0].rotation_euler = [math.pi/2, 0, -math.pi*1.2]
                    traffic_lights_at_intersection.append(obj[0])

                    collection.objects.link(obj[0])
                    obj[0].users_collection[0].objects.unlink(obj[0])
                    obj[0].select_set(False)
                traffic_light_objs.append(traffic_lights_at_intersection)

                
                
        # # object.hide_viewport = True
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)
        
        tree = spatial.KDTree(sidewalk_intersections)
        for traffic_lights in traffic_light_objs: # import 4 traffic lights and place them in [] so its a [][]
            

            # get nearest sidewalk intersections:
            distances, indexes = tree.query(traffic_lights[0].location, k = 20)
            final_indexes = [indexes[0]]
            for i in indexes:
                flag = False
                for final_index in final_indexes:
                    if math.dist(sidewalk_intersections[final_index], sidewalk_intersections[i]) < 5:
                        flag = True
                        # break
                if not flag:
                    final_indexes.append(i)
                if len(final_indexes) == 4:
                    break

            
            
            # abcd are sidewalk intersections closest to traffic light
            for i, index in enumerate(final_indexes):
                traffic_light = traffic_lights[i]
                a = sidewalk_intersections[index]

                [x, y, z] = traffic_light.location
                # creating vectors from traffic light to sidewalk intersection
                v1 = [x - a[0],y - a[1],z - a[2]]
                theta1 = math.atan2(v1[1],v1[0])
                traffic_light.location = a
                traffic_light.rotation_euler[2] = theta1 + 2.40


    def addRooftopObjects(self, roofObjects, collection):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()

        # select roofs and store in an array
        roofs = []
        for c in bpy.data.collections:
            if "osm_buildings" in c.name:
                buildings = c.name
                active_obj = bpy.data.objects[buildings]
                bpy.context.view_layer.objects.active = active_obj
                myObjs = bpy.context.active_object
                for o in myObjs.children:
                    if "roof" in o.name:
                        roofs.append(o)

        self.deselectObjects()
        all_objs_added = []

        # go through each roof and subdivide 
        for roof in roofs:
            bpy.context.view_layer.objects.active = roof
            roof.select_set(True)

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            bpy.ops.mesh.poke()
            bpy.ops.mesh.subdivide()
            
            context = bpy.context
            me = context.edit_object.data
            bm = bmesh.from_edit_mesh(me)
            vertices = [v for v in bm.verts]            
            vertices = list(filter(lambda v : len(v.link_edges)>4, vertices))
            rot = 0

            # Deciding number of objects to add
            if len(vertices) > 6:
                num_of_objects = random.randint(0, int(len(vertices)/2))
            else: num_of_objects == len(vertices)
            
            for num in range(num_of_objects):
        
                i = random.randint(0, len(roofObjects)-1)
                bpy.ops.import_scene.obj(filepath=roofObjects[i], filter_glob=".fbx;*.mtl", axis_forward='-Z', axis_up='Y')

                obj = bpy.context.selected_objects
                it = 0 # increment this if a particular vertex location is overlapping with an object
                # check for overlap with other roof objects
                flag = True
                skip = False
                while(flag):
                    if num + it >= len(vertices): 
                        skip = True 
                        break
                    v = vertices[num+it]
                    it+=1

                    coords = (roof.matrix_world @ v.co)
                    obj[0].location = [coords[0], coords[1], coords[2]]
                    if len(all_objs_added)==0: flag=False
                    overlap = False
                    for o in all_objs_added:
                        if checkOverlap(o.name, obj[0].name): 
                            overlap = True
                    if overlap == False:
                        break
                            
                    
                if skip:
                    obj[0].select_set(False)
                    bpy.data.objects.remove(obj[0], do_unlink=True)
                    continue
                obj[0].rotation_euler = [math.pi/2, 0, rot]
                obj[0].scale = [0.5, 0.5, 0.5]

                rot = rot + math.pi/4

                all_objs_added.append(obj[0])

                obj[0].select_set(False)
                bpy.ops.wm.save_as_mainfile(filepath=self.filepath) 

            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            self.deselectObjects()

        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)
        return all_objs_added
        

    def hide_center_road(self):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()
        center_road = bpy.data.objects["secondary_roads.000"]
        center_road.select_set(True)
        center_road.hide_render = True # hiding this road as two streets will be created from this
        center_road.hide_viewport = True
        self.deselectObjects()

    def hide_path(self):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()
        for o in bpy.data.objects:
            if "osm_paths_footway" in o.name:
                path = o
        path.select_set(True)
        path.hide_render = True # hiding this road as two streets will be created from this
        path.hide_viewport = True
        self.deselectObjects()

    
    def add_cars(self):
        self.pokeLeftStreetVerts = []







                
        