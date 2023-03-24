
import bpy
import os
import random
import bmesh
import mathutils
import math
from .camera import Camera


class Simulator:

    from .weather import addWeather
    
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
        self.cameras = []
        self.active_camera = None

    def createScene(self, minLong, minLat, maxLong, maxLat, isSuburbs=False, terrainTexture='', 
                    roofTextures=[], streetTextures=[], treeObjects=[], benchObjects=[], streetLampObjects=[]):
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

        # self.addTextureToBuildings()
        # bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addTextureToTerrain()
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        # self.addTextureToRoofs()
        # bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addStreets()
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addTrees(["./assets/Tree/tree.obj"], 1)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        intersections = self.getIntersections("secondary_streets.000")
        print(intersections)

        self.addingToSidewalks("street_lamps", ['./assets/StreetLamps/twoStreetLights2.obj'], 80, intersections)
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)
        print("added streetlights")

        self.addingToSidewalks("benches", ['./assets/Bench/twinBenches.obj'], 20, intersections)
        print("added benches")
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

        self.addTextureToRoads()
        bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

    def addCamera(self):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        self.deselectObjects()

        if self.isTwoWay:
            # left and right street
            streets = ["secondary_streets.001", "secondary_streets.002"]

            street = streets[0] #picking the left street for now
            street = bpy.data.objects[street]

            # Selecting the edit mode version of the street
            street.select_set(True)
            bpy.context.view_layer.objects.active = street
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            obj = bpy.context.edit_object # getting the context
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            faces = [f for f in bm.faces if f.select] # getting all the selected faces

            # poke faces
            if not self.pokeLeftStreet : 
                poked = bmesh.ops.poke( bm, faces=faces)
                bmesh.update_edit_mesh(me)
                # bm = bmesh.from_edit_mesh(me)

                obj = bpy.context.object
                me = obj.data
                bm = bmesh.from_edit_mesh(me)
                self.pokeLeftStreet = True
            
            vertices = [v for v in bm.verts]
            
            # ****** Can use these vertices to construct any kind of curve you want *****

            vertices = [vertex for vertex in vertices if len(vertex.link_edges) == 4]
            bpy.ops.mesh.select_all(action='DESELECT')
            
            animation_count = 20
            coords = []
            for i,v in enumerate(vertices):
                # if i > 20:
                v.select_set(True)
                world_coords = street.matrix_world @ v.co
                coords.append(world_coords)
                    # if animation_count + 20 == i:
                    #     break
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
            # print(polyline.points[0])
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
            # camera.rotation = [1.38569, -8.8702e-07, -1.53589]

            self.deselectObjects()

            bpy.ops.wm.save_as_mainfile(filepath=self.filepath)

            camera_obj = Camera(cam_name)
            print("cam name : ", cam_name)
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

    def addTextureToBuildings(self):
        
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
        grouped_buildings = self.chunks(list_of_buildings, round(len(list_of_buildings)/4))

        list_of_building_url = ["https://ambientcg.com/view?id=Facade018A", "https://ambientcg.com/view?id=Facade001", "https://ambientcg.com/view?id=Facade020A", "https://ambientcg.com/view?id=Facade005", "https://ambientcg.com/view?id=Facade006"]
        list_of_building_materials = ["ambientCG/Facade018A/1K-JPG", "ambientCG/Facade001/1K-JPG", "ambientCG/Facade020A/1K-JPG", "ambientCG/Facade005/1K-JPG", "ambientCG/Facade006/1K-JPG"]
        
        for idx, group in enumerate(grouped_buildings):
            
            # select all buildings in a group
            for building in group:
                bpy.data.objects[building].select_set(True)

                # bpy.context.view_layer.objects.active = bpy.data.objects[group[0]]
                bpy.context.view_layer.objects.active = bpy.data.objects[building]
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                # pick material    
                if len(bpy.context.object.material_slots) == 0:
                    continue
                bpy.context.object.active_material = bpy.data.materials['wall']
                material_url = list_of_building_url[idx]
                bpy.ops.material.new()

                bpy.ops.object.lily_surface_import(url=material_url)
            
                # apply material to buildings in the group
                bpy.ops.uv.smart_project()
                material = list_of_building_materials[idx]
                bpy.data.materials[material].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 2
                bpy.data.materials[material].node_tree.nodes["Mapping"].inputs[3].default_value[1] = 2
                bpy.ops.object.mode_set(mode = 'OBJECT')
            
                bpy.data.objects[building].select_set(False)
            self.deselectObjects()

    def addTextureToTerrain(self):
        '''
        Adds texture to the ground terrain. Using textures from https://ambientcg.com/

        Args:
            None
        Returns:
            None
        '''
        self.deselectObjects()

        material_urls = ["https://ambientcg.com/view?id=PavingStones087", "https://ambientcg.com/view?id=PavingStones053", "https://ambientcg.com/view?id=PavingStones065"]
        material = ["ambientCG/PavingStones087/1K-JPG", "ambientCG/PavingStones053/1K-JPG", "ambientCG/PavingStones065/1K-JPG"]

        idx = 1

        bpy.context.view_layer.objects.active = bpy.data.objects["Terrain"]
        obj = bpy.context.active_object
        obj.select_set(True)

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        bpy.ops.material.new()
        bpy.ops.object.lily_surface_import(url=material_urls[idx])
        # bpy.ops.uv.smart_project()
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)


        bpy.data.materials[material[idx]].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 110
        bpy.data.materials[material[idx]].node_tree.nodes["Mapping"].inputs[3].default_value[1] = 110

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
            obj.name = 'secondary_streets.000' # will use this joined road to create two new roads which will be translated left and right to create two different flows of traffic

            bpy.ops.object.duplicate(linked=False)
            bpy.ops.transform.translate(value=(-1.59264, -3.9816, 0), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            # bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.816367, 10.3733, 1.72802), "orient_axis_ortho":'X', "orient_type":'LOCAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'LOCAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0.816367, 10.3733, 0), "orient_axis_ortho":'X', "orient_type":'LOCAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'LOCAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            # selecting the roads
            for collection in bpy.data.collections:
                if "osm" in collection.name:
                    for obj in collection.all_objects:
                        if "road" in obj.name or "street" in obj.name:
                            obj.select_set(True)
                            bpy.context.view_layer.objects.active = obj

            # translate the roads to be higher than the plane
            # bpy.ops.transform.translate(value=(0, 0, 1.24545), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            
            bpy.data.objects['secondary_streets.000'].hide_render = True # hiding this road as two streets will be created from this
            bpy.data.objects['secondary_streets.000'].hide_viewport = True

    def addTextureToRoads(self):
        '''
        Adding texture to roads. 

        Args:
            None

        Returns:
            None
        '''

        self.deselectObjects()
        roads = None
        if self.isTwoWay:
            roads = ['primary', 'service', 'tertiary', 'unclassified', 'secondary_streets.001', 'secondary_streets.002']
        else:
            roads = ['primary', 'service', 'tertiary', 'unclassified']

        roadTextureUrls = ["https://www.cgbookcase.com/textures/highway-road-cracks-01"]
        roadTextures = ["cgbookcase/Highway Road Cracks 01/1K"]
        view_layer = bpy.context.view_layer

        roadObjects = []

        for i in roads:
            nonMeshObjExists = False
            for collection in bpy.data.collections:
                if "osm" in collection.name:
                    for obj in collection.all_objects:
                        if i in obj.name:
                            obj.select_set(True)
                            roadObjects.append(obj)
                            view_layer.objects.active = obj
                            if obj != "MESH":
                                nonMeshObjExists = True
     

        if nonMeshObjExists:
            bpy.ops.object.convert(target='MESH') # convert curve to mesh
            

        self.deselectObjects()

        for obj in roadObjects:
            obj.select_set(True)
            view_layer.objects.active = obj     
            obj.hide_set(False)     
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            

            # bpy.ops.material.new()
            bpy.ops.object.lily_surface_import(url=roadTextureUrls[0])
            bpy.data.materials[roadTextures[0]].node_tree.nodes["Mapping"].inputs[3].default_value[0] = 4.6

            for i in range(len(obj.material_slots)):
                if roadTextures[0] in obj.material_slots[i].name:
                    bpy.context.object.active_material_index = i
                    break
            
            bpy.context.object.active_material_index = i
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

    def addTrees(self, treeFilePaths, numOfTrees):
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
                # print("treefilepaths : ", treeFilePaths)
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
        
        print("here")
        # self.deselectObjects()

        return vertices

    def deselectObjects(self):
        for obj in bpy.data.objects:
            obj.select_set(False)

    def addingToSidewalks(self, nameOfObj, objectFilePaths, numOfObjects, intersections):
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
        
        
        object = bpy.data.objects["secondary_streets.000"]

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
        random.shuffle(vertices) # we want to place objects randomly
        
        # bpy.ops.object.mode_set(mode = 'OBJECT')
        # self.deselectObjects()

        count = 0
        
        set_of_objects = []
        print(nameOfObj)
        print("len of verticeds", len(vertices))

        for v in vertices:
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
                print(obj)
                print(len(obj))

                # placing object
                print("vertex_coords : ", vertex_coords)
                obj[0].location = [vertex_coords.x, vertex_coords.y, coords.z - 0.45]
                obj[0].scale = [0.5, 0.5, 0.5]

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
                if count == numOfObjects:
                    break
                else:
                    count = count + 1
                obj[0].select_set(False)
                set_of_objects.append(obj[0])
                

        
        
        self.deselectObjects()

        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        object = bpy.data.objects["secondary_streets.000"]
        object.hide_viewport = visibility_viewport
        object.hide_render = visibility_render
        
        self.deselectObjects()
        
        
    def addTextureToRoofs(self):
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
        grouped_roofs = self.chunks(list_of_roofs, round(len(list_of_roofs)/2))

        roof_textures_url = ["https://ambientcg.com/view?id=Concrete017", "https://ambientcg.com/view?id=Concrete036", "https://ambientcg.com/view?id=Concrete019"]
        roof_textures = ["ambientCG/Concrete017/1K-JPG", "ambientCG/Concrete036/1K-JPG", "ambientCG/Concrete019/1K-JPG"]
        
        for idx, group in enumerate(grouped_roofs):
            print("len of groups : ", len(grouped_roofs))
            print("idx : ", idx)
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
                material = roof_textures[idx]
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
            