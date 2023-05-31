CityScenes
====

1. Clone the WorldGen environment:

.. code-block:: bash
    cd $HOME/WorldGenBase
    git clone https://github.com/prgumd/WorldGen.git

2. Folder Setup:
The source code for the CityMaps is inside :code:`WorldGen/CityMaps`. Any additional assets can be added into the :code:`assets/` folder.

3. Config Files:
There are two main config files that you can modify:

A.  :code:`config.yaml` contains all the settings for creating the city scenes, camera and render settings.

B. :code:`materials.yaml` contains the file paths or links to various objects and materirals/textures.

4. Create your first city scene:
(Setup the config and material files first. Look at Config and Material)
Now, in the terminal, run

.. code-block:: bash
    
    blender -b -P run_worldgen.py # This creates a city scene without opening GUI

5. Render the generated :code:`.blend` scene by following `Render <Render>`_.

.. note::

    If only doing annotations, make sure only_render_annotations: True in config.yaml and add the outputs you want in the output variable of the file :code:`blender -b <path to blend file> -P run_worldgen.py` 
