Why WorldGen?
====

Data is a critical determining factor in the performance of neural networks for autonomous systems such as self driving cars and drones. Generating large datasets in simulation environments suffers from various difficulties such as scalability and photorealism. 

Creating 3D scenes in simulation environments often requires a lot of manual effort that makes the data generation process expensive, time consuming and strenuous. 


.. image:: ../images/paper/manual.gif
  :width: 45%
  :alt: Creating Scenes Manually
  
.. image:: ../images/paper/manual2.gif
  :width: 45%
  :alt: Annotating Scenes Manually

On the other side of the coin, the real data annotation and cleaning requires extensive manual effort to label the data which often leads in not-so-perfect annotations due to human errors.

Rather than manually recreating the entire world in the simulation, we take advantage of the real world that we have already created. We utilize the semantic, structural and depth information from the satellite maps in order to create a high definition 3D model of the entire cities and warp appropriate texture maps on this data.

.. image:: ../images/paper/worldgen.gif
  :width: 100%
  :alt: Annotating Scenes Manually

WorldGen is a generative simulator for various applications ranging from a drone flying over the city, through the city all the way to self driving car views. Since, we have the entire control over the models, we have the ability to dynamically changing scene lighting, weather conditions and textures in our 3D map. WorldGen can generate models of countless real world cities in a simulation environment.


