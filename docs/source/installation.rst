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

3. Create Blender alias and test run Blender with GUI

.. code-block:: bash

    echo "alias blender='$HOME/WorldGenBase/blender/blender-3.3.7-linux-x64/./blender'" >> ~/.bashrc
    source ~/.bashrc
    blender

4. Install pip in blender-python

.. code-block:: bash
    
    cd blender-3.3.7-linux-x64/3.3/python/bin
    wget https://bootstrap.pypa.io/get-pip.py
    ./python3.10 get-pip.py

5. Install `pip` packages in blender-python

.. code-block:: bash
    
    cd $HOME/WorldGenBase/blender/blender-3.3.7-linux-x64/3.3/python/bin
    ./pip install numpy scipy opencv-python matplotlib mathutils setuptools==65.2.0 imath openexr
    

6. Dependencies:

sudo apt-get install openexr,
sudo apt-get install libopenexr-dev
sudo apt-get install zlib1g-dev






Blender add-ons
--------------------

Install the following add-ons:

* `Lily Surface Scraper <https://github.com/eliemichel/LilySurfaceScraper/>`_
* `tinyCAD <https://docs.blender.org/manual/en/latest/addons/mesh/tinycad.html/>`_
* `blender-osm <https://prochitecture.gumroad.com/l/blender-osm/>`_

