
Installation Guide
==========

* Systems supported : Ubuntu 22 LTS
* GPU: NVIDIA TITAN Xp and older
* RAM: 4GB (Minimum), 16GB (Recommended)
* Python 3.7+
* Blender Version : 3.0+ (Tested on 3.2.2)


Linux
=====

1. System Package Update

.. code-block:: bash
    
    sudo apt update
    sudo apt upgrade

2. Download and extract Blender.

.. code-block:: bash

    mkdir -p $HOME/WorldGenBase/blender
    cd $HOME/WorldGenBase/blender
    wget https://mirrors.ocf.berkeley.edu/blender/release/Blender3.3/blender-3.3.7-linux-x64.tar.xz
    tar -xf blender-3.3.7-linux-x64.tar.xz

3. Install Python 3.10 in your system
.. code-block:: bash
    sudo apt-get install python3.10 python3.10-dev


4. Create Blender alias and test run Blender with GUI

.. code-block:: bash
    
    # Add System Python Path to Blender
    echo "PYTHONPATH=/usr/lib/python3.10" >> ~/.bashrc
    echo "alias blender='$HOME/WorldGenBase/blender/blender-3.3.7-linux-x64/./blender --python-use-system-env'" >> ~/.bashrc
    source ~/.bashrc
    blender

.. note::
    Confirm you installed version is `3.3.7`. You can close the blender GUI now. Go back to the terminal and continue with installing custom packages.

.. note::
   Blender comes with its own version to Python. Packages already in your system's Python will not be loaded into Blender unless you load them using Python Path.

----

5. Install pip3.10 in python if it is not default:

.. code-block:: bash
    
    cd $HOME/
    wget https://bootstrap.pypa.io/get-pip.py
    python3.10 get-pip.py
    python3.10 -m setup.py install

6. Install Dependencies

.. code-block:: bash
    
    sudo apt-get install openexr libopenexr-dev zlib1g-dev

7. Install `pip` packages in blender-python

.. code-block:: bash
    
    pip3.10 install numpy scipy opencv-python matplotlib mathutils setuptools==65.2.0

.. note::
   To install pip packages in blender-python in future, use this as a reference.

8. Install OpenEXR

.. code-block:: bash
   pip3.10 install openexr imath

.. note::
    If you run into errors while install openexr, please follow `this <https://stackoverflow.com/questions/72364623/modulenotfounderror-no-module-named-openexr-on-blender>`_.  
   

   









Blender add-ons
--------------------

Install the following add-ons:

* `Lily Surface Scraper <https://github.com/eliemichel/LilySurfaceScraper/>`_
* `tinyCAD <https://docs.blender.org/manual/en/latest/addons/mesh/tinycad.html/>`_
* `blender-osm <https://prochitecture.gumroad.com/l/blender-osm/>`_

