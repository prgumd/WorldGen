import bpy
import random
from mathutils.bvhtree import BVHTree
import bmesh


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


def assign_pass_indexes(classNames):
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


# def checkOverlap(obj1_name, obj2_name):
    # obj1_name : string
    # obj2_name : string
    # returns boolean - True if both objects overlap

    # Get the objects
    obj1 = bpy.data.objects[obj1_name]
    obj2 = bpy.data.objects[obj2_name]
    

    # Get their world matrix
    mat1 = obj1.matrix_world
    mat2 = obj2.matrix_world

    # Get the geometry in world coordinates
    vert1 = [mat1 @ v.co for v in obj1.data.vertices] 
    poly1 = [p.vertices for p in obj1.data.polygons]
    print("obj1: ", obj1)
    print("vert1: ", len(vert1))


    vert2 = [mat2 @ v.co for v in obj2.data.vertices] 
    poly2 = [p.vertices for p in obj2.data.polygons]
    print("obj2: ", obj2)
    print("vert2: ", len(vert1))

    # Create the BVH trees
    bvh1 = BVHTree.FromPolygons( vert1, poly1 )
    bvh2 = BVHTree.FromPolygons( vert2, poly2 )
    print("overlap : ", bvh1.overlap(bvh2))

    # Test if overlap
    
    if len(bvh1.overlap(bvh2)) > 0:
        print('insside check overlap : ', bvh1.overlap(bvh2))
        return True
    else:
        return False