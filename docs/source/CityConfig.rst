CityConfig
====

A sample :code:`config.yaml` file looks like:

.. code-block:: yaml

python_system_path: /usr/lib/python3.10 # Use the libraries from your system python (must match the python version of blender python)


.. list-table:: Config Parameters
    :widths: 5 10


    * - python_system_path
      - Path to Python packages (e.g., "/home/chahatdeep/.local/lib/python3.8/site-packages"). The Python version must match the Blender Python version.


    * - render_dir
      - Path to save the blend file.


    * - blend_filepath
      - Path to save the blend file created.

    * - only_render_annotations
      - If set to True, no city will be made (all other settings are overridden, only outputs will be looked at). To generate a city, set this to False and provide a blend file for annotations generation.
      
    * - render_engine
      - Required. Choose from BLENDER_EEVEE or CYCLES.
      
    * - image_resolution
      - Required. In this format : [x_resolution, y_resolution, resolution_percentage]
    
    * - scene_coordinates
      - This may help you pick out scene coordinates : http://prochitecture.com/blender-osm/extent/?blender_version=3.0&addon=blender-osm&addon_version=2.6.3 For no errors, make sure you are choosing a large enough area, best performance occurs in cities, try creating a smaller city, if that works then try to create as big of a city as you want.
      
    * - outputs
      - possible values : [‘image’, ‘depth’, ‘stereo’, ‘semantic-seg’, ‘flow’, ‘events’]; note: to generate events, make sure you also select image : [image, events]
    
    * - weather
      - Format is an array of a single string: ['midday']. Choose from 'midday', 'sunset', or 'night'.
    
    * - class_names
      - ["Trees", "StreetLamps", "TwinBenches", "buildings", "roads", "Terrain", "buildings", "car"] # DO NOT TOUCH THIS
      


