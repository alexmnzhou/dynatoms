# Dynatoms Introduction
<img src="https://i.ibb.co/rc0GWqw/Dynatoms.png" alt="Dynatoms logo" width="100" height="100">

Molecular model kits are an awesome, tactile way to visualize chemicals. However, standard kit implementations fall short of modern research and higher-educational applications in a number of important ways:

1. Each molecule has to be assembled *by hand* (and later taken apart when the pieces need to be reused). Assembly can be prohibitively time-consuming and costly as molecular geometries increase in complexity.
2. Dihedral angles are limited to only the most common configurations (e.g. Carbon atoms typically have four "holes" for bonds, which can only work in tetrahedral geometries).
3. Actual bond distances aren't preserved as most kits have 1 or 2 set bond lengths.
4. The size of the atoms and bond lengths is static, *so only small geometries can be modeled at a reasonable size.*
5. Visualizing equal energy structures and changes in molecular geometry requires multiple models.

A number of protocols have been published to demonstrate the effectiveness of 3D printing molecular models, which solves many of these problems, but not all of them. Most importantly, 3D printing technology is capable of modeling the changes in molecular structure, but no existing protocol includes this functionality. Dynatoms solves this problem with a dedicated UI that allows for generating highly customizable, dynamic 3D printable molecular models on the fly.

## Features

![Dynatoms interface](https://i.ibb.co/ryGFCcg/Screen-Shot-2020-04-13-at-11-05-46-PM.png)

**Dynamic Joints**

Dynatoms can function as a simple model generator that takes in the most common chemical file formats (.pdb, .mol, .cif) and outputs a 3D printing-ready solid model file (.stl), but many chemical software suites have this functionality built in.
The main contribution of Dynatoms lies in its parametric, entirely 3D printed joints! So far, there are two designs: a rotating cylindrical joint and a ball joint.

Simply select a joint loaded from an xyz, cif, or pdb file and press the "Place Joint Here" button on the sidebar. This will attempt to remove the joint and render a default cylindrical joint and then rotate the entire part to make the joint horizontal with the surface to optimize printing.

Clicking "Render STL" will attempt to generate a 3D model STL file from what is on screen ready for slicing and 3D printing.

**Customization**

Dynatoms has a number of settings to tinker with to get the molecular model you want. Change relative ball/model size, scaling factor (relative to atomic weight), or colors. By default, sphere size is set to the Van Der Waals radius with extremely heavy atoms scaled downwards.
