CATMAID-to-Blender
==================

Plugin for [Blender](http://www.blender.org "Blender Homepage") to interface with [CATMAID](https://github.com/catmaid/CATMAID "CATMAID Repo") servers, request and analyze data. Tested with Blender 2.77 and CATMAID 2016.09.01

*I encourage you to open an issue or contact me directly if you run into problems or have a __feature request__!*

## Installation:
First download [CATMAIDImport.py](https://raw.githubusercontent.com/schlegelp/CATMAID-to-Blender/master/CATMAIDImport.py), then:

######Option A:
2. Directly place CATMAIDImport.py in \Blender\...\scripts\addons
3. Start Blender -> 'File' -> 'User Preferences' -> 'Addons' -> Search for 'CATMAIDImport' addon 
4. Activate the script by ticking the check box and click 'Save User Settings' (see [here](http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Add-Ons) for more detailed description)

######Option B:
2. Start Blender -> 'File' -> 'User Preferences' -> 'Addons' -> 'Install from File' and select CATMAIDImport.py
3. Activate by ticking check box and click 'Save User Setting'

######Required Python packages:
[Blender](http://www.blender.org "Blender Homepage") for Windows and MacOS should come with all necessary Python packages. On Linux make sure [numpy](http://www.numpy.org/) is installed. Without [numpy](http://www.numpy.org/) the addon will work but some functions are limited.

There are several ways to install additional packages for Blender's Python. The easiest way is probably this:

- Download pip's [get-pip.py](https://pip.pypa.io/en/stable/installing/) and save e.g. in your downloads directory
- Run [get-pip.py](https://pip.pypa.io/en/stable/installing/) from Blender Python console:

```python
with open('/Users/YOURNAME/Downloads/get-pip.py') as source_file:
    exec(source_file.read())
```

- Then use pip to install any given package. Here, we install as Scipy an example:
```python
import pip
pip.main(['install','scipy'])
```

## Before First Use:
Open User Preferences, navigate to 'Add-ons' -> 'CATMAIDImport' and change 'CATMAID Server URL' in 'preferences' to your server.
You may also save your credentials for convenience.

![server_url](https://cloud.githubusercontent.com/assets/7161148/13985056/9b915b22-f0fa-11e5-8b8f-ecac97405708.PNG)

## Tokens:
The CATMAID API authorizes requests using an API token tied to user account instead of a username and password.
For Information on how to retrieve your Token look [here](http://catmaid.github.io/dev/api.html#api-token).

## Quickstart Guide:
Import/Export panel will show up under the 'Scene' tab in the 'Properties' windows

![import_panel](https://cloud.githubusercontent.com/assets/7161148/5356718/c244a7a6-7f9f-11e4-8cef-b69b3cf20b32.PNG)

- Functions (e.g. Retrieving skeletons/connectors) that need you to be logged into your CATMAID server will be grayed-out until you did so by hitting 'Connect 2 CATMAID'
- Skeletons can be retrieved by their skeleton ID, by annotations or based on connectivity (Retrieve Partners)
  - Important side node: in order to identify cell bodies, the script searches for nodes with a radius > 10
- Once imported, skeleton/connector data can be readily exported to vector graphics (SVG) with a broad range of options (e.g. coloring, filters, scaling). Look at lower left panel when exporting for these options.

![export_options](https://cloud.githubusercontent.com/assets/7161148/5356716/bf994da4-7f9f-11e4-8e10-c5c628baab47.PNG)

## Examples:

####1. Color neurons by similarity and export to vector graphic (SVG)
<img src="https://cloud.githubusercontent.com/assets/7161148/14020628/465496f4-f1d8-11e5-899b-5bb1f6baf8b0.png" width="650">


####2. Group postsynaptic sites based on what presynaptic neuron they connect to
<img src="https://cloud.githubusercontent.com/assets/7161148/14020676/7df96468-f1d8-11e5-9f04-aba115112890.png" width="650">

####3. Check out [Schlegel et al., 2016](http://biorxiv.org/content/early/2016/04/07/044990) for more examples.

## License:
This code is under GNU GPL V3

## Acknowledgments and how to cite:

#### General:
Please cite [Schlegel et al., 2016 (eLife)](https://elifesciences.org/content/5/e16799) if you use the plugin in your publication.

#### Specific Methods:
Some functions available within the plugin are based on/derived from previously published methods. Please cite the original papers if you make use of these specific methods.

1. **Comparison of neurons based on morphology**: Cell. 2013 Dec 19;155(7):1610-23. doi: 10.1016/j.cell.2013.11.025.
*A bidirectional circuit switch reroutes pheromone signals in male and female brains.*
Kohl J, Ostrovsky AD, Frechter S, Jefferis GS. 
http://www.cell.com/abstract/S0092-8674(13)01476-1
2. **Comparison of neurons based on connectivity**: Science. 2012 Jul 27;337(6093):437-44. doi: 10.1126/science.1221762.
*The connectome of a decision-making neural network.*
Jarrell TA, Wang Y, Bloniarz AE, Brittin CA, Xu M, Thomson JN, Albertson DG, Hall DH, Emmons SW.
http://science.sciencemag.org/content/337/6093/437.long
3. **Comparison of neurons based on synapse distribution**: eLife. doi: 10.7554/eLife.16799 
*Synaptic transmission parallels neuromodulation in a central food-intake circuit.*
Schlegel, P., Texada, M. J., Miroschnikow, A., Schoofs, A., Hückesfeld, S., Peters, M., … Pankratz, M. J.
https://elifesciences.org/content/5/e16799
