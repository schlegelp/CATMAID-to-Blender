CATMAID-to-Blender
==================

Plugin for [Blender](http://www.blender.org "Blender Homepage") to interface
with [CATMAID](https://github.com/catmaid/CATMAID "CATMAID Repo") servers,
request and analyze data. Tested with Blender 2.92 and CATMAID 2020.02.15

## Important notice
As of version `7.0.0` this plugin is compatible with Blender 2.9x (2.8x should
also work but I haven't tested it). This unfortunately also makes it
incompatible with older Blender versions (i.e. 2.7x).

I took this opportunity to do a full refactor of the code to make things
faster and easier to maintain. This includes dropping a bunch of functionality
and to focus on the visualization aspects.

Notably I removed:

- coloring neurons by user
- importing pairs of neurons
- importing synaptic partners
- neuron statistics (cable length, # of branch points, etc)
- exporting neurons/connectors as SVGs
- similarity metrics
- animation of history

If for some reason you really really need a function that got dropped,
please open an issue here on Github. I also highly recommend you check out
[pymaid](https://github.com/schlegelp/pymaid) and [navis](https://github.com/schlegelp/navis)
which - in combination - let you do all the stuff that was dropped from this
plugin (see the [tutorials](https://navis.readthedocs.io/en/latest/source/gallery.html)).

## Installation:
First download [CATMAIDImport.py](https://raw.githubusercontent.com/schlegelp/CATMAID-to-Blender/master/CATMAIDImport.py), then:

#### Option A:
1. Start Blender -> **File** -> **User Preferences** -> **Addons** -> **Install from File** and select CATMAIDImport.py
2. Activate by ticking check box and click **Save User Setting**

#### Option B:
1. Directly place CATMAIDImport.py in \Blender\...\scripts\addons
2. Start Blender -> **File** -> **User Preferences** -> **Addons** -> Search for **CATMAIDImport** addon
3. Activate the script by ticking the check box and click **Save User Settings** (see [here](http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Add-Ons) for more detailed description)

#### Dependencies:
None! [Blender](http://www.blender.org "Blender Homepage") for Windows and MacOS
brings its own Python distribution and the plugin is written such that it
works without any external libraries.

## Setting a default connection:
Open **File** -> **User Preferences**, navigate to **Add-ons** ->
**CATMAIDImport** and change **CATMAID Server URL** in **preferences** to
your server. I also recommend saving your credentials for convenience:

Public CATMAID instances (like that hosted by
[VirtualFlyBrain](https://catmaid.virtualflybrain.org/)) to not require an API
token or HTTP users/passwords. If you want to connect to a private instance
however, chances are you will need to add credentials. For Information on how
to retrieve your Token look [here](http://catmaid.github.io/dev/api.html#api-token).

![server_url](https://user-images.githubusercontent.com/7161148/135828603-59352a8b-7b93-4c19-884c-e7b0d008e02b.png)

## Quickstart Guide:
The CATMAID panel will show up in the **Sidebar** of the **3D View**. This
sidebar might be hidden by default in which case you can either press
"N" while hovering over the 3D view or click the little left-pointing arrow in
the upper right corner to open it.

![import_panel](https://user-images.githubusercontent.com/7161148/135828762-1d833cd3-5f8a-4c58-9880-2220d3aa0560.png)

A couple notes:
- functions that need you to be logged into your CATMAID server will be
  disabled (greyed out) until you did so by using 'Connect to CATMAID'
- in order to identify cell bodies, the plugin searches for nodes with a `soma` tag

## Tutorials:
Please check out the Github [Wiki](https://github.com/schlegelp/CATMAID-to-Blender/wiki) for additional information and tutorials.

Note: these tutorials are still based on pre `7.0.0` version.

## License:
This code is under GNU GPL V3.

## Acknowledgments and how to cite:

#### General:
Please cite [Schlegel et al., 2016 (eLife)](https://elifesciences.org/content/5/e16799) if you use the plugin in your publication.
