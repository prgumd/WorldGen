import bpy
import random
from mathutils.bvhtree import BVHTree
import bmesh
from scipy import spatial
import mathutils


def new_plane(location, size, name):
    bpy.ops.mesh.primitive_plane_add(
        size=size,
        calc_uvs=True,
        enter_editmode=False,
        align='WORLD',
        location=location,
        rotation=(0, 0, 0),
        scale=(0, 0, 0))
    current_name = bpy.context.selected_objects[0].name
    plane = bpy.data.objects[current_name]
    plane.name = name
    plane.data.name = name + "_mesh"
    return plane

def new_sphere(location, scale, name):
    # location is a tuple, scale is a tuple, name is a string

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=location, scale=scale)
    current_name = bpy.context.selected_objects[0].name
    sphere = bpy.data.objects[current_name]
    sphere.name = name
    sphere.data.name = name + "_mesh"
    return sphere

def add_wind(location, scale):
    bpy.ops.object.effector_add(type='WIND', enter_editmode=False, align='WORLD', location=location, scale=scale)

def select_objects(collection, is_selected):
    for obj in collection.all_objects:
        obj.select_set(is_selected)
        if is_selected:
            bpy.context.view_layer.objects.active = obj

def deselect_all_objects():
    for obj in bpy.data.objects:
        obj.select_set(False)

def get_obj_with_name(name):
    objs = []
    for obj in bpy.data.objects:
        if name in obj.name:
            objs.append(obj)
            # obj.select_set(True)
            # bpy.context.view_layer.objects.active = obj
    return objs

def create_collection(collection_name):
    # assumes that there is no collection with collection_name

    new_collection = bpy.data.collections.new(collection_name)

    bpy.ops.object.select_all( action='DESELECT' ) # Deselect all objects
    bpy.ops.object.select_pattern(pattern=collection_name)

    for col in bpy.data.collections:
        if len(col.objects) > 0:
            for obj in col.objects:
                
                col.objects.unlink(obj)

def assign_pass_indexes_by_name(classNames):
    pass_index = 0
    is_collection_name = False
    for className in classNames:

         

        # # pick a random pass index to assign to this class
        # num = random.randint(0,100)
        # while(num in pass_indexes):
        #     num = random.randint(0,100)

        for collection in bpy.data.collections:
            # if collection of objects then assign same pass index to all
            if collection.name == className:
                is_collection_name = True
                for obj in collection.all_objects:
                    obj.pass_index = pass_index
                break
        
        if is_collection_name == False:
            # if its not a collection name, then look for objects with this name
            # for obj in bpy.data.objects:
            #     if className in obj.name:
            #         obj.pass_index = pass_index
            for o in bpy.data.objects:
                if className in o.name:
                    for c in o.children:
                        c.pass_index = pass_index

                    o.pass_index = pass_index
        
        is_collection_name = False # reset for next iteration
        pass_index = pass_index + 1

def assign_pass_indexes_by_collection_name(classNames):
    pass_index = 0
    is_collection_name = False
    for className in classNames:

         

        # # pick a random pass index to assign to this class
        # num = random.randint(0,100)
        # while(num in pass_indexes):
        #     num = random.randint(0,100)

        for collection in bpy.data.collections:
            # if collection of objects then assign same pass index to all
            if collection.name == className:
                is_collection_name = True
                for obj in collection.all_objects:
                    obj.pass_index = pass_index
                break
        
        if is_collection_name == False:
            # if its not a collection name, then look for objects with this name
            # for obj in bpy.data.objects:
            #     if className in obj.name:
            #         obj.pass_index = pass_index
            for o in bpy.data.objects:
                if className in o.name:
                    for c in o.children:
                        c.pass_index = pass_index

                    o.pass_index = pass_index
        
        is_collection_name = False # reset for next iteration
        pass_index = pass_index + 1
        
def getListofBuildings(name):
    list_of_buildings = []
    for collection in bpy.data.collections:
            if name in collection.name:
                buildings = collection.name
                active_obj = bpy.data.objects[buildings]
                bpy.context.view_layer.objects.active = active_obj
                myObjs = bpy.context.active_object
                for o in myObjs.children:
                    list_of_buildings.append(o.name)
    print("listof buildings : ", list_of_buildings)
    return list_of_buildings

def checkOverlap(obj1, obj2):
    scene = bpy.context.scene

    #create bmesh objects
    bm1 = bmesh.new()
    bm2 = bmesh.new()

    #fill bmesh data from objects
    bm1.from_mesh(scene.objects[obj1].data)
    bm2.from_mesh(scene.objects[obj2].data)

    #fixed it here:
    bm1.transform(scene.objects[obj1].matrix_world)
    bm2.transform(scene.objects[obj2].matrix_world) 

    #make BVH tree from BMesh of objects
    obj_now_BVHtree = BVHTree.FromBMesh(bm1)
    obj_next_BVHtree = BVHTree.FromBMesh(bm2)         

    #get intersecting pairs
    inter = obj_now_BVHtree.overlap(obj_next_BVHtree)

    #if list is empty, no objects are touching
    return inter != []

def pokeStreet(street): 
     #picking the left street for now
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
    poked = bmesh.ops.poke( bm, faces=faces)
    bmesh.update_edit_mesh(me)

    obj = bpy.context.object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    poked = [[vert.co.x, vert.co.y, vert.co.z] for vert in poked["verts"]]

    bpy.ops.object.mode_set(mode = 'OBJECT')
    deselect_all_objects()
    
    return poked

def createCurve(coords, name):
    curveData = bpy.data.curves.new('curve', type='CURVE')
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
    curveOB = bpy.data.objects.new(name, curveData)
    return curveOB, polyline

def getCoordsForCurve(poked, street):
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

    return coords