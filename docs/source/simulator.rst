Simulator Usage
====================

Initializing settings
------------------------
Need to initalize settings as follows. Can choose between BLENDER_EEVEE and CYCLES and change image resolution as needed.

.. code-block:: python

    WorldGen.set_render_engine('BLENDER_EEVEE') # choose from BLENDER_EEVEE, CYCLES, BLENDER_WORKBENCH
    WorldGen.set_metadata_properties() # can edit this in WorldGen/settings.py
    WorldGen.set_image_resolution(1084, 1084, 100) 
    

Setting up the simulator
------------------------

To use WorldGen, first initialize by passing in the file path to the blend file, followed by coordinates to the scene in following format (minLon, minLat, maxLon, maxLat). Can use this to figure out coordinates : http://prochitecture.com/blender-osm/extent/?blender_version=3.0&addon=blender-osm&addon_version=2.6.3

.. code-block:: python

   simulator = WorldGen("./name_of_blend_file.blend")
   simulation.createScene(-122.4, 37.7865, -122.387, 37.7925) # (minLon, minLat, maxLon, maxLat)
   
If the scene is rural or suburbs then set isSuburbs to true for slanted roofs:

.. code-block:: python

   simulation.createScene(-122.4, 37.7865, -122.387, 37.7925, isSuburbs=True)

> def createScene ( minLong, minLat, maxLong, maxLat, 
> isSuburbs=False,     # if True then will use gabled roofs 
> terrainTexture='',   # optional, can pass link to your own texture for the ground
> roofTextures=[],     # optional, can pass a list of roof textures
> streetTextures=[],   # optional, can pass a list of street textures
> treeObjects=[],      # optional, can pass a list of filepaths to tree objects
> benchObjects=[],     # optional, can pass a list of filepaths to bench objects
> streetLampObjects=[] # optional, can pass a list of filepaths to street lamp objects
> )

Creates scene given latitude and longitude, flat roofs are imported by default

Args:
    minLong, minLat, maxLong, maxLat (int): longitudes and latitudes of region
    isSuburbs (boolean) : Must specify whether scene created is of a suburb/rural area. If true, then slanted/gabled roofs will be enabled

Returns:
    None
   
.. _RST Textures:
Adding textures/materials
------------------------------------

WorldGen uses LilySurface Scrapper (https://github.com/eliemichel/LilySurfaceScraper) for importing materials for the building, roads, and terrain. If you wish to use materials other than the default ones used, you can select them from 

- https://www.3dassets.one/#order=latest
- https://polyhaven.com/textures
- https://www.cgbookcase.com/textures/
- https://ambientcg.com/

Configuring weather and lighting conditions
------------------------------------------------
WorldGen supports 3 different lighting conditions and 4 different weather conditions. You can also specify the background image by passing in an hdri link to the hdri_img variable.

.. code-block:: python
    
    simulation.addWeather(
        lighting='midday'|'sunset'|'night', 
        weather = 'rain'|'cloudy'|'clear'|'fog'
        hdri_img="" #choose from the textures and materials libraries mentioned above
    )





