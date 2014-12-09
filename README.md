CATMAID-to-Blender
==================

Plugin for [Blender](www.blender.org "Blender Homepage") to interface with [CATMAID](https://github.com/acardona/CATMAID "CATMAID Repo") servers and request data. Tested with Blender 2.6x and 2.7x

## Installation:
1. Download CATMAIDImport.py and place in \Blender\...\scripts\addons
2. Start Blender -> 'File' -> 'User Preferences' -> 'Addons' -> Search for 'CATMAID' addon and activate by checking box -> 'Save User Settings'

## Before First Use:
Open CATMAIDImport.py and change server_url to your server's url. 

## Quickstart Guide:
- Import/Export panel will show up under the 'Scene' tab in the 'Properties' windows
- Functions (e.g. Retrieving skeletons/connectors) that need you to be logged into your CATMAID server will be grayed out-until did so by hitting 'Connect 2 CATMAID'
- Skeletons can be retrieved by their skeleton ID, by annotations or based on connectivity (Retrieve Partners)
  - Important side node: in order to identify cell bodies, the script searches for nodes with a radius > 10
- Once imported, skeleton/connector data can be readily exported to vector graphics (SVG) with a broad range of options (e.g. coloring, filters, scaling). Look at lower left panel when exporting for these options.

## Pro Tip of the Day:
Open Blender's console to e.g. see error messages or follow the progress while importing.
'Window' -> 'Toggle System Console'

## License:
This code is under GNU GPL V3
