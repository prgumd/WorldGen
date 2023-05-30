About WorldGen
====

.. image:: ../images/paper/Banner.png
  :width: 75%
  :alt: WorldGen Banner Image
  :align: center

Generative ability of WorldGen (shown in the figure above): (a) Comparison between Google Street View (left) and the same street in WorldGen (right), (b) Comparison of Google Maps satellite image vs. WorldGen top view, (c) Collection of 3D objects in motion, (d) Object fragmentation,(e) Annotation from left to right: depth, optical flow, surface normals, stereo anaglyph, image segmentation, event frame.

----

Abstract
----

In the era of deep learning, data is the critical determining factor in the performance of neural network models. Generating large datasets suffers from various difficulties such as scalability, cost efficiency and photorealism. To avoid expensive and strenuous dataset collection and annotations, researchers have inclined towards computer-generated datasets. Although, a lack of photorealism and a limited amount of computer-aided data, has bounded the accuracy of network predictions.

To this end, we present WorldGen - an open source framework to autonomously generate countless structured and unstructured 3D photorealistic scenes such as city view, object collection, and object fragmentation along with its rich ground truth annotation data. WorldGen being a generative model gives the user full access and control to features such as texture, object structure, motion, camera and lens properties for better generalizability by diminishing the data bias in the network. We demonstrate the effectiveness of WorldGen by presenting an evaluation on deep optical flow. We hope such a tool can open doors for future research in a myriad of domains related to robotics and computer vision by reducing manual labor and the cost of acquiring rich and high-quality data.


----

Environments
----
Currently, WorldGen supports three different environments: (more coming soon)

#. CiyMaps: This utilizes semantics from OpenStreet Maps and combines it with open-source models, textures and HDRI sources to generate a digital twin of existing cities in Blender rendering engine.
#. ObjectPile: We import open source collection of 3D objects in a table top environment with different textures wrapped over these objects as well as use dynamic lighting and depth of field effects for rendering. We also incorporate variational UV mapping to modify these objects in terms of both textures and structure.
#. Object Fragmentation: This environment shows how an objects fall on a table top scene or collide with another object and breaks into a user-define N segments.

For all these 3D environments, we currently support generation of high quality data using 'CYCLES' (or 'EEVEE' only for RGB and Depth) rendering engine with annotations:

#. RGB Images
#. Depth Maps
#. Optical Flow
#. Surface Normals
#. Stereopsis
#. Semantic Segmentation
#. Event Camera Frames



Citation
----

.. image:: ../images/paper/paper_thumb.png
  :width: 15%
  :alt: Paper Thumbnail

* | Singh, C.D., Kumari, R., Fermüller, C., Sanket, N.J. and Aloimonos, Y., 
  | WorldGen: A Large Scale Generative Simulator. 
  | 2023 IEEE International Conference on Robotics and Automation (ICRA)
`Video <https://www.youtube.com/watch?v=IOz8-KL900A&pp=ygUPd29ybGRnZW4gcHJndW1k>`__

BibTeX:

* | @article{singh2022worldgen,
  | title={WorldGen: A Large Scale Generative Simulator},
  | author={Singh, Chahat Deep and Kumari, Riya and Ferm{\"u}ller, Cornelia and Sanket, Nitin J and Aloimonos, Yiannis},
  | journal={arXiv preprint arXiv:2210.00715},
  | year={2022}
  | }
