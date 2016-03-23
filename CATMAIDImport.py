"""
    CATMAID to Blender Import Script - connects to CATMAID servers and retrieves
    skeleton data
    Copyright (C) 2014 Philipp Schlegel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    

### CATMAID to Blender Import Script - Version History:

### V4.3 23/03/2015:
    - changed addon name to CATMAIDImport - needs to be the same as bl_label of Addon preference class
    - added Addon Settings for credentials and server url
    - added self.report() to all error messages -> will show error message at cursor loc
    - connecting to CATMAID now does a test call by asking for user list
    - improved prepare 4 blender functionality
    - added advanced tooltip to some functions
    - added 'Active/Selected/All neurons' option to remaining functions
    - optimized function icons


### V4.21 15/03/2015:
    - added option to export dendrogram svg of similarity clustering

### V4.2 14/03/2015:
    - added option to export barplot to SVG export- this will export distribution of pre-, postsynaptic sites or node count along vertical 
      and horizontal axis
    - various bug fixes

### V4.1 21/12/2015:
    - added Token System to replace catmaid user+pw 

### V4.01 17/11/2015:
    - had to change get_connectivity_url due to changes in CATMAID API to skeletons/connectivity and postdata to source_skeleton_ids

### V4.0 10/11/2015:
    - added import of neurons in given volume
    - added clustering (coloring) of neurons based on morphological similarity (after Kohl et al., 2013)
    - added option to import only longest neurite up to given length for all ways to import neurons
    - added missing descriptions to import/export options -> just hover over checkbox/drop-down/textfield/etc.

### V3.94 9/11/2015:
    - had to change the way neurons with given annotation are retrieved: both url and postdata changed!

### V3.93 20/10/2015
    - fixed some bugs due to changes in CATMAID API:
        - changed annotations url to skeleton/annotationlist
        - changed url to get list of all annotations to /annotations/

### V3.92 15/10/2015
    - fixed color by synapses lut calculation: 
        * values needed to be reduced by 1, such that range for calculation is 0 to (max_value-1)
    - fixed get_annotations_from_list -> CATMAID returns now a list of dictionaries for each neuron:
      {'skeletons' : { 'skeleton ID' : [{'id': annotation id, 'uid' : dont know what this is}] , [....]}
       'annotations': {'annotation_id':'annotation_name', ... }
      }
    - added option to apply threshold when importing synaptic partners to single connections instead of the
      sum of all connections
    - added option to change project ID when logging into CATMAID (default = 1)

### V3.91 28/08/2015
    - added option to color by annotation

### V3.9 04/08/2015
    - had to compensate for new format of connectivity data: now contains list of synapses with confidences 0-5
        old: {'incoming': { 'neuronXY': {'skids': { 'upstream_neuronZ' : 5 } } }
        new: {'incoming': { 'neuronXY': {'skids': { 'upstream_neuronZ' : [0,0,2,1,2] } } }

### V3.81 14/07/2015
    - adjusted annotation import to fix new layout of received dict

### V3.8 29/06/2015
    - added option to color_by_pairs and load_paired: will color/load neurons based on given annotation
      'paired with #skid' 

### V3.73 17/05/2015
    - added option to color_by_synapses: if 'shift color' is set, the color will only be changed
      by given value RELATIVE to it's current color
    - added option to filter by annotation when importing partners
        -> works only with a single annotation and has to be exact
    - added option to also adopt bevel_depth when coloring by synapse count
    - added option to use curve's bevel_depth when exporting morphology

### V3.72 26/03/2015
    - soma radius is now based on node radius in CATMAID
    - also applies for exports to svg: soma radius is multiplied by basic_radius (default = 1)

### V3.71 20/03/2015
    - added option to import weighted connectors from selected neurons
    - added option to export connectors to SVG and give them mesh color (will apply to inputs AND outputs)

### V3.7 10/01/2015
    - fixed bug in export morphology that would cause neuron names to be created at the same location if exporting multiple neurons
    - added option to randomize grayscale colors
    - added option to SVG exports to color by density of given CURVE object (e.g. DCV tracings)
        - alternatively: choose 'Synapses' as density object and it will load connectors
        -> added filter option: -'incoming' or 'outgoing' will include only post/presynaptic sites. If no filter is given, both are processed
                                -any other filter will be applied to the connected neurons' names!
    - added option to SVG morphology export to color arbors by ratio between post- and presynaptic sites
        - Keep in mind that the subdivision into arbors can be misleading, especially for very large arbors
    - added option to choose which views should be exported
    - added perspective to connector-to-svg export
    - added new perspective 'Perspective-Dorsal' and made it standard:
        - looks at the brain from behind at an elevated angle - comparable to squeeze mounting 
    - added option to filter for synapse threshold when exporting connectors by using e.g. '>3'    
    - fixed bug that occured when exporting connectors and a treenode has more than one connector upstream and led to all but one connectors be ignored

### V3.6 16/12/2014
    - fixed bugs in connector export

### V3.6 09/12/2014
    - added license information

### V3.6 20/10/2014
### - added option to color neurons by #of synapses with given partner(s) 
### - added option to export to svg using the colors from Blender
### - fixed bug in version check: was called to early when not __main__:
###   - version check is now done manually via button OR whenever 'Connect 2 Catmaid' is
###     called

### V3.52 09/09/2014
### - added check for latest version (update.txt at Github repository)

### V3.51 05/09/2014
### - changed server url to 'https://...'
### - removed subtype 'PASSWORD' from CATMAID Login as this seems to be bugged in Blender 2.71
###   -> forces you to enter passwords in reverse


### V3.5 23/07/14
### - added orthographic perspective for export

### V3.4 13/07/14
### - added resampling option for importing and updating neurons
### - added option to skip connectors when importing

### V3.31 07/07/14
### - exchanged compact-json url for compact-skeleton url to retrieve morphology/connectors
### -> compact-json doesn't work anymore!!!
### -> neuron's names now have to be retrieved by separate get_neuronnames() function
### - fixed 'Retrieve Partners' (wouldn't check thresholds before)
### - minor clean ups

### V3.3 28/06/14
### - added function to also export neuron's morphology when exporting it's connectors to svg
### - fixed some bugs in legend creation of connector export (still quite some left)

### V3.22 26/06/2014
### - changed Blender operators polls to check if connection to CATMAID was successful
### -> buttons will be greyed out until connected to CATMAID server
### - newly imported neurons will have 'name', 'skeleton_id' and 'date_imported' assigned as custom properties

### V3.21 23/06/2014
### - changed request of skeleton name via ancestry to neuronnames -> requests a list instead of single names (MAJOR speed up!)
### -> removed progress bar for cursor
### - credentials will be read from txt file - if no file is found credentials will be empty

### V3.2 18/06/2014
### - added filter option to export connectors
### - added poll function to all Blender operators to gray out buttons if not connected to CATMAID server
###     Note: just checks whether connection has been attempted, not if successfull
### - improved creation of legends for export connectors (probably still some glitches here)
### - added progress bar for cursor

### V3.1 16/06/2014
### - added color by spatial position (soma-based)

### V3.0 03/06/14
### - added Import by Annotation
### - added 'Reload Neurons'

### V2.22 28/05/14
### - removed Import from TXT/neuroML as they are no longer needed
### - added 'Setup 4 Render' that sets up Materials for Rendering
### - removed 'Render All' button

### V2.21 27/05/14
### - adjusted data format to changes in CATMAID
### - added option to export outlines of ring gland as well
### - added masked pw entry to 'Connect' button
### - fixed export for brain shapes: if multiple neurons are processed only one brain shape will be created

### V2.2
### - added lateral view
### - added option for scaled presynapse export

### V2.1
### - changed the way data is imported from CATMAID - should be almost as fast as CATMAIDs'
###   3D viewer now
### - added connector retrieval from CATMAID to Blender and a SVG file:
###     - both options require connecting to CATMAID!!!
###     - will retrieve number of targets for all downstream connectors and resize
###       nodes relative to that
###     - won't affect upstream nodes as there is always only one presynaptic source  
   
### V2.0
### - implemented support for CATMAID API to directly interact with database

### V1.2
### - changed NeuroML Import according to CATMAID Export changes (complete names exported)

### V1.1
### - made Import from NeuroML read data line-by-line instead of importing all at once
###     -> didn't speed things up, but made it more stable and more reactive if necessary
### - added better monitoring of progress in system console while importing
### - NOTE: Creation of the Neurons seems to be the bottleneck
### - added 'Render All Function'. What it does:
###     - Creates Cameras if neccessary and then does single neuron renders of all neurons

"""

import bpy
import os
import re
import random
import time
import datetime
import urllib
import json
import math
import colorsys
import copy
import http.cookiejar as cj
import mathutils
import numpy as np
import base64
import statistics

from bpy.types import Operator, AddonPreferences
from bpy_extras.io_utils import ImportHelper, ExportHelper 
from bpy.props import FloatVectorProperty, FloatProperty, StringProperty, BoolProperty, EnumProperty, IntProperty

remote_instance = None
connected = False

bl_info = {
 "name": "CATMAIDImport",
 "author": "Philipp Schlegel",
 "version": (4, 3, 0),
 "blender": (2, 7, 7),
 "location": "Properties > Scene > CATMAID Import",
 "description": "Imports Neuron from CATMAID server, Analysis tools, Export to SVG",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "Object"}
 
 
class CATMAIDimportPanel(bpy.types.Panel):
    """Creates Menu in Properties - Scene """
    bl_label = "CATMAID Import"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"      
     
    def draw(self, context):       
        
        layout = self.layout   
        
        #Version Check
        config = bpy.data.scenes[0].CONFIG_VersionManager               
        layout.label(text="Script Versions")
        layout.label(text="Your System: %s" % str(round(config.current_version,3)))
        if config.latest_version == 0:
            layout.label(text="On Github: Unable to Retrieve")
        else:
            layout.label(text="On Github: %s" % str(round(config.latest_version,3))) 
            
        if config.last_stable_version > config.current_version:
            layout.label(text="Your are behind the last working", icon = 'ERROR')  
            layout.label(text="       version of the Script!")          
            layout.label(text="Please Download + Replace with the")
            layout.label(text="latest Version of CATMAIDImport.py:")
            layout.label(text="https://github.com/schlegelp/CATMAID-to-Blender")
        elif config.latest_version > config.current_version and config.new_features != '':
            layout.label(text="New Features in Latest Version: %s" % config.new_features)
            
        if config.message != '':
            print('Message from Github: %s' % config.message)

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("check.version", text = "Check Version", icon ='VISIBLE_IPO_ON')
               
        layout.label('Materials')        

        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("random.all_materials", text = "Randomize Color", icon ='COLOR')

        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_similarity", text = "By Similarity", icon ='PARTICLE_PATH')
        row.operator("display.help", text = "", icon ='QUESTION').entry = 'color.by_similarity'

        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_spatial", text = "By Spatial Distr.", icon ='ROTATECENTER')
        row.operator("display.help", text = "", icon ='QUESTION').entry = 'color.by_spatial'
        
        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_annotation", text = "By Annotation", icon ='SORTALPHA')
        
        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_synapse_count", text = "By Synapse Count", icon ='IPO_QUART')
        
        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_pairs", text = "By Pairs", icon ='MOD_ARRAY')
        row.operator("display.help", text = "", icon ='QUESTION').entry = 'color.by_pairs'       

        
        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("for_render.all_materials", text = "Setup 4 Render", icon ='SCENE')
        

        layout.label('CATMAID Import')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("connect.to_catmaid", text = "Connect 2 CATMAID", icon = 'PLUGIN')#.number=1

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.neuron", text = "Retrieve by SkeletonID", icon = 'ARMATURE_DATA')#.number=1

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.by_annotation", text = "Retrieve by Annotation", icon = 'OUTLINER_DATA_FONT')#.number=1

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.partners", text = "Retrieve Partners", icon = 'AUTOMERGE_ON')#.number=1

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.by_pairs", text = "Retrieve Paired", icon = 'MOD_ARRAY')#.number=1
        row.operator("display.help", text = "", icon ='QUESTION').entry = 'retrieve.by_pairs' 

        row = layout.row(align=True)
        row.alignment = 'EXPAND'        
        row.operator("retrieve.in_volume", text = "Retrieve in Volume", icon = 'BBOX')#.number=1

        row = layout.row(align=True)
        row.alignment = 'EXPAND'        
        row.operator("reload.neurons", text = "Reload Neurons", icon = 'FILE_REFRESH')#.number=1

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.connectors", text = "Retrieve Weighted Connectors", icon = 'PMARKER_SEL')#.number=1

        
        layout.label(text="Export to SVG:")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("exportall.to_svg", text = 'Export Morphology', icon = 'EXPORT')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("connectors.to_svg", text = 'Export Connectors', icon = 'EXPORT')        
        
        
class VersionManager(bpy.types.PropertyGroup):    
    current_version = bpy.props.FloatProperty(name="Your Script Version", default=0,min=0, description="Current Version of the Script you are using")
    latest_version = bpy.props.FloatProperty(name="Latest Version", default=0,min=0, description="Latest Version on Github")
    last_stable_version = bpy.props.FloatProperty(name="Last Stable Version", default=0,min=0, description="Last Stable Version of the Script")
    message = bpy.props.StringProperty(name="Message", default="", description="Message from Github") 
    new_features = bpy.props.StringProperty(name="New Features", default="", description="New features in latest Version of the Script on Github")     

class get_version_info(Operator):
    """
    Operator for Checking Addon Version on Github. 
    Can be run by clicking the button. Will also be
    called when connection to CATMAID servers is attempted.    
    """

    bl_idname = "check.version" 
    bl_label = "Check Version on Github" 
    
    def execute(self,context):
        self.check_version()        
        return{'FINISHED'}
    
    def check_version(context):
        #Read current version from bl_info and convert from tuple into float
        print('Checking Version on Github...')
        current_version = str(bl_info['version'][0]) + '.'
        for i in range(len(bl_info['version'])-1):
            current_version += str(bl_info['version'][i+1])
        current_version = float(current_version)    
        print('Current version of the Script: ', current_version)
        try:        
            update_url = 'https://raw.githubusercontent.com/schlegelp/CATMAID-to-Blender/master/update.txt'    
            update_file = urllib.request.urlopen(update_url) 
            file_content = update_file.read().decode("utf-8")        
            latest_version = re.search('current_version.*?{(.*?)}',file_content).group(1)
            last_stable = re.search('last_stable.*?{(.*?)}',file_content).group(1)   
            new_features = re.search('new_features.*?{(.*?)}',file_content).group(1)   
            message = re.search('message.*?{(.*?)}',file_content).group(1)       
            print('Latest version on Github: ', latest_version)              
        except:
            print('Error fetching info on latest version')
            self.report({'ERROR'},'Error fetching latest info')
            latest_version = 0
            last_stable = 0
            new_features = ''
            message = ''

        config = bpy.data.scenes[0].CONFIG_VersionManager    
        config.current_version = current_version
        config.latest_version = float(latest_version)
        config.last_stable_version = float(last_stable)
        config.message = message
        config.new_features = new_features
        
    #@classmethod
    #def poll(cls, context):                
    #    return context.active_object is not None    

class CatmaidInstance:
    """ A class giving access to a CATMAID instance.
    """

    def __init__(self, server, authname, authpassword, authtoken):
        self.server = server
        self.authname = authname
        self.authpassword = authpassword
        self.authtoken = authtoken
        self.opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())    

    def djangourl(self, path):
        """ Expects the path to lead with a slash '/'. """
        return self.server + path

    def auth(self, request):
        if self.authname:
            base64string = base64.encodestring(('%s:%s' % (self.authname, self.authpassword)).encode()).decode().replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
        if self.authtoken:
            request.add_header("X-Authorization", "Token {}".format(self.authtoken))

    def fetch(self, url, post=None):
        """ Requires the url to connect to and the variables for POST, if any, in a dictionary. """
        if post:
            data = urllib.parse.urlencode(post)
            data = data.encode('utf-8')
            request = urllib.request.Request(url, data = data)
        else:
            request = urllib.request.Request(url)

        self.auth(request)

        response = self.opener.open(request)

        return json.loads(response.read().decode("utf-8"))
    

    #Use to parse url for retrieving stack infos
    def get_stack_info_url(self, pid, sid):
        return self.djangourl("/" + str(pid) + "/stack/" + str(sid) + "/info")

    #Use to parse url for retrieving skeleton nodes (no info on parents or synapses, does need post data)
    def get_skeleton_nodes_url(self, pid):
        return self.djangourl("/" + str(pid) + "/treenode/table/list")

    #ATTENTION: this url doesn't work properly anymore as of 07/07/14
    #use compact-skeleton instead
    #Used to parse url for retrieving all info the 3D viewer gets (does NOT need post data)
    #Format: name, nodes, tags, connectors, reviews
    def get_skeleton_for_3d_viewer_url(self, pid, skid):
        return self.djangourl("/" + str(pid) + "/skeleton/" + str(skid) + "/compact-json")
    
    #Use to parse url for retrieving connectivity (does need post data)
    def get_connectivity_url(self, pid):
        return self.djangourl("/" + str(pid) + "/skeletons/connectivity" )
    
    #Use to parse url for retrieving info connectors (does need post data)
    def get_connectors_url(self, pid):
        return self.djangourl("/" + str(pid) + "/connector/skeletons" )

    #Use to parse url for names for a list of skeleton ids (does need post data: pid, skid)    
    def get_neuronnames(self, pid):
        return self.djangourl("/" + str(pid) + "/skeleton/neuronnames" )

    #Get user list for project
    def get_user_list(self):
        return self.djangourl("/user-list" )

    #Use to parse url for a SINGLE neuron (will also give you neuronid)   
    def get_single_neuronname(self, pid, skid):
        return self.djangourl("/" + str(pid) + "/skeleton/" + str(skid) + "/neuronname" )    

    #Use to get skeletons review status
    def get_review_status(self, pid):
        return self.djangourl("/" + str(pid) + "/skeleton/review-status" )

    #Use to get annotations for given neuron. DOES need skid as postdata
    def get_neuron_annotations(self, pid):
        return self.djangourl("/" + str(pid) + "/annotations/table-list" )    

    """
    ATTENTION!!!!: This does not seem to work anymore as of 20/10/2015 -> although it still exists in CATMAID code
    use get_annotations_for_skid_list2
    """
    #Use to get annotations for given neuron. DOES need skid as postdata
    def get_annotations_for_skid_list(self, pid):
        return self.djangourl("/" + str(pid) + "/annotations/skeletons/list" )   
    """
    !!!!
    """ 

    #Use to get annotations for given neuron. DOES need skid as postdata
    def get_annotations_for_skid_list2(self, pid):
        return self.djangourl("/" + str(pid) + "/skeleton/annotationlist" )    

    #Use to parse url for retrieving list of all annotations (and their IDs!!!) (does NOT need post data)
    def get_annotation_list(self, pid):        
        return self.djangourl("/" + str(pid) + "/annotations/" )

    #Use to parse url for retrieving contributor statistics for given skeleton (does NOT need post data)
    def get_contributions_url(self, pid, skid):
       return self.djangourl("/" + str(pid) + "/skeleton/" + str(skid) + "/contributor_statistics" )     

    #Use to parse url for retrieving annotated neurons (does need post data)
    def get_annotated_url(self, pid):
        #return self.djangourl("/" + str(pid) + "/neuron/query-by-annotations" )
        return self.djangourl("/" + str(pid) + "/annotations/query-targets" )

    #Use to parse url for retrieving list of nodes (needs post data)
    def get_node_list(self, pid):
        return self.djangourl("/" + str(pid) + "/node/list" )

    #Use to parse url for retrieving all info the 3D viewer gets (does NOT need post data)
    #Returns, in JSON, [[nodes], [connectors], [tags]], with connectors and tags being empty when 0 == with_connectors and 0 == with_tags, respectively
    def get_compact_skeleton_url(self, pid, skid, connector_flag = 1, tag_flag = 1):        
        return self.djangourl("/" + str(pid) + "/" + str(skid) + "/" + str(connector_flag) + "/" + str(tag_flag) + "/compact-skeleton")

    #The difference between this function and the compact_skeleton function is that
    #the connectors contain the whole chain from the skeleton of interest to the
    #partner skeleton: contains [treenode_id, confidence_to_connector, connector_id, confidence_from_connector, connected_treenode_id, connected_skeleton_id, relation1, relation2]
    #relation1 = 1 means presynaptic (this neuron is upstream), 0 means postsynaptic (this neuron is downstream)
    def get_compact_arbor_url(self, pid, skid, nodes_flag = 1, connector_flag = 1, tag_flag = 1):        
        return self.djangourl("/" + str(pid) + "/" + str(skid) + "/" + str(nodes_flag) + "/" + str(connector_flag) + "/" + str(tag_flag) + "/compact-arbor")    

    #Use to parse url for retrieving edges between given skeleton ids (does need postdata)
    #Returns list of edges: [source_skid, target_skid, weight]
    def get_edges_url(self, pid):
        return self.djangourl("/" + str(pid) + "/skeletongroup/skeletonlist_confidence_compartment_subgraph" )

def get_3D_skeleton ( skids, remote_instance, connector_flag = 1, tag_flag = 1 ):

    #If list of skids is provided
    if type(skids) == type(list()):
        sk_data = []
        for skeleton_id in skids:
            #Create URL for retrieving example skeleton from server
            remote_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , skeleton_id, connector_flag, tag_flag )

            #Retrieve node_data for example skeleton
            skeleton_data = remote_instance.fetch( remote_compact_skeleton_url )

            sk_data.append(skeleton_data)

            print('%s retrieved' % str(skeleton_id))
    #if only a single skids is provided
    else:
        remote_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , skids, connector_flag, tag_flag )
        sk_data = remote_instance.fetch( remote_compact_skeleton_url )

    return (sk_data)
    
    
def get_annotations_from_list (skid_list, remote_instance):
    #Takes list of skids and retrieves annotations
    #Attention! It seems like this URL does not process more than 250 skids at a time!

    remote_get_annotations_url = remote_instance.get_annotations_for_skid_list2( project_id )

    get_annotations_postdata = {'metaannotations':0,'neuronnames':0}              

    for i in range(len(skid_list)):
        key = 'skeleton_ids[%i]' % i
        get_annotations_postdata[key] = str(skid_list[i])

    print('Asking for %i skeletons annotations (Project ID: %i)' % (len(get_annotations_postdata),project_id), end = ' ')   

    annotation_list_temp = remote_instance.fetch( remote_get_annotations_url , get_annotations_postdata )
    
    #print(annotation_list_temp)
    
    annotation_list = {}    

    for skid in annotation_list_temp['skeletons']:
        annotation_list[skid] = [] 
        for entry in annotation_list_temp['skeletons'][skid]['annotations']:
            annotation_id = entry['id']
            annotation_list[skid].append(annotation_list_temp['annotations'][str(annotation_id)])              

    print('Annotations for %i neurons retrieved' % len(annotation_list))
    
    #Returns dictionary: annotation_list = {skid1 : [annotation1,annotation2,....], skid2: []}
   
    return(annotation_list)

def retrieve_connectivity (skids, remote_instance, threshold = 1):
    """
    ATTENTION! Threshold doesn't seem to be working
    """

    remote_connectivity_url = remote_instance.get_connectivity_url( 1 )

    connectivity_post = {}
    #connectivity_post['threshold'] = threshold
    connectivity_post['boolean_op'] = 'OR'
    i = 0
    for skid in skids:
        tag = 'source_skeleton_ids[%i]' %i
        connectivity_post[tag] = skid
        i +=1
    print('Retrieving... Postdata:')
    print(connectivity_post)

    connectivity_data = remote_instance.fetch( remote_connectivity_url , connectivity_post )

    #As of 08/2015, # of synapses is returned as list of nodes with 0-5 confidence: {'skid': [0,1,2,3,4,5]}
    #This is being collapsed into a single value before returning it:

    #print('Connectivity_data:', connectivity_data)

    for direction in ['incoming','outgoing']:
        for entry in connectivity_data[direction]:
            for skid in connectivity_data[direction][entry]['skids']:
                connectivity_data[direction][entry]['skids'][skid] = sum(connectivity_data[direction][entry]['skids'][skid])
        
    return(connectivity_data)

def get_partners (skid_list, remote_instance, hops, upstream=True,downstream=True):

    #By seperating up and downstream retrieval we make sure that we don't go back in the second hop
    #E.g. we only want inputs of inputs and NOT inputs+outputs of inputs
    skids_upstream_to_retrieve = skid_list
    skids_downstream_to_retrieve = skid_list   

    partners = {}
    partners['incoming'] = []
    partners['outgoing'] = []    
    skids_already_seen = {}

    remote_connectivity_url = remote_instance.get_connectivity_url( project_id )        
    for hop in range(hops):  
        upstream_partners_temp = {}
        connectivity_post = {}
        #connectivity_post['threshold'] = 1
        connectivity_post['boolean_op'] = 'OR' 
        if upstream is True:        
            for i in range(len(skids_upstream_to_retrieve)):
                tag = 'source_skeleton_ids[%i]' % i
                connectivity_post[tag] = skids_upstream_to_retrieve[i]
                
            print( "Retrieving Upstream Partners for %i neurons [%i. hop]..." % (len(skids_upstream_to_retrieve),hop+1))
            connectivity_data = []
            connectivity_data = remote_instance.fetch( remote_connectivity_url , connectivity_post ) 
            print("Done.")
            
            #print(connectivity_data)  
        
            new_skids_upstream_to_retrieve = []
            for skid in connectivity_data['incoming']:
                upstream_partners_temp[skid] = connectivity_data['incoming'][skid]
                
                #Make sure we don't do circles (connection is still added though!):
                #Unneccessary if we are already at the last hop
                if skid not in skids_upstream_to_retrieve:
                    new_skids_upstream_to_retrieve.append(skid)
                    
                    if skid in skids_already_seen:
                        print('Potential circle detected! %s between hops: %s and %i upstream' % (skid,skids_already_seen[skid],hop))
                        skids_already_seen[skid] += 'and' + str(hop) + ' upstream'
                    else:    
                        skids_already_seen[skid] = str(hop) + ' upstream'
                    
            
            #Set skids to retrieve for next hop        
            skids_upstream_to_retrieve = new_skids_upstream_to_retrieve
            
            partners['incoming'].append(upstream_partners_temp)
        
        connectivity_post = {}     
        connectivity_post['threshold'] = 1
        connectivity_post['boolean_op'] = 'OR'         
        downstream_partners_temp = {}
        if downstream is True:        
            for i in range(len(skids_downstream_to_retrieve)):
                tag = 'source_skeleton_ids[%i]' % i
                connectivity_post[tag] = skids_downstream_to_retrieve[i]
        
            print( "Retrieving Downstream Partners for %i neurons [%i. hop]..." % (len(skids_downstream_to_retrieve),hop+1))
            connectivity_data = []
            connectivity_data = remote_instance.fetch( remote_connectivity_url , connectivity_post )   
            print("Done!")
        
            new_skids_downstream_to_retrieve = []
            for skid in connectivity_data['outgoing']:
                downstream_partners_temp[skid] = connectivity_data['outgoing'][skid]
                
                #Make sure we don't do circles (connection is still added though!):
                #Unneccessary if we are already at the last hop
                if skid not in skids_downstream_to_retrieve:
                    new_skids_downstream_to_retrieve.append(skid)
                    
                    if skid in skids_already_seen:
                        print('Potential circle detected! %s between hops: %s and %i downstream' % (skid,skids_already_seen[skid],hop))
                        skids_already_seen[skid] += 'and' + str(hop) + ' downstream'
                    else:    
                        skids_already_seen[skid] = str(hop) + ' downstream'
            
            #Set skids to retrieve for next hop        
            skids_downstream_to_retrieve = new_skids_downstream_to_retrieve
            
            partners['outgoing'].append(downstream_partners_temp)   
    
    
    return(partners)


def get_neuronnames(skids):
    """Retrieves and Returns a list of names for a list of neurons"""
    
    ### Get URL to neuronnames function
    remote_get_names = remote_instance.get_neuronnames( project_id )
    
    ### Create postdata out of given skeleton IDs
    get_names_postdata = {}
    get_names_postdata['pid'] = 1
    
    i = 0
    for skid in skids:
        if str(skid).isdigit():        
            key = 'skids[%i]' % i
            get_names_postdata[key] = skid
            i += 1
        else:
            print('Skipped illegal skid in retrieving neuron names: ', skid)

    ### Retrieve neuron names: {'skid': 'neuron_name' , ... }
    neuron_names = remote_instance.fetch( remote_get_names , get_names_postdata )
    
    return(neuron_names)


def get_neurons_in_volume ( left, right, top, bottom, z1, z2, remote_instance ):
    ''' Retrieve an JSON array with four entries:
    [0] an array of arrays, each array representing a treenode: [id, parent_id, x , y, z, confidence, radius, skeleton_id, user_id ]
    [1] an array of arrays, each array representing a connector and containing
    arrays inside that specify the relations between the connector and treenodes.
    In this function tuples are used as much as possible for immutable list,
    and uses directly the tuples returned by the database cursor.
    [2] the labels, if requested.
    [3] a boolean which is true when the node limit has been reached.
    The returned JSON data is therefore sensitive to indices in the array,
    so care must be taken never to alter the order of the variables in the SQL
    statements without modifying the accesses to said data both in this function
    and in the client that consumes it.


    Coordinates need to be in nm! Meaning - for whatever reason - that x and y (not z) has to be multiplied by resolution of 3.8
    '''    

    def retrieve_nodes( left, right, top, bottom, z1, z2, remote_instance, incursion ):  

        print(incursion,':',left, right, top, bottom, z1, z2)      

        remote_nodes_list = remote_instance.get_node_list (1)

        x_y_resolution = 3.8

        #Atnid seems to be related to fetching the active node too (will be ignored if atnid = -1)
        node_list_postdata = {      'left':left * x_y_resolution,
                                    'right':right * x_y_resolution,
                                    'top': top * x_y_resolution,
                                    'bottom': bottom * x_y_resolution,
                                    'z1': z1,
                                    'z2': z2,
                                    'atnid':-1,
                                    'labels': False
                                }

        node_list = remote_instance.fetch( remote_nodes_list , node_list_postdata )

        

        if node_list[3] is True:
            print('Incursing')   
            incursion += 1         
            node_list = list()
            #Front left top
            node_list += retrieve_nodes( left, 
                                        left + (right-left)/2, 
                                        top, 
                                        top + (bottom-top)/2, 
                                        z1, 
                                        z1 + (z2-z1)/2, 
                                        remote_instance, incursion )
            #Front right top
            node_list += retrieve_nodes( left  + (right-left)/2, 
                                        right, 
                                        top,
                                        top + (bottom-top)/2, 
                                        z1, 
                                        z1 + (z2-z1)/2, 
                                        remote_instance, incursion )
            #Front left bottom            
            node_list += retrieve_nodes( left, 
                                        left + (right-left)/2, 
                                        top + (bottom-top)/2, 
                                        bottom, 
                                        z1, 
                                        z1 + (z2-z1)/2, 
                                        remote_instance, incursion )
            #Front right bottom
            node_list += retrieve_nodes( left  + (right-left)/2, 
                                        right, 
                                        top + (bottom-top)/2, 
                                        bottom, 
                                        z1, 
                                        z1 + (z2-z1)/2, 
                                        remote_instance, incursion )
            #Back left top
            node_list += retrieve_nodes( left, 
                                        left + (right-left)/2, 
                                        top, 
                                        top + (bottom-top)/2, 
                                        z1 + (z2-z1)/2, 
                                        z2, 
                                        remote_instance, incursion )
            #Back right top
            node_list += retrieve_nodes( left  + (right-left)/2, 
                                        right, 
                                        top,
                                        top + (bottom-top)/2, 
                                        z1 + (z2-z1)/2, 
                                        z2, 
                                        remote_instance, incursion )
            #Back left bottom            
            node_list += retrieve_nodes( left, 
                                        left + (right-left)/2, 
                                        top + (bottom-top)/2, 
                                        bottom, 
                                        z1 + (z2-z1)/2, 
                                        z2, 
                                        remote_instance, incursion )
            #Back right bottom
            node_list += retrieve_nodes( left  + (right-left)/2, 
                                        right, 
                                        top + (bottom-top)/2, 
                                        bottom, 
                                        z1 + (z2-z1)/2, 
                                        z2, 
                                        remote_instance, incursion )
        else:
            #If limit not reached, node list is still an array of 4
            print("Incursion finished.",len(node_list[0]))
            return node_list[0]            
        
        print("Incursion finished.",len(node_list))

        return node_list

    print('Retrieving Nodes in Volume...')

    node_list = retrieve_nodes( left, right, top, bottom, z1, z2, remote_instance, 1 )

    skeletons = set()

    for node in node_list:                       
        skeletons.add(node[7]) 

    print(len(skeletons),'found in volume')          

    return list(skeletons)
    
    
class TestHttpRequest(Operator):
    """Operator Test Class for Debugging only"""

    bl_idname = "test.request" 
    bl_label = "Test Http Requests" 
    
    
    def execute(self,context):
        skids = [10418394,4453485]
        
        remote_get_names = remote_instance.get_neuronnames( project_id )
        
        get_names_postdata = {}
        get_names_postdata['pid'] = 1
        
        for i in range(len(skids)):
            key = 'skids[%i]' % i
            get_names_postdata[key] = skids[i]
        
        #get_names_postdata = {'pid' : 1 ,'skids[0]': '10418394', 'skids[1]': '4453485'}

        names = remote_instance.fetch( remote_get_names , get_names_postdata )
        
        print(names)
        
        return{'FINISHED'}


class UpdateNeurons(Operator):      
    """Updates existing Neurons in Scene from CATMAID Server"""

    bl_idname = "reload.neurons"  
    bl_label = "Update Neurons from CATMAID Server"   
    bl_options = {'UNDO'}    
    
    which_neurons = EnumProperty(name = "Which Neurons?", 
                                      items = [('Active','Active','Active'),('Selected','Selected','Selected'),('All','All','All')],
                                      description = "Choose which neurons to reload.")
    keep_resampling = BoolProperty(name="Keep Old Resampling?", default = True)
    new_resampling = IntProperty(name="Else: New Resampling Factor", default = 2, min = 1, max = 20,
                                 description = "Will reduce node count by given factor. Root, ends and forks are preserved!")
    import_connectors = BoolProperty(   name="Import Connectors", 
                                        default = True,
                                        description = "Imports Connectors (pre-/postsynapses), similarly to 3D Viewer in CATMAID")
    truncate_neuron = EnumProperty(name="Truncate Neuron?",
                                   items = (('none','No','Load full neuron'),
                                            ('main_neurite','Main Neurite','Truncate Main Neurite'),
                                            ('strahler_index','Strahler Index','Truncate Based on Strahler index')
                                            ),
                                    default =  "none",
                                    description = "Choose if neuron should be truncated.")
    
    truncate_value = IntProperty(   name="Truncate by Value", 
                                        min=-10,
                                        max=10,
                                        default = 1,
                                        description = "Defines length of truncated neurite or steps in Strahler Index from root node!"
                                    ) 
    interpolate_virtual = BoolProperty( name="Interpolate Virtual Nodes", 
                                        default = False,
                                        description = "If true virtual nodes will be interpolated. Only important if you want the resolution of all neurons to be the same. Will slow down import!")
    
    
    def execute(self,context):
        neurons_to_reload = {}
        resampling = 1
        
        ### Gather skeleton IDs
        if self.which_neurons == 'All':
            to_check = bpy.data.objects
        elif self.which_neurons == 'Selected':
            to_check = bpy.context.selected_objects            
        elif self.which_neurons == 'Active':
            to_check = [bpy.context.active_object]

        for neuron in to_check:
            if neuron.name.startswith('#'):
                try:
                    skid = re.search('#(.*?) -',neuron.name).group(1)
                    neurons_to_reload[neuron.name] = {}
                    neurons_to_reload[neuron.name]['skid'] = skid
                    if 'resampling' in neuron:
                        neurons_to_reload[neuron.name]['resampling'] = neuron['resampling']
                    else:
                        neurons_to_reload[neuron.name]['resampling'] = 1
                except:
                    print('Unable to process neuron', neuron.name)                    
    
        print(len(neurons_to_reload),'neurons to reload:',neurons_to_reload)

        ### Deselect all objects, then select objects to update (Skeletons, Inputs/Outputs)                         
        for object in bpy.data.objects:
            object.select = False
            if object.name.startswith('#') or object.name.startswith('Outputs of') or object.name.startswith('Inputs of') or object.name.startswith('Soma of'):
                for neuron in neurons_to_reload:
                    if neurons_to_reload[neuron]['skid'] in object.name:
                        object.select = True                    
                
        ### Delete selected objects        
        bpy.ops.object.delete(use_global=False)        
        
        ### Get Neuron Names (in case they changed):
        print('Retrieving most recent neuron names from server...')
        skids_to_retrieve = []
        for neuron in neurons_to_reload:
            skids_to_retrieve.append(neurons_to_reload[neuron]['skid'])
        neuron_names = get_neuronnames(skids_to_retrieve)

        ### Reload neurons
        for neuron in neurons_to_reload:
            skid = neurons_to_reload[neuron]['skid']            
            print('Updating Neuron %s' % neuron)
            if self.keep_resampling is True:       
                resampling = neurons_to_reload[neuron]['resampling']     
                RetrieveNeuron.add_skeleton(self, skid, neuron_names[skid], resampling, self.import_connectors, self.truncate_neuron, self.truncate_value, self.interpolate_virtual) 
            else:
                RetrieveNeuron.add_skeleton(self, skid, neuron_names[skid], self.new_resampling, self.import_connectors, self.truncate_neuron, self.truncate_value, self.interpolate_virtual) 
        
        return{'FINISHED'} 
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)        
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False


class RetrieveNeuron(Operator):      
    """Retrieves Skeletons from CATMAID database; use any delimiter; ID may contain only integers"""
    ### ATTENTION: operator accepts only 400 characters - equals about 50 neurons
    bl_idname = "retrieve.neuron"  
    bl_label = "Enter skeleton ID(s)"
    
    skeleton_id = StringProperty(name="Skeleton ID(s)",
                                 description = "Enter skeleton IDs. Separate multiple skids by comma without spaces!"
                                ) 

    import_connectors = BoolProperty(   name="Import Connectors", 
                                        default = True,
                                        description = "Imports Connectors (pre-/postsynapses), similarly to 3D Viewer in CATMAID")
    resampling = IntProperty(name="Resampling Factor", 
                             default = 2, 
                             min = 1, 
                             max = 20,
                             description = "Will reduce number of nodes by given factor n. Root, ends and forks are preserved!")
    truncate_neuron = EnumProperty(name="Truncate Neuron?",
                                   items = (('none','No','Load full neuron'),
                                            ('main_neurite','Main Neurite','Truncate Main Neurite'),
                                            ('strahler_index','Strahler Index','Truncate Based on Strahler index')
                                            ),
                                    default =  "none",
                                    description = "Choose if neuron should be truncated.")
    
    truncate_value = IntProperty(   name="Truncate by Value", 
                                        min=-10,
                                        max=10,
                                        default = 1,
                                        description = "Defines length of truncated neurite or steps in Strahler Index from root node!"
                                    )  
    interpolate_virtual = BoolProperty( name="Interpolate Virtual Nodes", 
                                        default = False,
                                        description = "If true virtual nodes will be interpolated. Only important if you want the resolution of all neurons to be the same. Will slow down import!")
      
    
    def execute(self, context):  
        global remote_instance
        
        errors = []
        
        ### Extract skeleton IDs from skeleton_id string
        skeletons_to_retrieve = re.findall('[0-9]+',self.skeleton_id)
        print('%i skeleton ids found - resolving names...' % len(skeletons_to_retrieve))
        
        neuron_names = get_neuronnames(skeletons_to_retrieve)
        
        print('Done:')
        print(neuron_names)

        self.count = 1
        
        for skid in skeletons_to_retrieve:
            ### Check if skeleton id has only numbers
            if re.search('[a-zA-Z]', self.skeleton_id):
                print ('Invalid Skeleton ID')                     
        
            else:
                print( "Retrieving Treenodes for %s [%i of %i]" % (skid,self.count,len(skeletons_to_retrieve)))
                error_temp = self.add_skeleton(skid,neuron_names[skid], self.resampling, self.import_connectors, self.truncate_neuron, self.truncate_value, self.interpolate_virtual)
                self.count += 1
                
                if error_temp != '':
                    errors.append(error_temp)
                
        if len(errors) == 0:
            msg = 'Success! %i neurons imported' % len(skeletons_to_retrieve)
            self.report({'INFO'}, msg)

        else:
            print('%i Error(s) while Importing:' % len(errors))
            self.report({'ERROR'},'Error(s) while importing (see console)')

            for entry in errors:
                print(entry)
                        
        return {'FINISHED'}


    def add_skeleton(self, skeleton_id, neuron_name = '', resampling = 1, import_connectors = True, truncate_neuron = 'none', truncate_value = 1,  interpolate_virtual = False):
        
        if neuron_name == '':
            print('Retrieving name of skeleton %s' % str(skeleton_id))
            neuron_name = get_neuronnames([neuron_name])[0]
        
        error = ''
        
        cellname = skeleton_id + ' - ' + neuron_name  
        #truncated neuron name down to 63 letters if necessary
        if len(cellname) >= 60:
            cellname = cellname[:56] +'...'
            print('Object name too long - truncated: ', cellname)
        
        object_name = '#' + cellname
            
        if object_name in bpy.data.objects:
            print('Neuron already exists! Skipping.')
            return error        
        

        node_data = get_3D_skeleton ( [skeleton_id], remote_instance, int(import_connectors), 1 )[0]

        print("%i entries for neuron %s retrieved" % (len(node_data),skeleton_id) )
                
        ### Continue only of data retrieved contains 5 entries (if less there was an error while importing)
        if len(node_data) == 3 or len(node_data) == 2:             
            CATMAIDtoBlender.extract_nodes(node_data, skeleton_id, neuron_name, resampling, import_connectors, truncate_neuron, truncate_value, interpolate_virtual)
        else:
            print('No/bad data retrieved')
            print('Data:')
            print(node_data)
            error = ('Error(s) retrieving data for neuron #%s' % skeleton_id)
            self.count += 1
            
        return error    
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)    
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False
        
        
        
        
class RetrievePairs(Operator):      
    """Retrieve Neurons from CATMAID database based on Annotation"""
    bl_idname = "retrieve.by_pairs"  
    bl_label = "Retrieve paired Neurons of existing Neurons"    
    
    which_neurons = EnumProperty(       name = "For which Neuron(s)?", 
                                      items = [('Active','Active','Active'),('Selected','Selected','Selected'),('All','All','All')],
                                      default = 'All',
                                      description = "Choose for which neurons to connectors.")
    import_connectors = BoolProperty(   name="Import Connectors", 
                                        default = True,
                                        description = "Imports Connectors (pre-/postsynapses), similarly to 3D Viewer in CATMAID")
    resampling = IntProperty(name="Resampling Factor", 
                             default = 2, 
                             min = 1, 
                             max = 20,
                             description = "Will reduce number of nodes by given factor n. Root, ends and forks are preserved!")
    truncate_neuron = EnumProperty(name="Truncate Neuron?",
                                   items = (('none','No','Load full neuron'),
                                            ('main_neurite','Main Neurite','Truncate Main Neurite'),
                                            ('strahler_index','Strahler Index','Truncate Based on Strahler index')
                                            ),
                                    default =  "none",
                                    description = "Choose if neuron should be truncated.")
    
    truncate_value = IntProperty(   name="Truncate by Value", 
                                        min=-10,
                                        max=10,
                                        default = 1,
                                        description = "Defines length of truncated neurite or steps in Strahler Index from root node!"
                                    ) 
    interpolate_virtual = BoolProperty( name="Interpolate Virtual Nodes", 
                                        default = False,
                                        description = "If true virtual nodes will be interpolated. Only important if you want the resolution of all neurons to be the same. Will slow down import!")
    
    
    def execute(self, context):  
        global remote_instance
        
        neurons = []
        
        if self.which_neurons == 'Active':
            if bpy.context.active_object != None:
                if bpy.context.active_object.name.startswith('#'):
                    try:                        
                        neurons.append(re.search('#(.*?) -',neuron.name).group(1))
                    except:
                        pass
                else:
                    self.report({'ERROR'},'ERROR: Active object not a neuron')
                    print('ERROR: Active object not a neuron!')
            else:
                self.report({'ERROR'},'ERROR: No active Object')
                print('ERROR: No active Object')
        elif self.which_neurons == 'Selected':
            for neuron in bpy.context.selected_objects:    
                if neuron.name.startswith('#'):
                    try:                        
                        neurons.append(re.search('#(.*?) -',neuron.name).group(1))
                    except:
                        pass
        elif self.which_neurons == 'All':
            for neuron in bpy.data.objects:    
                if neuron.name.startswith('#'):
                    try:                        
                        neurons.append(re.search('#(.*?) -',neuron.name).group(1))
                    except:
                        pass
                
        annotations = get_annotations_from_list (neurons, remote_instance)      
        
        #Determine pairs
        paired = []
        for neuron in annotations:
            paired_skid = None
            try:
                for annotation in annotations[neuron]:
                    if annotation.startswith('paired with #'):
                        skid = annotation[13:]                        
                        #Filter for errors in annotation:
                        if neuron == paired_skid:
                            print('Warning - Neuron %s paired with itself' % str(neuron))
                            self.report({'ERROR'},'Error(s) occurred: see console')
                            continue
                            
                        if paired_skid != None:
                            print('Warning - Multiple paired Annotations found for neuron %s! Neuron skipped!' % str(neuron))
                            self.report({'ERROR'},'Error(s) occurred: see console')
                            paired_skid = None
                            continue
                            
                        paired_skid = skid
            except:
                pass
                    
            if paired_skid != None:
                if paired_skid in paired:
                    print('Warning - Neuron %s annotated as paired in multiple Neurons!' % str(paired_skid))
                    self.report({'ERROR'},'Error(s) occurred: see console')
                else:
                    paired.append(paired_skid)
                
        if len(paired) != 0:
            self.retrieve_paired(paired)   

        
        return{'FINISHED'}
              

    def retrieve_paired(self, paired):
        
        count = 0        
        neuron_names = get_neuronnames(paired)           
        
        if len(neuron_names) < len(paired):
            print('Warning! Wrong paired skid(s) in annotations found!')
            self.report({'ERROR'},'Error(s) occurred: see console')
                
        for skid in paired:            
            print('Retrieving skeleton %s [%i of %i]' % (skid,count,len(paired)))
            try:
                RetrieveNeuron.add_skeleton(self,skid,neuron_names[skid], self.resampling, self.import_connectors, self.truncate_neuron, self.interpolate_virtual)            
                count += 1         
            except:
                print('Error importing skid %s - wrong annotated skid?' %skid)
                self.report({'ERROR'},'Error(s) occurred: see console')
        
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)
    

    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False    

         

class RetrieveInVolume(Operator):      
    """Retrieve Neurons from CATMAID database based on given Volume"""
    bl_idname = "retrieve.in_volume"  
    bl_label = "Define Bounding Box (CATMAID Coordinates):"    
    
    top = IntProperty(name="Top", default = 21000, min = 1, max = 28128)
    bot = IntProperty(name="Bottom", default = 26000, min = 1, max = 28128)
    left = IntProperty(name="Left", default = 14000, min = 1, max = 28128)
    right = IntProperty(name="Right", default = 18000, min = 1, max = 28128)
    z1 = IntProperty(name="Z1", default = 39000, min = 6050, max = 248050,
                        description = "Not Slices!")
    z2 = IntProperty(name="Z2", default = 40000, min = 6050, max = 248050,
                        description = "Not Slices!")
    resampling = IntProperty(name="Resampling Factor", 
                             default = 2, 
                             min = 1, 
                             max = 20,
                             description = "Will reduce number of nodes by given factor n. Root, ends and forks are preserved!")
    import_connectors = BoolProperty(   name="Import Connectors", 
                                        default = False,
                                        description = "Imports Connectors (pre-/postsynapses), similarly to 3D Viewer in CATMAID")
    truncate_neuron = EnumProperty(name="Truncate Neuron?",
                                   items = (('none','No','Load full neuron'),
                                            ('main_neurite','Main Neurite','Truncate Main Neurite'),
                                            ('strahler_index','Strahler Index','Truncate Based on Strahler index')
                                            ),
                                    default =  "none",
                                    description = "Choose if neuron should be truncated.")
    
    truncate_value = IntProperty(   name="Truncate by Value", 
                                        min=-10,
                                        max=10,
                                        default = 1,
                                        description = "Defines length of truncated neurite or steps in Strahler Index from root node!"
                                    ) 
    interpolate_virtual = BoolProperty( name="Interpolate Virtual Nodes", 
                                        default = False,
                                        description = "If true virtual nodes will be interpolated. Only important if you want the resolution of all neurons to be the same. Will slow down import!")                                       

    def execute(self, context):  
        global remote_instance
        
        #Get Neurons in Volume:
        skid_list = get_neurons_in_volume ( self.left, self.right, self.top, self.bot, self.z1, self.z2, remote_instance )

        neuron_names = get_neuronnames(skid_list)        

        for i,skid in enumerate(skid_list):            
            print('Retrieving skeleton %s [%i of %i]' % (skid,i,len(skid_list)))
            RetrieveNeuron.add_skeleton(self,str(skid),neuron_names[str(skid)], self.resampling, self.import_connectors, self.truncate_neuron, self.interpolate_virtual)
        
        return{'FINISHED'}                                  


    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)
    

    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False                             
    

class RetrieveByAnnotation(Operator):      
    """Retrieve Neurons from CATMAID database based on Annotation"""
    bl_idname = "retrieve.by_annotation"  
    bl_label = "Enter Annotation:"    
    
    annotation = StringProperty(    name="Annotation",
                                    description = "Enter single annotation. Case-SENSITIVE!"
                                    )    
    resampling = IntProperty(name="Resampling Factor", 
                             default = 2, 
                             min = 1, 
                             max = 20,
                             description = "Will reduce number of nodes by given factor n. Root, ends and forks are preserved!")
    import_connectors = BoolProperty(   name="Import Connectors", 
                                        default = True,
                                        description = "Imports Connectors (pre-/postsynapses), similarly to 3D Viewer in CATMAID")
    truncate_neuron = EnumProperty(name="Truncate Neuron?",
                                   items = (('none','No','Load full neuron'),
                                            ('main_neurite','Main Neurite','Truncate Main Neurite'),
                                            ('strahler_index','Strahler Index','Truncate Based on Strahler index')
                                            ),
                                    default =  "none",
                                    description = "Choose if neuron should be truncated.")
    
    truncate_value = IntProperty(   name="Truncate by Value", 
                                        min=-10,
                                        max=10,
                                        default = 1,
                                        description = "Defines length of truncated neurite or steps in Strahler Index from root node!"
                                    ) 
    
    interpolate_virtual = BoolProperty( name="Interpolate Virtual Nodes", 
                                        default = False,
                                        description = "If true virtual nodes will be interpolated. Only important if you want the resolution of all neurons to be the same. Will slow down import!")
    
    
    def execute(self, context):  
        global remote_instance
        
        ### Get annotation ID of self.annotation
        annotation_id = self.retrieve_annotation_list()
        
        if annotation_id != 'not found':
            self.retrieve_annotated(self.annotation, annotation_id)
        else:
            print('Annotation not found in List! Import stopped!')
            self.report({'ERROR'},'Annotation not found!')
        
        return{'FINISHED'}
    
    
    def retrieve_annotation_list(self):
        print('Retrieving list of Annotations...')
        
        remote_annotation_list_url = remote_instance.get_annotation_list( project_id )
        list = remote_instance.fetch( remote_annotation_list_url )
        
        for dict in list['annotations']:
            #print(dict['name'])
            if dict['name'] == self.annotation:
                annotation_id = dict['id']
                print('Found Matching Annotation!')
                break
            else:
                annotation_id = 'not found'
        
        return annotation_id            

    
    def retrieve_annotated(self, annotation, annotation_id):
        print('Looking for Annotation | %s | (id: %s)' % (annotation,annotation_id))
        #annotation_post = {'neuron_query_by_annotation': annotation_id, 'display_start': 0, 'display_length':500}
        annotation_post = {'annotated_with0': annotation_id, 'rangey_start': 0, 'range_length':500, 'with_annotations':False}
        remote_annotated_url = remote_instance.get_annotated_url( project_id )
        neuron_list = remote_instance.fetch( remote_annotated_url, annotation_post )
        count = 0        
        
        wm = bpy.context.window_manager
        ### Start progress bar at cursor (currently doesn't seem to work b/c window is not properly updated)
        wm.progress_begin(0, len(neuron_list['entities']))
        
        print('Retrieving names of annotated neurons...')
        annotated_skids = []
        for entry in neuron_list['entities']:
            if entry['type'] == 'neuron':
                annotated_skids.append(str(entry['skeleton_ids'][0]))
        neuron_names = get_neuronnames(annotated_skids)
        
        for entry in neuron_list['entities']:
            if entry['type'] == 'neuron':
                skid = str(entry['skeleton_ids'][0])
                print('Retrieving skeleton %s [%i of %i]' % (skid,count,len(neuron_list['entities'])))
                RetrieveNeuron.add_skeleton(self,skid,neuron_names[skid], self.resampling, self.import_connectors, self.truncate_neuron, self.truncate_value, self.interpolate_virtual)
                wm.progress_update(count)
                count += 1
            
        wm.progress_end()          
         
        
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)
    

    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False


class RetrieveConnectors(Operator):      
    """Retrieves Connectors of active/selected/all Neuron from CATMAID database"""
    bl_idname = "retrieve.connectors"  
    bl_label = "Connectors will be created in Layer 3!!!"

    which_neurons = EnumProperty(name = "For which Neuron(s)?", 
                                      items = [('Active','Active','Active'),('Selected','Selected','Selected'),('All','All','All')],
                                      description = "Choose for which neurons to connectors.")
    color_prop = EnumProperty(name = "Colors", 
                                      items = [('Black','Black','Black'),('Mesh-color','Mesh-color','Mesh-color'),('Random','Random','Random')],
                                      description = "How to color the connectors.")    
    basic_radius = FloatProperty(   name="Basic Radius", 
                                    default = 0.01,
                                    description = "Set to -1 to not weigh connectors")
    layer = IntProperty(   name="Create in Layer", 
                                    default = 2,
                                    min = 0,
                                    max = 19,
                                    description = "Set layer in which to create connectors")
    get_inputs = BoolProperty(name="Retrieve Inputs", default = True)
    get_outputs = BoolProperty(name="Retrieve Ouputs", default = True)
    filter = StringProperty(name="Filter Connectors",
                            description='Filter neuron names pre/postsynaptic of connectors')
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False
        
    
    def execute(self, context):  
        global remote_instance
        
        bpy.context.scene.layers[self.layer] = True
        
        if self.which_neurons == 'Active':
            if bpy.context.active_object is None:
                self.report({'ERROR'},'No Active Object!')
                print ('No Object Active')
            elif bpy.context.active_object is not None and '#' not in bpy.context.active_object.name:
                self.report({'ERROR'},'Active Object not a Neuron!')
                print ('Active Object not a Neuron') 
            else:                      
                active_skeleton = re.search('#(.*?) -',bpy.context.active_object.name).group(1)
                self.get_connectors(active_skeleton, bpy.context.active_object.active_material.diffuse_color[0:3])   
        
        if self.which_neurons == 'All':
            n = 0
            n_total = len(bpy.data.objects)
            for neuron in bpy.data.objects:
                n += 1
                if '#' in neuron.name:
                    print('Importing Connectors for Neuron %i [of %i]' % (n,n_total))
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    self.get_connectors(skid, neuron.active_material.diffuse_color[0:3])
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)
        
        if self.which_neurons == 'Selected':
            n = 0
            n_total = len(bpy.context.selected_objects)
            for neuron in bpy.context.selected_objects:
                n += 1
                if '#' in neuron.name:
                    print('Importing Connectors for Neuron %i [of %i]' % (n,n_total))
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    self.get_connectors(skid, neuron.active_material.diffuse_color[0:3])           
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)
                
            
        return {'FINISHED'}   
    
        
    def get_connectors(self, active_skeleton, mesh_color = None):
        node_data = []
        connector_ids = []
                        
        ### Retrieve compact json data and filter connector ids
        print('Retrieving connector data for skid %s...' % active_skeleton)
        node_data = get_3D_skeleton ( active_skeleton, remote_instance, connector_flag = 1, tag_flag = 0 )

        if node_data:
            print('Success!')            

        i_pre = 0
        i_post = 0
        connector_post_postdata = {}
        connector_pre_postdata = {}
        connector_post_coords = {}
        connector_pre_coords = {}
            
        print('Extracting coordinates..')
        
        ### Get coordinates, divide into pre-/postsynapses and bring them into Blender space: switch y and z, divide by 10.000/10.000/-10.000
        for connection in node_data[1]:
            
            if connection[2] == 1 and self.get_inputs is True:
                connector_pre_coords[connection[1]] = {}
                connector_pre_coords[connection[1]]['id'] = connection[1]
                connector_pre_coords[connection[1]]['coords'] = (connection[3]/10000,connection[5]/10000,connection[4]/-10000)   

                connector_tag = 'connector_ids[%i]' % i_pre
                connector_pre_postdata[connector_tag] = connection[1]         

                i_pre += 1            
                
            if connection[2] == 0 and self.get_outputs is True:
                connector_post_coords[connection[1]] = {}
                connector_post_coords[connection[1]]['id'] = connection[1]
                connector_post_coords[connection[1]]['coords'] = (connection[3]/10000,connection[5]/10000,connection[4]/-10000)            

                connector_ids.append(connection[1])
                connector_tag = 'connector_ids[%i]' % i_post
                ### Add connector_id of this synapse to postdata
                connector_post_postdata[connector_tag] = connection[1]
                
                i_post += 1            
       
        print('%s Down- / %s Upstream connectors for skid %s found' % (len(connector_post_coords), len(connector_pre_coords), active_skeleton))

        remote_connector_url = remote_instance.get_connectors_url( project_id )

        if self.get_outputs is True and len(connector_post_postdata) > 0:
            print( "Retrieving Postsynaptic Targets..." )
            ### Get connector data for all presynapses to determine number of postsynaptic targets and filter
            connector_data_post = remote_instance.fetch( remote_connector_url , connector_post_postdata )
        else:
            connector_data_post = []        
        
        if self.get_inputs is True and len(connector_pre_postdata) > 0:
            print( "Retrieving Presynaptic Targets..." )
            ### Get connector data for all presynapses to filter later           
            connector_data_pre = remote_instance.fetch( remote_connector_url , connector_pre_postdata ) 
        else:
            connector_data_pre = []  
        
        skids_to_check = []        
        
        for connector in connector_data_post+connector_data_pre:
           if connector[1]['presynaptic_to'] != None:
               skids_to_check.append(connector[1]['presynaptic_to'])
           
           for target_skid in connector[1]['postsynaptic_to']:
               if target_skid != None:
                   skids_to_check.append(target_skid)
                   
        skids_to_check = set(skids_to_check)
       
        neuron_names = get_neuronnames(skids_to_check)
                    
        if connector_data_post or connector_data_pre:
            print("Connector data successfully retrieved")
            number_of_targets = {}
            neurons_included = []
            
            if self.filter:
                #Filter Downstream Targets
                connectors_to_delete = {}
                for connector in connector_data_post:
                    connectors_to_delete[connector[0]] = True
                    for target_skid in connector[1]['postsynaptic_to']:
                        if self.filter in neuron_names[str(target_skid)]:
                            connectors_to_delete[connector[0]] = False
                            neurons_included.append(neuron_names[str(target_skid)])
                
                for connector_id in connectors_to_delete:
                    if connectors_to_delete[connector_id] is True:
                        connector_post_coords.pop(connector_id)
                
                #Filter Upstream Targets
                connectors_to_delete = {}
                for connector in connector_data_pre:
                    connectors_to_delete[connector[0]] = True
                    if connector[1]['presynaptic_to'] != None:
                        if self.filter in neuron_names[str(connector[1]['presynaptic_to'])]:
                            connectors_to_delete[connector[0]] = False
                            neurons_included.append(neuron_names[str(connector[1]['presynaptic_to'])])
                
                for connector_id in connectors_to_delete:
                    if connectors_to_delete[connector_id] is True:
                        connector_post_coords.pop(connector_id)
                        
                print('Neurons remaining after filtering: ',set(neurons_included))
            
            if len(connector_post_coords) > 0:
                ### Extract number of postsynaptic targets for connectors    
                for connector in connector_data_post:
                    number_of_targets[connector[0]] = len(connector[1]['postsynaptic_to'])              
                
            ### Create a sphere for every connector - presynapses will be scaled based on number of postsynaptic targets
            if self.color_prop == 'Black':
                connector_color = (0,0,0)
            elif self.color_prop == 'Random':
                connector_color = [random.randrange(0,100)/100 for e in [0,0,0]]
            elif self.color_prop == 'Mesh-color':
                connector_color = mesh_color

            Create_Mesh.make_connector_spheres (active_skeleton, connector_post_coords, connector_pre_coords, number_of_targets, connector_color, self.basic_radius)
                
        else:
            print('No connector data for presnypases retrieved')                    
                        
        return {'FINISHED'}      


    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)
    
def availableObjects(self, context):
    available_objects = []
    for obj in bpy.data.objects:
        name = obj.name
        available_objects.append((name,name,name))
    available_objects.append(('Synapses','Synapses','Synapses'))
    return available_objects


class ConnectorsToSVG(Operator, ExportHelper):      
    """Retrieves Connectors of active Neuron from CATMAID database and outputs SVG"""
    bl_idname = "connectors.to_svg"  
    bl_label = "Export Connectors (=Synapses) to SVG"

    # ExportHelper mixin class uses this
    filename_ext = ".svg"   

    which_neurons = EnumProperty(name = "Which Neurons?", 
                                      items = [('Active','Active','Active'),('Selected','Selected','Selected'),('All','All','All')],
                                      description = "Choose which neurons to reload.")    
    random_colors = BoolProperty(name="Use Random Colors", default = False)
    mesh_colors = BoolProperty(name="Use Mesh Colors", default = False,
                                description = "Neurons are exported with their Blender material diffuse color")
    #gray_colors = BoolProperty(name="Use Gray Colors", default = False)
    merge = BoolProperty(name="Merge into One", default = True,
                        description = "All neurons to process are rendered into the same brain.")
    color_by_input = BoolProperty(name="Color by Input", default = False,
                        description = "Postsynapses from the same presynaptic neuron are given the same color.")
    color_by_strength = BoolProperty(name="Color Presynapses by # of Postsynapses", default = False)
    color_by_connections = StringProperty(name="Color by Connections to Neuron (Skid)", default = '',
                                     description="Count connections of neuron to process and given neuron -> colors connectors appropriately. Attention: whether up- and or downstream partners are counted is set by [export inputs] and [export outputs]")
    color_by_density = BoolProperty(name = "Color by Density", 
                                    default = False, 
                                    description = "Colors Connectors by # of Nodes of given [Object for Density] within [Proximity Threshold]")                                    
    object_for_density = EnumProperty(name = "Object for Density", 
                                      items = availableObjects,
                                      description = "Choose Object for Coloring Connetors by Density")
    proximity_radius_for_density = FloatProperty(name="Proximity Threshold (Blender Units!)", 
                                                 default = 0.25,
                                                 description = "Maximum allowed distance between Connector and a Node")        
    export_inputs = BoolProperty(name="Export Inputs", default = True)
    export_outputs = BoolProperty(name="Export Outputs", default = False)
    scale_outputs = BoolProperty(name="Scale Presynapses", default = False,
                                 description = "Size of Presynapses based on number of postsynaptically connected neurons")    
    basic_radius = FloatProperty(name="Base Radius", default = 0.5) 
    export_as = EnumProperty(name="Export as:",
                                   items = (("Circles","Circles","Circles"),
                                            ("Arrows","Arrows","Arrows"),
                                            ("Lines","Lines","Lines")                                                                                        
                                            ),
                                    default =  "Circles",
                                    description = "Choose symbol that connectors will be exported as.")    
    export_ring_gland = BoolProperty(name="Export Ring Gland", default = False,
                                    description = "Export Outlines of the ring gland in addition to outlines of CNS")
    export_neuron = BoolProperty(name="Include Neuron", default = True,
                                    description = "Export neurons skeletons as well")
    barplot = BoolProperty(name="Add Barplot", default = False,
                                    description = "Export Barplot along X/Y axis to show synapse distribution")
    filter_connectors = StringProperty(name="Filter Connector:", default = '',
                                     description="Filter Connectors by edges from/to neuron name(s)! (syntax: to exclude start with ! / to set synapse threshold start with > / applies to neuron names / case INsensitive / comma-separated -> ORDER MATTERS! ) ")
    #filter_downstream = StringProperty(name="Filter Outputs:", default = '')
    
    x_persp_offset = FloatProperty(name="Horizontal Perspective", default = 0.9, max = 2, min = -2)  
    y_persp_offset = FloatProperty(name="Vertical Perspective", default = -0.01, max = 2, min = -2)
    views_to_export = EnumProperty(name="Views to export",
                                   items = (("Front/Top/Lateral/Perspective-Dorsal","Front/Top/Lateral/Perspective-Dorsal","Front/Top/Lateral/Perspective-Dorsal"),
                                            ("Front/Top/Lateral","Front/Top/Lateral","Front/Top/Lateral"),
                                            ("Front","Front","Front"),
                                            ("Top","Top","Top"),
                                            ("Lateral","Lateral","Lateral"),
                                            ("Perspective-Front","Perspective-Front","Perspective-Front"),
                                            ("Perspective-Dorsal","Perspective-Dorsal","Perspective-Dorsal")
                                            ),
                                    default =  "Front/Top/Lateral/Perspective-Dorsal",
                                    description = "Choose which views should be included in final SVG")
    add_legend = BoolProperty(name="Add legend", default = True,
                                    description = "Add legend to figure")

                    
    
    neuron_names = {}
    
    connections_for_color = {}
    
    mesh_color = {}
    
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False 
           
    
    def execute(self, context):  
        global remote_instance
        
        connector_data = {}
        neurons_to_export = []  
        skids_to_export = []  

        if self.which_neurons == 'Active':
            if bpy.context.active_object is None and self.which_neurons == 'Active':
                print ('No Object Active')
                self.report({'ERROR'},'No Active Object!')       
                return
            elif bpy.context.active_object is not None and '#' not in bpy.context.active_object.name and self.which_neurons == 'Active':
                print ('Active Object not a Neuron') 
                self.report({'ERROR'},'Active Object not a Neuron!')
                return
            active_skid = re.search('#(.*?) -',bpy.context.active_object.name).group(1)                
            skids_to_export.append(active_skid)
            neurons_to_export.append(bpy.context.active_object)

            if self.mesh_colors:
                self.mesh_color[active_skeleton] =  bpy.context.active_object.active_material.diffuse_color   

        elif self.which_neurons == 'Selected':
            for neuron in bpy.context.selected_objects:
                if neuron.name.startswith('#'):
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    skids_to_export.append(skid)
                    neurons_to_export.append(neuron)
                    if self.mesh_colors:
                        self.mesh_color[skid] =  neuron.active_material.diffuse_color

        elif self.which_neurons == 'All':
            for neuron in bpy.data.objects:
                if neuron.name.startswith('#'):
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    skids_to_export.append(skid)
                    neurons_to_export.append(neuron)
                    if self.mesh_colors:
                        self.mesh_color[skid] =  neuron.active_material.diffuse_color

        for n in skids_to_export:
            connector_data[n] = self.get_connectors(n)

        if self.color_by_connections:
            #If outputs are exported then count only upstream connections (upstream sources of these outputs)
            #If inputs are exported then count only downstream connections (downstream targets of these inputs)
            #-> just use them invertedly for use_inputs/outputs when calling get_connectivity
            self.connections_for_color = self.get_connectivity(skids_to_export,self.export_outputs,self.export_inputs)  

        if self.export_neuron is True:        
            neurons_svg_string = self.create_svg_for_neuron(neurons_to_export)                    
        else:
            neurons_svg_string = {}
    
        self.export_to_svg(connector_data, neurons_svg_string) 

        """
        if bpy.context.active_object is None and self.all_neurons is False:
            print ('No Object Active')       
        elif bpy.context.active_object is not None and '#' not in bpy.context.active_object.name and self.all_neurons is False:
            print ('Active Object not a Neuron')         
        elif self.all_neurons is False:                       
            active_skeleton = re.search('#(.*?) -',bpy.context.active_object.name).group(1)
            connector_data[active_skeleton] = self.get_connectors(active_skeleton)
            
            if self.color_by_connections:
                #If outputs are exported then count only upstream connections (upstream sources of these outputs)
                #If inputs are exported then count only downstream connections (downstream targets of these inputs)
                #-> just use them invertedly for use_inputs/outputs when calling get_connectivity
                self.connections_for_color = self.get_connectivity([active_skeleton],self.export_outputs,self.export_inputs)  
                
            if self.mesh_colors:
                self.mesh_color[active_skeleton] =  bpy.context.active_object.active_material.diffuse_color            

            if self.export_neuron is True:        
                neurons_svg_string = self.create_svg_for_neuron([bpy.context.active_object])                    
            else:
                neurons_svg_string = {}                
            
            self.export_to_svg(connector_data,neurons_svg_string)           
        elif self.all_neurons is True:             
            
            for neuron in bpy.data.objects:
                if neuron.name.startswith('#'):
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    connector_data[skid] = self.get_connectors(skid)   
                    neurons_to_export.append(neuron)
                    skids_to_export.append(skid)
                    if self.mesh_colors:
                        self.mesh_color[skid] =  neuron.active_material.diffuse_color
                    
            if self.color_by_connections:
                #If outputs are exported then count only upstream connections (upstream sources of these outputs)
                #If inputs are exported then count only downstream connections (downstream targets of these inputs)
                #-> just use them invertedly for use_inputs/outputs when calling get_connectivity
                self.connections_for_color = self.get_connectivity(skids_to_export,self.export_outputs,self.export_inputs)                
            
            if self.export_neuron is True:        
                neurons_svg_string = self.create_svg_for_neuron(neurons_to_export)                    
            else:
                neurons_svg_string = {}
        
            self.export_to_svg(connector_data, neurons_svg_string) 
        """
            
        return {'FINISHED'} 
      
        
    def get_connectors(self, active_skeleton):
        
        node_data = []
        connector_ids = []
        
        if self.filter_connectors:
            filter_list = self.filter_connectors.split(',')
            #Check if filter is based on inclusion, exclusion or both:
            filter_exclusion = False
            filter_inclusion = False        
            for entry in filter_list:
                if entry[0] == '!' or entry[0] == '>':
                    filter_exclusion = True
                else:
                    filter_inclusion = True
                
                        
        ### Retrieve compact json data and filter connector ids
        print('Retrieving connector data for skid %s...' % active_skeleton)
        node_data = get_3D_skeleton ( [active_skeleton], remote_instance, connector_flag = 1, tag_flag = 0 )[0]

        if node_data:
            print('Success!')

        i = 0
        connector_postdata_postsynapses = {}
        connector_postdata_presynapses = {}
        connector_post_coords = {}
        connector_pre_coords = {}
        nodes_list = {}
            
        print('Extracting coordinates..')
        
        ### Convert coordinates to Blender
        for node in node_data[0]:
            
            X = float(node[3])/10000
            Y = float(node[4])/-10000
            Z = float(node[5])/10000            
            
            nodes_list[node[0]] = (X,Z,Y)

        for connection in node_data[1]:
                        
            if connection[2] == 1 and self.export_inputs is True:
                ### For Sources the Treenodes the Connector is connecting TO are listed
                ### Reason: One connector can connector to the same neuron (at different treenodes) multiple times!!!
                ### !!!Attention: Treenode can be connected to multiple connectors (up- and downstream)
                
                if connection[0] not in connector_pre_coords:
                    connector_pre_coords[connection[0]] = {}
                    
                #Format: connector_pre_coord[target_treenode_id][upstream_connector_id] = coords of target treenode
                connector_pre_coords[connection[0]][connection[1]] = {} 
                connector_pre_coords[connection[0]][connection[1]]['coords'] = nodes_list[connection[0]] #these are treenode coords, NOT connector coords
                
                """
                connector_pre_coords[connection[0]] = {}
                connector_pre_coords[connection[0]]['connector_id'] = connection[1]
                connector_pre_coords[connection[0]]['coords'] = nodes_list[connection[0]]                
                """               

                ### This format is necessary for CATMAID url postdata:
                ### Dictonary: 'connector_ids[x]' : connectorid
                connector_tag = 'connector_ids[%i]' % i
                connector_postdata_presynapses[connector_tag] = connection[1]

            if connection[2] == 0 and self.export_outputs is True:
                connector_post_coords[connection[1]] = {}
                connector_post_coords[connection[1]]['id'] = connection[1]
                connector_post_coords[connection[1]]['coords'] = (connection[3]/10000,connection[5]/10000,connection[4]/-10000)            

                connector_ids.append(connection[1])
                connector_tag = 'connector_ids[%i]' % i
                connector_postdata_postsynapses[connector_tag] = connection[1]
                
            i += 1
        
        print('%s Down- / %s Upstream connectors for skid %s found' % (len(connector_post_coords), len(connector_pre_coords), active_skeleton))
        remote_connector_url = remote_instance.get_connectors_url( project_id )
    
        if self.export_outputs is True:        
            print( "Retrieving Target Connectors..." )        
            connector_data_post = remote_instance.fetch( remote_connector_url , connector_postdata_postsynapses )
            #print(connector_data_post)
        else:
            connector_data_post = []

        if self.export_inputs is True:    
            print( "Retrieving Source Connectors..." )
            connector_data_pre = remote_instance.fetch( remote_connector_url , connector_postdata_presynapses )
            #print(connector_data_pre)
        else:
            connector_data_pre = []

        if connector_data_pre or connector_data_post:
            print("Connectors successfully retrieved")     
            number_of_targets = {}
            presynaptic_to = {}
            postsynaptic_to = {}
            
            ### Only proceed if neuron actually has Outputs (e.g. motor neurons)
            if len(connector_post_coords) > 0:
                
                skids_to_check = []
                total_synapse_count = {}
                ### Count all neurons postsynaptic to the connector
                for connector in connector_data_post:
                    number_of_targets[connector[0]] = len(connector[1]['postsynaptic_to'])
                    for entry in connector[1]['postsynaptic_to']:
                        skids_to_check.append(entry)
                        ### Count number of connections for each presynaptic neuron                    
                        if entry not in total_synapse_count:                                                
                            total_synapse_count[entry] = 1
                        else:
                            total_synapse_count[entry] += 1
                        
                
                print('Retrieving Ancestry of all downstream neurons...')
                self.check_ancestry(skids_to_check) 
                print('Done')                

                neurons_included = []  
                entries_to_delete = {}                
                neurons_included = []
                
                ### Create list of targets for all source treenodes:   
                ### connector_post_coords[connector_id]                 
                for connector in connector_data_post:                         
                    connector_id = connector[0]
                    
                    if connector_id in connector_post_coords:
                        connector_post_coords[connector_id]['postsynaptic_to'] = connector[1]['postsynaptic_to']
                    
                    if connector_id not in postsynaptic_to:
                        postsynaptic_to[connector_id] = []                        
                    
                    entries_to_delete[connector_id] = True                     
                    
                    if self.filter_connectors:
                        print('Filtering Connector %i (postsynaptic to: %s) for: < %s >' % (connector[0], str(connector[1]['postsynaptic_to']), self.filter_connectors))
                        if len(connector[1]['postsynaptic_to']) == 0 or None in connector[1]['postsynaptic_to']:
                            print('Connector w/o postsynaptic connection found: %s - will NOT be exported' % connector[0] )   
                    
                    ### Connector_data_XXX is a list NOT a dictionary, so we have to cycle through it
                    for target_skid in connector[1]['postsynaptic_to']:                            
                        if self.filter_connectors:                                
                            #Set whether connector will is included unless exclusion_tag is found or whether they will be excluded unless inclusion_tag is found
                            if filter_inclusion is True:
                                include_connector = False                                 
                            else:
                                include_connector = True
                            
                            for tag in filter_list:
                                ### Check for match with filter:
                                ### If filter startswith '!' then those neurons will be excluded
                                if tag.startswith('!'):
                                    if target_skid != None and tag[1:].lower() in self.neuron_names[target_skid].lower():
                                        print('Excluded: match with %s - %s (# %s)' % (tag,self.neuron_names[target_skid],target_skid))
                                        include_connector = False
                                    #else:
                                        #If a single target of connector is to be exlucded, remove the whole connector from dict[connector_id]
                                        #connector_post_coords.pop(connector_id)  
                                elif tag.startswith('>'):
                                    try:
                                        synapse_threshold = int(tag[1:])
                                        if total_synapse_count[target_skid] >= synapse_threshold:
                                            print('Above threshold: -- %s -- : %s (%i)' % (connector[1]['presynaptic_to'],self.neuron_names[connector[1]['presynaptic_to']],total_synapse_count[connector[1]['presynaptic_to']]))
                                            include_connector = True
                                        #else:
                                            #If connector is below threshold: remove him from dict[treenode]
                                            #connector_post_coords.pop(connector_id)
                                    except:
                                        print('Unable to convert filter string to int for synapse threshold!!')
                                else:                                    
                                    if target_skid != None and tag.lower() in self.neuron_names[target_skid].lower():
                                        print('Included: match with %s - %s (# %s)' % (tag,self.neuron_names[target_skid],target_skid))
                                        include_connector = True
                                        
                            if include_connector is True:
                                postsynaptic_to[connector_id].append(target_skid)
                                entries_to_delete[connector_id] = False
                                neurons_included.append(self.neuron_names[target_skid])
                        else:
                            postsynaptic_to[connector_id].append(target_skid)
                            entries_to_delete[connector_id] = False
                
                #print(entries_to_delete)                
                ### Delete Treenode from connectors list, if no match has been found
                count = 0
                for connector_id in entries_to_delete:                    
                    if entries_to_delete[connector_id] is True:
                        #print('Deleted entry for treenode %s' % treenode)
                        connector_post_coords.pop(connector_id)
                        count += 1
                print('%i target treenodes left (%s removed by Filter)' % (len(connector_post_coords),count))
                
                if self.filter_connectors:
                    print('Downstream Neurons remaining after filtering:')
                    print(set(neurons_included))
                      
            
            ### Only proceed if neuron actually has Inputs (e.g. sensory neurons)
            if len(connector_pre_coords) > 0:
                print('Total of %s connectors for %s inputs found: ' % (str(len(connector_data_pre)), str(len(connector_pre_coords))))                
                
                ### Retrieve Ancestry(= name for all upstream neurons):
                print('Retrieving Ancestry of all upstream neurons...')
                skids_to_check = []                
                total_synapse_count = {}
                neurons_included = []  
                entries_to_delete = {}
                
                for connector in connector_data_pre:
                    skids_to_check.append(connector[1]['presynaptic_to'])
                    
                self.check_ancestry(skids_to_check) 
                print('Done')                
                
                #Create weight map for subsequent threshold filtering
                for connector in connector_data_pre:
                    ### If connector IDs match. Keep in mind: A single treenode can receive input from more than one connector!!!                    
                    input = connector[1]['presynaptic_to']
                    ### Count number of connections for each presynaptic neuron                    
                    if input not in total_synapse_count:                                                
                        total_synapse_count[input] = 1
                    else:
                        total_synapse_count[input] += 1
                            
                #print(total_synapse_count)
          
                ### Create list of sources for all target treenodes:                     
                for treenode in connector_pre_coords:
                    #print('Searching for treenode %s connected to connector %s' % (str(treenode),str(connector_pre_coords[treenode]['connector_id']) ) )
                    if treenode not in presynaptic_to:
                        presynaptic_to[treenode] = []
                    entries_to_delete[treenode] = True

                    
                    ### Connector_data_XXX is a list NOT a dictionary, so we have to cycle through it
                    for connector in connector_data_pre:                    
                        ### If connector IDs match. Keep in mind: A single treenode can receive input from more than one connector!!!
                        #if connector[0] == connector_pre_coords[treenode]['connector_id']:                                                
                        if connector[0] in connector_pre_coords[treenode]:
                            connector_pre_coords[treenode][connector[0]]['presynaptic_to'] = connector[1]['presynaptic_to']
                            
                            if self.filter_connectors:
                                print('Filtering Connector %s (presynaptic to %s) for: %s' % (connector[0], connector[1]['presynaptic_to'] ,self.filter_connectors))                     
                                
                                #Set whether connector will is included unless exclusion_tag is found or whether they will be excluded unless inclusion_tag is found
                                if filter_inclusion is True:
                                    include_connector = False                                 
                                else:
                                    include_connector = True
                                    
                                if connector[1]['presynaptic_to'] is None:
                                    print('Connector w/o presynaptic connection found: %s - will NOT be exported' % connector[0] )  
                                    include_connector = False     
                                
                                for tag in filter_list:
                                    ### Check for match with filter:
                                    ### If filter startswith '!' then those neurons will be excluded
                                    if tag.startswith('!'):
                                        if connector[1]['presynaptic_to'] != None and tag[1:].lower() in self.neuron_names[connector[1]['presynaptic_to']].lower():
                                            print('Excluded: match with < %s > : %s (# %s)' % (tag,self.neuron_names[connector[1]['presynaptic_to']],connector[1]['presynaptic_to']))
                                            include_connector = False 
                                    elif tag.startswith('>'):
                                        try:
                                            synapse_threshold = int(tag[1:])
                                            if total_synapse_count[connector[1]['presynaptic_to']] >= synapse_threshold:
                                                print('Above threshold: -- %s -- : %s (%i)' % (connector[1]['presynaptic_to'],self.neuron_names[connector[1]['presynaptic_to']],total_synapse_count[connector[1]['presynaptic_to']]))
                                                include_connector = True 
                                        except:
                                            print('Unable to convert filter string to int')
                                    else:                                    
                                        if connector[1]['presynaptic_to'] != None and tag.lower() in self.neuron_names[connector[1]['presynaptic_to']].lower():
                                            print('Included: match with < %s >: %s (# %s)' % (tag,self.neuron_names[connector[1]['presynaptic_to']],connector[1]['presynaptic_to']))
                                            include_connector = True
                                                                                        
                                if include_connector is True:
                                    presynaptic_to[treenode].append(connector[1]['presynaptic_to'])
                                    entries_to_delete[treenode] = False
                                    neurons_included.append(self.neuron_names[connector[1]['presynaptic_to']])
                            
                            else:
                                presynaptic_to[treenode].append(connector[1]['presynaptic_to'])
                                entries_to_delete[treenode] = False
                                
                ### Delete Treenode from connectors list, if no match has been found
                count = 0
                for treenode in entries_to_delete:                    
                    if entries_to_delete[treenode] is True:
                        #print('Deleted entry for treenode %s' % treenode)
                        connector_pre_coords.pop(treenode)
                        count += 1
                print('%i target treenodes left (%s removed by Filter)' % (len(connector_pre_coords),count))
                
                if self.filter_connectors:
                    print('Upstream Neurons remaining after filtering:')
                    print(set(neurons_included))


            return((number_of_targets, connector_pre_coords, connector_post_coords, presynaptic_to))
           
        else:
            print('No data retrieved')   
                        
        return {'FINISHED'}
    
    
    def export_to_svg(self, connector_data, neurons_svg_string):      
        print('%i Neurons in Connector data found' % len(connector_data))
        
        svg_header =    '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
        svg_end =       '\n</svg> '
        
        offsetX = 0
        offsetY = 0 

        offsetY_for_top = 60
        offsetX_for_top = 135
        
        offsetY_for_front = -150
        offsetX_for_front = 5 
        
        offsetY_for_lateral = 0
        offsetX_for_lateral = 0   
        
        offsetY_for_persp = 150
        offsetX_for_persp = 0   

        offsetY_forMergeLegend = -150 
        
        if "Perspective-Dorsal" in self.views_to_export:
            #For dorsal perspective change offsets:
            y_persp_offset = -1 * self.x_persp_offset
            x_persp_offset = 0            
            #y_center sets the pivot along y axis (0-25) -> all this does is move the object along y axis, does NOT change perspective
            y_center = 5  
        else:
            x_persp_offset = self.x_persp_offset
            y_persp_offset = self.y_persp_offset
        
        if self.merge is True:
            offsetIncrease = 0
        else:
            offsetIncrease = 250        
        basic_radius = self.basic_radius
        
        density_gradient = {'start_rgb': (0,255,0),
                            'end_rgb':(255,0,0)}
        density_data = []        

        brain_shape_top_string = '<g id="brain shape top">\n <polyline points="28.3,-5.8 34.0,-7.1 38.0,-9.4 45.1,-15.5 50.8,-20.6 57.7,-25.4 59.6,-25.6 63.2,-22.8 67.7,-18.7 70.7,-17.2 74.6,-14.3 78.1,-12.8 84.3,-12.6 87.7,-15.5 91.8,-20.9 98.1,-32.4 99.9,-38.3 105.2,-48.9 106.1,-56.4 105.6,-70.1 103.2,-75.8 97.7,-82.0 92.5,-87.2 88.8,-89.1 82.6,-90.0 75.0,-89.9 67.4,-89.6 60.8,-85.6 55.3,-77.2 52.4,-70.2 51.9,-56.7 55.0,-47.0 55.9,-36.4 56.0,-32.1 54.3,-31.1 51.0,-33.4 50.7,-42.5 52.7,-48.6 49.9,-58.4 44.3,-70.8 37.4,-80.9 33.1,-84.0 24.7,-86.0 14.2,-83.9 8.3,-79.1 2.9,-68.3 1.3,-53.5 2.5,-46.9 3.0,-38.3 6.3,-28.2 10.9,-18.7 16.3,-9.7 22.2,-6.4 28.3,-5.8" \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n <polyline points="88.8,-89.1 90.9,-97.7 92.9,-111.3 95.6,-125.6 96.7,-139.4 95.9,-152.0 92.8,-170.2 89.4,-191.0 87.2,-203.7 80.6,-216.6 73.4,-228.3 64.5,-239.9 56.4,-247.3 48.8,-246.9 39.0,-238.3 29.6,-226.9 24.7,-212.0 22.9,-201.2 23.1,-186.9 18.7,-168.3 14.1,-150.4 12.6,-138.0 13.7,-121.5 16.3,-105.1 18.3,-84.8 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>' 
        brain_shape_front_string = '<g id="brain shape front"> \n <polyline points="51.5,24.0 52.0,21.3 52.0,17.6 50.2,11.2 46.8,6.5 40.5,2.5 33.8,1.1 25.4,3.4 18.8,8.0 13.2,12.5 8.3,17.9 4.3,23.8 1.8,29.3 1.4,35.6 1.6,42.1 4.7,48.3 7.9,52.5 10.8,56.9 13.1,64.3 14.3,73.2 12.8,81.0 16.2,93.6 20.9,101.5 28.2,107.5 35.3,112.7 42.2,117.0 50.8,119.3 57.9,119.3 67.1,118.0 73.9,114.1 79.0,110.4 91.1,102.7 96.3,94.2 96.3,85.3 94.0,81.4 95.4,74.8 96.6,68.3 97.5,64.7 100.9,59.7 103.8,52.5 105.4,46.7 106.1,38.8 105.4,32.4 103.1,26.4 98.9,21.0 94.1,16.3 88.3,11.1 82.0,6.5 74.8,3.3 67.8,3.1 61.7,5.1 56.8,9.6 53.4,15.2 52.2,19.7 52.3,25.3 51.4,24.1 " \n  style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n <polyline points="46.6,34.0 45.5,36.1 43.2,38.6 41.1,43.3 39.7,48.7 39.7,51.0 42.6,55.2 51.4,59.5 54.9,60.9 60.8,60.8 62.9,58.2 62.9,52.6 60.3,47.6 57.7,43.9 56.1,40.2 55.1,35.9 55.1,34.4 51.8,33.6 49.1,33.5 46.6,34.0 " \n  style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'         
        brain_shape_lateral_string = '<g id="brain shape lateral"> \n <polyline points="247.2,91.6 246.8,94.6 246.3,95.5 245.0,96.7 239.8,99.0 225.8,103.4 210.9,107.5 200.8,109.1 186.0,109.9 166.0,110.7 150.8,111.3 135.8,112.8 120.9,114.2 107.3,114.9 98.6,115.7 88.7,117.9 81.3,119.1 66.2,119.2 58.3,118.7 51.6,118.5 46.0,116.4 40.7,114.4 36.6,112.0 34.2,109.6 30.7,104.8 27.3,100.3 25.3,98.2 22.2,91.9 21.1,86.8 19.6,80.6 17.4,73.9 15.2,68.9 11.2,61.8 11.0,52.3 9.1,49.9 7.4,46.4 6.6,42.6 6.3,35.7 7.0,27.1 7.4,24.5 10.2,18.7 15.8,13.2 22.3,8.5 26.2,7.1 32.6,7.0 36.1,6.2 41.2,3.9 47.2,1.8 54.8,1.7 64.5,3.2 73.4,5.3 81.1,11.2 86.7,16.4 89.0,21.1 90.2,33.2 89.3,42.8 86.6,48.7 82.1,53.9 78.8,57.2 77.9,59.2 91.4,61.6 98.5,62.2 116.6,62.4 131.7,61.0 146.1,59.8 161.1,60.1 176.0,61.3 190.8,63.3 206.2,66.0 219.5,70.6 224.5,72.8 239.5,82.1 245.5,86.0 246.9,87.9 247.2,91.6 " \n  style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'          
        
        ring_gland_top = '<g id="ring gland top"> \n <polyline points="57.8,-43.9 59.9,-43.8 62.2,-43.3 64.4,-41.1 67.3,-37.7 70.8,-34.0 73.9,-30.7 75.1,-28.3 76.2,-24.8 76.0,-22.1 75.2,-19.7 73.0,-17.3 70.4,-16.1 66.5,-16.1 64.4,-15.2 61.8,-12.3 58.8,-9.5 55.7,-8.6 51.3,-8.1 47.6,-8.3 44.0,-8.7 41.4,-10.3 40.8,-12.6 42.5,-16.1 45.4,-20.7 47.9,-25.5 48.9,-28.9 50.1,-32.3 51.8,-33.0 51.5,-35.1 51.7,-37.9 52.4,-41.2 53.9,-42.8 55.8,-43.8 57.8,-43.9 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'          
        ring_gland_front = '<g id="ring gland front"> \n <polyline points="45.5,11.3 44.3,12.3 41.9,14.2 40.9,16.8 41.3,20.1 42.7,24.7 44.0,27.8 45.9,28.6 49.0,27.7 50.1,27.7 53.0,28.1 56.5,28.4 59.2,28.3 62.2,27.5 64.5,26.6 67.1,26.6 69.7,27.2 70.9,26.9 73.1,25.4 74.8,22.8 75.9,20.3 75.9,17.6 74.8,15.1 72.8,12.8 69.3,10.2 66.7,8.6 64.2,7.7 61.9,7.6 59.0,8.4 57.1,9.4 56.6,11.1 55.1,10.0 53.5,9.2 51.3,8.9 49.6,9.2 45.5,11.3 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>' 
        ring_gland_lateral = '<g id="ring gland lateral"> \n <polyline points="9.0,16.8 13.7,13.3 23.4,9.8 27.9,9.1 31.1,9.5 34.8,8.1 38.8,7.7 41.2,8.4 42.6,9.8 44.0,12.7 44.2,16.6 43.5,22.3 41.2,25.1 36.3,26.4 31.6,26.4 26.9,27.2 22.1,26.7 20.2,27.1 15.7,28.6 12.7,28.2 11.0,28.7 9.3,27.7 8.3,24.8 8.3,20.9 9.0,16.8 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>' 
        
        arrows_defs = '<defs> \n <marker id="markerArrow" markerWidth="13" markerHeight="13" refx="2" refy="6" orient="auto"> \n <path d="M2,2 L2,11 L10,6 L2,2" style="fill: #000000;" /> \n </marker> \n </defs>'
 
        print('Writing SVG to file %s' % self.filepath)
        f = open(self.filepath, 'w', encoding='utf-8')  
        f.write(svg_header)
        
        """
        if self.use_arrows is True:
            f.write(arrows_defs)   
        """
        
        #Create list of nodes for given density object
        if self.color_by_density is True:
            density_color_map = {}
            max_density = 0
            try:
                for spline in bpy.data.objects[self.object_for_density].data.splines:
                    for node in spline.points:
                        #node.co = vector(x,y,z,?)
                        if node.co not in density_data:
                            density_data.append(node.co)
                #print(density_data)
            except:
                print('ERROR: Unable to create density data for object!') 
                self.report({'ERROR'},'Error(s) occurred: see console')
            
            #Fill density_color_map with density counts first and get max_density
            for neuron in connector_data:
                #Presynaptic connectors (=Treenodes)    
                for target_treenode in connector_data[neuron][1]:
                    for connector in connector_data[neuron][1][target_treenode]:
                        if connector not in density_color_map:
                            connector_co = connector_data[neuron][1][target_treenode][connector]['coords']
                            density_count = 0
                            for node in density_data:
                                dist1 = math.sqrt(
                                                  (connector_co[0]-node[0])**2 +
                                                  (connector_co[1]-node[1])**2 +
                                                  (connector_co[2]-node[2])**2
                                                 )
                                if dist1 < self.proximity_radius_for_density:
                                    density_count += 1   
                                    
                            if density_count > max_density:
                                max_density = density_count
                                
                            density_color_map[connector] = density_count
                
                #Postsynaptic connectors            
                for connector in connector_data[neuron][2]:
                    if connector not in density_color_map:
                        connector_co = connector_data[neuron][2][connector]['coords']
                        density_count = 0
                        for node in density_data:
                            dist1 = math.sqrt(
                                              (connector_co[0]-node[0])**2 +
                                              (connector_co[1]-node[1])**2 +
                                              (connector_co[2]-node[2])**2
                                             )
                            if dist1 < self.proximity_radius_for_density:
                                density_count += 1   
                                
                        if density_count > max_density:
                            max_density = density_count
                            
                        density_color_map[connector] = density_count
                            
            #Convert density_color_map from density counts to colors
            for connector in density_color_map:
                density_count = density_color_map[connector]                
                if max_density > 0 and density_count > 0:
                    density_color = (
                                    int(density_gradient['start_rgb'][0] + (density_gradient['end_rgb'][0] - density_gradient['start_rgb'][0])/max_density * density_count),                    
                                    int(density_gradient['start_rgb'][1] + (density_gradient['end_rgb'][1] - density_gradient['start_rgb'][1])/max_density * density_count),                         
                                    int(density_gradient['start_rgb'][2] + (density_gradient['end_rgb'][2] - density_gradient['start_rgb'][2])/max_density * density_count)                             
                                                )
                else:
                    #print('No density data within given radius found!')
                    density_color = (0,0,0)
                    
                density_color_map[connector] = density_color
                               

        ### Create random color map for every input / red is reserved for all outputs            
        if self.color_by_input is True or self.color_by_strength is True:            
            input_color_map = {}
            input_weight_map = {}
            max_values = {}
            presynaptic_to = {}
            
            print('Creating input/weight color map...')
            
            for neuron in connector_data:   
                presynaptic_to[neuron] = connector_data[neuron][3]  
                #print(presynaptic_to[neuron])
                input_weight_map[neuron] = {}
                max_values[neuron] = []
                                        
                for target_treenode in presynaptic_to[neuron]:                    
                    for input in presynaptic_to[neuron][target_treenode]: 
                                            
                        ### Create random color map for all source neurons
                        if input not in input_color_map:
                            input_color_map[input] = (random.randrange(0,255), random.randrange(0,255),random.randrange(0,255)) 
                            outputs_color = (255, 0, 0)
                        ### ATTENTION: this input color map is replaced down the page by a non-random version!

                        ### Count number of connections for each presynaptic neuron                    
                        if input not in input_weight_map[neuron]:                                                
                            input_weight_map[neuron][input] = {}
                            input_weight_map[neuron][input]['connections'] = 1
                        else:
                            input_weight_map[neuron][input]['connections'] += 1
                
                ### Get min & max values of weight map       
                for entry in input_weight_map[neuron]:
                    if entry != None:
                        max_values[neuron].append(input_weight_map[neuron][entry]['connections'])
                #print(input_weight_map)
                
                if self.export_inputs is True:
                    half_max = max(max_values[neuron])/2
                    print('Half_max = ' + str(half_max))
                else:
                    half_max = 0
                            
                ### Create color scheme from green to red based on min/max
                for input in input_weight_map[neuron]:                    
                    ### If Input weight is bigger than half max then gradually reduce green channel, red channel stays max
                    if input_weight_map[neuron][input]['connections'] > half_max:
                        red_channel = 255
                        green_channel = int(255 - (255/half_max) * (input_weight_map[neuron][input]['connections']/2))
                    ### Else gradually increase red channel
                    else:
                        green_channel = 255
                        red_channel = int((255/half_max) * (input_weight_map[neuron][input]['connections']))  
                                
                    input_weight_map[neuron][input]['color'] = (red_channel, green_channel, 0)
                    """
                    print('Calculating weight-based color for input %s (%s synapses) of neuron %s: %s' % (str(input), str(input_weight_map[neuron][input]['connections']), \
                           str(neuron), str(input_weight_map[neuron][input]['color'])))          
                    """

            #Create more evenly distributed input_color_map:
            new_input_color_map = ColorCreator.random_colors(len(input_color_map))
        
            shapes = ShapeCreator.create_shapes(2,self.basic_radius)        
            input_shape_map = {}
            
            #print('Shapes: ', shapes)
                    
            shape_index = 0 
            for input in input_color_map:            
                input_color_map[input] = new_input_color_map[0]
                new_input_color_map.pop(0)            
                
                shape_index += 1            
                if shape_index == 1:
                    input_shape_map[input] = 'circle'
                elif shape_index == 2:
                    input_shape_map[input] = shapes[0]
                elif shape_index == 3:
                    input_shape_map[input] = shapes[1]
                    shape_index = 0
        
        #print('Input shape map: ', input_shape_map)

        neuron_count = len(connector_data)
        
        ### Double the number of colors if inputs and outputs are to be exported
        if self.export_inputs is True and self.export_outputs is True:
            neuron_count *= 2        
            
        colormap = ColorCreator.random_colors(neuron_count)
        print(str(neuron_count) + ' random colors created')        
 
        ### Retrieve Ancestry(name for exported neurons):
        print('Retrieving Ancestry of all upstream neurons...')
        skids_to_check = []
        
        for neuron in connector_data:
            skids_to_check.append(neuron)
            
        self.check_ancestry(skids_to_check) 
        print('Ancestry Check Done')    
        source_neurons_list = {}
        first_neuron = True
        
        max_connection = 0
        if self.color_by_connections:
            for neuron in self.connections_for_color:
                if self.connections_for_color[neuron] > max_connection:
                    max_connection = self.connections_for_color[neuron]
        print('Max connections for color_by_connection:', max_connection)
        
        ### Creating SVG starts here
        for neuron in connector_data:
            connectors_weight = connector_data[neuron][0]
            connectors_pre = connector_data[neuron][1]
            connectors_post = connector_data[neuron][2]
            ### presynaptic_to[neuron] = connector_data[neuron][3]
            ### Contains source neurons and their respective color
            ### Set colors here - if color_by_input is False
            ### If self.random_colors is True and self.color_by_input is False and self.color_by_weight is False:
            if self.random_colors is True and self.color_by_input is False:                                
                if self.export_outputs is True:
                    outputs_color = colormap[0]
                    colormap.pop(0)
                
                if self.export_inputs is True:
                    inputs_color = colormap[0]
                    colormap.pop(0)
            elif self.mesh_colors is True:
                inputs_color = (int(self.mesh_color[neuron][0] * 255),
                                int(self.mesh_color[neuron][1] * 255),
                                int(self.mesh_color[neuron][2] * 255))
                outputs_color = (int(self.mesh_color[neuron][0] * 255),
                                int(self.mesh_color[neuron][1] * 255),
                                int(self.mesh_color[neuron][2] * 255))
                                
            elif self.color_by_connections and max_connection != 0:
                #Make connection brighter the less important they are
                outputs_color = (255,
                                 255-int(self.connections_for_color[neuron] * 255/max_connection),
                                 255-int(self.connections_for_color[neuron] * 255/max_connection)
                                )
                inputs_color = ( 255-int(self.connections_for_color[neuron] * 255/max_connection),
                                 255-int(self.connections_for_color[neuron] * 255/max_connection),
                                 255
                                )                             
            else:
                outputs_color = (255, 0, 0)
                inputs_color = (0, 0, 255)

            ### Set standard stroke parameters here
            inputs_color_stroke = (0, 0, 0)
            inputs_width_stroke = 0.05
            outputs_width_stroke = 0.05
            ### Create SVG Group
            line_to_write = '<g id="%s neuron" transform="translate(%i,%i)">' % (neuron,offsetX,offsetY)
            f.write(line_to_write + '\n')
                        
            if 'Front' in self.views_to_export:
                ### Add Connectors from FRONT view
                line_to_write = '<g id="%s front" transform="translate(%i,%i)">' % (neuron,offsetX_for_front,offsetY_for_front)            
                f.write(line_to_write + '\n')            
                ### Add Neuron's morphology if required            
                if self.export_neuron is True:
                    f.write('<g id="neuron">')
                    f.write(neurons_svg_string[neuron]['front'])
                    f.write('</g> \n')
                ### Export Inputs from front view
                line_to_write = '<g id="Inputs">'                                        
                
                for target_treenode in connectors_pre:
                    for connector in connectors_pre[target_treenode]: 
                        if self.color_by_input is True or self.color_by_strength is True:
                            #source_neuron = presynaptic_to[neuron][target_treenode][0]
                            source_neuron = connectors_pre[target_treenode][connector]['presynaptic_to']
                            inputs_color_stroke, inputs_color, source_neuron = self.get_treenode_colors(source_neuron, input_color_map, input_weight_map,neuron)
                            source_neurons_list[source_neuron] = input_color_map[source_neuron]
                            
                        elif self.color_by_density is True:
                            inputs_color = density_color_map[connector]
                                            
                        connector_x = round(connectors_pre[target_treenode][connector]['coords'][0] * 10,1)
                        connector_y = round(connectors_pre[target_treenode][connector]['coords'][2] * - 10,1)                      
                        
                        #If color by input is true, also use different shapes
                        if self.color_by_input is True:                                 
                            if input_shape_map[source_neuron] != 'circle':          
                                shape_temp = ''
                                for node in input_shape_map[source_neuron]:
                                    shape_temp += str(node[0]+connector_x) + ',' + str(node[1]+connector_y) + ' '
                                line_to_write +='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.export_as == 'Arrows' or self.export_as == 'Lines':
                            #Arrow line
                            line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-2,connector_y,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            if self.export_as == 'Arrows':
                                #Arrow head
                                line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                                % ( connector_x-1,connector_y,
                                                    connector_x-3,connector_y+1,
                                                    connector_x-3,connector_y-1,                                                
                                                    str(inputs_color)
                                                   )                                                 
                        elif self.export_as == 'Circles':                 
                            line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        line_to_write += '\n'

                if self.export_inputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n')   
          
                ### Export Outputs from front view
                line_to_write = '<g id="Outputs">'                                        
                
                for connector in connectors_post:
                    connector_x = round(connectors_post[connector]['coords'][0] * 10,1)
                    connector_y = round(connectors_post[connector]['coords'][2] * - 10,1)
                    
                    if self.color_by_density is True:
                        outputs_color = density_color_map[connector]
                    
                    ### Connectors with 5 targets will be double the size
                    if self.scale_outputs is True:
                        radius = basic_radius * (0.8 + connectors_weight[connector]/5) 
                    else:
                        radius = basic_radius
                        
                    if self.export_as == 'Arrows' or self.export_as == 'Lines':
                        line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x-10,connector_y,
                                            connector_x-2,connector_y,
                                            str(outputs_color),str(radius/3)
                                           )
                        if self.export_as == 'Arrows':
                            line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-8,connector_y+1,
                                                connector_x-8,connector_y-1,                                                
                                                str(outputs_color)
                                               )                     
                    elif self.export_as == 'Circles':
                        line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                     % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(outputs_width_stroke))
                    line_to_write += '\n'

                if self.export_outputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n')

                if self.barplot is True and self.merge is False:
                    self.create_barplot(f, connector_data, [neuron] , 0, 2 , x_factor = 1, y_factor = -1)    
                elif self.barplot is True and self.merge is True and first_neuron is True:
                    self.create_barplot(f, connector_data, [n for n in connector_data] , 0, 2 , x_factor = 1, y_factor = -1)            

                ### Add front brain shape
                if self.merge is False or first_neuron is True:
                    f.write('\n' + brain_shape_front_string + '\n') 
                
                    if self.export_ring_gland is True:
                        f.write('\n' + ring_gland_front + '\n') 

                line_to_write = '</g>'
                f.write(line_to_write + '\n \n \n')

            if 'Lateral' in self.views_to_export:
                ### Add Connectors from LATERAL view
                line_to_write = '<g id="%s lateral" transform="translate(%i,%i)">' % (neuron,offsetX_for_lateral,offsetY_for_lateral)
                f.write(line_to_write + '\n')
                ### Add Neuron's morphology if required
                if self.export_neuron is True:
                    f.write('<g id="neuron">')
                    f.write(neurons_svg_string[neuron]['lateral'])
                    f.write('</g> \n')
                ### Export Inputs from lateral view
                line_to_write = '<g id="Inputs"> \n'                                
                
                for target_treenode in connectors_pre:                                                
                    for connector in connectors_pre[target_treenode]: 
                        if self.color_by_input is True or self.color_by_strength is True:
                            #source_neuron = presynaptic_to[neuron][target_treenode][0]
                            source_neuron = connectors_pre[target_treenode][connector]['presynaptic_to']
                            inputs_color_stroke, inputs_color, source_neuron = self.get_treenode_colors(source_neuron, input_color_map, input_weight_map,neuron)
                            source_neurons_list[source_neuron] = input_color_map[source_neuron]

                        elif self.color_by_density is True:
                            inputs_color = density_color_map[connector]                             
                                            
                        connector_x = round(connectors_pre[target_treenode][connector]['coords'][1] * 10,1)
                        connector_y = round(connectors_pre[target_treenode][connector]['coords'][2] * - 10,1)   
                        

                        #If color by input is true, also use different shapes
                        if self.color_by_input is True:                                 
                            if input_shape_map[source_neuron] != 'circle':          
                                shape_temp = ''
                                for node in input_shape_map[source_neuron]:
                                    shape_temp += str(node[0]+connector_x) + ',' + str(node[1]+connector_y) + ' '
                                line_to_write += '<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write += '<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.export_as == 'Arrows' or self.export_as == 'Lines':
                            line_to_write += '<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x,connector_y-10,
                                                connector_x,connector_y-2,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            if self.export_as == 'Arrows':
                                line_to_write += '<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                                % ( connector_x,connector_y-1,
                                                    connector_x+1,connector_y-3,
                                                    connector_x-1,connector_y-3,                                                
                                                    str(inputs_color)
                                                   )
                        elif self.export_as == 'Circles':                 
                            line_to_write += '<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        line_to_write += '\n'

                if self.export_inputs is True:        
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n')

                ### Export Outputs from lateral view
                line_to_write = '<g id="Outputs">'                 
                
                for connector in connectors_post:
                    connector_x = round(connectors_post[connector]['coords'][1] * 10,1)
                    connector_y = round(connectors_post[connector]['coords'][2] * - 10,1)
                    
                    if self.color_by_density is True:
                        outputs_color = density_color_map[connector]
                    
                    if self.scale_outputs is True:
                        radius = basic_radius * (0.8 + connectors_weight[connector]/5) #connectors with 5 targets will be double the size
                    else:
                        radius = basic_radius                    
                        
                    if self.export_as == 'Arrows' or self.export_as == 'Lines':
                        line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x,connector_y-9,
                                            connector_x,connector_y-2,
                                            str(outputs_color),str(radius/3)
                                           )
                        if self.export_as == 'Arrows':      
                            line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x,connector_y-10,
                                                connector_x+1,connector_y-8,
                                                connector_x-1,connector_y-8,                                                
                                                str(outputs_color)
                                               )    
                    elif self.export_as == 'Circles': 
                        line_to_write += '<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                        % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(outputs_width_stroke))         
                    line_to_write += '\n'          

                if self.export_outputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n')

                if self.barplot is True and self.merge is False:
                    self.create_barplot(f, connector_data, [neuron] , 1, 2 , x_factor = 1, y_factor = -1)
                elif self.barplot is True and self.merge is True and first_neuron is True:
                    self.create_barplot(f, connector_data, [n for n in connector_data] , 1, 2 , x_factor = 1, y_factor = -1)

                ### Add lateral brain shape
                if self.merge is False or first_neuron is True:
                    f.write('\n' + brain_shape_lateral_string + '\n') 
                
                    if self.export_ring_gland is True:
                        f.write('\n' + ring_gland_lateral + '\n')             

                line_to_write = '</g>'
                f.write(line_to_write + '\n \n \n')
            
            if 'Perspective' in self.views_to_export:
                ### Add Connectors from PERSPECTIVE view
                line_to_write = '<g id="%s perspective" transform="translate(%i,%i)">' % (neuron,offsetX_for_persp,offsetY_for_persp)
                f.write(line_to_write + '\n')
                ### Add Neuron's morphology if required
                if self.export_neuron is True:
                    f.write('<g id="neuron">')
                    f.write(neurons_svg_string[neuron]['perspective'])
                    f.write('</g> \n')
                ### Export Inputs from perspective view
                line_to_write = '<g id="Inputs">'                 
                
                for target_treenode in connectors_pre:       
                    for connector in connectors_pre[target_treenode]:                          
                        if self.color_by_input is True or self.color_by_strength is True:
                            #source_neuron = presynaptic_to[neuron][target_treenode][0]
                            source_neuron = connectors_pre[target_treenode][connector]['presynaptic_to']
                            inputs_color_stroke, inputs_color, source_neuron = self.get_treenode_colors(source_neuron, input_color_map, \
                                                                                                        input_weight_map,neuron)
                            source_neurons_list[source_neuron] = input_color_map[source_neuron]
                            
                        elif self.color_by_density is True:
                            inputs_color = density_color_map[connector]
                            
                        if "Perspective-Dorsal" in self.views_to_export:
                            persp_scale_factor = round((y_center-connectors_pre[target_treenode][connector]['coords'][1]) *10,1)  
                            #Attention!: for dorsal view we want to look at it from behind at an angle -> invert X pos  
                            
                            connector_x = round(connectors_pre[target_treenode][connector]['coords'][0]*-10,1) + x_persp_offset * persp_scale_factor
                            connector_y = round(connectors_pre[target_treenode][connector]['coords'][2]*-10,1) + y_persp_offset * persp_scale_factor
                                                                                                                       
                        else:                                                
                            persp_scale_factor = round(connectors_pre[target_treenode][connector]['coords'][1] *10,1)
                            connector_x = round(connectors_pre[target_treenode][connector]['coords'][0]*10,1) + x_persp_offset * persp_scale_factor
                            connector_y = round(connectors_pre[target_treenode][connector]['coords'][2]*-10,1) + y_persp_offset * persp_scale_factor 
                        
                        #If color by input is true, also use different shapes
                        if self.color_by_input is True:                                 
                            if input_shape_map[source_neuron] != 'circle':          
                                shape_temp = ''
                                for node in input_shape_map[source_neuron]:
                                    shape_temp += str(node[0]+connector_x) + ',' + str(node[1]+connector_y) + ' '
                                line_to_write +='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.export_as == 'Arrows' or self.export_as == 'Lines':
                            line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-2,connector_y,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            if self.export_as == 'Arrows':
                                line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                                % ( connector_x-1,connector_y,
                                                    connector_x-3,connector_y+1,
                                                    connector_x-3,connector_y-1,                                                
                                                    str(inputs_color)
                                                   )
                        elif self.export_as == 'Circles':                 
                            line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        line_to_write += '\n'

                if self.export_inputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n') 

                ### Export Outputs from perspective view
                line_to_write = '<g id="Outputs">'                                         
                
                for connector in connectors_post:                    
                    if self.color_by_density is True:
                        outputs_color = density_color_map[connector]
                    #connector_x = round(connectors_post[connector]['coords'][1] * 10,1)
                    #connector_y = round(connectors_post[connector]['coords'][2] * - 10,1)
                    if self.scale_outputs is True:
                        radius = basic_radius * (0.8 + connectors_weight[connector]/5) #connectors with 5 targets will be double the size
                    else:
                        radius = basic_radius
                    
                    if "Perspective-Dorsal" in self.views_to_export:
                        persp_scale_factor = round((y_center-connectors_post[connector]['coords'][1]) *10,1)  
                        #Attention!: for dorsal view we want to look at it from behind at an angle -> invert X pos
                        connector_x = round(connectors_post[connector]['coords'][0]*-10,1) + x_persp_offset * persp_scale_factor
                        connector_y = round(connectors_post[connector]['coords'][2]*-10,1) + y_persp_offset * persp_scale_factor                                                                                             
                    else:                                                
                        persp_scale_factor = round(connectors_post[connector]['coords'][1] *10,1)
                        connector_x = round(connectors_post[connector]['coords'][0]*10,1) + x_persp_offset * persp_scale_factor
                        connector_y = round(connectors_post[connector]['coords'][2]*-10,1) + y_persp_offset * persp_scale_factor  
                    
                    if self.export_as == 'Arrows' or self.export_as == 'Lines':
                        line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x-9,connector_y,
                                            connector_x-2,connector_y,
                                            str(outputs_color),str(radius/3)
                                           )
                        if self.export_as == 'Arrows':
                            line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-8,connector_y+1,
                                                connector_x-8,connector_y-1,                                                
                                                str(outputs_color)
                                               ) 
                    elif self.export_as == 'Circles':
                        line_to_write += '<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                        % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(outputs_width_stroke))
                    line_to_write += '\n'

                if self.export_outputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n')    
                
                line_to_write = '</g>'
                f.write(line_to_write + '\n \n \n')
            
            
            if 'Top' in self.views_to_export:
                ### Add Connectors from TOP view
                line_to_write = '<g id="%s top" transform="translate(%i,%i)">' % (neuron,offsetX_for_top,offsetY_for_top)
                f.write(line_to_write + '\n')            

                connectors_pre = connector_data[neuron][1]
                connectors_post = connector_data[neuron][2]
                connectors_weight = connector_data[neuron][0]
                ### Add Neuron's morphology if required
                if self.export_neuron is True:
                    f.write('<g id="neuron">')
                    f.write(neurons_svg_string[neuron]['top'])
                    f.write('</g> \n')
                ### Export Inputs from top view
                line_to_write = '<g id="Inputs">'                 
                
                for target_treenode in connectors_pre:
                    for connector in connectors_pre[target_treenode]: 
                        if self.color_by_input is True or self.color_by_strength is True:
                            #source_neuron = presynaptic_to[neuron][target_treenode][0]
                            source_neuron = connectors_pre[target_treenode][connector]['presynaptic_to']
                            inputs_color_stroke, inputs_color, source_neuron = self.get_treenode_colors(source_neuron, input_color_map, input_weight_map,neuron)
                            source_neurons_list[source_neuron] = input_color_map[source_neuron]

                        elif self.color_by_density is True:
                            inputs_color = density_color_map[connector]                              
                                            
                        connector_x = round(connectors_pre[target_treenode][connector]['coords'][0] * 10,1)
                        connector_y = round(connectors_pre[target_treenode][connector]['coords'][1] * - 10,1)                                
                        #If color by input is true, also use different shapes
                        if self.color_by_input is True:                                 
                            if input_shape_map[source_neuron] != 'circle':          
                                shape_temp = ''
                                for node in input_shape_map[source_neuron]:
                                    shape_temp += str(node[0]+connector_x) + ',' + str(node[1]+connector_y) + ' '
                                line_to_write +='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.export_as == 'Arrows' or self.export_as == 'Lines':
                            line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-2,connector_y,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            if self.export_as == 'Arrows':
                                line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                                % ( connector_x-1,connector_y,
                                                    connector_x-3,connector_y+1,
                                                    connector_x-3,connector_y-1,                                                
                                                    str(inputs_color)
                                                   )                              
                        elif self.export_as == 'Circles':                 
                            line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        line_to_write += '\n'
                            
                if self.export_inputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n')

                ### Export Outputs from top view
                line_to_write = '<g id="Outputs">'                                         
                
                for connector in connectors_post:
                    connector_x = round(connectors_post[connector]['coords'][0] * 10,1)
                    connector_y = round(connectors_post[connector]['coords'][1] * - 10,1)
                    
                    if self.color_by_density is True:
                        outputs_color = density_color_map[connector]
                    
                    if self.scale_outputs is True:
                        radius = basic_radius * (0.8 + connectors_weight[connector]/5) #connectors with 5 targets will be double the size
                    else:
                        radius = basic_radius
                        
                    if self.export_as == 'Arrows' or self.export_as == 'Lines':
                        line_to_write +='<path d="M%f,%f L%f,%f" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x-9,connector_y,
                                            connector_x-2,connector_y,
                                            str(outputs_color),str(radius/3)
                                           )
                        if self.export_as == 'Arrows':
                            line_to_write +='<polygon points="%f,%f %f,%f %f,%f" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-8,connector_y+1,
                                                connector_x-8,connector_y-1,                                                
                                                str(outputs_color)
                                               ) 
                    elif self.export_as == 'Circles':                    
                        line_to_write +='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(inputs_width_stroke))
                    line_to_write += '\n'
                    
                if self.export_outputs is True:
                    line_to_write += '</g>' 
                    f.write(line_to_write + '\n') 

                if self.barplot is True and self.merge is False:
                    self.create_barplot(f, connector_data, [neuron] , 0, 1 , x_factor = 1, y_factor = -1)
                elif self.barplot is True and self.merge is True and first_neuron is True:
                    self.create_barplot(f, connector_data, [n for n in connector_data] , 0, 1 , x_factor = 1, y_factor = -1)
                
                ### Add top brain shape
                if self.merge is False or first_neuron is True:
                    f.write('\n' + brain_shape_top_string + '\n') 
                
                    if self.export_ring_gland is True:
                        f.write('\n' + ring_gland_top + '\n')             

            offsetY_forLegend = -150
            ### Create legend for neurons if merged
            if self.merge is True and self.color_by_input is False and self.color_by_strength is False and self.add_legend is True:
                line_to_write ='\n <g> \n <text x="150" y = "%s" font-size="8"> \n %s \n </text> \n' \
                                % (str(offsetY_forMergeLegend+5), str(self.neuron_names[int(neuron)]) + ' #' + neuron)                
                f.write(line_to_write + '\n')
                  
                if self.export_outputs is True:                
                    line_to_write ='<circle cx="133" cy="%s" r="2" fill="rgb%s" stroke="black" stroke-width="0.1"  />' \
                                    % (str(offsetY_forMergeLegend), str(outputs_color))
                    f.write(line_to_write + '\n')  
        
                if self.export_inputs is True:        
                    line_to_write ='<circle cx="140" cy="%s" r="2" fill="rgb%s" stroke="black" stroke-width="0.1"  />' \
                                    % (str(offsetY_forMergeLegend), str(inputs_color))
                    f.write(line_to_write + '\n')  
                
                f.write('</g> \n \n')
                offsetY_forMergeLegend += 10      
                
            elif self.merge is False:
                f.write('\n <g> \n <text x="10" y = "140" font-size="8">\n' + str(self.neuron_names[int(neuron)]) + ' #' + neuron + '\n</text> \n </g> \n')
                
            ### Add density info
            if self.color_by_density is True:
               f.write('\n <g id="density info"> \n <text x="15" y = "150" font-size="6">\n Density data - total nodes: ' + str(len(density_data)) + ' max density: ' + str(max_density) + '/' + str(round(self.proximity_radius_for_density,2)) + ' radius \n </text> \n </g> \n')

            ### Close remaining groups (3x)
            line_to_write = '</g> \n </g> \n \n </g> \n \n \n' 
            f.write(line_to_write) 
            offsetX += offsetIncrease
            ### Set first_neuron to false after first run (to prevent creation of a second brain's outline)
            first_neuron = False  

        #if self.merge is True or self.all_neurons is False: 
        if self.color_by_input is True or self.color_by_strength is True:
            self.create_legends(f, input_weight_map, input_shape_map , offsetX , source_neurons_list, connector_data, max_values,neuron_for_legend= neuron)

        ### Finish svg file with footer        
        f.write(svg_end)
        f.close()
        print('Export finished')
        self.report({'INFO'},'Export finished! See console for details')
        
        return {'FINISHED'}

    def create_barplot(self, f, connector_data , neurons_to_plot , x_coord, y_coord, x_factor = 1, y_factor = -1):
        """
        Creates Barplot for given svg based on distribution of 
        """

        #Bin width is in 1/1000 nm = um
        bin_width = 2
        scale_factor = 1

        hist_data = { e : {'x_pre':[],'y_pre':[],'x_post':[],'y_post':[]} for e in neurons_to_plot }        

        #Collect data first:
        for e in neurons_to_plot:
            connectors_pre = connector_data[e][1]
            connectors_post = connector_data[e][2]

            for tn in connectors_pre:
                for c in connectors_pre[tn]:                    
                    hist_data[e]['x_pre'].append( round(connectors_pre[tn][c]['coords'][x_coord] * 10 * x_factor, 1) ) 
                    hist_data[e]['y_pre'].append( round(connectors_pre[tn][c]['coords'][y_coord] * 10 * y_factor, 1) ) 

            for c in connectors_post:
                hist_data[e]['x_post'].append( round(connectors_post[c]['coords'][x_coord] * 10 * x_factor, 1) )
                hist_data[e]['y_post'].append( round(connectors_post[c]['coords'][y_coord] * 10 * y_factor, 1) )

        all_x_pre = [e for item in hist_data for e in hist_data[item]['x_pre'] ]
        all_y_pre = [e for item in hist_data for e in hist_data[item]['y_pre'] ]
        all_x_post = [e for item in hist_data for e in hist_data[item]['x_post'] ]
        all_y_post = [e for item in hist_data for e in hist_data[item]['y_post'] ]

        #First get min and max values and bin numbers over all neurons 
        all_max_x_pre = max(all_x_pre+[0])
        all_max_y_pre = max(all_y_pre+[0])
        all_max_x_post = max(all_x_post+[0])
        all_max_y_post = max(all_y_post+[0])

        all_min_x_pre = min(all_x_pre + [ max(all_x_pre + [0] ) ] )
        all_min_y_pre = min(all_y_pre + [ max(all_y_pre + [0] ) ] )
        all_min_x_post = min(all_x_post + [ max(all_x_post + [0] ) ] )
        all_min_y_post = min(all_y_post + [ max(all_y_post + [0] ) ] ) 


        #Everthing starts with 
        bin_sequences = {'x_pre': list ( np.arange( all_min_x_pre, all_max_x_pre, bin_width ) ),
                        'y_pre': list ( np.arange( all_min_y_pre, all_max_y_pre, bin_width ) ),
                        'x_post': list ( np.arange( all_min_x_post, all_max_x_post, bin_width ) ),
                        'y_post': list ( np.arange( all_min_y_post, all_max_y_post, bin_width ) )
                        }

        #Create Histograms
        histograms = { e : {} for e in neurons_to_plot }
        for e in neurons_to_plot:
            histograms[e]['x_pre'] , bin_edges_x_pre = np.histogram( hist_data[e]['x_pre'], bin_sequences['x_pre'] )
            histograms[e]['y_pre'] , bin_edges_y_pre = np.histogram( hist_data[e]['y_pre'], bin_sequences['y_pre'] )
            histograms[e]['x_post'] , bin_edges_x_post = np.histogram( hist_data[e]['x_post'], bin_sequences['x_post'] )
            histograms[e]['y_post'] , bin_edges_y_post = np.histogram( hist_data[e]['y_post'], bin_sequences['y_post'] )

        #Now calculate mean and stdevs over all neurons
        means = {}
        stdevs = {}     
        variances = {}   
        stderror = {}
        for d in ['x_pre','y_pre','x_post','y_post']:
            means[d] = []
            stdevs[d] = []
            variances[d] = []
            stderror[d] = []
            #print([histograms[n][d] for n in neurons_to_plot],bin_sequences[d])
            for i in range ( len( bin_sequences[d] ) - 1 ):                
                #conversion to int from numpy.int32 is important because statistics.stdev fails otherwise
                v = [ int ( histograms[n][d][i] ) for n in neurons_to_plot ]                
                means[d].append ( sum ( v ) / len ( v ) )
                #print(d,i,v,means[d],type(v[0]))
                if len ( neurons_to_plot ) > 1:
                    stdevs[d].append( statistics.stdev ( v ) )  
                    variances[d].append( statistics.pvariance ( v ) )
                    stderror[d].append( math.sqrt( statistics.pvariance ( v ) ) )

        #!!!!!!!!!!!
        #This defines which statistical value to use:
        #Keep in mind that stdev is probably the best parameter to use!
        stats = stdevs

        #Now start creating svg:            
        line_to_write = '<g id="Barplot" transform="translate(0,0)">' 
        f.write(line_to_write + '\n')

        f.write('<g id="x-axis">')
        #write horizontal barplot
        for e,b in enumerate ( means['x_pre'] ):
            #Inputs
            f.write( '<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,0,255)" stroke-width="0"/> \n' \
                    % ( bin_sequences['x_pre'][e], 0,
                        bin_width,
                        b * scale_factor
                        )
                    )

        #Error bar
        if len( neurons_to_plot ) > 1:
            for e,b in enumerate ( means['x_pre'] ):
                if stats['x_pre'][e] != 0:
                    f.write('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:0.25" /> \n' \
                        % ( bin_sequences['x_pre'][e] + 1/2 * bin_width, b * scale_factor + stats['x_pre'][e] * scale_factor,
                            bin_sequences['x_pre'][e] + 1/2 * bin_width, b * scale_factor - stats['x_pre'][e] * scale_factor
                            ) 
                        )

        for e,b in enumerate(means['x_post']):
            #Outputs
            f.write( '<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(255,0,0)" stroke-width="0"/> \n' \
                    % ( bin_sequences['x_post'][e], 0,
                        bin_width,
                        -b * scale_factor
                        )
                    )

        #Error bar
        if len( neurons_to_plot ) > 1:
            for e,b in enumerate(means['x_post']):
                if stats['x_post'][e] != 0:
                    f.write('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:0.25" /> \n' \
                        % ( bin_sequences['x_post'][e] + 1/2 * bin_width, -b * scale_factor + stats['x_post'][e] * scale_factor,
                            bin_sequences['x_post'][e] + 1/2 * bin_width, -b * scale_factor - stats['x_post'][e] * scale_factor
                            ) 
                        ) 

        #horizontal line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( min([all_min_x_pre, all_min_x_post]) , 0,
                            max([all_max_x_pre, all_max_x_post]) , 0                                       
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')

        f.write('<g id="y-axis">')

        #write vertical barplot
        for e,b in enumerate(means['y_pre']):
            #Inputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,0,255)" stroke-width="0"/> \n' \
                    % ( 0 , bin_sequences['y_pre'][e],
                        b * scale_factor,
                        bin_width
                        )
                    )

        #Error bar 
        if len( neurons_to_plot ) > 1: 
            for e,b in enumerate(means['y_pre']):
                if stats['y_pre'][e] != 0:
                    f.write('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:0.25" /> \n' \
                        % ( b * scale_factor + stats['y_pre'][e] * scale_factor, bin_sequences['y_pre'][e] + 1/2 * bin_width, 
                            b * scale_factor - stats['y_pre'][e] * scale_factor, bin_sequences['y_pre'][e] + 1/2 * bin_width
                            ) 
                        )

        for e,b in enumerate(means['y_post']):
            #Outputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(255,0,0)" stroke-width="0"/> \n' \
                    % ( 0, bin_sequences['y_post'][e],
                        -b * scale_factor,
                        bin_width
                        )
                    )
        #Error bar
        if len( neurons_to_plot ) > 1:
            for e,b in enumerate(means['y_post']):
                if stats['y_post'][e] != 0:
                    f.write('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:0.25" /> \n' \
                        % ( -b * scale_factor + stats['y_post'][e] * scale_factor, bin_sequences['y_post'][e] + 1/2 * bin_width, 
                            -b * scale_factor - stats['y_post'][e] * scale_factor, bin_sequences['y_post'][e] + 1/2 * bin_width
                            ) 
                        )

        #vertical line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( 0 , min([all_min_y_pre, all_min_y_post]),
                            0 , max([all_max_y_pre, all_max_y_post]) 
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')

        #Bin size bar
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( max([all_max_x_pre, all_max_x_post]) + 10 , 0 ,
                            max([all_max_x_pre, all_max_x_post]) + 10 + bin_width , 0                                       
                           )
        line_to_write += '<text x="%i" y = "%i" font-size="5"> \n %s \n </text>' \
                        % ( max([all_max_x_pre,all_max_x_post]) + 10,
                            - 1,
                            str(bin_width) + ' um'

                            )
        f.write(line_to_write + '\n')

        #Axis scale
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( max([all_max_x_pre,all_max_x_post]) + 10 + bin_width, 0 ,
                            max([all_max_x_pre,all_max_x_post]) + 10 + bin_width, 5                                       
                           )
        line_to_write += '<text x="%i" y = "%f" font-size="5"> \n %s \n </text>' \
                        % ( max([all_max_x_pre,all_max_x_post]) + 12 + bin_width, 
                            4,                                        
                            str(5 / scale_factor) + ' synapses'
                            )
        f.write(line_to_write + '\n')   


        line_to_write = '</g>' 
        f.write(line_to_write + '\n')

        """

        line_to_write = '<g id="Barplot" transform="translate(0,0)">' 
        f.write(line_to_write + '\n')
        barplot_y_data_pre = []
        barplot_x_data_pre = []
        barplot_y_data_post = []
        barplot_x_data_post = []

        #Gather coordinates of pre and postsynaptic connectors
        for tn in connectors_pre:
            for c in connectors_pre[tn]:                            
                barplot_y_data_pre.append( round(connectors_pre[tn][c]['coords'][y_coord] * 10 * y_factor, 1) )
                barplot_x_data_pre.append( round(connectors_pre[tn][c]['coords'][x_coord] * 10 * x_factor, 1) )

        for c in connectors_post:
            barplot_y_data_post.append( round(connectors_post[c]['coords'][y_coord] * 10 * y_factor, 1) )
            barplot_x_data_post.append( round(connectors_post[c]['coords'][x_coord] * 10 * x_factor, 1) )        

        #Make sure that there is at least 1 bin!
        # max(..._data_...) will fail if array is empty!
        max_barplot_x_data_pre = max(barplot_x_data_pre+[0])
        max_barplot_y_data_pre = max(barplot_y_data_pre+[0])
        max_barplot_x_data_post = max(barplot_x_data_post+[0])
        max_barplot_y_data_post = max(barplot_y_data_post+[0])

        min_barplot_x_data_pre = min(barplot_x_data_pre + [ max(barplot_x_data_pre + [0] ) ] )
        min_barplot_y_data_pre = min(barplot_y_data_pre + [ max(barplot_y_data_pre + [0] ) ] )
        min_barplot_x_data_post = min(barplot_x_data_post + [ max(barplot_x_data_post + [0] ) ] )
        min_barplot_y_data_post = min(barplot_y_data_post + [ max(barplot_y_data_post + [0] ) ] ) 
        
        x_bins_pre =  max([ int ( ( max_barplot_x_data_pre - min_barplot_x_data_pre ) / bin_width ) ,1])
        y_bins_pre =  max([ int ( ( max_barplot_y_data_pre - min_barplot_x_data_pre ) / bin_width ) ,1])
        x_bins_post = max([ int ( ( max_barplot_x_data_post - min_barplot_y_data_post ) / bin_width ),1])    
        y_bins_post = max([ int ( ( max_barplot_y_data_post - min_barplot_y_data_post ) / bin_width ),1])        
        
        
        hist_x_pre , bin_edges_x_pre = np.histogram( barplot_x_data_pre, x_bins_pre )
        hist_y_pre , bin_edges_y_pre = np.histogram( barplot_y_data_pre, y_bins_pre )
        hist_x_post , bin_edges_x_post = np.histogram( barplot_x_data_post, x_bins_post )
        hist_y_post , bin_edges_y_post = np.histogram( barplot_y_data_post, y_bins_post )

        f.write('<g id="x-axis">')

        #write horizontal barplot
        for e,b in enumerate(hist_x_pre):
            #Inputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,0,255)" stroke-width="0"/> \n' \
                    % ( bin_edges_x_pre[e], 0,
                        bin_width,
                        b * scale_factor
                        )
                    )
        for e,b in enumerate(hist_x_post):
            #Outputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(255,0,0)" stroke-width="0"/> \n' \
                    % ( bin_edges_x_post[e], 0,
                        bin_width,
                        -b * scale_factor
                        )
                    )        

        #horizontal line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( min([min_barplot_x_data_pre,min_barplot_x_data_post]) , 0,
                            max([max_barplot_x_data_pre,max_barplot_x_data_post]) , 0                                       
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')
        
        f.write('<g id="y-axis">')

        #write vertical barplot
        for e,b in enumerate(hist_y_pre):
            #Inputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,0,255)" stroke-width="0"/> \n' \
                    % ( 0, bin_edges_y_pre[e],
                        b * scale_factor,
                        bin_width
                        )
                    )
        for e,b in enumerate(hist_y_post):
            #Outputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(255,0,0)" stroke-width="0"/> \n' \
                    % ( 0, bin_edges_y_post[e],
                        -b * scale_factor,
                        bin_width
                        )
                    )

        #vertical line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( 0 , min([min_barplot_y_data_pre,min_barplot_y_data_post]),
                            0 , max([max_barplot_y_data_pre,max_barplot_y_data_post]) 
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')

        #Bin size bar
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( max([max_barplot_x_data_pre,max_barplot_x_data_post]) + 10 , 0 ,
                            max([max_barplot_x_data_pre,max_barplot_x_data_post]) + 10 + bin_width , 0                                       
                           )
        line_to_write += '<text x="%i" y = "%i" font-size="5"> \n %s \n </text>' \
                        % ( max([max_barplot_x_data_pre,max_barplot_x_data_post]) + 10,
                            - 1,
                            str(bin_width) + ' um'

                            )
        f.write(line_to_write + '\n')

        #Axis scale
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( max([max_barplot_x_data_pre,max_barplot_x_data_post]) + 10 + bin_width, 0 ,
                            max([max_barplot_x_data_pre,max_barplot_x_data_post]) + 10 + bin_width, 5                                       
                           )
        line_to_write += '<text x="%i" y = "%f" font-size="5"> \n %s \n </text>' \
                        % ( max([max_barplot_x_data_pre,max_barplot_x_data_post]) + 12 + bin_width, 
                            4,                                        
                            str(5 / scale_factor) + ' synapses'
                            )
        f.write(line_to_write + '\n')   


        line_to_write = '</g>' 
        f.write(line_to_write + '\n')
        """
    
    def create_legends (self, f, input_weight_map, input_shape_map ,x_pos = 0,  source_neurons_list = [], connector_data = [], max_values = [], neuron_for_legend = 'none' ):        
        offsetX = 0
        line_offsetY = 0
        print('Creating legend')    
        
        if self.color_by_input is True or self.color_by_strength is True:
            #print('%s different inputs for neuron %s found!' % (str(len(source_neurons_list)), str(self.neuron_names[neuron])))
            line_to_write ='<g id="Legend" transform="translate(%i,-150)">' % x_pos 
            f.write(line_to_write + '\n')
            
        if self.filter_connectors:
            line_to_write ='\n <text x="40" y = "%i" font-size="2"> \n Inputs/Outputs filtered by: %s \n </text> \n' \
                                % ((line_offsetY-5),self.filter_connectors)                
            f.write(line_to_write + '\n')    
            
        if self.color_by_input is True:
            line_to_write ='<g id="Upstream Neurons">' 
            f.write(line_to_write + '\n')
            
            for source in source_neurons_list:
                source_color = source_neurons_list[source]
                source_shape = input_shape_map[source]
                
                if self.merge is True or self.all_neurons is True:
                    ### Retrieve # of Synapses of Source Neuron Onto every Target Neuron
                    weights_string = '  '
                    for neuron in connector_data:
                        #print('Searching weight of source %s for neuron %s' % (source,neuron))
                        if source in input_weight_map[neuron]:
                            weights_string += str(input_weight_map[neuron][source]['connections']) + '/'
                        else:
                            weights_string += '0' + '/'
                else:                    
                    weights_string = ' ('+ str(input_weight_map[neuron_for_legend][source]['connections']) + ')'
                
                if source is not None:                    
                    source_tag = str(self.neuron_names[source]) + weights_string
                else:
                    source_tag = 'No Presynaptic Skeleton Found' + weights_string
                    
                #print(source, source_tag)
                
                line_to_write ='\n <text x="48" y = "%i" font-size="1"> \n %s - #%s \n </text> \n' \
                                % ((line_offsetY+1),source_tag, str(source))          
                f.write(line_to_write + '\n')
                
                if source_shape != 'circle':          
                    shape_temp = ''
                    for node in source_shape:
                        shape_temp += str(node[0]+45) + ',' + str(node[1]+line_offsetY) + ' '
                    line_to_write='<polygon points="%s" fill="rgb%s" stroke="black" stroke-width="0.1"  />' \
                                % (str(shape_temp),str(source_color))                                                        
                else:
                    line_to_write ='<circle cx="45" cy="%i" r="%s" fill="rgb%s" stroke="black" stroke-width="0.1"  />' \
                                % (line_offsetY,str(self.basic_radius),str(source_color))
                
                f.write(line_to_write + '\n')
                line_offsetY += 2
                
            line_to_write ='\n </g>'          
            f.write(line_to_write + '\n')
            
        if self.color_by_strength is True and self.merge is False:
            ### Create legend for source neurons weight
            line_to_write = '<g id = "Scale">'                
            f.write(line_to_write + '\n')
            
            input_scale_string = '<defs> \n <linearGradient id="MyGradient" x1="0%" y1="0%" x2="0%" y2="100%"> \n' \
                                 '<stop offset="5%" stop-color="rgb(255,0,0)" /> \n <stop offset="50%" stop-color="rgb(255,255,0)" /> \n' \
                                 '<stop offset="95%" stop-color="rgb(0,255,0)" /> \n </linearGradient> \n </defs> \n \n' \
                                 '<!-- The rectangle is filled using a linear gradient paint server --> \n' \
                                 '<rect fill="url(#MyGradient)" stroke="black" stroke-width="0" \n' \
                                 'x="' + str(125 + offsetX) + '" y="-150" width="4" height="250" /> \n'  

            line_to_write = input_scale_string
            f.write(line_to_write + '\n')
            line_to_write ='<text x="115" y = "-150" font-size="8"> \n %s \n </text> \n' % (str(max(max_values[neuron])))                
            f.write(line_to_write + '\n')
            line_to_write ='<text x="115" y = "100" font-size="8"> \n 1 \n </text> \n' 
            f.write(line_to_write + '\n')
            line_to_write = '</g> ' 
            f.write(line_to_write + '\n')
            
        if self.color_by_strength is True and self.merge is True:
            print('ERROR: Cannot create scale for synaptic strength if merged: heterogenous data. Do not merge data.')
            self.report({'ERROR'},'Error(s) occurred: see console')
            
        return{'FINISHED'}    
    

    def get_treenode_colors(self, source_neuron, input_color_map, input_weight_map, neuron):
        if self.color_by_input is True and self.color_by_strength is True:
            ### Attention: As the script is now - only the first input to a SINGLE treenode will be plotted
            #source_neuron = presynaptic_to[neuron][target_treenode][0]
    
            inputs_color_stroke = input_color_map[source_neuron]  
            inputs_color = input_weight_map[neuron][source_neuron]['color']  
            
            ### Add source to list for later legend                    
            #source_neurons_list[source_neuron] = input_color_map[source_neuron]                    
    
        elif self.color_by_strength is False:
            #source_neuron = presynaptic_to[neuron][target_treenode][0]
    
            inputs_color_stroke = (0,0,0)
            inputs_color = input_color_map[source_neuron]                      
    
            ### Add source to list for later legend
            #source_neurons_list[source_neuron] = input_color_map[source_neuron]
            
        elif self.color_by_input is False:
            #source_neuron = presynaptic_to[neuron][target_treenode][0]
    
            inputs_color_stroke = (0,0,0)
            inputs_color = input_weight_map[neuron][source_neuron]['color']                      
    
            ### Add source to list for later legend
            #source_neurons_list[source_neuron] = input_color_map[source_neuron]
            
        return inputs_color_stroke, inputs_color, source_neuron
    
    
    def check_ancestry(self, neurons_to_check):        
        count = 1
        skids_to_check = []
        
        for neuron in neurons_to_check:            
            if neuron not in self.neuron_names and neuron != None:
                skids_to_check.append(neuron)
            elif neuron not in self.neuron_names:
                print('ERROR: Invalid Neuron Name found: %s' % neuron )
                self.report({'ERROR'},'Error(s) occurred: see console')
        
        #print('Checking Skeleton IDs:')
        #print(skids_to_check)
        skids = []
        names = []
        new_names = get_neuronnames(skids_to_check)
        
        for entry in new_names:
            self.neuron_names[int(entry)] = new_names[entry]   
            
    def get_connectivity(self,neurons,use_upstream=True,use_downstream=True):
        """Counts connections of neurons to/from filter set by self.color_by_connections """
        print('Searching partners for connections to: ', self.color_by_connections)
        
        connection_count = {}        
        
        remote_connectivity_url = remote_instance.get_connectivity_url( project_id )  
        connectivity_post = {}
        #connectivity_post['threshold'] = 1
        connectivity_post['boolean_op'] = 'OR'                
        for i in range(len(neurons)):
            tag = 'source_skeleton_ids[%i]' % i
            connectivity_post[tag] = neurons[i]
            connection_count[neurons[i]] = 0
                
        print( "Retrieving Partners for %i neurons..." % len(neurons))
        connectivity_data = []
        connectivity_data = remote_instance.fetch( remote_connectivity_url , connectivity_post ) 
        print("Done.")      
        
        #Retrieve neuron names for filtering
        to_retrieve = list(connectivity_data['outgoing'])
        to_retrieve += list(connectivity_data['incoming'])
        
        neuron_names = get_neuronnames(list(set(to_retrieve)))
        
        neurons_included = []
        if use_upstream is True:
            for skid in connectivity_data['incoming']:
                if self.color_by_connections.lower() in neuron_names[skid].lower():
                    neurons_included.append(neuron_names[skid])
                    for entry in connectivity_data['incoming'][skid]['skids']:
                        connection_count[entry] += sum(connectivity_data['incoming'][skid]['skids'][entry])
        if use_downstream is True:
            for skid in connectivity_data['outgoing']:
                if self.color_by_connections.lower() in neuron_names[skid].lower():
                    neurons_included.append(neuron_names[skid])                    
                    for entry in connectivity_data['outgoing'][skid]['skids']:
                        connection_count[entry] += sum(connectivity_data['outgoing'][skid]['skids'][entry])
                        
        print('Neurons included after filtering:',neurons_included)
        print('Connection_count:',connection_count)
                        
        return connection_count
                


    def create_svg_for_neuron(self,neurons_to_export):
        neurons_svg_string = {}
        basic_radius = 1
        line_width = 0.35
                
        if "Perspective-Dorsal" in self.views_to_export:
            #For dorsal perspective change offsets:
            y_persp_offset = -1 * self.x_persp_offset
            x_persp_offset = 0            
            #y_center sets the pivot along y axis (0-25) -> all this does is move the object along y axis, does NOT change perspective
            y_center = 5  
        else:
            x_persp_offset = self.x_persp_offset
            y_persp_offset = self.y_persp_offset
    
        for neuron in neurons_to_export:
            skid = re.search('#(.*?) -',neuron.name).group(1)
            neurons_svg_string[skid] = {}
            neurons_svg_string[skid]['front'] = ''
            neurons_svg_string[skid]['top'] = ''
            neurons_svg_string[skid]['lateral'] = ''
            neurons_svg_string[skid]['perspective'] = ''
            
            ### Create List of Lines
            polyline_front = []
            polyline_top = []
            polyline_lateral = []
            polyline_perspective = []
            soma_found = False
            
            ## ONLY curves starting with a # will be exported
            if re.search('#.*',neuron.name) and neuron.type == 'CURVE':
    
                ### Standard color: light grey
                color = 'rgb' + str((160, 160, 160)) 
    
                ### File Lists of Lines
                for spline in neuron.data.splines:
                    polyline_front_temp = ''
                    polyline_top_temp = ''
                    polyline_lateral_temp = ''
                    polyline_persp_temp = ''
    
                    ### Go from first point to the second last
                    for source in range((len(spline.points))): 
                        target = source + 1;
    
                        polyline_front_temp += str(round(spline.points[source].co[0] *10,1)) +','+ str(round(spline.points[source].co[2]*-10,1)) + ' '
                        polyline_top_temp += str(round(spline.points[source].co[0] *10,1)) +','+ str(round(spline.points[source].co[1]*-10,1)) + ' '
                        polyline_lateral_temp += str(round(spline.points[source].co[1] *10,1)) +','+ str(round(spline.points[source].co[2]*-10,1)) + ' '
                        
                        if "Perspective-Dorsal" in self.views_to_export:
                            persp_scale_factor = round((y_center-spline.points[source].co[1]) *10,1)  
                            #Attention!: for dorsal view we want to look at it from behind at an angle -> invert X pos
                            polyline_persp_temp += str(round(spline.points[source].co[0] * -10,1) + x_persp_offset * persp_scale_factor) 
                            polyline_persp_temp += ','+ str(round(spline.points[source].co[2]*-10,1)+ y_persp_offset * persp_scale_factor) + ' '
                            
                        else:                                                
                            persp_scale_factor = round(spline.points[source].co[1] *10,1)
                            polyline_persp_temp += str(round(spline.points[source].co[0] *10,1) + x_persp_offset * persp_scale_factor) 
                            polyline_persp_temp += ','+ str(round(spline.points[source].co[2]*-10,1)+ y_persp_offset * persp_scale_factor) + ' '
                            

            
                    polyline_front.append(polyline_front_temp) 
                    polyline_top.append(polyline_top_temp)  
                    polyline_lateral.append(polyline_lateral_temp) 
                    polyline_perspective.append(polyline_persp_temp) 
                    
                ### Find soma            
                search_string = 'Soma of ' + neuron.name[1:7] + '.*'
                
                for soma in bpy.data.objects:
                    if re.search(search_string,soma.name):
                        print('Soma of %s found' % neuron.name)
                        soma_pos = soma.location
                        soma_radius = soma.dimensions[0]/2 * 10
                        soma_found = True
                        break
        
                ### Create front svg string            
                svg_neuron_front = ''
                for i in range(len(polyline_front)):        
                    svg_neuron_front += '<polyline points="' + polyline_front[i] + '" \n' \
                                        'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/> \n' \
                                        % (str(color), str(line_width))
    
                if soma_found is True:
                    svg_neuron_front += '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  /> \n' \
                                        % (str(round(soma_pos[0]*10,1)),str(round(soma_pos[2]*-10,1)), str(basic_radius*soma_radius), \
                                        str(color), str(color))
    
                neurons_svg_string[skid]['front'] = svg_neuron_front
                
                ### Create top svg string      
                svg_neuron_top = ''            
                for i in range(len(polyline_top)):    
                    svg_neuron_top += '<polyline points="' + polyline_top[i] + '" \n' \
                                      'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/> \n' \
                                      % (str(color),str(line_width))
    
                if soma_found is True:
                    svg_neuron_top += '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  /> \n' \
                                        % (str(round(soma_pos[0]*10,1)),str(round(soma_pos[1]*-10,1)), str(basic_radius), \
                                        str(color), str(color))
    
                neurons_svg_string[skid]['top'] = svg_neuron_top                
                
                ### Create lateral svg string  
                svg_neuron_lateral = ''                          
                for i in range(len(polyline_lateral)):    
                    svg_neuron_lateral += '<polyline points="' + polyline_lateral[i] + '"\n' \
                                          'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/> \n' \
                                           % (str(color),str(line_width))
    
                if soma_found is True:
                    svg_neuron_lateral += '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  /> \n' \
                                          % (str(round(soma_pos[1]*10,1)),str(round(soma_pos[2]*-10,1)), str(basic_radius*soma_radius), \
                                          str(color), str(color))
    
                neurons_svg_string[skid]['lateral'] = svg_neuron_lateral        
                
                ### Create perspective svg string  
                svg_neuron_perspective = ''                          
                for i in range(len(polyline_perspective)):    
                    svg_neuron_perspective += '<polyline points="' + polyline_perspective[i] + '"\n' \
                                          'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/> \n' \
                                           % (str(color),str(line_width))
    
                if soma_found is True:
                    if "Perspective-Dorsal" in self.views_to_export:
                        persp_scale_factor = round((y_center-soma_pos[1]) *10,1)  
                        #Attention!: for dorsal view we want to look at it from behind at an angle -> invert X pos
                        x_persp = str(round(soma_pos[0]*-10,1) + x_persp_offset * persp_scale_factor)
                        y_persp = str(round(soma_pos[2]*-10,1) + y_persp_offset * persp_scale_factor)                                                                                             
                    else:                                                
                        persp_scale_factor = round(soma_pos[1] *10,1)
                        x_persp = str(round(soma_pos[0]* 10,1) + x_persp_offset * persp_scale_factor)
                        y_persp = str(round(soma_pos[2]*-10,1) + y_persp_offset * persp_scale_factor)
                    
                    svg_neuron_perspective += '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  /> \n' \
                                          % (str(x_persp),str(y_persp), str(basic_radius*soma_radius), \
                                          str(color), str(color))
    
                neurons_svg_string[skid]['perspective'] = svg_neuron_perspective  
        
        return(neurons_svg_string)


class RetrievePartners(Operator):      
    """Retrieves Partners of either active Neuron or all selected Neurons from CATMAID database"""
    bl_idname = "retrieve.partners"  
    bl_label = "What partners to retrieve?"
    bl_options = {'UNDO'}
    
    which_neurons = EnumProperty(       name = "For which Neuron(s)?", 
                                      items = [('Active','Active','Active'),('Selected','Selected','Selected'),('All','All','All')],
                                      default = 'All',
                                      description = "Choose for which neurons to connectors.")
    #selected = BoolProperty(name="From Selected Neurons?", default = False)   
    inputs = BoolProperty(name="Upstream Partners", default = True)          
    outputs = BoolProperty(name="Downstream Partners", default = True)
    minimum_synapses = IntProperty(name="Synapse Threshold", default = 5)
    over_all_synapses = BoolProperty(name="Apply to total #", default = True,
                                  description = "If checked, synapse threshold applies to sum of synapses over all processed neurons. Incoming/Outgoing processed separately.")
    import_connectors = BoolProperty(   name="Import Connectors", 
                                        default = True,
                                        description = "Imports Connectors (pre-/postsynapses), similarly to 3D Viewer in CATMAID")   
    resampling = IntProperty(name="Resampling Factor", 
                             default = 2, 
                             min = 1, 
                             max = 20,
                             description = "Will reduce number of nodes by given factor n. Root, ends and forks are preserved!") 
    filter_by_annotation = StringProperty(name="Filter by Annotation", 
                                          default = '',
                                          description = 'Case-Sensitive. Must be exact. Separate multiple tags by comma w/o spaces.' )      
    
    truncate_neuron = EnumProperty(name="Truncate Neuron?",
                                   items = (('none','No','Load full neuron'),
                                            ('main_neurite','Main Neurite','Truncate Main Neurite'),
                                            ('strahler_index','Strahler Index','Truncate Based on Strahler index')
                                            ),
                                    default =  "none",
                                    description = "Choose if neuron should be truncated.")
    
    truncate_value = IntProperty(   name="Truncate by Value", 
                                        min=-10,
                                        max=10,
                                        default = 1,
                                        description = "Defines length of truncated neurite or steps in Strahler Index from root node!"
                                    ) 

    #Filter by annotation is case-sensitive and needs to be exact
    interpolate_virtual = BoolProperty( name="Interpolate Virtual Nodes", 
                                        default = False,
                                        description = "If true virtual nodes will be interpolated. Only important if you want the resolution of all neurons to be the same. Will slow down import!")
    make_curve = False

    def execute(self, context):  
        global remote_instance

        to_process = []

        if self.which_neurons == 'Active':
            if bpy.context.active_object.name.startswith('#'):
                to_process.append(object) 
            else:
                print ('ERROR: Active Object not a Neuron')
                self.report({'ERROR'},'Active Object not a Neuron!') 
        elif self.which_neurons == 'Selected':                                   
            for obj in bpy.context.selected_objects:
                if obj.name.startswith('#'):
                    to_process.append(obj)
        elif self.which_neurons == 'All':
            for obj in bpy.data.objects:
                if obj.name.startswith('#'):
                    to_process.append(obj)            
        
        skids = []
        for n in to_process:
            skids.append(re.search('#(.*?) -',n.name).group(1))
        print('Retrieving partners for %i neurons...' % len(skids))
        self.get_partners(skids)
                        
        return {'FINISHED'}  
    
    def get_partners(self, skids):        
        print( "Retrieving Partners..." )
        connectivity_data = retrieve_connectivity (skids, remote_instance)

        if connectivity_data:
            print("Connectivity successfully retrieved")
            self.extract_partners(connectivity_data, self.inputs, self.outputs, self.make_curve)
        else:
            print('No data retrieved') 
        
        
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False    

    def extract_partners (self, connectivity_data, get_inputs, get_outputs, make_curve):
        partners = []
        
        print('%i Inputs detected' % len(connectivity_data['incoming']))
        print('%i Outputs detected' % len(connectivity_data['outgoing']))

        neuron_names = {}
        
        ### Cycle through connectivity data and retrieve skeleton ids
        if get_inputs is True:            
            for entry in connectivity_data['incoming']:
                total_synapses = 0
                for connection in connectivity_data['incoming'][entry]['skids']:
                    total_synapses += connectivity_data['incoming'][entry]['skids'][connection]
                    if self.over_all_synapses is False:
                        if connectivity_data['incoming'][entry]['skids'][connection] >= self.minimum_synapses:
                            partners.append(entry)
                if total_synapses >= self.minimum_synapses and self.over_all_synapses is True:
                    partners.append(entry)                    
                
        if get_outputs is True:            
            for entry in connectivity_data['outgoing']:
                total_synapses = 0
                for connection in connectivity_data['outgoing'][entry]['skids']:
                    total_synapses += connectivity_data['outgoing'][entry]['skids'][connection]
                    if self.over_all_synapses is False:
                        if connectivity_data['outgoing'][entry]['skids'][connection] >= self.minimum_synapses:
                            partners.append(entry)
                if total_synapses >= self.minimum_synapses and self.over_all_synapses is True:
                    partners.append(entry)                     
                    
        neuron_names = get_neuronnames(list(set(partners)))
                
        ### Cycle over partner's skeleton ids and load neurons
        total_number = len(list(set(partners)))
        i = 0
        
        if self.filter_by_annotation:
            annotations = get_annotations_from_list(partners,remote_instance)          
            tags = self.filter_by_annotation.split(',')
                            
        for skid in list(set(partners)):            
            if self.filter_by_annotation:
                tag_found = False
                try:
                    for entry in annotations[skid]:
                        for tag in tags:
                            if entry == tag:
                                tag_found = True
                except:
                    print('WARNING: %s has no annotations - not imported' % skid)
                    annotations[skid] = 'no annotations found'
            else:
                tag_found = True
            
            i += 1
            
            if tag_found == False:
                print('WARNING: Tag not found for %s: %s' % (neuron_names[skid],str(annotations[skid])))
                continue           
                       
            print('Loading above-threshold partner: %s  [%i of %i]' % (neuron_names[skid],i,total_number))           
            
            RetrieveNeuron.add_skeleton(self, skid, neuron_names[skid], self.resampling, self.import_connectors, self.truncate_neuron, self.truncate_value, self.interpolate_virtual)
            
class ColorCreator():
    """Class used to create distinctive colors"""  

    def random_colors (color_count,color_range='RGB'):
        ### Make count_color an even number
        if color_count % 2 != 0:
            color_count += 1
             
        colormap = []
        interval = 2/color_count  
        runs = int(color_count/2)   
       
        ### Create first half with low brightness; second half with high brightness and slightly shifted hue
        if color_range == 'RGB':
            for i in range(runs):
                ### High brightness
                h = interval * i
                s = 1
                v =  1
                hsv = colorsys.hsv_to_rgb(h,s,v)
                colormap.append((int(hsv[0]*255),int(hsv[1]*255),int(hsv[2]*255)))             
                
                ### Lower brightness, but shift hue by half an interval
                h = interval * (i+0.5)
                s = 1
                v =  0.5
                hsv = colorsys.hsv_to_rgb(h,s,v)
                colormap.append((int(hsv[0]*255),int(hsv[1]*255),int(hsv[2]*255)))                       
        elif color_range == 'Grayscale':
            h = 0
            s = 0
            for i in range(color_count):
                v = 1/color_count * i
                hsv = colorsys.hsv_to_rgb(h,s,v)
                colormap.append((int(hsv[0]*255),int(hsv[1]*255),int(hsv[2]*255)))
                

        print(len(colormap),' random colors created')

        return(colormap)   
    

class ShapeCreator:
    """
    Class used to create distinctive shapes for svg export:
    Starts with a triangle -> pentagon -> etc.       
    """  

    def create_shapes (shape_count, size):                     
        shapemap = []   
        
        #Start of with triangle    
        nodes = 3
     
        for i in range(shape_count):
            shape_temp = []
            for k in range(nodes):
                shape_temp.append(ShapeCreator.get_coords_on_circle( size ,  2*math.pi/nodes * k) )
            shapemap.append(shape_temp)
            nodes += 2

        print(len(shapemap),' shapes created')

        return(shapemap)  
    
    def get_coords_on_circle(r,angle):    
        x = round(r * math.cos(angle),3)
        y = round(r * math.sin(angle),3)
        coords=(x,y)
        return coords  
      
    
class CATMAIDtoBlender:
    """Extracts Blender relevant data from data retrieved from CATMAID"""
    
    def extract_nodes (node_data, skid, neuron_name = 'name unknown', resampling = 1, import_connectors = True, truncate_neuron = 'none', truncate_value = 1 , interpolate_virtual = False):
        
        index = 1            
        cellname = skid + ' - ' + neuron_name                
        origin = (0,0,0)
        faces = []  
        XYZcoords = []
        connections = []
        edges = []
        soma_node = None
        soma = (0,0,0,0)
        connectors_post = []
        connectors_pre = []
        child_count = {}   
        nodes_list = {}    
        list_of_childs = {}         
        
        #Truncate object name is necessary 
        if len(cellname) >= 60:
            cellname = cellname[:56] +'...'
            print('WARNING: Object name too long - truncated: ', cellname)
        
        object_name = '#' + cellname     
        
        if object_name in bpy.data.objects:
            print('WARNING: Neuron %s already exists!' % cellname)
            return{'FINISHED'}
        
        print('Reading node data..')    
        #print(node_data[0])           
        
        for entry in node_data[0]:
            ### entry = [treenode_id, parent_treenode_id, creator , X, Y, Z, radius, confidence]
            ### Find and convert CATMAID coordinates to Blender
            X = float(entry[3])/10000
            Y = float(entry[4])/-10000
            Z = float(entry[5])/10000
            ### Z-axis in Blender is Y-axis in CATMAID!
            XYZcoords.append((X,Z,Y))
            
            if entry[0] not in nodes_list:                
                nodes_list[entry[0]] = (X,Z,Y)
                ### Polylines need 4 coords (don't know what the fourth does)
            
            if entry[1] not in list_of_childs:
                list_of_childs[entry[1]] = []

            if entry[0] not in list_of_childs:
                list_of_childs[entry[0]] = []
                       
            list_of_childs[entry[1]].append(entry[0])            
            
            ### Search for soma
            if entry[6] > 100:
                soma = (X,Z,Y,round(entry[6]/10000,2))
                soma_node = entry[0]
                print('Soma found')

        #if no soma is found, then search for nerve ending (for sensory neurons)
        #print(node_data[2])       
        if 'nerve ending' in node_data[2] and soma_node is None:
            soma_node = node_data[2]['nerve ending'][0]        

        if interpolate_virtual is True:
            print('Interpolating Virtual Nodes')
            list_of_childs,nodes_list = CATMAIDtoBlender.insert_virtual_nodes(list_of_childs,nodes_list)
        
        ### Root node's entry is called 'None' because it has no parent
        ### This will be starting point for creation of the curves
        root_node = list_of_childs[None][0]            

        if truncate_neuron != 'none' and soma_node is None:
            print('WARNING: Unable to truncate main neurite - no soma or nerve exit found! Neuron skipped!')
            return {'FINISHED'}

        if resampling > 1:            
            new_child_list = nodes_to_keep = CATMAIDtoBlender.resample_child_list(list_of_childs, root_node, soma_node, resampling)
        else:
            new_child_list = nodes_to_keep = list_of_childs                 

        #print('Before Trunc',new_child_list)

        #Do this is soma node has been found
        if truncate_neuron != 'none' and soma_node is not None:
            if soma_node != root_node:
                print('Soma is not Root - Rerooting...')
                new_child_list = nodes_to_keep = CATMAIDtoBlender.reroot_child_list(new_child_list, soma_node, nodes_list)
                print('After Reroot:',len(new_child_list))
                #print(new_child_list)            
            if truncate_neuron == 'main_neurite' and truncate_value > 0:
                longest_neurite_child_list = CATMAIDtoBlender.extract_longest_neurite(new_child_list)
                new_child_list = nodes_to_keep = CATMAIDtoBlender.trunc_neuron(longest_neurite_child_list,soma_node,nodes_list,truncate_value)
            elif truncate_neuron == 'main_neurite' and truncate_value <= 0:
                longest_neurite_child_list = CATMAIDtoBlender.extract_longest_neurite(new_child_list)
                new_child_list = nodes_to_keep = longest_neurite_child_list
            elif truncate_neuron == 'strahler_index':
                nodes_to_keep = CATMAIDtoBlender.trunc_strahler(new_child_list,soma_node,truncate_value)                                       
            print('Neuron Truncated to',len(new_child_list),'nodes:')    
            root_node = soma_node

        #Pop 'None' node, so that it doesn't cause trouble later
        try:
            new_child_list.pop(None)        
        except:
            pass

        Create_Mesh.make_curve_neuron (cellname, root_node, nodes_list, new_child_list, soma, skid, neuron_name, resampling, nodes_to_keep)            

        ### Search through connectors and create a list with coordinates
        if import_connectors is True:
            connector_pre = {}
            connector_post = {}
            for connector in node_data[1]:
                connector_id = connector[1]                           
                        
                ### Get connector coordinates
                X_cn = float(connector[3])/10000
                Y_cn = float(connector[4])/-10000
                Z_cn = float(connector[5])/10000 
                
                connector_coords = (X_cn, Z_cn, Y_cn)
    
                if connector[2] is 0: ### = presynaptic connection
                    #print('Data appended to Presynapses') 
                    connector_pre[connector_id] = (nodes_list[connector[0]], connector_coords)  
                    #print(connector_pre[connector_id])
    
                if connector[2] is 1: ### = postsynaptic connection
                    #print('Data appended to Postsynapses')
                    connector_post[connector_id] = (nodes_list[connector[0]], connector_coords)                          
                    #print(connector_post[connector_id])          
    
            print('%i Pre-/ %i Postsynaptic Connections Found' % (len(connector_pre), len(connector_post)))
        
            Create_Mesh.make_connectors(cellname, connector_pre, connector_post)
        
        return {'FINISHED'}

    def insert_virtual_nodes(list_of_childs,nodes_list):
        """
        Checks z resolution of given neuron -> due to virtual nodes, some neurons have less nodes than others
        Will run into troubles if virtual_nodes_id (has to be integer) happens to be an already used treenode_id
        """
        virtual_nodes_id = 0
        to_delete = []
        to_add = []
        for n in list_of_childs:
            if n is None:
                continue
            for c in list_of_childs[n]:
                #Get distance to child
                d = round(math.fabs(nodes_list[c][1] - nodes_list[n][1]),3)
                #If distance is larger than 50nm
                if d > 0.005:
                    intervals = (
                                    (nodes_list[c][0]-nodes_list[n][0])/round(d/0.005),
                                    (nodes_list[c][1]-nodes_list[n][1])/round(d/0.005),
                                    (nodes_list[c][2]-nodes_list[n][2])/round(d/0.005)
                                )

                    #Mark parent - child connection for deletion                   
                    to_delete.append((n,c))

                    last_parent = int(n)

                    for i in range(1,round(d/0.005)):                        
                        nodes_list[virtual_nodes_id] = (
                                                nodes_list[n][0] + intervals[0] * i,
                                                nodes_list[n][1] + intervals[1] * i,
                                                nodes_list[n][2] + intervals[2] * i
                                                )

                        to_add.append((last_parent,virtual_nodes_id))                       

                        last_parent = virtual_nodes_id
                        virtual_nodes_id += 1
                    #Connect last virtual node to child                    
                    to_add.append((last_parent,int(c)))

        for entry in to_delete:
            list_of_childs[entry[0]].remove(entry[1])  

        for entry in to_add:
            if entry[0] not in list_of_childs:
                list_of_childs[entry[0]] = []
            list_of_childs[entry[0]].append(entry[1])


        return (list_of_childs,nodes_list)  
    
    def resample_child_list( list_of_childs, root_node ,soma_node, resampling_factor ):
        
        print('Resampling Child List (Factor: %i)' % resampling_factor)        
        new_child_list = {}
        new_child_list[None] = [root_node]
        
        #Collect root node, end nodes and branching points in list: fix_nodes
        fix_nodes = []
        fix_nodes.append(root_node)
        fix_nodes.append(soma_node)
        for node in list_of_childs:
            if len(list_of_childs[node]) == 0:
                fix_nodes.append(node)
            if len(list_of_childs[node]) > 1:
                fix_nodes.append(node)                
        
        #Start resampling with every single fix node until you hit the next fix node
        for fix_node in fix_nodes:
            new_child_list[fix_node] = []
            #Cycle through childs of fix nodes (end nodes will thus be skipped)
            for child in list_of_childs[fix_node]:                
                new_child = CATMAIDtoBlender.get_new_child(child, list_of_childs,resampling_factor)
                new_child_list[fix_node].append(new_child)
                #Continue resampling until you hit a fix node
                while new_child not in fix_nodes:
                    old_child = new_child
                    new_child = CATMAIDtoBlender.get_new_child(old_child, list_of_childs,resampling_factor)
                    
                    new_child_list[old_child] = []
                    new_child_list[old_child].append(new_child)
                    
        print('Done Resampling. Node Count: %i/%i (new/old)' % (len(new_child_list),len(list_of_childs)))
                    
        return new_child_list  
        
                
    def get_new_child(old_child, list_of_childs,  resampling_factor):
        not_branching = True  
        not_end = True
        skipped = 0                
        new_child = old_child 
        #Check if old child is an end node or a branching point
        if len(list_of_childs[new_child]) == 0:
            not_end = False
        if len(list_of_childs[new_child]) > 1:
            not_branching = False                              
            
        while not_branching is True and not_end is True and skipped < resampling_factor:
            new_child = list_of_childs[new_child][0]
            skipped += 1
            #Check if new_child is an end node or a branching point                
            if len(list_of_childs[new_child]) == 0:
                not_end = False
            if len(list_of_childs[new_child]) > 1:
                not_branching = False 

        return new_child    

    def trunc_neuron(list_of_childs, soma_node, nodes_list, maximum_length):

        #if len(list_of_childs) < maximum_length:
        #    print('Child list already smaller than maximum length!')
        #    return list_of_childs

        new_child_list = dict()        
        new_child_list[int(soma_node)] = list(list_of_childs[soma_node])
        
        for child in list_of_childs[soma_node]:
            new_child_list.update( CATMAIDtoBlender.till_next_fork( list_of_childs, int(child) , nodes_list , maximum_length, new_child_list) )
        
            #print('Exception:',soma_node ,list_of_childs[soma_node])

        return new_child_list

    def dist(v1,v2):        
        return math.sqrt(sum(((a-b)**2 for a,b in zip(v1,v2))))

    def till_next_fork(list_of_childs, start_node, nodes_list, maximum_length, new_child_list = {}):
        this_node = int(start_node)
        length = 0
        fork = False
        end = False

        #filename = 'C:\\Users\schlegel.p\\SkyDrive\\Cloudbox\\Python\\CATMAID-Blender-Plugin\\CATMAIDImport_V3_9.py'
        #exec(compile(open(filename).read(), filename, 'exec'))

        while length < maximum_length and fork is False and end is False:
            if this_node not in new_child_list:
                new_child_list[this_node] = []

            new_child_list[this_node] += list(list_of_childs[this_node])

            if len(list_of_childs[this_node]) > 1:
                fork = True                
                for child in list_of_childs[this_node]:                    
                    #if this_node in list_of_childs[child]:
                    #    print('WARNING! Circular relation:',this_node,child)

                    new_child_list = CATMAIDtoBlender.till_next_fork( list_of_childs, int(child), nodes_list, maximum_length - length , new_child_list)
            elif len(list_of_childs[this_node]) == 1:
                length += CATMAIDtoBlender.dist(nodes_list[this_node],nodes_list[list_of_childs[this_node][0]])                
                this_node = list_of_childs[this_node][0]
            elif len(list_of_childs[this_node]) == 0:                
                end = True            

        #Make sure the last node is actually listed as not having childs!
        if length >= maximum_length:       
            new_child_list[this_node] = []

        return new_child_list

    def test_integrity(list_of_childs,msg=''):
        for node in list_of_childs:
            for child in list_of_childs[node]:
                if node in list_of_childs[child]:
                    print(msg,'- Integrity compromised! Circular relation:',node,list_of_childs[node],child,list_of_childs[child])
                    return 
        print(msg,'- Integrity passed')

    def reroot_child_list(list_of_childs, new_root, nodes_list):
        new_child_list = dict({int(new_root):list(list_of_childs[new_root])})

        #print('AAAA',new_child_list, new_root)

        list_of_childs.pop(None)

        #First go downstream of new root node 
        for child in list_of_childs[new_root]:
            new_child_list = CATMAIDtoBlender.till_next_fork( list_of_childs, child , nodes_list,  float("inf"), new_child_list )        

        #CATMAIDtoBlender.test_integrity(list_of_childs)        
             

        #Now go upstream and reroot these nodes:
        new_child_list = CATMAIDtoBlender.upstream_till_next_fork( list_of_childs, int(new_root), nodes_list, new_child_list ) 

        return new_child_list


    def upstream_till_next_fork(list_of_childs, start_node, nodes_list, new_child_list = {}):
        this_node = int(start_node)
        i = 0        
        has_parents = True

        #CATMAIDtoBlender.test_integrity(list_of_childs,'Initial Integrity Test')                                

        while has_parents is True:
            #First find parent node:
            #print(this_node)
            has_parents = False
            parent_node = None
            for node in list_of_childs:
                #print(node,list_of_childs[node], this_node)                
                if this_node in list_of_childs[node]:
                    parent_node = int(node) 
                    has_parents = True
                    #print('Found parent of',this_node,':',parent_node)
                    break

            if this_node not in new_child_list:
                    new_child_list[this_node] = []

            if has_parents is True:
                #CATMAIDtoBlender.test_integrity(list_of_childs,'1st Pass')
                #print(new_child_list)                

                new_child_list[this_node].append(parent_node) ##!!!!!!Das hier ist das Arschloch. Hier passiert der Zirkelschluss.

                #CATMAIDtoBlender.test_integrity(list_of_childs,'2nd Pass')   

                if len(list_of_childs[parent_node]) > 1:
                    #print('Parent forks:',list_of_childs[parent_node])
                    if parent_node not in new_child_list:
                        #Add parent node here, in case it is also a root node as this will end the while loop
                        new_child_list[parent_node] = []                    
                    for child in list_of_childs[parent_node]:
                        #Don't go backwards
                        if child == this_node:
                            continue
                        #print('Going down', child)  
                        #Add childs to parent node    
                        new_child_list[parent_node].append(int(child))     
                        #Go downstream all others childs -> at root node this should cover all childs and automatically go down the other way
                        new_child_list = CATMAIDtoBlender.till_next_fork( list_of_childs, int(child), nodes_list, float("inf"), new_child_list )

                this_node = int(parent_node)
            else:
                #print('Found old root node:',this_node,list_of_childs[this_node])
                pass

        return new_child_list

    def extract_longest_neurite(list_of_childs):
        #list_of_childs must be without 'None' entry!   
        try:
            list_of_childs.pop(None)     
        except:
            pass

        print('Searching for longest neurite...')

        end_nodes = []

        for node in list_of_childs:
            if len(list_of_childs[node]) == 0:
                end_nodes.append(node)

        max_length = 0

        for i,en in enumerate(end_nodes):
            #print('checking end node',i,'of',len(end_nodes))
            length = 0
            has_parents = True
            this_node = int(en)
            child_list_temp = dict({
                                    int(en):list(list_of_childs[en])
                                    })

            while has_parents is True:
                #First find parent node:                
                has_parents = False
                parent_node = None
                for node in list_of_childs:
                    #print(node,list_of_childs[node], this_node)                
                    if this_node in list_of_childs[node]:
                        parent_node = int(node) 
                        has_parents = True
                        #print('Found parent of',this_node,':',parent_node)
                        break                

                if has_parents is True:                  
                    length += 1                    
                    child_list_temp[int(parent_node)] = [this_node]
                    this_node = int(parent_node)                               

            if length > max_length:
                new_child_list = dict(child_list_temp)
                max_length = length

        print('Longest arbor found:' , max_length , '(nodes)')

        return new_child_list

    def trunc_strahler(list_of_childs,root_node,truncate_value):

        #print(list_of_childs)

        nodes_to_keep = dict(list_of_childs)

        strahler_index = CATMAIDtoBlender.calc_strahler_index(list_of_childs,root_node)

        max_strahler_index = strahler_index[root_node]        

        #First remove nodes that have a below threshold strahler index
        if truncate_value >= 0:
            for entry in strahler_index:
                if strahler_index[entry] < (max_strahler_index - truncate_value):
                    nodes_to_keep.pop(entry)
        else:
            for entry in strahler_index:
                if strahler_index[entry] > math.fabs(truncate_value):
                    nodes_to_keep.pop(entry)

        #Now remove connections to these nodes
        if truncate_value >= 0:
            for entry in nodes_to_keep:
                for child in list(nodes_to_keep[entry]):
                    if strahler_index[child] < (max_strahler_index - truncate_value): 
                        nodes_to_keep[entry].remove(child)  
        else:     
            for entry in nodes_to_keep:
                for child in list(nodes_to_keep[entry]):
                    if strahler_index[child] > math.fabs(truncate_value): 
                        nodes_to_keep[entry].remove(child)

        return nodes_to_keep


    def calc_strahler_index(list_of_childs,root_node):
        """
        Calculates Strahler Index -> starts with index of 1 at each leaf, at forks with varying incoming strahler index, the highest index
        is continued, at forks with the same incoming strahler index, highest index + 1 is continued
        Starts with end nodes, then works its way from branch nodes to branch nodes up to root node
        """

        try:
            list_of_childs.pop(None)     
        except:
            pass

        #print('Calculating Strahler Indices...')

        end_nodes = []
        branch_nodes = []
        strahler_index = {}

        for node in list_of_childs:
            strahler_index[node] = None
            if len(list_of_childs[node]) == 0:
                end_nodes.append(int(node))
            elif len(list_of_childs[node]) > 1:
                branch_nodes.append(int(node))                    

        starting_points = end_nodes + branch_nodes
        nodes_processed = []

        while starting_points:
            print(len(starting_points))
            starting_points_done = []

            for i,en in enumerate(starting_points):

                this_node = int(en)

                #First check, if all childs of this starting point have already been processed
                node_done = True 
                for child in list_of_childs[this_node]:
                    if child not in nodes_processed:
                        node_done = False

                #If not all childs of given starting node have been processed, skip it for now
                if node_done is False:
                    continue

                #Calculate index for this branch                
                previous_indices = []
                for child in list_of_childs[this_node]:
                    previous_indices.append(strahler_index[child])

                if len(previous_indices) == 0:
                    this_branch_index = 1
                elif len(previous_indices) == 1:
                    this_branch_index = previous_indices[0]
                elif previous_indices.count(max(previous_indices)) >= 2:
                    this_branch_index = max(previous_indices) + 1
                else:
                    this_branch_index = max(previous_indices)                

                strahler_index[this_node] = this_branch_index 
                nodes_processed.append(this_node)
                starting_points_done.append(this_node)

                #Find parent
                for node in list_of_childs:                    
                    if this_node in list_of_childs[node]:
                        parent_node = int(node)                                                 
                        break

                while parent_node not in branch_nodes and parent_node != None:
                    this_node = parent_node
                    parent_node = None

                    #Find next parent
                    for node in list_of_childs:                    
                        if this_node in list_of_childs[node]:
                            parent_node = int(node)                                                 
                            break 

                    if this_node not in branch_nodes:
                        strahler_index[this_node] = this_branch_index                   
                        nodes_processed.append(this_node)

            #Remove those starting_points that could be processed in this run before the next iteration
            for node in starting_points_done:
                starting_points.remove(node)        

        return  strahler_index




class ConnectToCATMAID(Operator):      
    """Creates CATMAID remote instances using given credentials"""
    bl_idname = "connect.to_catmaid"  
    bl_label = "Enter Credentials and press OK"    
    
    local_http_user = StringProperty(name="HTTP User")
    #subtype = 'PASSWORD' seems to be buggy in Blender 2.71 -> works fine in 2.77    
    local_http_pw = StringProperty( name="HTTP Password",
                                    subtype='PASSWORD')
    local_token = StringProperty(name="Token",
                                description="How to retrieve Token: http://catmaid.github.io/dev/api.html#api-token")    
    local_server_url = StringProperty(name="Server Url")    
    local_project_id = IntProperty(name='Project ID', default = 0)

    #save_prefs = BoolProperty(name='Save credentials', default = True, description = 'Saves credentials in addon preferences: User Preferences -> Add-ons -> CATMAIDImport -> Preferences')

    #Old settings from before API token was introduced
    #local_catmaid_user = StringProperty(name="CATMAID User")
    #subtype = 'PASSWORD' seems to be buggy in Blender 2.71 -> works fine in 2.77   
    #local_catmaid_pw = StringProperty(name="CATMAID Password", subtype = 'PASSWORD')
    
    
    def execute(self, context):               
        global remote_instance, connected, project_id

        addon_prefs = context.user_preferences.addons['CATMAIDImport'].preferences       
        
        #Check for latest version of the Script
        get_version_info.check_version(context)
        
        print('Connecting to CATMAID server')
        print('HTTP user: %s' % self.local_http_user)
        #print('CATMAID user: %s' % self.local_catmaid_user)        
        print('Token: %s' % self.local_token)        

        #remote_instance = CatmaidInstance( server_url, self.local_catmaid_user, self.local_catmaid_pw, self.local_http_user, \                                           self.local_http_pw )          
        remote_instance = CatmaidInstance( self.local_server_url, self.local_http_user, self.local_http_pw, self.local_token )      

        """
        response = json.loads( remote_instance.auth().decode( 'utf-8' ) )
        print( response ) 
        
        if  'error' in response:
            print ('Error while attempting 2 connect to CATMAID server')
            connected = False
        else:
            print ('Connection successful')
            connected = True
        """

        """
        #Save prefs does not work as of yet b/c the user preferences are being reset after each restart.
        if self.save_prefs:            
            addon_prefs.http_user = self.local_http_user
            addon_prefs.http_pw = self.local_http_pw
            addon_prefs.token = self.local_token
            addon_prefs.project_id = self.local_project_id
            self.report({'INFO'},'Credentials saved!')
        else:
            addon_prefs.http_user = ''
            addon_prefs.http_pw = ''
            addon_prefs.token = ''            
            self.report({'INFO'},'Credentials cleared!')
        """

        #Retrieve user list, to test if PW was correct:
        try:
            response = remote_instance.fetch( remote_instance.get_user_list() )
            connected = True    
            self.report({'INFO'},'Connection successful')
            print('Test call successful')
        except:
            self.report({'ERROR'},'Connection failed: see console')
            print('ERROR: Test call to server failed. Credentials incorrect?')
        #Set standard project ID
        project_id = self.local_project_id
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "local_http_user")
        row = layout.row(align=True)
        row.prop(self, "local_http_pw")
        row = layout.row(align=True)
        row.prop(self, "local_token")        
        row = layout.row(align=True)
        row.prop(self, "local_project_id")
        row = layout.row(align=True)
        row.prop(self, "local_server_url")
        #row = layout.row(align=True)
        #row.prop(self, "save_prefs")

        layout.label(text="Permanently set credentials and server url in addon prefs.")
     
    
    def invoke(self, context, event):
        addon_prefs = context.user_preferences.addons['CATMAIDImport'].preferences        
        self.local_http_user = addon_prefs.http_user
        self.local_token = addon_prefs.token
        self.local_http_pw = addon_prefs.http_pw
        self.local_project_id = addon_prefs.project_id
        self.local_server_url = addon_prefs.server_url
        #self.local_catmaid_user = catmaid_user
        #self.local_catmaid_pw = catmaid_pw
        return context.window_manager.invoke_props_dialog(self)      
      
    
class ExportAllToSVG(Operator, ExportHelper):
    """Exports all neurons (only curves) to SVG File"""
    bl_idname = "exportall.to_svg"  
    bl_label = "Export neuron(s) (only curves!) to SVG"
    bl_options = {'PRESET'}

    which_neurons = EnumProperty(name = "For which Neuron(s)?", 
                                      items = [('Active','Active','Active'),('Selected','Selected','Selected'),('All','All','All')],
                                      description = "Choose for which neurons to connectors.")
    merge = BoolProperty(name="Merge into One", default = False,
                        description = "If exporting more than one neuron, render them all on top of each other, not in separate panels.")
    random_colors = BoolProperty(name="Use Random Colors", 
                                 default = False,
                                 description = "Give Exported Neurons a random color (default = black)")
    colors_from_mesh = BoolProperty(name="Use Mesh Colors", 
                                    default = False,
                                    description = "Color Exported Neurons by the Color they have in Blender")
    color_by_inputs_outputs = BoolProperty(name="Color by Input/Outputs ratio", 
                                    default = False,
                                    description = "Color Arbors of Exported Neurons by the ratio of input to outputs")
    color_by_density = BoolProperty(name = "Color by Density", 
                                    default = False, 
                                    description = "Colors Edges between Nodes by # of Nodes of given Object (choose below)")                    
    object_for_density = EnumProperty(name = "Object for Density", 
                                      items = availableObjects,
                                      description = "Choose Object for Coloring Edges by Density (e.g. other neurons/connectors)")
    filter_synapses = StringProperty(name="Filter Synapses (Comma-seperated)",
                                    description = "Works only if Object for Density = Synapses. Set to 'incoming'/'outgoing' to filter up- or downstream synapses.")      
    proximity_radius_for_density = FloatProperty(name="Proximity Threshold", 
                                                 default = 0.15,
                                                 description = "Threshold for distance between Edge and Points in Density Object")    
    basic_radius = FloatProperty(name="Base Soma Size", default = 1) 
    line_width = FloatProperty(name="Base Line Width", default = 0.7)       
    use_bevel = BoolProperty(name="Use Bevel Depth", 
                             default = False,
                             description = "Use curve's bevel depth. Will be multiplied with base line width."  )       
    export_as_points = BoolProperty(name="Export as Pointcloud", 
                                    default = False,
                                    description ="Exports neurons as point cloud rather than edges (e.g. for dense core vesicles)")
    barplot = BoolProperty(name="Add Barplot", default = False,
                                    description = "Export Barplot along X/Y axis to show node distribution")
    export_ring_gland = BoolProperty(name="Export Ring Gland", 
                                     default = True,
                                     description = "Adds Outlines of Ring Gland to SVG")
    views_to_export = EnumProperty(name="Views to export",
                                   items = (("Front/Top/Lateral/Perspective-Dorsal","Front/Top/Lateral/Perspective-Dorsal","Front/Top/Lateral/Perspective-Dorsal"),
                                            ("Front/Top/Lateral","Front/Top/Lateral","Front/Top/Lateral"),
                                            ("Front","Front","Front"),
                                            ("Top","Top","Top"),
                                            ("Lateral","Lateral","Lateral"),
                                            ("Perspective-Front","Perspective-Front","Perspective-Front"),
                                            ("Perspective-Dorsal","Perspective-Dorsal","Perspective-Dorsal")
                                            ),
                                    default =  "Front/Top/Lateral/Perspective-Dorsal",
                                    description = "Choose which views should be included in final SVG")
    x_persp_offset = FloatProperty(name="Horizontal Perspective", 
                                   description="Sets perspective shift along horizontal axis",
                                   default = 0.9, max = 2, min = -2)  
    y_persp_offset = FloatProperty(name="Vertical Perspective", 
                                   description="Sets perspective shift along vertical axis",
                                   default = -0.01, max = 2, min = -2)                                    
    add_neuron_name = BoolProperty(name='Include neuron name', 
                                   description='If checked, neuron name(s) will be included as figure legend.',
                                   default = True)

    
    # ExportHelper mixin class uses this
    filename_ext = ".svg"
    svg_header =    '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
    svg_end =       '\n</svg> '    
    
    
    def execute(self, context):
        offsetX = 0
        offsetY = 0
        offsetY_forText = -150        
        offsetY_for_top = 60
        offsetX_for_top = 135        
        offsetY_for_front = -150
        offsetX_for_front = 5         
        offsetY_for_lateral = 0
        offsetX_for_lateral = 0   
        offsetY_for_persp = 150
        offsetX_for_persp = 0       
        first_neuron = True
        
        if "Perspective-Dorsal" in self.views_to_export:
            #For dorsal perspective change offsets:
            y_persp_offset = -1 * self.x_persp_offset
            x_persp_offset = 0            
            #y_center sets the pivot along y axis (0-25) -> all this does is move the object along y axis, does NOT change perspective
            y_center = 5  
        else:
            x_persp_offset = self.x_persp_offset
            y_persp_offset = self.y_persp_offset
                    
        if self.merge is False: 
            offsetIncrease = 260
        else:
            offsetIncrease = 0
            
        density_gradient = {'start_rgb': (0,255,0),
                            'end_rgb':(255,0,0)}
        ratio_gradient = {'start_rgb': (0,0,255),
                            'end_rgb':(255,0,0)}
        density_data = []       
        
        #Check Connection to CATMAID server as requirement for this option to work
        if self.color_by_inputs_outputs is True and connected is False:
            print('ERROR: You need to connect to CATMAID server first to use <Color by Input/Output Ratio>!') 
            self.report({'ERROR'},'Error(s) occurred - cannot color by input/output: see console')
            self.color_by_inputs_outputs = False
            
        if self.color_by_density is True and self.object_for_density == 'Synapses' and connected is False:
                print('ERROR: You need to connect to CATMAID server first to use <Color by Synapse Density>!')
                self.report({'ERROR'},'Error(s) occurred - cannot color by synapse density: see console')
                self.color_by_density = False       
        
        manual_max = None       
         
        if self.filter_synapses:
            filter_for_synapses = self.filter_synapses.split(',')            
            #Manual Max can be set by adding max=value to filter            
            for i in range(len(filter_for_synapses)):
                if 'max=' in filter_for_synapses[i]:
                    manual_max = filter_for_synapses[i]
                    
            #if manual_max was found, remove this entry from filter list and truncate/convert to int
            if manual_max != None:
                filter_for_synapses.remove(manual_max)        
                manual_max = int(manual_max[4:])           
        else:
            filter_for_synapses = []      
            
        if 'all' in filter_for_synapses:
            print('<all> tag has been set - all connectors minus excluded ones will be plotted')
                            
        #Create list of nodes for given density object
        if self.color_by_density is True and self.object_for_density != 'Synapses':     
            try:
                for spline in bpy.data.objects[self.object_for_density].data.splines:
                    for node in spline.points:
                        #node.co = vector(x,y,z,?)
                        if node.co not in density_data:
                            density_data.append(node.co)
                #print(density_data)
            except:
                print('ERROR: Unable to create density data for object!') 
                self.report({'ERROR'},'Error(s) occurred: see console')

        brain_shape_top_string = '<g id="brain shape top">\n <polyline points="28.3,-5.8 34.0,-7.1 38.0,-9.4 45.1,-15.5 50.8,-20.6 57.7,-25.4 59.6,-25.6 63.2,-22.8 67.7,-18.7 70.7,-17.2 74.6,-14.3 78.1,-12.8 84.3,-12.6 87.7,-15.5 91.8,-20.9 98.1,-32.4 99.9,-38.3 105.2,-48.9 106.1,-56.4 105.6,-70.1 103.2,-75.8 97.7,-82.0 92.5,-87.2 88.8,-89.1 82.6,-90.0 75.0,-89.9 67.4,-89.6 60.8,-85.6 55.3,-77.2 52.4,-70.2 51.9,-56.7 55.0,-47.0 55.9,-36.4 56.0,-32.1 54.3,-31.1 51.0,-33.4 50.7,-42.5 52.7,-48.6 49.9,-58.4 44.3,-70.8 37.4,-80.9 33.1,-84.0 24.7,-86.0 14.2,-83.9 8.3,-79.1 2.9,-68.3 1.3,-53.5 2.5,-46.9 3.0,-38.3 6.3,-28.2 10.9,-18.7 16.3,-9.7 22.2,-6.4 28.3,-5.8" \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n <polyline points="88.8,-89.1 90.9,-97.7 92.9,-111.3 95.6,-125.6 96.7,-139.4 95.9,-152.0 92.8,-170.2 89.4,-191.0 87.2,-203.7 80.6,-216.6 73.4,-228.3 64.5,-239.9 56.4,-247.3 48.8,-246.9 39.0,-238.3 29.6,-226.9 24.7,-212.0 22.9,-201.2 23.1,-186.9 18.7,-168.3 14.1,-150.4 12.6,-138.0 13.7,-121.5 16.3,-105.1 18.3,-84.8 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>' 
        brain_shape_front_string = '<g id="brain shape front"> \n <polyline points="51.5,24.0 52.0,21.3 52.0,17.6 50.2,11.2 46.8,6.5 40.5,2.5 33.8,1.1 25.4,3.4 18.8,8.0 13.2,12.5 8.3,17.9 4.3,23.8 1.8,29.3 1.4,35.6 1.6,42.1 4.7,48.3 7.9,52.5 10.8,56.9 13.1,64.3 14.3,73.2 12.8,81.0 16.2,93.6 20.9,101.5 28.2,107.5 35.3,112.7 42.2,117.0 50.8,119.3 57.9,119.3 67.1,118.0 73.9,114.1 79.0,110.4 91.1,102.7 96.3,94.2 96.3,85.3 94.0,81.4 95.4,74.8 96.6,68.3 97.5,64.7 100.9,59.7 103.8,52.5 105.4,46.7 106.1,38.8 105.4,32.4 103.1,26.4 98.9,21.0 94.1,16.3 88.3,11.1 82.0,6.5 74.8,3.3 67.8,3.1 61.7,5.1 56.8,9.6 53.4,15.2 52.2,19.7 52.3,25.3 51.4,24.1 " \n  style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n <polyline points="46.6,34.0 45.5,36.1 43.2,38.6 41.1,43.3 39.7,48.7 39.7,51.0 42.6,55.2 51.4,59.5 54.9,60.9 60.8,60.8 62.9,58.2 62.9,52.6 60.3,47.6 57.7,43.9 56.1,40.2 55.1,35.9 55.1,34.4 51.8,33.6 49.1,33.5 46.6,34.0 " \n  style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'
        brain_shape_lateral_string = '<g id="brain shape lateral"> \n <polyline points="247.2,91.6 246.8,94.6 246.3,95.5 245.0,96.7 239.8,99.0 225.8,103.4 210.9,107.5 200.8,109.1 186.0,109.9 166.0,110.7 150.8,111.3 135.8,112.8 120.9,114.2 107.3,114.9 98.6,115.7 88.7,117.9 81.3,119.1 66.2,119.2 58.3,118.7 51.6,118.5 46.0,116.4 40.7,114.4 36.6,112.0 34.2,109.6 30.7,104.8 27.3,100.3 25.3,98.2 22.2,91.9 21.1,86.8 19.6,80.6 17.4,73.9 15.2,68.9 11.2,61.8 11.0,52.3 9.1,49.9 7.4,46.4 6.6,42.6 6.3,35.7 7.0,27.1 7.4,24.5 10.2,18.7 15.8,13.2 22.3,8.5 26.2,7.1 32.6,7.0 36.1,6.2 41.2,3.9 47.2,1.8 54.8,1.7 64.5,3.2 73.4,5.3 81.1,11.2 86.7,16.4 89.0,21.1 90.2,33.2 89.3,42.8 86.6,48.7 82.1,53.9 78.8,57.2 77.9,59.2 91.4,61.6 98.5,62.2 116.6,62.4 131.7,61.0 146.1,59.8 161.1,60.1 176.0,61.3 190.8,63.3 206.2,66.0 219.5,70.6 224.5,72.8 239.5,82.1 245.5,86.0 246.9,87.9 247.2,91.6 " \n  style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'          
        brain_shape_dorsal_perspective_05_string = '<g id="brain shape dorsal perspective" transform="scale(0.21) translate(-511,-30)"> \n <polyline points="255,974 238,968 184,939 174,932 113,880 100,863 92,845 79,793 64,751 46,706 45,685 51,636 72,565 77,536 78,524 73,508 64,462 60,427 52,395 31,370 17,348 9,321 3,284 2,230 7,185 22,153 40,126 59,105 88,82 126,60 145,51 163,47 175,46 201,53 214,62 234,88 243,104 263,90 275,63 280,33 285,27 293,14 308,5 319,2 343,3 389,21 424,44 451,74 469,110 491,145 504,177 508,204 507,235 501,269 482,309 466,334 452,345 445,351 443,377 435,393 429,433 427,462 425,515 436,558 444,571 452,600 451,624 454,655 441,690 429,707 423,729 403,839 382,893 365,913 335,936 271,969 255,974" \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n <polyline points="52,395 90,401 129,392 145,374 153,346" \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n <polyline points="445,351 433,355 417,355 396,346 381,336 382,337" \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round" /> \n <polygon points="257,349 242,348 230,332 216,313 208,300 215,283 228,261 245,234 260,201 265,168 262,143 266,141 270,164 283,192 288,208 303,242 312,265 318,276 305,303 290,323 281,332 268,343" \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'
        brain_shape_dorsal_perspective_09_string = '<g id="brain shape dorsal perspective" transform="scale(0.173) translate(-620,-112)"> \n <path d="M514 676l5 64 1 92 30 122 9 144 -40 122 -26 223 -29 121 -108 118 -28 20 -26 8 -29 -20 -68 -78 -31 -46 -43 -69 -21 -34 -17 -115 -16 -86 -23 -101 0 -104 33 -235 -4 -146c-3,-22 -5,-31 -7,-42 -1,-12 4,-18 -2,-27 -6,-10 -22,-17 -32,-27 -9,-9 -19,-16 -26,-30 -7,-15 -9,-38 -12,-54 -2,-17 -3,-28 -4,-45 0,-17 0,-34 1,-57 0,-23 2,-64 3,-81 1,-17 0,-14 3,-22 3,-8 3,-8 13,-27 9,-19 33,-67 43,-85 4,-7 28,-41 33,-46 9,-9 28,-24 38,-30 31,-20 63,1 99,17 18,7 23,15 29,19 6,4 2,5 6,6 5,2 13,4 21,2 8,-2 21,-8 27,-15 6,-7 3,-14 6,-23 3,-9 9,-22 13,-31 3,-9 5,-15 9,-24 3,-8 5,-19 10,-26 5,-6 13,-9 20,-13 8,-4 15,-7 23,-9 8,-3 16,-6 27,-6 11,0 21,1 35,8 15,8 37,25 49,35 12,11 16,17 24,29 8,13 15,27 24,47 9,20 25,49 32,71 8,23 9,48 13,64 3,16 6,21 9,31 3,10 7,19 8,31 1,12 -1,28 -1,40 -1,13 -1,22 -3,35 -2,13 -3,30 -7,45 -5,15 -8,22 -18,42 -9,20 -30,60 -40,75 -11,14 -15,0 -20,9 -5,9 -5,19 -7,38 -3,19 -8,50 -8,74l0 2z" \n style="fill:#D9DADA;stroke-width:0" /> \n <path d="M301 495c-9,-17 -19,-33 -28,-50 3,-2 6,-4 9,-6 4,-6 8,-11 12,-17 5,-10 9,-20 13,-30 5,-20 10,-40 15,-60 -2,-14 -4,-28 -6,-41 0,-4 1,-7 2,-11 -1,-10 -2,-21 -4,-31 -2,-3 -4,-7 -6,-10 3,-2 6,-3 8,-5 1,9 1,17 2,25 5,16 11,32 16,48 3,17 7,35 10,52 8,17 17,34 25,50 -9,21 -17,42 -26,63 -8,12 -16,24 -25,36 -5,-4 -11,-9 -17,-13z" \n style="fill:#FEFEFE;stroke-width:0"/> \n </g> \n'
        
        ring_gland_top = '<g id="ring gland top"> \n <polyline points="57.8,-43.9 59.9,-43.8 62.2,-43.3 64.4,-41.1 67.3,-37.7 70.8,-34.0 73.9,-30.7 75.1,-28.3 76.2,-24.8 76.0,-22.1 75.2,-19.7 73.0,-17.3 70.4,-16.1 66.5,-16.1 64.4,-15.2 61.8,-12.3 58.8,-9.5 55.7,-8.6 51.3,-8.1 47.6,-8.3 44.0,-8.7 41.4,-10.3 40.8,-12.6 42.5,-16.1 45.4,-20.7 47.9,-25.5 48.9,-28.9 50.1,-32.3 51.8,-33.0 51.5,-35.1 51.7,-37.9 52.4,-41.2 53.9,-42.8 55.8,-43.8 57.8,-43.9 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'          
        ring_gland_front = '<g id="ring gland front"> \n <polyline points="45.5,11.3 44.3,12.3 41.9,14.2 40.9,16.8 41.3,20.1 42.7,24.7 44.0,27.8 45.9,28.6 49.0,27.7 50.1,27.7 53.0,28.1 56.5,28.4 59.2,28.3 62.2,27.5 64.5,26.6 67.1,26.6 69.7,27.2 70.9,26.9 73.1,25.4 74.8,22.8 75.9,20.3 75.9,17.6 74.8,15.1 72.8,12.8 69.3,10.2 66.7,8.6 64.2,7.7 61.9,7.6 59.0,8.4 57.1,9.4 56.6,11.1 55.1,10.0 53.5,9.2 51.3,8.9 49.6,9.2 45.5,11.3 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>' 
        ring_gland_lateral = '<g id="ring gland lateral"> \n <polyline points="9.0,16.8 13.7,13.3 23.4,9.8 27.9,9.1 31.1,9.5 34.8,8.1 38.8,7.7 41.2,8.4 42.6,9.8 44.0,12.7 44.2,16.6 43.5,22.3 41.2,25.1 36.3,26.4 31.6,26.4 26.9,27.2 22.1,26.7 20.2,27.1 15.7,28.6 12.7,28.2 11.0,28.7 9.3,27.7 8.3,24.8 8.3,20.9 9.0,16.8 " \n style="fill:none;stroke:darkslategray;stroke-width:0.5;stroke-linecap:round;stroke-linejoin:round"/> \n </g>' 
        ring_gland_dorsal_perspective_05 = '<g id="ring gland perspective" transform="scale(1.5) translate(-51,-4)"> \n <polygon points="15,18 13,17 11,15 10,13 5,11 3,12 1,10 0,8 1,6 3,4 7,3 10,3 13,2 17,0 20,0 20,0 23,0 24,2 24,5 23,8 22,10 18,10 17,10 17,12 16,14 16,16 " style="fill:#D8D9D9;stroke-width:0;stroke-linecap:round;stroke-linejoin:round"/> \n </g>'        
        ring_gland_dorsal_perspective_09 = '<g id="ring gland perspective" transform="scale(0.094) translate(-818,-220)"> \n <polygon points="249,25 257,21 266,16 275,13 283,9 292,7 300,5 301,5 302,5 316,2 330,0 343,0 355,1 366,3 375,6 384,11 390,17 394,24 396,33 397,45 395,59 391,77 387,96 381,115 375,132 369,144 363,152 356,157 350,161 343,163 335,163 327,162 318,161 313,159 310,163 303,167 298,170 294,173 293,173 292,177 289,183 285,187 284,187 281,194 280,196 279,199 277,205 274,211 271,218 268,223 264,228 262,229 263,230 262,237 265,241 270,254 273,270 274,287 274,303 271,318 267,332 261,344 261,352 259,366 256,380 252,392 247,403 242,410 235,415 227,415 219,411 215,407 215,407 210,405 205,400 200,394 194,387 189,380 185,374 182,367 179,362 179,361 177,359 171,348 167,339 165,332 165,326 165,326 164,324 162,320 160,316 159,313 158,310 157,308 157,306 158,303 158,303 155,299 151,292 147,289 141,286 135,282 128,278 128,278 125,279 120,279 115,279 111,277 107,274 104,271 101,268 99,264 96,261 95,260 87,256 78,252 68,248 60,244 56,241 54,241 44,236 35,230 28,225 21,218 15,212 10,205 5,197 2,190 1,182 1,177 1,175 0,163 2,151 8,141 16,132 26,123 38,116 51,111 64,106 77,103 88,101 98,101 107,101 115,104 118,105 120,103 131,95 142,86 154,77 167,69 181,61 195,54 210,47 217,44 229,37 243,29 " style="fill:#9D9E9E;stroke-width:0"/> \n </g> \n'

        print('Writing SVG to file %s' % self.filepath)
        f = open(self.filepath, 'w', encoding='utf-8')  
        f.write(self.svg_header)

        to_process = []
        if self.which_neurons == 'Active':
            if re.search('#.*',bpy.context.active_object.name) and bpy.context.active_object.type == 'CURVE':                
                to_process.append(bpy.context.active_object)
            else:
                print('ERROR: Active Object is not a Neuron')
                self.report({'ERROR'},'Active Object not a Neuron!')                
                return
        elif self.which_neurons == 'Selected':
            for obj in bpy.context.selected_objects:
                if re.search('#.*',obj.name) and obj.type == 'CURVE':                    
                    to_process.append(obj) 
        elif self.which_neurons == 'All':
            for obj in bpy.data.objects:
                if re.search('#.*',obj.name) and obj.type == 'CURVE':                    
                    to_process.append(obj) 
        
        #Sort objects in to_process by color
        sorted_by_color = {}
        for obj in to_process:           
            try:                
                color = str(obj.active_material.diffuse_color)
            except:
                color = 'None'
            if color not in sorted_by_color:
                sorted_by_color[color] = []
            sorted_by_color[color].append(obj)
        
        to_process_sorted = []
        for color in sorted_by_color:
            to_process_sorted += sorted_by_color[color]
        
        neuron_count = 0

        for neuron in to_process_sorted:            
            if re.search('#.*',neuron.name) and neuron.type == 'CURVE':
                neuron_count += 1
            
        colormap = ColorCreator.random_colors(neuron_count)
        print ( str ( neuron_count) + ' colors created')
        
        if self.use_bevel is True:
            base_line_width = self.line_width        

        for neuron in to_process_sorted:            
            ### Create List of Lines
            polyline_front = []
            polyline_top = []
            polyline_lateral = []
            polyline_persp = []
            
            polyline_ratios = []
            
            lines_front_by_density = []
            lines_top_by_density = []
            lines_lateral_by_density = []
            lines_persp_by_density = []
            
            soma_found = False
            
            ### ONLY curves starting with a # will be exported
            if re.search('#.*',neuron.name) and neuron.type == 'CURVE':            
                if self.random_colors is True:
                    #color = 'rgb' + str((random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)))
                    color = 'rgb' + str(colormap[0])
                    colormap.pop(0)
                elif self.colors_from_mesh is True:
                    try:
                        #Take material in first mat slot
                        mat = neuron.material_slots[0].material
                        mesh_color = mat.diffuse_color
                        color = 'rgb' + str((
                                             int(mesh_color[0]*255),
                                             int(mesh_color[1]*255), 
                                             int(mesh_color[2]*255)
                                           ))   
                    except:
                        print('WARNING: Unable to retrieve color for ', neuron.name , '- using black!')
                        color = 'rgb' + str((0, 0, 0)) 
                else:
                    ### Standard color
                    color = 'rgb' + str((0, 0, 0)) 
                    
                if self.use_bevel is True:
                    self.line_width = neuron.data.bevel_depth/0.007 * base_line_width
                
                    
                if self.color_by_density is True and self.object_for_density == 'Synapses':   
                    print('Retrieving Connectors for Color by Density..')
                    skid = re.search('#(.*?) ',neuron.name).group(1)
                    node_data = get_3D_skeleton ( [skid], remote_instance, connector_flag = 1, tag_flag = 0 )[0]
                    
                    #Reset density_data for every neuron!
                    density_data = []
                    
                    #Check if filtering of connectors is requested
                    apply_filter = False
                    for entry in filter_for_synapses:
                        if entry != 'incoming' and entry != 'outgoing':
                            apply_filter = True
                            
                    #Filter no filter is set, just add all connectors to density data
                    if apply_filter is False:                    
                        for connection in node_data[1]:
                            if 'outgoing' in filter_for_synapses or 'incoming' in filter_for_synapses:
                                if connection[2] == 0 and 'outgoing' not in filter_for_synapses:
                                    continue
                                if connection[2] == 1 and 'incoming' not in filter_for_synapses:
                                    continue
                                

                            density_data.append((
                                               round(connection[3]/10000,3),
                                               round(connection[5]/10000,3),
                                               round(connection[4]/-10000,3)
                                               ))
                    else:
                        connector_postdata = {}
                        index = 0
                        connector_tags = {}
                        skids_to_check = []
                        
                        #Generate list of connector ids first
                        for connection in node_data[1]:
                            if 'outgoing' in filter_for_synapses or 'incoming' in filter_for_synapses:
                                if connection[2] == 0 and 'outgoing' not in filter_for_synapses:
                                    continue
                                if connection[2] == 1 and 'incoming' not in filter_for_synapses:
                                    continue
                            connector_tag = 'connector_ids[%i]' % index
                            connector_postdata[connector_tag] = connection[1]
                            index += 1
                           
                        remote_connector_url = remote_instance.get_connectors_url( project_id )
                        print( "Retrieving Info on Connectors for Filtering..." )        
                        connector_data = remote_instance.fetch( remote_connector_url , connector_postdata )                    
                        print("Connectors retrieved: ", len(connector_data))
                        
                        #Get neuron names of upstream and downstream neurons of this connector                                
                        for connector in connector_data:
                            skids_to_check.append(connector[1]['presynaptic_to'])
                            for entry in connector[1]['postsynaptic_to']:
                                skids_to_check.append(entry)
                        names_dict = get_neuronnames(skids_to_check)                    
                        
                        #Create dict for each connector containing the connected neurons' names
                        for connector in connector_data:
                            connector_tags[connector[0]] = []
                            if connector[1]['presynaptic_to'] != None: 
                                connector_tags[connector[0]].append(names_dict[str(connector[1]['presynaptic_to'])])
                            for entry in connector[1]['postsynaptic_to']:
                                if entry != None:
                                    connector_tags[connector[0]].append(names_dict[str(entry)])                        
                        
                        #Filter connectors before adding to density data
                        matches = []                                                
                        exclude_matches = []
                        for connection in node_data[1]:
                            if 'outgoing' in filter_for_synapses or 'incoming' in filter_for_synapses:
                                if connection[2] == 0 and 'outgoing' not in filter_for_synapses:
                                    continue
                                if connection[2] == 1 and 'incoming' not in filter_for_synapses:
                                    continue
                            
                            include_connector = False
                            exclude_connector = False
                            
                            #Add 'all' to filter to have all connectors be automatically included
                            #this is important if you want to just exclude a subset by also adding '!exclusion tag'
                            #e.g. ['incoming','all','!Hugin PC'] will give you all synapses except the ones that are
                            #taged 'Hugin PC'
                            if 'all' in filter_for_synapses:
                                include_connector = True

                            for entry in filter_for_synapses:
                                if entry != 'incoming' and entry != 'outgoing' and entry != 'all':
                                    if entry.startswith('!'):
                                        tag = entry[1:]
                                    else:
                                        tag = entry                                        
                                    for neuron_name in connector_tags[connection[1]]:
                                        if tag in neuron_name:
                                            if entry.startswith('!'):
                                                exclude_connector = True
                                                exclude_matches.append(neuron_name)
                                            else:
                                                include_connector = True
                                                matches.append(neuron_name)
                            
                            if include_connector is True and exclude_connector is False:
                                density_data.append((
                                               round(connection[3]/10000,3),
                                               round(connection[5]/10000,3),
                                               round(connection[4]/-10000,3)
                                               ))
                        print('Found match(es) in connected neuron(s): ', set(matches))
                        print('Found exlucsion match(es) in connected neuron(s): ', set(exclude_matches))                        
                                                       
                    
                if self.color_by_inputs_outputs is True:
                    #Retrieve list of connectors for this neuron           
                    skid = re.search('#(.*?) ',neuron.name).group(1)
                    print('Retrieving connector data for skid %s...' % skid)                    
                    node_data = get_3D_skeleton ( [skid], remote_instance, connector_flag = 1, tag_flag = 0 )[0]
                    
                    list_of_synapses = {}
                    
                    for connection in node_data[1]:
                        treenode_id = connection[0]
                        if treenode_id not in list_of_synapses:
                            list_of_synapses[treenode_id] = {}
                            list_of_synapses[treenode_id]['inputs'] = 0
                            list_of_synapses[treenode_id]['outputs'] = 0
                            
                        if connection[2] == 0:
                            list_of_synapses[treenode_id]['outputs'] += 1
                        else:
                            list_of_synapses[treenode_id]['inputs'] += 1
                            
                    for node in node_data[0]:
                        treenode_id = node[0]
                        if treenode_id in list_of_synapses:
                            list_of_synapses[treenode_id]['coords'] = (
                                                                       round(node[3]/10000,2),
                                                                       round(node[5]/10000,2),
                                                                       round(node[4]/-10000,2)
                                                                       )
                                                                       
                    print('Treenodes with synapses found: ', len(list_of_synapses))
                    
                    #Find closest treenode in neuron to treenode from list_of_synapses 
                    #Keep in mind that resampling might have removed treenodes, so you might not get 100% match                      
                    #Also: does not take distance along arbor into account!
                    
                    #Fill polyline_ratios first
                    for i in range(len(neuron.data.splines)):
                        polyline_ratios.append([0,0])                   
                    
                    #print(rounded_co)
                    #Assign each treenode=synapse to their spline (based on distance to closest spline)
                    for treenode in list_of_synapses:
                        closest_dist = 999999
                        treenode_co = list_of_synapses[treenode]['coords']
                        for i in range(len(neuron.data.splines)):
                            for k in range(len(neuron.data.splines[i].points)):
                                node_co = neuron.data.splines[i].points[k].co
                                dist = math.sqrt(
                                                  (treenode_co[0]-node_co[0])**2 +
                                                  (treenode_co[1]-node_co[1])**2 +
                                                  (treenode_co[2]-node_co[2])**2
                                                 )
                                if dist < closest_dist:                                    
                                    closest_dist = dist
                                    closest_spline = i
                                    
                        polyline_ratios[closest_spline][0] += list_of_synapses[treenode]['inputs']
                        polyline_ratios[closest_spline][1] += list_of_synapses[treenode]['outputs']
                    
                    max_inputs_per_spline = 0 
                    max_outputs_per_spline = 0    
                    for i in range(len(polyline_ratios)):
                        if polyline_ratios[i][0] > max_inputs_per_spline:
                            max_inputs_per_spline = polyline_ratios[i][0]
                        if polyline_ratios[i][1] > max_outputs_per_spline:
                            max_outputs_per_spline = polyline_ratios[i][1]
                            
                    #Create colors:
                    polyline_ratio_colors = []
                    for i in range(len(polyline_ratios)):
                        if polyline_ratios[i][0] != 0 or polyline_ratios[i][1] != 0:
                            #Ratio = # of outputs - # of inputs / (total # of synapses)
                            ratio = (polyline_ratios[i][1]-polyline_ratios[i][0])/ (polyline_ratios[i][1]+polyline_ratios[i][0])
                            """
                            ratio = (polyline_ratios[i][1]-polyline_ratios[i][0])
                            if ratio < 0:
                                ratio = ratio/max_inputs_per_spline
                            if ratio > 0:
                                ratio = ratio/max_outputs_per_spline
                                
                            """    
                            #ratio ranges normally from -1 to 1 but for the color we increase it to 0-2
                                    #therefore ratio of -1 = start_rgb = only inputs; +1 = end_rgb = only outputs 
                            polyline_ratio_colors.append('rgb' + str((
                                            int(ratio_gradient['start_rgb'][0] + (ratio_gradient['end_rgb'][0] - ratio_gradient['start_rgb'][0])/2 * (ratio+1)),  
                                            int(ratio_gradient['start_rgb'][1] + (ratio_gradient['end_rgb'][1] - ratio_gradient['start_rgb'][1])/2 * (ratio+1)),                         
                                            int(ratio_gradient['start_rgb'][2] + (ratio_gradient['end_rgb'][2] - ratio_gradient['start_rgb'][2])/2 * (ratio+1))                             
                                                        )))
                        else:
                            polyline_ratio_colors.append('rgb(0,0,0)')     

                ### File Lists of Lines
                max_density = 0
                for spline in neuron.data.splines:                                        
                    polyline_front_temp = ''
                    polyline_top_temp = ''
                    polyline_lateral_temp = ''
                    polyline_persp_temp = ''                    

                    
                    for source in range((len(spline.points))): #go from first point to the second last
                        target = source + 1                        
                        
                        if "Perspective-Dorsal" in self.views_to_export:
                            persp_scale_factor = round((y_center-spline.points[source].co[1]) *10,2)                                                                                                
                            
                            #Attention!: for dorsal view we want to look at it from behind at an angle -> invert X pos
                            x_persp = str(round(spline.points[source].co[0] * -10,2) + (x_persp_offset * persp_scale_factor))
                            y_persp = str(round(spline.points[source].co[2] * -10,2) + (y_persp_offset * persp_scale_factor))
                            
                            if target < len(spline.points):
                                #Try creating coordinates of end point of this edge for color_by_density (will fail if target > length of spline)
                                x_persp_targ = str(round(spline.points[target].co[0] * -10,2) + (x_persp_offset * persp_scale_factor))
                                y_persp_targ = str(round(spline.points[target].co[2] * -10,2) + (y_persp_offset * persp_scale_factor))
                            
                        if 'Perspective-Front' in self.views_to_export:                                                
                            persp_scale_factor = round(spline.points[source].co[1] *10,1)                                              
                            
                            x_persp = str(round(spline.points[source].co[0] * 10,2) + (x_persp_offset * persp_scale_factor))
                            y_persp = str(round(spline.points[source].co[2] * -10,2) + (y_persp_offset * persp_scale_factor))
                            
                            if target < len(spline.points):
                                #Try creating coordinates of end point of this edge for color_by_density (will fail if target > length of spline)                                
                                x_persp_targ = str(round(spline.points[target].co[0] * 10,2) + (x_persp_offset * persp_scale_factor))
                                y_persp_targ = str(round(spline.points[target].co[2] * -10,2) + (y_persp_offset * persp_scale_factor))
                            
                        polyline_front_temp += str(round(spline.points[source].co[0] *10,2)) \
                                              +','+ str(round(spline.points[source].co[2]*-10,2)) + ' '
                        polyline_top_temp += str(round(spline.points[source].co[0] *10,2)) \
                                            +','+ str(round(spline.points[source].co[1]*-10,2)) + ' '
                        polyline_lateral_temp += str(round(spline.points[source].co[1] *10,2)) \
                                                +','+ str(round(spline.points[source].co[2]*-10,2)) + ' '
                        if 'Perspective' in self.views_to_export:
                            polyline_persp_temp += x_persp +','+ y_persp + ' '
                        
                        #Skip at last index
                        if target >= len(spline.points):
                            continue
                                                
                        if self.color_by_density is True:
                            #Get # of nodes around this edge
                            start_co = spline.points[target].co
                            end_co = spline.points[source].co
                            density_count = 0
                            #print(start_co[0:2],end_co[0:2],'\n')
                            for node in density_data:                                
                                dist1 = math.sqrt(
                                                  (start_co[0]-node[0])**2 +
                                                  (start_co[1]-node[1])**2 +
                                                  (start_co[2]-node[2])**2
                                                 )
                                dist2 = math.sqrt(
                                                  (end_co[0]-node[0])**2 +
                                                  (end_co[1]-node[1])**2 +
                                                  (end_co[2]-node[2])**2
                                                 )
                                if dist1 < self.proximity_radius_for_density or dist2 < self.proximity_radius_for_density:
                                    density_count += 1   
                            
                            #Max_density is updated if higher value is found        
                            if density_count > max_density:
                                max_density = density_count
                                    
                            lines_front_by_density.append((
                                                               str(round(spline.points[source].co[0] *10,2)) \
                                                               +','+ str(round(spline.points[source].co[2]*-10,2)) + ' ' \
                                                               + str(round(spline.points[target].co[0] *10,2)) \
                                                               +','+ str(round(spline.points[target].co[2]*-10,2)) + ' ' \
                                                               , density_count
                                                               )
                                                              )
                            lines_top_by_density.append((
                                                               str(round(spline.points[source].co[0] *10,2)) \
                                                               +','+ str(round(spline.points[source].co[1]*-10,2)) + ' ' \
                                                               + str(round(spline.points[target].co[0] *10,2)) \
                                                               +','+ str(round(spline.points[target].co[1]*-10,2)) + ' ' \
                                                               , density_count
                                                               )
                                                              )
                            lines_lateral_by_density.append((
                                                               str(round(spline.points[source].co[1] *10,2)) \
                                                               +','+ str(round(spline.points[source].co[2]*-10,2)) + ' ' \
                                                               + str(round(spline.points[target].co[1] *10,2)) \
                                                               +','+ str(round(spline.points[target].co[2]*-10,2)) + ' ' \
                                                               , density_count
                                                               )
                                                              )
                            if 'Perspective' in self.views_to_export:
                                lines_persp_by_density.append((
                                                                   x_persp +','+ y_persp + ' ' \
                                                                   + x_persp_targ +','+ y_persp_targ + ' '
                                                                   , density_count
                                                                   )
                                                                  )
    
                    polyline_front.append(polyline_front_temp) 
                    polyline_top.append(polyline_top_temp)  
                    polyline_lateral.append(polyline_lateral_temp) 
                    polyline_persp.append(polyline_persp_temp) 
                
                #If manual_max has been set, override previously calculated max
                if manual_max != None:
                    print(neuron.name,' - max density of ', max_density, ' overriden by manual density: ', manual_max)
                    max_density = manual_max
                else:    
                    print(neuron.name,' - max density: ', max_density)
                    
                ### Find soma                
                search_string = 'Soma of ' + neuron.name[1:7] + '.*'
                for soma in bpy.data.objects:
                    
                    if re.search(search_string,soma.name):
                        print('Soma of %s found' % neuron.name)
                        soma_pos = soma.location
                        soma_radius = soma.dimensions[0]/2 * 10
                        soma_found = True
                        break
                        
                ### Start creating svg file here (header before for loop)
                
                if "Front" in self.views_to_export:
                    line_to_write = '<g id="%s front" transform="translate(%i,%i)">' % (neuron.name, offsetX+offsetX_for_front, offsetY+offsetY_for_front)
                    f.write(line_to_write + '\n')
            
                    ### Add neuron from front view  
                    if self.color_by_density is False:      
                        for i in range(len(polyline_front)):                            
                            if self.color_by_inputs_outputs is True:
                                color = polyline_ratio_colors[i]                           
                            
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + polyline_front[i] + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(color), str(self.line_width))
                                f.write(line_to_write + '\n')   
                            else:                                
                                point_coords = re.findall('(.*?,.*?) ',polyline_front[i])                                
                                for point in point_coords:                                    
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]                                    
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(self.line_width/5), str(color), str(color))
                                    f.write(line_to_write + '\n')                    
                    else:
                        for i in range(len(lines_front_by_density)):                           
                            density_count = lines_front_by_density[i][1]
                            coordinates = lines_front_by_density[i][0]
                            if max_density > 0 and density_count > 0:
                                density_line_width = 1/2 * self.line_width + self.line_width/max_density * density_count
                                density_color = 'rgb' + str((
                                                int(density_gradient['start_rgb'][0] + (density_gradient['end_rgb'][0] - density_gradient['start_rgb'][0])/max_density * density_count),                    
                                                int(density_gradient['start_rgb'][1] + (density_gradient['end_rgb'][1] - density_gradient['start_rgb'][1])/max_density * density_count),                         
                                                int(density_gradient['start_rgb'][2] + (density_gradient['end_rgb'][2] - density_gradient['start_rgb'][2])/max_density * density_count)                             
                                                            ))
                            else:
                                #print('No density data within given radius found!')
                                density_color = 'rgb(0,0,0)'
                                density_line_width = 1/2 * self.line_width                           
                            
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + coordinates + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(density_color), str(density_line_width))
                                f.write(line_to_write + '\n')
                                
                                """
                                x_coord = coordinates[0:coordinates.find(',')]
                                y_coord = coordinates[coordinates.find(',')+1:coordinates.find(' ')] 
                                line_to_write = '<text x="%s" y = "%s" font-size="1">\n %i \n </text>' % (x_coord,y_coord,density_count)
                                f.write(line_to_write + '\n')
                                """
                            else:
                                point_coords = re.findall('(.*?,.*?) ',coordinates)  
                                #nodes are represented twice in point_coords, b/c they are derived from start+end points from edges
                                #therefore skip every second point -> will result in last node missing if odd length                                                              
                                for point in point_coords[0:-1:2]:
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]  
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(density_line_width/5), str(density_color), str(density_color))                                            
                                    f.write(line_to_write + '\n')
                                
                                    """
                                    line_to_write = '<text x="%s" y = "%s" font-size="1">\n %i \n </text>' % (x_coord,y_coord,density_count)
                                    f.write(line_to_write + '\n')
                                    """
                        

                    ### Add soma to front view if previously found
                    if soma_found is True:
                        line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  />' \
                                        % (str(round(soma_pos[0]*10,1)),str(round(soma_pos[2]*-10,1)), str(self.basic_radius*soma_radius), str(color), str(color))
                        f.write(line_to_write + '\n')

                    if self.barplot is True and self.merge is False:
                        self.create_barplot( f, [neuron] , 0, 2 , x_factor = 1, y_factor = -1) 
                    elif self.barplot is True and self.merge is True and first_neuron is True:
                        self.create_barplot( f, to_process_sorted , 0, 2 , x_factor = 1, y_factor = -1) 


                    ### Add front brain shape
                    if self.merge is False or first_neuron is True:
                        f.write('\n' + brain_shape_front_string + '\n') 

                        if self.export_ring_gland is True:
                            f.write('\n' + ring_gland_front + '\n') 

                    line_to_write = '</g>'
                    f.write(line_to_write + '\n \n \n')                 
                
                ### Add neuron from top view
                if "Top" in self.views_to_export:
                    line_to_write = '<g id="%s top" transform="translate(%i,%i)">' \
                                     % (neuron.name, offsetX+offsetX_for_top, offsetY+offsetY_for_top)
                    f.write(line_to_write + '\n')
                    
                    if self.color_by_density is False:  
                        for i in range(len(polyline_top)):
                            if self.color_by_inputs_outputs is True:
                                color = polyline_ratio_colors[i]
                            
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + polyline_top[i] + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(color),str(self.line_width))
                                f.write(line_to_write + '\n')
                            else:                                
                                point_coords = re.findall('(.*?,.*?) ',polyline_top[i])                                
                                for point in point_coords:                                    
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]                                    
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(self.line_width/5), str(color), str(color))
                                    f.write(line_to_write + '\n')  
                    else:
                        for i in range(len(lines_top_by_density)):                           
                            density_count = lines_top_by_density[i][1]
                            coordinates = lines_top_by_density[i][0]
                            if max_density > 0 and density_count > 0:
                                density_line_width = 1/2 * self.line_width + self.line_width/max_density * density_count
                                density_color = 'rgb' + str((
                                                int(density_gradient['start_rgb'][0] + (density_gradient['end_rgb'][0] - density_gradient['start_rgb'][0])/max_density * density_count),                    
                                                int(density_gradient['start_rgb'][1] + (density_gradient['end_rgb'][1] - density_gradient['start_rgb'][1])/max_density * density_count),                         
                                                int(density_gradient['start_rgb'][2] + (density_gradient['end_rgb'][2] - density_gradient['start_rgb'][2])/max_density * density_count)                             
                                                            ))
                            else:
                                #print('No density data within given radius found!')
                                density_color = 'rgb(0,0,0)'
                                density_line_width = 1/2 * self.line_width
                                
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + coordinates + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(density_color), str(density_line_width))
                                f.write(line_to_write + '\n')
                            else:
                                point_coords = re.findall('(.*?,.*?) ',coordinates)      
                                #nodes are represented twice in point_coords, b/c they are derived from start+end points from edges
                                #therefore skip every second point -> will result in last node missing if odd length                                                          
                                for point in point_coords[0:-1:2]:
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]  
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(density_line_width/5), str(density_color), str(density_color))                                            
                                    f.write(line_to_write + '\n')                                

                    ### Add soma to top view if previously found
                    if soma_found is True:
                        line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  />' \
                                        % (str(round(soma_pos[0]*10,1)),str(round(soma_pos[1]*-10,1)), str(self.basic_radius*soma_radius), str(color), str(color))
                        f.write(line_to_write + '\n')

                    if self.barplot is True and self.merge is False:
                        self.create_barplot( f, [neuron] , 0, 1 , x_factor = 1, y_factor = -1) 
                    elif self.barplot is True and self.merge is True and first_neuron is True:
                        self.create_barplot( f, to_process_sorted , 0, 1 , x_factor = 1, y_factor = -1)
                
                    ### Add top brain shape
                    if self.merge is False or first_neuron is True:
                        f.write('\n' + brain_shape_top_string + '\n') 
                    
                        if self.export_ring_gland is True:
                            f.write('\n' + ring_gland_top + '\n')                
                    
                    line_to_write = '</g>'
                    f.write(line_to_write + '\n \n \n')
                
                ### Add neuron from perspective view
                if "Perspective" in self.views_to_export:
                    line_to_write = '<g id="%s perspective" transform="translate(%i,%i)">' \
                                     % (neuron.name, offsetX+offsetX_for_persp, offsetY+offsetY_for_persp)
                    f.write(line_to_write + '\n')
                    
                    ### Add perspective brain shape                    
                    if self.merge is False or first_neuron is True:
                        if 'Perspective-Dorsal' in self.views_to_export:                            
                            if round(self.x_persp_offset,2) == 0.5:
                                f.write('\n' + brain_shape_dorsal_perspective_05_string + '\n')
                                
                                if self.export_ring_gland is True:
                                    f.write('\n' + ring_gland_dorsal_perspective_05 + '\n')
                            
                            elif round(self.x_persp_offset,2) == 0.9:                                
                                f.write('\n' + brain_shape_dorsal_perspective_09_string + '\n')
                                
                                if self.export_ring_gland is True:
                                    f.write('\n' + ring_gland_dorsal_perspective_09 + '\n')
                    
                    if self.color_by_density is False:  
                        for i in range(len(polyline_persp)):
                            if self.color_by_inputs_outputs is True:
                                color = polyline_ratio_colors[i] 
                            
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + polyline_persp[i] + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(color),str(self.line_width))
                                f.write(line_to_write + '\n')
                            else:                                
                                point_coords = re.findall('(.*?,.*?) ',polyline_persp[i])                                
                                for point in point_coords:                                    
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]                                    
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(self.line_width/5), str(color), str(color))
                                    f.write(line_to_write + '\n')                              
                    else:
                        for i in range(len(lines_persp_by_density)):                           
                            density_count = lines_persp_by_density[i][1]
                            coordinates = lines_persp_by_density[i][0]
                            if max_density > 0 and density_count > 0:
                                density_line_width = 1/2 * self.line_width + self.line_width/max_density * density_count
                                density_color = 'rgb' + str((
                                                int(density_gradient['start_rgb'][0] + (density_gradient['end_rgb'][0] - density_gradient['start_rgb'][0])/max_density * density_count),                    
                                                int(density_gradient['start_rgb'][1] + (density_gradient['end_rgb'][1] - density_gradient['start_rgb'][1])/max_density * density_count),                         
                                                int(density_gradient['start_rgb'][2] + (density_gradient['end_rgb'][2] - density_gradient['start_rgb'][2])/max_density * density_count)                             
                                                            ))
                            else:
                                #print('No density data within given radius found!')
                                density_color = 'rgb(0,0,0)'
                                density_line_width = 1/2 * self.line_width
                                
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + coordinates + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(density_color), str(density_line_width))
                                f.write(line_to_write + '\n')
                            else:
                                point_coords = re.findall('(.*?,.*?) ',coordinates)        
                                #nodes are represented twice in point_coords, b/c they are derived from start+end points from edges
                                #therefore skip every second point -> will result in last node missing if odd length                        
                                for point in point_coords[0:-1:2]:
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]  
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(density_line_width/5), str(density_color), str(density_color))                                            
                                    f.write(line_to_write + '\n')                                

                    ### Add soma to perspective view if previously found
                    if soma_found is True:
                        if "Perspective-Dorsal" in self.views_to_export:
                            persp_scale_factor = round((y_center-soma_pos[1]) *10,1)  
                            #Attention!: for dorsal view we want to look at it from behind at an angle -> invert X pos
                            x_persp = str(round(soma_pos[0]*-10,1) + x_persp_offset * persp_scale_factor)
                            y_persp = str(round(soma_pos[2]*-10,1) + y_persp_offset * persp_scale_factor)                                                                                             
                        else:                                                
                            persp_scale_factor = round(soma_pos[1] *10,1)
                            x_persp = str(round(soma_pos[0]* 10,1) + x_persp_offset * persp_scale_factor)
                            y_persp = str(round(soma_pos[2]*-10,1) + y_persp_offset * persp_scale_factor)
                        
                        line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  />' \
                                        % (x_persp,y_persp, str(self.basic_radius*soma_radius), str(color), str(color))
                        f.write(line_to_write + '\n')
                        
                    
                    line_to_write = '</g>'
                    f.write(line_to_write + '\n \n \n')
                
                
                ### Add neuron from lateral view
                if "Lateral" in self.views_to_export:
                    line_to_write = '<g id="%s lateral" transform="translate(%i,%i)">' \
                                    % (neuron.name, offsetX+offsetX_for_lateral, offsetY+offsetY_for_lateral)
                    f.write(line_to_write + '\n')  
                    
                    if self.color_by_density is False:  
                        for i in range(len(polyline_lateral)):
                            if self.color_by_inputs_outputs is True:
                                color = polyline_ratio_colors[i]
                            
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + polyline_lateral[i] + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                 % (str(color),str(self.line_width))
                                f.write(line_to_write + '\n')
                            else:                                
                                point_coords = re.findall('(.*?,.*?) ',polyline_lateral[i])                                
                                for point in point_coords:                                    
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]                                    
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(self.line_width/5), str(color), str(color))
                                    f.write(line_to_write + '\n')                                  
                    else:
                        for i in range(len(lines_lateral_by_density)):                           
                            density_count = lines_lateral_by_density[i][1]
                            coordinates = lines_lateral_by_density[i][0]
                            if max_density > 0 and density_count > 0:
                                density_line_width = 1/2 * self.line_width + self.line_width/max_density * density_count
                                density_color = 'rgb' + str((
                                                int(density_gradient['start_rgb'][0] + (density_gradient['end_rgb'][0] - density_gradient['start_rgb'][0])/max_density * density_count),                    
                                                int(density_gradient['start_rgb'][1] + (density_gradient['end_rgb'][1] - density_gradient['start_rgb'][1])/max_density * density_count),                         
                                                int(density_gradient['start_rgb'][2] + (density_gradient['end_rgb'][2] - density_gradient['start_rgb'][2])/max_density * density_count)                             
                                                            ))
                            else:
                                #print('No density data within given radius found!')
                                density_color = 'rgb(0,0,0)'
                                density_line_width = 1/2 * self.line_width
                                
                            if self.export_as_points is False:
                                line_to_write = '<polyline points="' + coordinates + '"\n' \
                                                'style="fill:none;stroke:%s;stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' \
                                                % (str(density_color), str(density_line_width))
                                f.write(line_to_write + '\n')
                            else:
                                point_coords = re.findall('(.*?,.*?) ',coordinates)                                
                                #nodes are represented twice in point_coords, b/c they are derived from start+end points from edges
                                #therefore skip every second point -> will result in last node missing if odd length
                                for point in point_coords[0:-1:2]:
                                    x_coord = point[0:point.find(',')]
                                    y_coord = point[point.find(',')+1:]  
                                    line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0"  />' \
                                            % (x_coord,y_coord, str(density_line_width/5), str(density_color), str(density_color))                                            
                                    f.write(line_to_write + '\n')                                

                    ### Add soma to lateral view if previously found
                    if soma_found is True:
                        line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.1"  />' \
                                        % (str(round(soma_pos[1]*10,1)),str(round(soma_pos[2]*-10,1)), str(self.basic_radius*soma_radius), \
                                        str(color), str(color))
                        f.write(line_to_write + '\n')

                    if self.barplot is True and self.merge is False:
                        self.create_barplot( f, [neuron] , 1 , 2 , x_factor = 1, y_factor = -1) 
                    elif self.barplot is True and self.merge is True and first_neuron is True:
                        self.create_barplot( f, to_process_sorted , 1 , 2 , x_factor = 1, y_factor = -1)   
                
                    ### Add lateral brain shape
                    if self.merge is False or first_neuron is True:
                        f.write('\n' + brain_shape_lateral_string + '\n')                          
                    
                        if self.export_ring_gland is True:                    
                            f.write('\n' + ring_gland_lateral + '\n')                  
                        
                    line_to_write = '</g>'
                    f.write(line_to_write + '\n \n \n') 
        
                ### Add neuron name to svg/ create legend if merge is True
                if self.merge is False and self.add_neuron_name is True:
                    f.write('\n <g id="name"> \n <text x="%i" y = "140" font-size="8">\n %s \n</text> \n </g> \n'
                                    % (10+offsetX,neuron.name) )
                elif self.merge is True and self.add_neuron_name is True:
                    line_to_write = '\n <g id="name"> \n <text x="260" y = "%s" fill="%s" font-size="8"> \n %s \n </text> \n' \
                                    % ( str(offsetY_forText+5), 
                                        str(color), 
                                        str(neuron.name)
                                        )                
                    f.write(line_to_write + '\n')
                    f.write('</g> \n \n')                
                    offsetY_forText += 10 
                    
                ### Add density info
                if self.color_by_density is True:
                   #Calculated volume of searched area: 4/3 * pi * radius**3
                   #Conversion from Blender Units into um: * 10.000 / 1.000 -> * 10
                   search_volume = 4/3 * math.pi * (self.proximity_radius_for_density * 10)**3
                   f.write('\n <g id="density info"> \n <text x="%i" y = "150" font-size="6">\n Density data - total nodes: %i max density: %i [per %i um3] / \n </text> \n </g> \n'
                                        % ( 15+offsetX,
                                            len(density_data),
                                            max_density,
                                            round(search_volume,1)))
                   
                   #Circle has size of proximity radius - for debugging
                   """
                   f.write('<circle cx="50" cy="150" r="%s" fill="None" stroke="rgb(0,0,0)" stroke-width="0.1"  />' \
                                        % str(self.proximity_radius_for_density * 10))
                   """
                first_neuron = False 
                offsetX += offsetIncrease

        ### Finish svg file with footer        
        f.write(self.svg_end)
        f.close()        
        print('Export finished')
        self.report({'INFO'},'Export finished. See console for details')
        
        #Write back line_width in case it has been changed due to bevel_depth
        if self.use_bevel is True:
            self.line_width = base_line_width
        
        return{'FINISHED'} 

    
    def create_barplot(self, f, neurons_to_plot , x_coord, y_coord, x_factor = 1, y_factor = -1):
        """
        Creates Barplot for given svg based on distribution of nodes
        """

        to_plot = []

        #First filter neurons_to_plot for non neurons
        for neuron in neurons_to_plot:
            if re.search('#.*',neuron.name) and neuron.type == 'CURVE': 
                to_plot.append(neuron)

        print(to_plot,x_coord,y_coord)

        #Bin width is in 1/1000 nm = um
        bin_width = 2
        scale_factor = 0.2

        all_nodes = { 'x' : [] , 'y' : [] }

        for e in to_plot:
            #Create list of all points for all splines
            nodes_y = [round( n.co[y_coord] * 10 * y_factor , 1 ) for sp in e.data.splines for n in sp.points]
            nodes_x = [round( n.co[x_coord] * 10 * x_factor , 1 ) for sp in e.data.splines for n in sp.points]
            
            all_nodes['x'] += nodes_x
            all_nodes['y'] += nodes_y

        #First get min and max values and bin numbers over all neurons 
        all_max_x = max(all_nodes['x']+[0])
        all_max_y = max(all_nodes['y']+[0])        

        all_min_x = min(all_nodes['x'] + [ max(all_nodes['x'] + [0] ) ] )
        all_min_y = min(all_nodes['y'] + [ max(all_nodes['y'] + [0] ) ] )

        #Everthing starts with 
        bin_sequences = {'x': list ( np.arange( all_min_x, all_max_x, bin_width ) ),
                        'y': list ( np.arange( all_min_y, all_max_y, bin_width ) )
                        }

        #Create Histograms
        histograms = { e : {} for e in to_plot }
        for e in to_plot:
            nodes_y = [round( n.co[y_coord] * 10 * y_factor , 1 ) for sp in e.data.splines for n in sp.points]
            nodes_x = [round( n.co[x_coord] * 10 * x_factor , 1 ) for sp in e.data.splines for n in sp.points]

            histograms[e]['x'] , bin_edges_x_pre = np.histogram( nodes_x, bin_sequences['x'] )
            histograms[e]['y'] , bin_edges_y_pre = np.histogram( nodes_y, bin_sequences['y'] )        

        #Now calculate mean and stdevs over all neurons
        means = {}
        stdevs = {}     
        variances = {}   
        stderror = {}
        for d in ['x','y']:
            #print('!!!!',d)
            means[d] = []
            stdevs[d] = []
            variances[d] = []
            stderror[d] = []
            #print([histograms[n][d] for n in neurons_to_plot],bin_sequences[d])
            for i in range ( len( bin_sequences[d] ) - 1 ):                
                #conversion to int from numpy.int32 is important because statistics.stdev fails otherwise
                v = [ int ( histograms[n][d][i] ) for n in to_plot ]                
                means[d].append ( sum ( v ) / len ( v ) )
                #print(d,i,v,means[d],type(v[0]))
                if len ( to_plot ) > 1:
                    stdevs[d].append( statistics.stdev ( v ) )  
                    variances[d].append( statistics.pvariance ( v ) )
                    stderror[d].append( math.sqrt( statistics.pvariance ( v ) ) )
                    #print(v, sum ( v ) / len ( v ), math.sqrt( statistics.pvariance ( v ) ))

        #!!!!!
        #This defines which statistical value to use:
        #Keep in mind that stdev is probably the best parameter to use
        stats = stdevs

        #Now start creating svg:            
        line_to_write = '<g id="Barplot" transform="translate(0,0)">' 
        f.write(line_to_write + '\n')

        f.write('<g id="x-axis">')
        #write horizontal barplot
        for e,b in enumerate ( means['x'] ):
            #Inputs
            f.write( '<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,255,0)" stroke-width="0"/> \n' \
                    % ( bin_sequences['x'][e], 0,
                        bin_width,
                        b * scale_factor
                        )
                    )

        #Error bar
        for e,b in enumerate ( means['x'] ):
            if len ( to_plot ) > 1:
                if stats['x'][e] != 0:
                    f.write('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:0.25" /> \n' \
                        % ( bin_sequences['x'][e] + 1/2 * bin_width, ( b * scale_factor ) + ( stats['x'][e] * scale_factor ),
                            bin_sequences['x'][e] + 1/2 * bin_width, ( b * scale_factor ) - ( stats['x'][e] * scale_factor )
                            ) 
                        )        

        #horizontal line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( all_min_x , 0,
                            all_max_x , 0                                       
                           )
        f.write(line_to_write + '\n')

        f.write('</g>')

        f.write('<g id="y-axis">')

        #write vertical barplot
        for e,b in enumerate(means['y']):
            #Inputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,255,0)" stroke-width="0"/> \n' \
                    % ( 0 , bin_sequences['y'][e],
                        b * scale_factor,
                        bin_width
                        )
                    )

        #Error bar
        for e,b in enumerate(means['y']):
            if len ( to_plot ) > 1:
                if stats['y'][e] != 0:
                    f.write('<line x1="%f" y1="%f" x2="%f" y2="%f" style="stroke:rgb(0,0,0);stroke-width:0.25" /> \n' \
                        % ( ( b * scale_factor ) + ( stats['y'][e] * scale_factor ), bin_sequences['y'][e] + 1/2 * bin_width, 
                            ( b * scale_factor ) - ( stats['y'][e] * scale_factor ), bin_sequences['y'][e] + 1/2 * bin_width
                            ) 
                        )

        #vertical line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( 0 , all_min_y,
                            0 , all_max_y
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')

        #Bin size bar
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( all_max_x + 10 , 0 ,
                            all_max_x + 10 + bin_width , 0                                       
                           )
        line_to_write += '<text x="%i" y = "%i" font-size="5"> \n %s \n </text>' \
                        % ( all_max_x + 10,
                            - 1,
                            str(bin_width) + ' um'

                            )
        f.write(line_to_write + '\n')

        #Axis scale
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( all_max_x + 10 + bin_width, 0 ,
                            all_max_x + 10 + bin_width, 5                                       
                           )
        line_to_write += '<text x="%i" y = "%f" font-size="5"> \n %s \n </text>' \
                        % ( all_max_x + 12 + bin_width, 
                            4,                                        
                            str(5 / scale_factor) + ' nodes'
                            )
        f.write(line_to_write + '\n')

        line_to_write = '</g>' 
        f.write(line_to_write + '\n')

        """
        line_to_write = '<g id="Barplot" transform="translate(0,0)">'
        f.write(line_to_write + '\n')
        barplot_y_data = []
        barplot_x_data = []

        #Create list of all points for all splines
        nodes = [n.co for sp in splines for n in sp.points]

        #Gather coordinates of nodes
        for n in nodes:
            barplot_y_data.append( round(n[y_coord] * 10 * y_factor, 1) )
            barplot_x_data.append( round(n[x_coord] * 10 * x_factor, 1) )

        #Make sure that there is at least 1 bin!
        # max(..._data_...) will fail if array is empty!
        max_barplot_x_data = max(barplot_x_data)
        max_barplot_y_data = max(barplot_y_data)

        min_barplot_x_data = min(barplot_x_data)
        min_barplot_y_data = min(barplot_y_data)
        
        x_bins =  max([ int ( ( max_barplot_x_data - min_barplot_x_data ) / bin_width ) ,1])
        y_bins =  max([ int ( ( max_barplot_y_data - min_barplot_x_data ) / bin_width ) ,1])
        
        
        hist_x , bin_edges_x = np.histogram( barplot_x_data, x_bins )
        hist_y , bin_edges_y = np.histogram( barplot_y_data, y_bins )        

        f.write('<g id="x-axis">')        

        #write horizontal barplot
        for e,b in enumerate(hist_x):
            #Inputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,255,0)" stroke-width="0"/> \n' \
                    % ( bin_edges_x[e], 0,
                        bin_width,
                        b * scale_factor
                        )
                    )

        
        #This plots a line on top of the barplot
        #line_plot_coords = [(x + (0.5 * bin_width) , y * scale_factor ) for x,y in zip(bin_edges_x,hist_x)]
        #f.write('<path d="M %i,%i L %s" stroke="rgb(0,255,0)" stroke-width="0.5" fill="none"/> \n' \
        #         % (line_plot_coords[0][0],line_plot_coords[0][1],
        #            " ".join(str(p)[1:-1] for p in line_plot_coords[1:])
        #            )
        #        )
        


        #horizontal line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( min_barplot_x_data , 0,
                            max_barplot_x_data , 0                                       
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')
        
        f.write('<g id="y-axis">')

        #write vertical barplot
        for e,b in enumerate(hist_y):
            #Inputs
            f.write('<rect x="%f" y="%f" width="%f" height="%f" fill="rgb(0,255,0)" stroke-width="0"/> \n' \
                    % ( 0, bin_edges_y[e],
                        b * scale_factor,
                        bin_width
                        )
                    )        

        #vertical line
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/>' \
                        % ( 0 , min_barplot_y_data,
                            0 , max_barplot_y_data 
                           )
        f.write(line_to_write + '\n') 

        f.write('</g>')

        #Bin size bar
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( max_barplot_x_data + 10 , 0 ,
                            max_barplot_x_data + 10 + bin_width , 0                                       
                           )
        line_to_write += '<text x="%i" y = "%i" font-size="5"> \n %s \n </text>' \
                        % ( max_barplot_x_data + 10,
                            - 1,
                            str(bin_width) + ' um'

                            )
        f.write(line_to_write + '\n')

        #Axis scale
        line_to_write ='<path d="M%f,%f L%f,%f" stroke="rgb(0,0,0)" stroke-width="0.5"/> \n' \
                        % ( max_barplot_x_data + 10 + bin_width, 0 ,
                            max_barplot_x_data + 10 + bin_width, 5                                       
                           )
        line_to_write += '<text x="%i" y = "%f" font-size="5"> \n %s \n </text>' \
                        % ( max_barplot_x_data + 12 + bin_width, 
                            4,                                        
                            str(5 / scale_factor) + ' nodes'
                            )
        f.write(line_to_write + '\n')   


        line_to_write = '</g>' 
        f.write(line_to_write + '\n')

        """
    

class Create_Mesh (Operator):
    """Class used to instance neurons"""  
    bl_idname = "create.new_neuron"  
    bl_label = "Create New Neuron"  

    def make_connector_spheres (neuron_name, connectors_post, connectors_pre, connectors_weight, connector_color = (0,0,0), basic_radius = 0.01, unify_materials = True):
        ### Takes Connector data and create spheres in layer 3!!!
        ### For Downstream targets: sphere radius refers to # of targets
        print('Creating connector meshes')   
        start_creation = time.clock()
         
        for connector in connectors_post:
            #print('Creating connector %s' % connectors_post[connector]['id']) 
            if basic_radius != -1:   
                co_size = basic_radius * connectors_weight[connectors_post[connector]['id']]    
            else:
                co_size = 0.01
            co_loc = connectors_post[connector]['coords']                
            connector_pre_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=6, size=co_size, view_align=False, \
                                                                    enter_editmode=False, location=co_loc, rotation=(0, 0, 0), \
                                                                    layers=(False, False, True, False, False, False, False, False, \
                                                                    False, False, False, False, False, False, False, False, False, \
                                                                    False, False, False))            
            bpy.context.active_object.name = 'Post_Connector %s of %s'  % (connectors_post[connector]['id'], neuron_name)            
            bpy.ops.object.shade_smooth()                        
            
            if unify_materials is False:
                Create_Mesh.assign_material (bpy.context.active_object, 'PreSynapses_Mat of' + neuron_name, connector_color[0] , connector_color[1] , connector_color[2])        
            else:
                Create_Mesh.assign_material (bpy.context.active_object, None , connector_color[0] , connector_color[1] , connector_color[2])        

        for connector in connectors_pre:
            #print('Creating connector %s' % connectors_pre[connector]['id']) 
            if basic_radius != -1:
                co_size = basic_radius
            else:
                co_size = 0.01
            co_loc = connectors_pre[connector]['coords']                
            connector_pre_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=6, size=co_size, view_align=False, \
                                                                    enter_editmode=False, location=co_loc, rotation=(0, 0, 0), \
                                                                    layers=(False, False, True, False, False, False, False, False, \
                                                                    False, False, False, False, False, False, False, False, False, \
                                                                    False, False, False))            
            bpy.context.active_object.name = 'Pre_Connector %s of %s'  % (connectors_pre[connector]['id'], neuron_name)            
            bpy.ops.object.shade_smooth()                        
            
            if unify_materials is False:
                Create_Mesh.assign_material (bpy.context.active_object, 'PostSynapses_Mat of' + neuron_name, connector_color[0] , connector_color[1] , connector_color[2])       
            else:
                Create_Mesh.assign_material (bpy.context.active_object, None , connector_color[0] , connector_color[1] , connector_color[2])       

        print('Done in ' + str(time.clock()-start_creation)+'s')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)


    def make_curve_neuron (neuron_name, root_node, nodes_dic, child_list, soma, skid = '', name = '', resampling = 1, nodes_to_keep = []):
        ### Creates Neuron from Curve data that was imported from CATMAID
        #start_creation = time.clock()        
        now = datetime.datetime.now()        
        cu = bpy.data.curves.new(neuron_name + ' Mesh','CURVE')
        ob = bpy.data.objects.new('#' + neuron_name,cu)
        bpy.context.scene.objects.link(ob)
        ob.location = (0,0,0)
        ob.show_name = True
        ob['skeleton_id'] = skid
        ob['name'] = name                
        ob['date_imported'] = now.strftime("%Y-%m-%d %H:%M")
        ob['resampling'] = resampling
        cu.dimensions = '3D'
        cu.fill_mode = 'FULL'
        cu.bevel_depth = 0.007
        cu.bevel_resolution = 5        
        neuron_material_name = 'M#' + neuron_name
        
        if len(neuron_material_name) > 59:
            neuron_material_name = neuron_material_name[0:59]
             
        print('Creating Neuron %s  (%s nodes)' %(ob.name, len(child_list)))

        for child in child_list[root_node]:
            Create_Mesh.create_spline(root_node, child, nodes_dic, child_list, cu, nodes_to_keep)

        #print('Creating mesh done in ' + str(time.clock()-start_creation)+'s')        
        Create_Mesh.assign_material (ob, neuron_material_name, random.randrange(0,100)/100 , random.randrange(0,100)/100 , random.randrange(0,100)/100)
        
        if soma != (0,0,0,0):
            soma_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, size=soma[3], view_align=False, \
                                                            enter_editmode=False, location=(soma[0],soma[1],soma[2]), rotation=(0, 0, 0), \
                                                            layers=(True, False, False, False, False, False, False, \
                                                            False, False, False, False, False, False, False, False, \
                                                            False, False, False, False, False))
            bpy.ops.object.shade_smooth()
            bpy.context.active_object.name = 'Soma of ' + neuron_name
            bpy.context.active_object['Soma of'] = skid
            
            ### Apply the same Material as for neuron tree
            Create_Mesh.assign_material (bpy.context.active_object, neuron_material_name, random.randrange(0,100)/100 , \
                                        random.randrange(0,100)/100 , random.randrange(0,100)/100)
 
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)
        

    def create_spline (start_node, first_child, nodes_dic, child_list, cu, nodes_to_keep):
        if start_node in nodes_to_keep or first_child in nodes_to_keep:
            newSpline = cu.splines.new('POLY')
                
            ### Create start node            
            newPoint = newSpline.points[-1]
            newPoint.co = (nodes_dic[start_node][0], nodes_dic[start_node][1], nodes_dic[start_node][2], 0)

        active_node = first_child
        number_of_childs = len(child_list[active_node])
        ### nodes_created is a failsafe for while loop
        nodes_created = 0
            
        while nodes_created < 10000:
            if active_node in nodes_to_keep:
                newSpline.points.add()
                newPoint = newSpline.points[-1]
                newPoint.co = (nodes_dic[active_node][0], nodes_dic[active_node][1], nodes_dic[active_node][2], 0)
            nodes_created += 1
            
            ### Stop after creation of leaf or branch node
            if number_of_childs == 0 or number_of_childs > 1:
                break
            
            active_node = child_list[active_node][0]
            #print('Number of child of node %s: %i' % (active_node, len(child_list[active_node])) )
            number_of_childs = len(child_list[active_node])

        if nodes_created >= 10000:
            print('ERROR: Creation aborted - possible infinite loop detected!')
            self.report({'ERROR'},'Error(s) occurred: see console')
            
            ### If active node is branch point, start new splines for each child    
        if number_of_childs  > 1:
            for child in child_list[active_node]:
                Create_Mesh.create_spline(active_node, child, nodes_dic, child_list, cu, nodes_to_keep)

    
    def make_neuron(neuron_name, index, XYZcoords, origin, edges, faces, convert_to_curve=True, soma = (0,0,0)): 
        ### Create mesh and object
        #print('createSkeleton started')
        
        start_creation = time.clock()
        me = bpy.data.meshes.new(neuron_name+' Mesh')        
        ob = bpy.data.objects.new('#' + neuron_name, me)
        ob.location = origin
        ob.show_name = True   
        
        ### Apparently material names cannot be longer than about 60 Characters
        ### If name is longer, it will be truncated:
        neuron_material_name = 'M#' + neuron_name
        
        if len(neuron_material_name) > 59:
            neuron_material_name = neuron_material_name[0:59]
             
        print('Creating Neuron %s  at Position %s (%s nodes)' %(ob.name, index, len(XYZcoords)))
        ### Link object to scene
        bpy.context.scene.objects.link(ob)        
        ### Create mesh from given verts, edges, faces. Either edges or faces should be [], or you ask for problems
        me.from_pydata(XYZcoords, edges, faces)

        ### Update mesh with new data
        me.update(calc_edges=True)
        print('Creating mesh done in ' + str(time.clock()-start_creation)+'s')
        
        ### Conversion to curve is essential for rendering - mere skeletons don't have faces
        ### Depending on neuron size this may take a while...
        if convert_to_curve is True:            
            Create_Mesh.curve_convert(ob, 0.007)     
            Create_Mesh.assign_material (ob, neuron_material_name, random.randrange(0,100)/100 , random.randrange(0,100)/100 , random.randrange(0,100)/100)

        ### If soma present, add sphere
        if soma != (0,0,0):
            soma_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, size=0.2, view_align=False, \
                                                            enter_editmode=False, location=soma, rotation=(0, 0, 0), \
                                                            layers=(True, False, False, False, False, False, False, \
                                                            False, False, False, False, False, False, False, False, \
                                                            False, False, False, False, False))
            bpy.ops.object.shade_smooth()
            bpy.context.active_object.name = 'Soma of ' + neuron_name
            ### Apply the same Material as for neuron tree
            Create_Mesh.assign_material (bpy.context.active_object, neuron_material_name, random.randrange(0,100)/100 , \
                                        random.randrange(0,100)/100 , random.randrange(0,100)/100)

        time_elapsed = time.clock() - start_creation 
        print('Done in ' + str(time_elapsed) + 's')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)
        
    
    def create_hull(XYZcoords, edges): 
        ### Input is vert and edge list - Outputs neuron hull (8 edged circle)
        ### Shift is replacement for 45, 125, 225 and 315 position
        radius = 0.003
        shift = math.sqrt((radius**2) / 2)        
        newXYZcoords = []
        newEdges = []
        newFaces = []  
        origin = (0,0,0)        
        index = 0         
        print('Creating Hull Coordinates...')
        
        for edge in edges:            
            ### Cycle through edges, retrieve vert coordinates and create hull coordinates      
            vertA_coords = XYZcoords[edge[0]]
            vertB_coords = XYZcoords[edge[1]]            
            ### Coordinates clockwise, 0 through 7 = 8 Total positions, every 45degree: 0, 45, 90, etc.            
            Pos_U_A = (vertA_coords[0],vertA_coords[1],vertA_coords[2]-radius) #0 
            Pos_UR_A = (vertA_coords[0]+shift,vertA_coords[1],vertA_coords[2]-shift) #45
            Pos_R_A = (vertA_coords[0]+radius,vertA_coords[1],vertA_coords[2]) #90
            Pos_DR_A = (vertA_coords[0]+shift,vertA_coords[1],vertA_coords[2]+shift) #135
            Pos_D_A = (vertA_coords[0],vertA_coords[1],vertA_coords[2]+radius) #180
            Pos_DL_A = (vertA_coords[0]-shift,vertA_coords[1],vertA_coords[2]+shift) #225
            Pos_L_A = (vertA_coords[0]-radius,vertA_coords[1],vertA_coords[2]) #270
            Pos_UL_A = (vertA_coords[0]-shift,vertA_coords[1],vertA_coords[2]-shift) #315
            
            Pos_U_B = (vertB_coords[0],vertB_coords[1],vertB_coords[2]-radius) #0 
            Pos_UR_B = (vertB_coords[0]+shift,vertB_coords[1],vertB_coords[2]-shift) #45
            Pos_R_B = (vertB_coords[0]+radius,vertB_coords[1],vertB_coords[2]) #90
            Pos_DR_B = (vertB_coords[0]+shift,vertB_coords[1],vertB_coords[2]+shift) #135
            Pos_D_B = (vertB_coords[0],vertB_coords[1],vertB_coords[2]+radius) #180
            Pos_DL_B = (vertB_coords[0]-shift,vertB_coords[1],vertB_coords[2]+shift) #225
            Pos_L_B = (vertB_coords[0]-radius,vertB_coords[1],vertB_coords[2]) #270
            Pos_UL_B = (vertB_coords[0]-shift,vertB_coords[1],vertB_coords[2]-shift) #315
            
            newXYZcoords.append(Pos_U_A)  
            newXYZcoords.append(Pos_UR_A)
            newXYZcoords.append(Pos_R_A)
            newXYZcoords.append(Pos_DR_A)
            newXYZcoords.append(Pos_D_A)
            newXYZcoords.append(Pos_DL_A)
            newXYZcoords.append(Pos_L_A)
            newXYZcoords.append(Pos_UL_A)

            newXYZcoords.append(Pos_U_B)  
            newXYZcoords.append(Pos_UR_B)
            newXYZcoords.append(Pos_R_B)
            newXYZcoords.append(Pos_DR_B)
            newXYZcoords.append(Pos_D_B)
            newXYZcoords.append(Pos_DL_B)
            newXYZcoords.append(Pos_L_B)
            newXYZcoords.append(Pos_UL_B)
            
            newFaces.append((index * 16 + 0, index * 16 + 1, index * 16 + 9, index * 16 + 8))
            newFaces.append((index * 16 + 1, index * 16 + 2, index * 16 + 10, index * 16 + 9))
            newFaces.append((index * 16 + 2, index * 16 + 3, index * 16 + 11, index * 16 + 10))
            newFaces.append((index * 16 + 3, index * 16 + 4, index * 16 + 12, index * 16 + 11))
            newFaces.append((index * 16 + 4, index * 16 + 5, index * 16 + 13, index * 16 + 12))
            newFaces.append((index * 16 + 5, index * 16 + 6, index * 16 + 14, index * 16 + 13))
            newFaces.append((index * 16 + 6, index * 16 + 7, index * 16 + 15, index * 16 + 14))
            newFaces.append((index * 16 + 7, index * 16 + 0, index * 16 + 8, index * 16 + 15))
            
            index += 1
        
        print('Creating Hull Mesh...')
        me = bpy.data.meshes.new('Hull')        
        ob = bpy.data.objects.new('#Hull', me)
        ob.location = origin
        ob.show_name = True 
        ### Link object to scene
        bpy.context.scene.objects.link(ob)        
        ### Create mesh from given verts, edges, faces. Either edges or faces should be [], or you ask for problems
        me.from_pydata(newXYZcoords, newEdges, newFaces)
        ### Update mesh with new data
        me.update(calc_edges=True)            
            
        
    def make_connectors(neuron_name, connectors_pre, connectors_post, origin = (0,0,0)):
        ### Creates Mesh and Objects for Connectors (pre and post seperately)
        
        start_creation = time.clock()
        print('Creating Connectors of %s' % ( neuron_name ))    
 
        cu_pre = bpy.data.curves.new('Outputs of ' + neuron_name,'CURVE')
        ob_pre = bpy.data.objects.new('Outputs of ' + neuron_name, cu_pre)
        bpy.context.scene.objects.link(ob_pre)
        ob_pre.location = (0,0,0)
        ob_pre.show_name = True 
        
        cu_post = bpy.data.curves.new('Inputs of ' + neuron_name,'CURVE')
        ob_post= bpy.data.objects.new('Inputs of ' + neuron_name, cu_post)
        bpy.context.scene.objects.link(ob_post)
        ob_post.location = (0,0,0)
        ob_post.show_name = True                  

        cu_pre.dimensions = '3D'
        cu_pre.fill_mode = 'FULL'
        cu_pre.bevel_depth = 0.007
        cu_pre.bevel_resolution = 5 
        
        cu_post.dimensions = '3D'
        cu_post.fill_mode = 'FULL'
        cu_post.bevel_depth = 0.007
        cu_post.bevel_resolution = 5 
    
        for connector in connectors_pre:
            newSpline = cu_pre.splines.new('POLY')                
            newPoint = newSpline.points[-1]
            newPoint.co = (connectors_pre[connector][0][0], connectors_pre[connector][0][1], connectors_pre[connector][0][2], 0)
            newSpline.points.add()
            newPoint = newSpline.points[-1]
            newPoint.co = (connectors_pre[connector][1][0], connectors_pre[connector][1][1], connectors_pre[connector][1][2], 0)

        for connector in connectors_post:
            newSpline = cu_post.splines.new('POLY')                
            newPoint = newSpline.points[-1]
            newPoint.co = (connectors_post[connector][0][0], connectors_post[connector][0][1], connectors_post[connector][0][2], 0)
            newSpline.points.add()
            newPoint = newSpline.points[-1]
            newPoint.co = (connectors_post[connector][1][0], connectors_post[connector][1][1], connectors_post[connector][1][2], 0)         

        Create_Mesh.assign_material (ob_pre, 'PreSynapses_Mat', 1 , 0 , 0)
        Create_Mesh.assign_material (ob_post, 'PostSynapses_Mat', 0 , 0.8 , 0.8)
        print('Creating connectors done in ' + str(time.clock()-start_creation)+'s')
            
            
    def curve_convert (ob, bevel=0.007):
        ### Converts objects into curves         
        print('Converting to curve... May take a moment or two')        
        start_convert_curve = time.clock()        
        bpy.context.scene.objects.active = ob
        ob.select = True          
        bpy.ops.object.convert(target='CURVE', keep_original=False)
        print('Done in ' + str(time.clock()-start_convert_curve) +'s')
        time.sleep(0.05)
        ob.data.bevel_resolution = 3                
        time.sleep(0.05)
        ob.data.bevel_depth = bevel
        time.sleep(0.05)
        ob.data.fill_mode = 'FULL'        

        
    def assign_material (ob, material=None, diff_1=0.8, diff_2=0.8, diff_3=0.8):
        #If Material is not none, check if material exists, if not is is created and assigned
        if material:
            if material not in bpy.data.materials:
                new_mat = bpy.data.materials.new(material)
                new_mat.diffuse_color[0] = diff_1
                new_mat.diffuse_color[1] = diff_2            
                new_mat.diffuse_color[2] = diff_3            
            else:
                new_mat = bpy.data.materials[material]
        #If no material is provided, check if given color already exists for any generic material
        else:
            new_mat = None
            for mat in bpy.data.materials:
                if mat.diffuse_color[0:3] == (diff_1, diff_2, diff_3) and mat.name.startswith('Generic'):
                    new_mat = mat
                    break

            if new_mat is None:
                new_mat = bpy.data.materials.new('Generic Mat %f %f %f' % (diff_1, diff_2, diff_3))
                new_mat.diffuse_color[0] = diff_1
                new_mat.diffuse_color[1] = diff_2            
                new_mat.diffuse_color[2] = diff_3  

            
        bpy.context.scene.objects.active = ob
        ob.select = True
        bpy.context.active_object.active_material = new_mat
        

class RandomMaterial (Operator):
    """Assigns Random Materials to Neurons"""  
    bl_idname = "random.all_materials"  
    bl_label = "Assign Random Materials"  
    bl_options = {'UNDO'}
    
    color_range = EnumProperty(name="Range",
                                   items = (('RGB','RGB','RGB'),
                                            ("Grayscale","Grayscale","Grayscale"),                                            
                                            ),
                                    default =  "RGB",
                                    description = "Choose mode of randomizing colors")

    def execute(self, context):        
        neuron_count = 0        
        
        for neuron in bpy.data.objects:    
            if neuron.name.startswith('#'):
                neuron_count += 1
        
        colormap = ColorCreator.random_colors(neuron_count,self.color_range)    
        #print(colormap)
        
        for neuron in bpy.data.objects:    
            if neuron.name.startswith('#'):
                neuron.active_material.diffuse_color[0] = colormap[0][0]/255
                neuron.active_material.diffuse_color[1] = colormap[0][1]/255
                neuron.active_material.diffuse_color[2] = colormap[0][2]/255                
                neuron.active_material.emit = 0
                neuron.active_material.use_transparency = True
                neuron.active_material.transparency_method = 'Z_TRANSPARENCY'
                
                colormap.pop(0)
                
        return {'FINISHED'}
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)  
    
class ColorByPairs (Operator):
    """Gives Paired Neurons the same Color (Annotation-based)"""  
    bl_idname = "color.by_pairs"  
    bl_label = "Gives Paired Neurons the same Color (Annotation-based)"  
    bl_options = {'UNDO'}
    
    color_range = EnumProperty(name="Range",
                                   items = (('RGB','RGB','RGB'),
                                            ("Grayscale","Grayscale","Grayscale"),                                            
                                            ),
                                    default =  "RGB",
                                    description = "Choose mode of randomizing colors.")
    
    unpaired_black = BoolProperty(  name="Don't color unpaired",                                   
                                    default =  True,
                                    description = "If unchecked, unpaired neurons will be given random color."
                                 )

    def execute(self, context):        
        neuron_count = 0      
        neurons = []                 
        
        print('Retrieving annotation of neurons')
        for neuron in bpy.data.objects:    
            if neuron.name.startswith('#'):
                try:
                    neuron_count += 1
                    neurons.append(re.search('#(.*?) -',neuron.name).group(1))
                except:
                    pass
                
        annotations = get_annotations_from_list (neurons, remote_instance)
        
        #Determine pairs
        paired = {}
        pairs = []
        non_paired = {}
        for neuron in neurons:
            paired_skid = None
            try:
                for annotation in annotations[neuron]:
                    if annotation.startswith('paired with #'):
                        skid = annotation[13:]
                        
                        #Filter for errors in annotation:
                        if neuron == paired_skid:
                            print('WARNING: Neuron %s paired with itself' % str(neuron))
                            continue
                            
                        if paired_skid != None:
                            print('WARNING: Multiple paired Annotations found for neuron %s!' % str(neuron))
                            paired_skid = None
                            continue
                            
                        paired_skid = skid
            except:
                pass
                    
            if paired_skid != None:
                #paired[neuron] = paired_skid
                
                #Count only if partner hasn't already been counted
                if (paired_skid, neuron) not in pairs:
                    pairs.append((neuron,paired_skid))               
            elif paired_skid == None:
                non_paired[neuron] = ()
                 
        
        #Create required number of colors:
        if self.unpaired_black is False:
            colormap = ColorCreator.random_colors(len(pairs)+len(non_paired),self.color_range)    
        elif self.unpaired_black is True:
            colormap = ColorCreator.random_colors(len(pairs),self.color_range)            
        #print(colormap)
        
        #Assign colors to pairs and single neurons:
        for pair in pairs:
            paired[pair[0]] = colormap[0]
            paired[pair[1]] = colormap[0]
            colormap.pop(0)
        for neuron in non_paired:
            if self.unpaired_black is True:
                non_paired[neuron] = (0,0,0)
            else:                
                non_paired[neuron] = colormap[0]
                colormap.pop(0)
        
        for neuron in bpy.data.objects:    
            if neuron.name.startswith('#'):
                try:            
                    skid = re.search('#(.*?) -',neuron.name).group(1)
                except:
                    continue
                if skid in paired:
                    neuron.active_material.diffuse_color[0] = paired[skid][0]/255
                    neuron.active_material.diffuse_color[1] = paired[skid][1]/255
                    neuron.active_material.diffuse_color[2] = paired[skid][2]/255               
                    neuron.active_material.emit = 0
                    neuron.active_material.use_transparency = True
                    neuron.active_material.transparency_method = 'Z_TRANSPARENCY'
                else:
                    neuron.active_material.diffuse_color[0] = non_paired[skid][0]/255
                    neuron.active_material.diffuse_color[1] = non_paired[skid][1]/255
                    neuron.active_material.diffuse_color[2] = non_paired[skid][2]/255               
                    neuron.active_material.emit = 0
                    neuron.active_material.use_transparency = True
                    neuron.active_material.transparency_method = 'Z_TRANSPARENCY'                    
                
        return {'FINISHED'}
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self) 
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False   
        
    
class SetupMaterialsForRender (Operator):
    """Prepares all Neuron's materials for Render: Emit Value and Transparency"""  
    bl_idname = "for_render.all_materials"  
    bl_label = "Prepare neurons' materials"  
    bl_options = {'UNDO'}

    emit_value = FloatProperty(     name="Emit Value",                                   
                                    default =  1,
                                    description = "Makes neurons emit light."
                                 )
    use_trans = BoolProperty(     name="Use Transparency",                                   
                                    default =  True,
                                    description = "Makes neurons use Transparency."
                                 )
    trans_value = FloatProperty(     name="Transparency Value",                                   
                                    default =  1,
                                    min = 0,
                                    max = 1,
                                    description = "Set transparency (0-1)"
                                 )

    def execute(self, context):
        for material in bpy.data.materials:
            if re.findall('#',material.name):
                #print(material)
                material.emit = self.emit_value
                material.use_transparency = self.use_trans
                material.alpha = self.trans_value
                
        return {'FINISHED'}           

    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self) 


class RenderAllNeurons(Operator):
    """Render all existing neurons consecutively"""  
    bl_idname = "render.all_neurons"  
    bl_label = "Render All Neurons"  
    
    def execute (self,context):
        ### Set Render Settings
        ### Check if cameras exist and create if not
        objects_in_scene = []
        for object in bpy.data.objects:
            objects_in_scene.append(object.name)
            
        if 'Front Camera' not in objects_in_scene:
            bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(5.5, -21, -5.7), rotation=(90, 0, 0), \
                                     layers=(True, True, False, False, False, False, False, False, False, False, False, False, \
                                     False, False, False, False, False, False, False, False))
            bpy.context.active_object.name = 'Front Camera'
            bpy.data.scenes['Scene'].camera = bpy.data.objects['Front Camera']
        
        if 'Text' not in objects_in_scene:
            bpy.ops.object.text_add(view_align=False, enter_editmode=False, location=(-0.85, -6, -9.3), rotation=(90, 0, 0), \
                                    layers=(True, True, False, False, False, False, False, False, False, False, False, False, \
                                    False, False, False, False, False, False, False, False))
            bpy.ops.transform.resize(value=(0.8,0.8,0.8))
        
        ### Cycle through neurons, hide them from render layer, render and unhide
        for object in bpy.data.objects:
            if re.findall('#',object.name):
                object.hide_render = True
        
        for object in bpy.data.objects:            
            if re.findall('#',object.name):
                print('Rendering neuron ' + object.name)
                bpy.data.objects['Text'].data.body = object.name
                object.hide_render = False
                bpy.data.scenes['Scene'].render.filepath = '//' + object.name + '_Front'            
                bpy.ops.render.render(write_still=True)
                object.hide_render = True
        
        for object in bpy.data.objects:
            if re.findall('#',object.name):
                object.hide_render = False
        
        return{'FINISHED'}

class ColorBySynapseCount(Operator):
    """Color neurons by # of Synapses with given partner(s)"""  
    bl_idname = "color.by_synapse_count"  
    bl_label = "Color Neurons by # of Synapses with given Partner(s)" 
    bl_options = {'UNDO'}
    
    ### 'filter' takes argument to filter for up- and downstream partners      
    filter_include = StringProperty(name="Include Annotation (comma separated)", 
                                    default = "",
                                    description="Filter based on Annotations(!). Case-insensitive. Separate by Comma if multiple tags")
    filter_exclude = StringProperty(name="Exclude Annotation (comma separated)", 
                                    default = "",
                                    description="Filter based on Annotations(!). Case-insensitive. Separate by Comma if multiple tags")
    use_upstream = BoolProperty(name="Consider Upstream", default = True)
    use_downstream = BoolProperty(name="Consider Downstream", default = True)
    change_bevel = BoolProperty(name="Also change bevel?", default = True)
    hops = IntProperty(name="Hops", 
                            description="Hops (Synapses) to Search Over. 1 = only direct connections",
                            default = 1, min = 1, max = 4)  
    synapse_decay = FloatProperty(name="Synapse Decay", 
                            description="Factor to Lower Synapse Weight at each Hop (after the first)",
                            default = 1, min = 0.01, max = 2)                              
    manual_max_value = IntProperty(name="Manual Max Synapse Count", 
                                    description="Leave at 0 for dynamic calculation. Use if you want to e.g. compare among different sets of neurons/partners.",
                                    default = 0, min = 0, max = 99)  
    shift_color = BoolProperty(     name="Shift Color",
                                    description = "If set, color will only be changed by given value RELATIVE to current color",
                                    default = False )                                    
    only_if_connected = BoolProperty( name="Only if Synapses", 
                                        description="Change Color only if neuron is synaptically connected. Otherwise preserve current color",
                                        default = False)
    start_color = FloatVectorProperty(name="Start Color", 
                                description="Low Value Color", 
                                default = (0.0, 1 , 0.0), 
                                min=0.0,
                                max=1.0,
                                subtype='COLOR'
                                )  
    end_color = FloatVectorProperty(name="End Color", 
                                description="Hig Value Color", 
                                default = (1, 0.0, 0.0), 
                                min=0.0,
                                max=1.0,
                                subtype='COLOR'
                                )   
    take_longest_route = BoolProperty( name="LUT takes longest route", 
                                        description="If checked, LUT will cover longest connection between start and end color",
                                        default = True)                               
    emit_max =          IntProperty(name="Emit", 
                                    description="Max Emit Value - set to 0 for no emit",
                                    default = 1, min = 0, max = 5)
    
    def execute (self, context):       
        synapse_count = {}    
        connectivity_post = {} 
        connectivity_post['threshold'] = 0
        connectivity_post['boolean_op'] = 'OR'         

        filter_include_list = self.filter_include.split(',')
        if self.filter_exclude != '':
            filter_exclude_list = self.filter_exclude.split(',')
        else:
            filter_exclude_list = []

        print('Include tags: ', filter_include_list)        
        print('Exclude tags: ', filter_exclude_list)
        
        ### Set all Materials to Black first
        #for material in bpy.data.materials:
        #    material.diffuse_color = (0,0,0)  
        
        i = 0
        skids_to_retrieve = []
        for object in bpy.data.objects:
            if object.name.startswith('#'):
                try:
                    skid = re.search('#(.*?) -',object.name).group(1)
                    synapse_count[skid] = 0        
                    skids_to_retrieve.append(skid)
                    tag = 'source[%i]' % i
                    connectivity_post[tag] = skid
                    i += 1   
                except:
                    pass            

        connectivity_data = get_partners (  skids_to_retrieve, 
                                            remote_instance, 
                                            self.hops, 
                                            self.use_upstream,
                                            self.use_downstream)               

        if connectivity_data:
            print("Connectivity successfully retrieved: ", list(connectivity_data))            
        else:
            print('No data retrieved')  
        
        if self.use_upstream is True:    
            for hop in range(len(connectivity_data['incoming'])):
                
                annotations = get_annotations_from_list(list(set(connectivity_data['incoming'][hop])),remote_instance)                                               
                
                for entry in connectivity_data['incoming'][hop]:                
                    #Filter Neurons by Annotations
                    include_flag = False
                    exclude_flag = False 
                    
                    try:
                        for annotation in annotations[entry]:
                            for tag in filter_include_list: 
                                if tag.lower() == annotation.lower():
                                    include_flag = True
                            for tag in filter_exclude_list:
                                if tag.lower() == annotation.lower():
                                    exclude_flag = True                     
                    except:
                        pass     
                         
                    if include_flag is True and exclude_flag is False:
                        #Go back each hop until at first hop (=0) to find/calculate connection to initial neurons                                    
                        if hop > 0:                            
                            backtraced = {}
                            connections = []
                            branch_points = []
                            #backtraced = self.backtrace_connectivity(backtraced,connectivity_data['incoming'],hop-1,skid)
                            backtraced = self.backtrace_connectivity(backtraced,connectivity_data['incoming'],hop,connections,branch_points,entry)[0]
                            #print('Upstream: ',hop,entry,backtraced)
                            for origin_skid in backtraced:
                                #synapse_count[origin_skid] += connectivity_data['incoming'][hop][entry]['skids'][skid] * (self.synapse_decay/hop)                       
                                for trace in backtraced[origin_skid]:
                                    weight = 1
                                    if len(trace) == 2:
                                        factors = [2/3,1/3]
                                    elif len(trace) > 2:
                                        factors = [4/7,2/7,1/7,1/7,1/7,1/7]                                    
                                    for i in range(len(trace)):                                            
                                        #Start with first synaptic connection 
                                        weight *= trace[len(trace)-1-i] ** factors[i]
                                    synapse_count[origin_skid] += weight            
                        else:
                            #print('Upstream 1-Synapse: ',hop,entry,connectivity_data['incoming'][hop][entry]['skids'])
                            for skid in connectivity_data['incoming'][hop][entry]['skids']:
                                synapse_count[skid] += sum(connectivity_data['incoming'][hop][entry]['skids'][skid])

                        
        if self.use_downstream is True:    
            for hop in range(len(connectivity_data['outgoing'])):
                
                annotations = get_annotations_from_list(list(set(connectivity_data['outgoing'][hop])),remote_instance)
                
                for entry in connectivity_data['outgoing'][hop]:                  
                    #Filter Neurons by Annotations
                    include_flag = False
                    exclude_flag = False 
                    
                    try:
                        for annotation in annotations[entry]:
                            for tag in filter_include_list: 
                                if tag.lower() == annotation.lower():
                                    include_flag = True
                            for tag in filter_exclude_list:
                                if tag.lower() == annotation.lower():
                                    exclude_flag = True                     
                    except:
                        pass   
                                        
                    if include_flag is True and exclude_flag is False:
                        #Go back each hop until at first hop (=0) to find/calculate connection to initial neurons                                    
                        if hop > 0:                        
                            backtraced = {}
                            connections = []
                            branch_points = []
                            #backtraced = self.backtrace_connectivity(backtraced,connectivity_data['outgoing'],hop-1,skid)
                            backtraced = self.backtrace_connectivity(backtraced,connectivity_data['outgoing'],hop,connections,branch_points,entry)[0]
                            #print('Downstream: ',hop,entry,skid,backtraced)
                            for origin_skid in backtraced:
                                #synapse_count[origin_skid] += connectivity_data['outgoing'][hop][entry]['skids'][skid] * (self.synapse_decay/hop)                       
                                for trace in backtraced[origin_skid]:
                                    weight = 1
                                    if len(trace) == 2:
                                        factors = [2/3,1/3]
                                    elif len(trace) > 2:
                                        factors = [4/7,2/7,1/7,1/7,1/7,1/7]
                                    for i in range(len(trace)):
                                        #Start with first synaptic connection 
                                        weight *= trace[len(trace)-1-i] * factors[i]
                                    synapse_count[origin_skid] += weight                                     
                        else:
                            #print('Downstream 1-Synapse: ', hop,entry,connectivity_data['outgoing'][hop][entry]['skids'])
                            for skid in connectivity_data['outgoing'][hop][entry]['skids']:
                                #print(connectivity_data['outgoing'][hop][entry]['skids'][skid])
                                synapse_count[skid] += sum(connectivity_data['outgoing'][hop][entry]['skids'][skid])


        #get max value in synapse count for gradient calculation if self.manual_max_value is not set
        if self.manual_max_value == 0:
            max_count = 0
            for entry in synapse_count:
                if synapse_count[entry] > max_count:
                    max_count = synapse_count[entry]
            print('Maximum # of synaptic connections found: ', max_count)
        else:
            max_count = self.manual_max_value
            print('Using manually set max value for coloring of synaptic connections (may be capped!): ',max_count)

        print('Synapse count:')
        for object in bpy.data.objects:
            if object.name.startswith('#'):
                try:                
                    skid = re.search('#(.*?) -',object.name).group(1)
                    mat = object.active_material
                    #print(object.name,synapse_count[skid])
                    if synapse_count[skid] > 0:                        
                        #Reduce # of synapses by 1 such that the lowest value is actually 0 to (max_count-1)
                        hsv = calc_color((synapse_count[skid]-1),(max_count-1),self.start_color,self.end_color,self.take_longest_route)
                        
                        if self.shift_color is False:
                            mat.diffuse_color[0] = hsv[0]
                            mat.diffuse_color[1] = hsv[1]
                            mat.diffuse_color[2] = hsv[2]  
                        elif mat.diffuse_color == mathutils.Color((0.0,0.0,0.0)):
                            mat.diffuse_color[0] = colorsys.hsv_to_rgb(self.end_hue/360,1,1)[0]
                            mat.diffuse_color[1] = colorsys.hsv_to_rgb(self.end_hue/360,1,1)[1]
                            mat.diffuse_color[2] = colorsys.hsv_to_rgb(self.end_hue/360,1,1)[2]
                        #elif synapse_count[skid] >= 3:
                        else:
                            mat.diffuse_color = (0.5,0.5,0.5)
                            #mat.diffuse_color[0] = math.fabs((mat.diffuse_color[0] - colorsys.hsv_to_rgb(self.end_hue/360,1,1)[0])/2)
                            #mat.diffuse_color[1] = math.fabs((mat.diffuse_color[1] - colorsys.hsv_to_rgb(self.end_hue/360,1,1)[1])/2)
                            #mat.diffuse_color[2] = math.fabs((mat.diffuse_color[2] - colorsys.hsv_to_rgb(self.end_hue/360,1,1)[2])/2)
                        mat.emit = synapse_count[skid]/max_count * self.emit_max
                        
                        if self.change_bevel is True:
                            object.data.bevel_depth = 0.007 + synapse_count[skid]/max_count * 0.014
                           
                    elif self.only_if_connected is False:
                        mat.diffuse_color = (0.5,0.5,0.5)              
                except:
                    print('ERROR: Unable to process object: ', object.name)
                    self.report({'ERROR'},'Error(s) occurred: see console')

        return{'FINISHED'}

    """    
    def backtrace_connectivity(self,backtraced,connectivity_data,hop,connections,skid):
        if hop > 0:
            for entry in connectivity_data[hop][skid]['skids']:                
                connections.append(connectivity_data[hop][skid]['skids'][entry])                
                backtraced.update(self.backtrace_connectivity(backtraced,connectivity_data,hop-1,entry))
        else:
            backtraced = (connectivity_data[hop][skid]['skids'],connections)
        
        return backtraced
    """

    def backtrace_connectivity(self,backtraced,connectivity_data,hop,connections,branch_points,skid):        
        for i in range(len(connectivity_data[hop][skid]['skids'])-1):
            branch_points.append(len(connections))
            #print('Branch point added: ', hop ,connections) 
        if hop > 0:
            for entry in connectivity_data[hop][skid]['skids']:                
                connections.append(connectivity_data[hop][skid]['skids'][entry])                
                #print(entry)
                temp = self.backtrace_connectivity(backtraced,connectivity_data,hop-1,connections,branch_points,entry)
                backtraced.update(temp[0])
                connections = temp[1]
        else:        
            for entry in connectivity_data[hop][skid]['skids']:            
                connections.append(connectivity_data[hop][skid]['skids'][entry])            
                if entry not in backtraced:
                    backtraced[entry] = []
                backtraced[entry].append(connections)
                #print(entry,connections)
                #Go back to last branch point
                if len(branch_points) > 0:
                    #print('Going back to branch point: ', branch_points[-1])
                    connections = connections[0:branch_points[-1]]
                    #print(connections)
                    branch_points.pop(-1)
        
        return (backtraced,connections)        
            
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)  
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False
        
class ColorByAnnotation(Operator):
    """Color neurons by Annotation"""  
    bl_idname = "color.by_annotation"  
    bl_label = "Color Neurons based on whether they have given annotation" 
    bl_options = {'UNDO'}      
    
    annotation = StringProperty(name="Annotation",description="Seperate multiple annotations by comma without space. Must be exact! Case-sensitive!")
    exclude_annotation = StringProperty(name="Exclude",description="Seperate multiple annotations by comma without space. Must be exact! Case-sensitive!")
    color = FloatVectorProperty(name="Color", 
                                description="Color value", 
                                default = (1, 0.0, 0.0), 
                                min=0.0,
                                max=1.0,
                                subtype='COLOR'
                                )
    make_non_matched_grey = BoolProperty(name="Color others grey",
                                         description="If unchecked, color of neurons without given annotation(s) will not be changed",
                                         default=True)
    
    
    def execute (self, context):        
        skids_to_retrieve = []
        for object in bpy.data.objects:
            if object.name.startswith('#'):
                try:
                    skid = re.search('#(.*?) -',object.name).group(1)                    
                    skids_to_retrieve.append(skid)
                except:
                    pass
                                
        annotations = get_annotations_from_list(skids_to_retrieve, remote_instance)
        
        include_annotations = self.annotation.split(',')
        exclude_annotations = self.exclude_annotation.split(',')

        included_skids = []
        excluded_skids = []
        color_changed = []
        
        for object in bpy.data.objects:
            if object.name.startswith('#'):                
                try:
                    skid = re.search('#(.*?) -',object.name).group(1)        
                    
                    include = False
                    exclude = False
                    
                    for tag in annotations[skid]:
                        if tag in include_annotations:
                            include = True
                            included_skids.append(skid)
                        if tag in exclude_annotations:
                            exclude = True
                            excluded_skids.append(skid)
                            
                    if include is True and exclude is False:
                        object.active_material.diffuse_color = self.color
                        color_changed.append(skid)
                    elif self.make_non_matched_grey is True:
                        object.active_material.diffuse_color = (0.4,0.4,0.4)
                except:
                    pass

        print('Include annotations:',include_annotations)
        print('Exclude annotations:',exclude_annotations)

        print('Included based on annotation:', included_skids)
        print('Excluded based on annotation:', excluded_skids)
        print('Color changed for neurons ',color_changed)
        
        return{'FINISHED'}
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)      
    
    @classmethod        
    def poll(cls, context):
        if connected:
            return True
        else:
            return False

def availableOptions(self, context):
    """
    This function sets available options for calculating the matching score.    
    """
    available_options = [('Morphology','Morphology','Morphology')]
    if connected:
        available_options.append(('Synapse-Distr.','Synapse-Distr.','Synapse-Distr.'))
    else:
        available_options.append(('Connect For More Options','Connect For More Options','Connect For More Options'))
    return available_options            

class ColorBySimilarity(Operator):
    """Color neurons by similarity"""  
    bl_idname = "color.by_similarity"  
    bl_label = "Color neurons by similarity of morphology or synapse distribution" 
    bl_options = {'UNDO'}

    which_neurons = EnumProperty(name = "Which Neurons?", 
                                      items = [('Selected','Selected','Selected'),('All','All','All')],
                                      description = "Choose which neurons to reload.",
                                      default = 'All')
    compare = EnumProperty( name='Compare',
                            items=availableOptions
                            )
    method = EnumProperty( name='Cluster Method (Distance)',
                            items=[('avg','avg','avg'),('min','min','min'),('max','max','max')],
                            description = "Define if clusters are merged based on average, minimal or maximal distance between its members."
                            )
    cluster_at = FloatProperty (
                                name='Cluster at similarity of:',
                                min = 0,
                                max = 1,
                                default = 0.2,
                                description = 'Sets similarity threshold for picking clusters that will have the same color. 1 = perfect match; 0 = not similar at all.'
                                )
    use_saved = BoolProperty (
                                name='Try using saved data',
                                default = True,
                                description = 'If true, will try to use previous data from this session. Uncheck to compute from scratch!'
                                )
    save_dendrogram = BoolProperty (
                                name='Save Dendrogram',
                                default = True,
                                description = 'Will save dendrogram of similarity to dendrogram.svg'
                                )

    def execute (self, context):
        #Get neurons first
        neurons = []
        neuron_names = {}
        skids = []
        if self.which_neurons == 'All':   
            for obj in bpy.data.objects:
                if obj.name.startswith('#'):
                    try:
                        skid = re.search('#(.*?) -',obj.name).group(1)
                        neurons.append(obj)                
                        skids.append(skid)
                        obj['skid'] = skid
                        neuron_names[skid] = obj.name
                    except:
                        pass
        elif self.which_neurons == 'Selected':
            for obj in bpy.context.selected_objects:
                if obj.name.startswith('#'):
                    try:
                        skid = re.search('#(.*?) -',obj.name).group(1)
                        neurons.append(obj)              
                        skids.append(skid)
                        obj['skid'] = skid
                        neuron_names[skid] = obj.name
                    except:
                        pass

        print('Collecting data of %i neurons' % len(neurons))
        if self.compare == 'Morphology':
            neuron_data = {}
            neuron_parent_vectors = {}
            for n in neurons:                
                neuron_data[n['skid']] = []
                neuron_parent_vectors[n['skid']] = []
                for spline in n.data.splines:
                    for i,point in enumerate(spline.points):
                        #Skip first node (root node of each spline -> has no parent)
                        if i == 0:
                            continue                        
                        parent_vector = list(map(lambda x,y:(x-y) , point.co, spline.points[i-1].co))                        
                        normal_parent_vector = list(map(lambda x: x/self.length(parent_vector), parent_vector))
                        neuron_data[n['skid']].append(point.co)
                        neuron_parent_vectors[n['skid']].append(normal_parent_vector)
        elif self.compare == 'Synapse-Distr.':
            synapse_data = {}
            skeleton_data = get_3D_skeleton (skids, remote_instance, 1 , 0)
            for i,n in enumerate(skids):
                synapse_data[n] = skeleton_data[i][1]          
                        
        print('Done!')

        global matching_scores

        if self.use_saved is True:
            try:
                matching_scores
            except:
                print('Creating matching scores from scratch!')
                matching_scores = {'Synapse-Distr.':{},'Morphology':{}}                
        else:
            print('Creating matching scores from scratch!')
            matching_scores = {'Synapse-Distr.':{},'Morphology':{}}
            
        
        for i,neuronA in enumerate(neurons):                
            print('Comparing neuron', neuronA.name, '[',i,'of',len(neurons),']')
            #print('Resolution:', self.check_resolution(neuronA))  
            for neuronB in neurons:
                if self.compare == 'Morphology' and str(neuronA['skid'])+'-'+str(neuronB['skid']) not in matching_scores[self.compare]:
                    matching_scores[self.compare][str(neuronA['skid'])+'-'+str(neuronB['skid'])] = round(     self.calc_morphology_matching_score(
                                                                                                                                    neuron_data[neuronA['skid']],
                                                                                                                                    neuron_parent_vectors[neuronA['skid']],
                                                                                                                                    neuron_data[neuronB['skid']],
                                                                                                                                    neuron_parent_vectors[neuronB['skid']],
                                                                                                                                    0.2
                                                                                                                                   )
                                                                                                ,5)
                elif self.compare == 'Synapse-Distr.' and str(neuronA['skid'])+'-'+str(neuronB['skid']) not in matching_scores[self.compare]:
                     matching_scores[self.compare][str(neuronA['skid'])+'-'+str(neuronB['skid'])] = round(     self.calc_synapse_matching_score(
                                                                                                                                    synapse_data[neuronA['skid']],
                                                                                                                                    synapse_data[neuronB['skid']],
                                                                                                                                    2000,
                                                                                                                                    2000
                                                                                                                                  )
                                                                                                ,5)

        print('Matchin scores:,',matching_scores[self.compare])

        all_clusters,merges_at = self.create_clusters(skids,matching_scores[self.compare],self.method)    

        for i in range(len(merges_at)):
            try:
                if merges_at[i+1] < self.cluster_at:
                    clusters_to_plot = all_clusters[i]
                    break
            except:
                print('%s - all Clusters merged before threshold %f - using next cluster constellation at %f:' % (self.compare,self.cluster_at,merges_at[i]))
                print( all_clusters[i])
                clusters_to_plot = all_clusters[i]                   

        colors = ColorCreator.random_colors(len(clusters_to_plot),'RGB')

        colormap = {}
        for c in clusters_to_plot:                      
            for skid in c:                                
                colormap[skid] = colors[0]
            colors.pop(0)

        for n in neurons:
            skid = re.search('#(.*?) -',n.name).group(1)
            n.active_material.diffuse_color[0] = colormap[skid][0]/255
            n.active_material.diffuse_color[1] = colormap[skid][1]/255
            n.active_material.diffuse_color[2] = colormap[skid][2]/255
        #for entry in matching_scores:
        #    print(entry,'\t',matching_scores[entry])

        if self.save_dendrogram is True and bpy.data.filepath != '':
            try:
                svg_file = os.path.join ( os.path.dirname( bpy.data.filepath ) , 'dendrogram.svg' )
                self.plot_dendrogram(skids, all_clusters, merges_at, remote_instance, 'dendrogram.svg', neuron_names , self.cluster_at)
                print('Dendrogram.svg created in ', os.path.dirname( bpy.data.filepath ))
                self.report({'INFO'},'dendrogram at ' + svg_file )
            except:
                self.report({'ERROR'},'Could not create dendrogram. See Console!') 
                self.report({'INFO'},'ERROR. See Console!') 
                print('ERROR: Could not create dendrogram')
                if not os.access( os.path.dirname( bpy.data.filepath ) , os.W_OK ):
                    print('Do not have permission to write in', os.path.dirname( bpy.data.filepath ))
                    print('Try saving the .blend file elsewhere!')
        elif bpy.data.filepath == '':
            print('ERROR: Need to first save the .blend file before creating dendrogram!')
            self.report({'ERROR'},'ERROR creating Dendrogram: see console')
                
        return{'FINISHED'}

    def calc_synapse_matching_score(self,synapsesA,synapsesB,sigma=50,omega=500):
        all_values = []
        coordsA = {}
        coordsB = {}

        #Create numpy arrays for pre- and postsynaptic connectors separately,
        #to allow comparison of only pre- with pre- and post- with postsynaptic sites
        coordsA['presynapses'] = np.array([e[3:6] for e in synapsesA if e[2] == 0])
        coordsA['postsynapses'] = np.array([e[3:6] for e in synapsesA if e[2] == 1])        

        coordsB['presynapses'] = np.array([e[3:6] for e in synapsesB if e[2] == 0])
        coordsB['postsynapses'] = np.array([e[3:6] for e in synapsesB if e[2] == 1])

        for direction in ['presynapses','postsynapses']:
            for synA in coordsA[direction]:
                try:
                    #Generate distance Matrix of point a and all points in nB
                    d = np.sum((coordsB[direction]-synA)**2,axis=1)

                    #Calculate final distance by taking the sqrt!
                    min_dist = math.sqrt(d[d.argmin()])
                    closest_syn = coordsB[direction][d.argmin()]                    

                    #Distances of synA to all synapses of the same neuron
                    dA = np.sum((coordsA[direction]-synA)**2,axis=1)
                    around_synA = len([e for e in dA if math.sqrt(e) < omega])

                    #Distances of closest synapses in B to all synapses of the same neuron
                    dB = np.sum((coordsB[direction]-closest_syn)**2,axis=1)
                    around_synB = len([e for e in dB if math.sqrt(e) < omega])

                    this_synapse_value = math.exp( -1 * math.fabs(around_synA - around_synB) / (around_synA + around_synB) )   *   math.exp( -1 * (min_dist**2) / (2 * sigma**2))

                except:
                    #will fail if no pre-/postsynapses in coordsB
                    this_synapse_value = 0

                all_values.append(this_synapse_value) 

        try:
            return (sum(all_values)/len(all_values))    
        except:
            #When len(all_values) = 0
            return 0


    def calc_morphology_matching_score(self,nodeDataA,parentVectorsA,nodeDataB,parentVectorsB,sigma=50):
        #nodes_list = [treenode_id, parent_treenode_id, creator , X, Y, Z, radius, confidence]

        #Sigma defines how close two points have to be to be considered similar (in nanometers)
        #Kohl et al. -> 3000nm (light microscopy + registration)    

        all_values = []

        nA = np.array(nodeDataA)     
        nB = np.array(nodeDataB)

        for i,a in enumerate(nA):
            #Generate distance Matrix of point a and all points in nB
            d = np.sum((nB-a)**2,axis=1)

            #Calculate final distance by taking the sqrt!
            min_dist = math.sqrt(d[d.argmin()])

            normal_parent_vectorB = parentVectorsB[d.argmin()] 
            normal_parent_vectorA = parentVectorsA[i]

            dp = self.dotproduct(normal_parent_vectorA, normal_parent_vectorB)

            this_treenode_value = math.fabs(dp) * math.exp( -1 * (min_dist**2) / (2 * sigma**2))            

            all_values.append(this_treenode_value)  

        
        return (sum(all_values)/len(all_values))  

    def closest_node(node,nodes):
        nodes = numpy.asarray(nodes)
        dist = numpy.sum((nodes - node)**2, axis = 1)
        return np.argmin(dist_2)    

    def dotproduct(self,v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))

    def length(self,v):
        return math.sqrt(self.dotproduct(v, v))  

    def dist(self,v1,v2):        
        return math.sqrt(sum(((a-b)**2 for a,b in zip(v1,v2))))   

    def manhattan_dist(self,v1,v2):
        return sum(((a-b) for a,b in zip(v1,v2)))

    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)  

    def check_resolution(self,neuron):
        """
       Checks z resolution of given neuron -> due to virtual nodes, some neurons have less nodes than others
        """

        distances = []
        for spline in neuron.data.splines:
            for i,point in enumerate(spline.points):
                #Skip first node (root node of each spline -> has no parent)
                if i == 0:
                    continue  
                #Virtual nodes basically skip z-sections, so points are more than 50nm (0.005 in CATMAID coords)) apart in z-direction (y-direction in Blender)
                dist = math.fabs(point.co[1] - spline.points[i-1].co[1])
                if dist > 0:
                    distances.append(dist)

        return round(sum(distances)/len(distances),3)

    def create_clusters(self,skids,matching_scores,method):
        """
        Sort skids into clusters based on similarity in matching score
        """
        similarity = 1
        step_size = 0.01

        clusters = list(map(lambda x:[x], skids))   
        all_clusters = [copy.deepcopy(clusters)]
        merges_at = [1] 

        print('Start clusters:',clusters)

        while similarity >= 0:
            #Find cluster that will be merged in this round
            #merge contains indices of c in clusters
            merge = {}
            for c1 in clusters:
                for c2 in clusters:
                    #if clusters are identical
                    if c1 == c2:
                        continue
                    all_similarities = []
                    for neuronA in c1:              
                        #if c1 has already been merged to c2 in previous iteration
                        #if clusters.index(c2) in merge:
                        #   if clusters.index(c1) in merge[clusters.index(c2)]:
                                #print('!Skipped redundant merging:',c1,c2)
                        #       continue
                        #merged = False
                        for neuronB in c2:
                            #if merged is True:
                            #   continue
                            #Calculate average from both comparisons: A -> B and B -> A (will be different!!!!)
                            avg_matching_score = (matching_scores[str(neuronA)+'-'+str(neuronB)] + matching_scores[str(neuronB)+'-'+str(neuronA)]) / 2
                            all_similarities.append(avg_matching_score)                     


                    #Important: for method 'max' (maximal distance), find pair of neurons for which the similarity is minimal 
                    #           for method 'min' (minimal distance), find pair of neurons for which the similarity is maximal
                    if ((    method == 'avg' and (sum(all_similarities)/len(all_similarities)) >= similarity ) 
                        or ( method == 'max' and min(all_similarities) >= similarity )  
                        or ( method == 'min' and max(all_similarities) >= similarity )): 
                        if clusters.index(c1) not in merge:
                            merge[clusters.index(c1)] = []
                        if clusters.index(c2) not in merge[clusters.index(c1)]:
                            merge[clusters.index(c1)].append(clusters.index(c2))
                            #merged = True

            if len(merge) != 0:
                #Check if multiple clusters need to be merged:
                print('Merge:',merge)
                temp_to_be_merged = []
                for c1 in merge:
                    #print('C1:',c1)
                    exists = []
                    for c2 in merge[c1]:                                        
                        for entry in temp_to_be_merged:
                            if c1 in entry or c2 in entry:
                                if temp_to_be_merged.index(entry) not in exists:
                                    exists.append(temp_to_be_merged.index(entry))

                    #print('Exists:', exists)

                    if len(exists) > 0:
                        temp_to_be_merged[exists[0]].append(c1)
                        temp_to_be_merged[exists[0]] += merge[c1]
                        for entry in exists[1:]:
                            temp_to_be_merged[exists[0]] += temp_to_be_merged[entry]
                            temp_to_be_merged.remove(temp_to_be_merged[entry])
                    else:
                        to_append = [c1]
                        to_append += merge[c1]
                        temp_to_be_merged.append(to_append)                 

                #Make sure each cluster shows up only once in to_be_merged:
                to_be_merged = []
                for entry in temp_to_be_merged:
                    to_be_merged.append(list(set(entry)))

                #print('Merging at similarity', similarity,':',to_be_merged,merge)

                temp_clusters = copy.deepcopy(clusters)

                #First merge clusters
                for entry in to_be_merged:  
                    for c in entry[1:]:
                        temp_clusters[entry[0]] += copy.deepcopy(clusters[c])

                #Then delete 
                for entry in to_be_merged:                                          
                    for c in entry[1:]:
                        temp_clusters.remove(clusters[c])       

                clusters = copy.deepcopy(temp_clusters)
                all_clusters.append(copy.deepcopy(temp_clusters))
                merges_at.append(similarity)
                

                print(temp_clusters,'\n')

            similarity -= step_size

        return all_clusters,merges_at

    def plot_dendrogram(self, skids, all_clusters, merges_at, remote_instance, filename, names, cluster_at=0): 
        """
        Creates dendrogram based on previously calculated similarity scores
        """
        if cluster_at != 0:
            for i in range(len(merges_at)):
                try:
                    if merges_at[i+1] < cluster_at:
                        clusters_to_plot = all_clusters[i]
                        break
                except:
                    print('Morphology - all Clusters merged before threshold %f - using next cluster constellation at %f:' % (cluster_at,merges_at[i]))
                    print( all_clusters[i])
                    clusters_to_plot = all_clusters[i]
            
            colors = ColorCreator.random_colors(len(clusters_to_plot))
            colormap = {}   
            for c in clusters_to_plot:                      
                for neuron in c:                              
                    colormap[neuron] = colors[0]
                colors.pop(0)
        
        svg_header =    '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" style="background:white">\n'
        text_color = (0,0,0)

        svg_file = os.path.join ( os.path.dirname( bpy.data.filepath ) , 'dendrogram.svg' )

        #Now create svg
        with open( svg_file, 'w', encoding='utf-8') as f:  
            f.write(svg_header)   

            #Write neurons first as they are sorted in the last cluster
            y_offset = 0
            neuron_offsets = {}
            clusters_by_neurons = {}
            for neuron in [item for sublist in all_clusters[-1] for item in sublist]:
                f.write('<text x="%i" y="%i" fill="rgb%s" style="font-size:14px;"> %s </text> \n'
                            % (
                                500 + 10,
                                y_offset,
                                str((0,0,0)),
                                names[neuron] 
                                )
                            )


                neuron_offsets[neuron] = y_offset - 5
                clusters_by_neurons[neuron] = (y_offset,500)
                y_offset += 30

            if cluster_at != 0:
                f.write('<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:rgb(0,0,0);stroke-width:1;stroke-dasharray:5,5" /> \n' 
                        % (
                            cluster_at * 500,                       
                            -10,
                            cluster_at * 500,
                            y_offset
                           )
                        )
                f.write('<text text-anchor="middle" x="%i" y="%i" fill="rgb(0,0,0)" style="font-size:10px;"> Cluster Threshold </text> \n' 
                        % (
                            cluster_at * 500,
                            -30                     
                          )
                        )



            #Write x axis:
            f.write('<line x1="0" y1="%i" x2="500" y2="%i" style="stroke:rgb(0,0,0);stroke-width:1" /> \n' % (y_offset,y_offset))
            
            f.write('<line x1="100" y1="%i" x2="100" y2="%i" style="stroke:rgb(0,0,0);stroke-width:1" /> \n' % (y_offset-5,y_offset+5))
            f.write('<text text-anchor="middle" x="100" y="%i" fill="rgb%s" style="font-size:12px;"> 0.2 </text> \n' % (y_offset+20,str(text_color)))
            f.write('<line x1="200" y1="%i" x2="200" y2="%i" style="stroke:rgb(0,0,0);stroke-width:1" /> \n' % (y_offset-5,y_offset+5))
            f.write('<text text-anchor="middle" x="200" y="%i" fill="rgb%s" style="font-size:12px;"> 0.4 </text> \n' % (y_offset+20,str(text_color)))
            f.write('<line x1="300" y1="%i" x2="300" y2="%i" style="stroke:rgb(0,0,0);stroke-width:1" /> \n' % (y_offset-5,y_offset+5))
            f.write('<text text-anchor="middle" x="300" y="%i" fill="rgb%s" style="font-size:12px;"> 0.6 </text> \n' % (y_offset+20,str(text_color)))
            f.write('<line x1="400" y1="%i" x2="400" y2="%i" style="stroke:rgb(0,0,0);stroke-width:1" /> \n' % (y_offset-5,y_offset+5))
            f.write('<text text-anchor="middle" x="400" y="%i" fill="rgb%s" style="font-size:12px;"> 0.8 </text> \n' % (y_offset+20,str(text_color)))

            f.write('<text text-anchor="middle" x="250" y="%i" fill="rgb%s" style="font-size:14px;"> Similarity Score </text> \n' % (y_offset+50,str(text_color)))

            previous_clusters = all_clusters[0]
            neurons_connected = []
            last_cluster_by_neuron = {}

            previous_merges = {}        
            for skid in skids:
                previous_merges[skid]=1 
                last_cluster_by_neuron[skid] = [skid]

            i = 0
            for step in all_clusters[1:]:
                #print(step)
                i += 1
                for c in step:
                    #If cluster has not changed, do nothing
                    if c in previous_clusters:                  
                        continue

                    try:
                        cluster_color = top_line_color = bot_line_color = colormap[c[0]]                     
                    except:
                        cluster_color = top_line_color = bot_line_color = (0,0,0)
                    
                    #Prepare clusters, colors and line width                
                    mid_line_width = top_line_width = bot_line_width = 1                

                    this_cluster_total = 0
                    for neuron in c:
                        try:                    
                            if colormap[neuron] != cluster_color:                       
                                cluster_color = (0,0,0)
                                #Check if either top or bot cluster is a single neuron (not in neurons_connected)
                                #-> if not, make sure that it still receives it's cluster color even if similarity to next cluster is < threshold
                                if c[0] not in neurons_connected:
                                    top_line_color = colormap[c[0]]
                                else:
                                    top_line_color = (0,0,0)
                                if c[-1] not in neurons_connected:
                                    bot_line_color = colormap[c[-1]]
                                else:
                                    bot_line_color = (0,0,0)
                        except:
                            cluster_color = top_line_color = bot_line_color = (0,0,0)                        

                    top_boundary = clusters_by_neurons[c[0]]
                    bottom_boundary = clusters_by_neurons[c[-1]]
                    center = top_boundary[0] + (bottom_boundary[0] - top_boundary[0])/2             

                    neurons_connected.append(c[0])
                    neurons_connected.append(c[-1])         

                    similarity = merges_at[i]

                    #Vertical Line
                    f.write('<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:rgb%s;stroke-width:%f" /> \n' % (500*similarity,top_boundary[0],500*similarity,bottom_boundary[0],str(cluster_color),round(mid_line_width,1)))
                    #Top horizontal line
                    f.write('<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:rgb%s;stroke-width:%f" /> \n' % (500*similarity,top_boundary[0],top_boundary[1],top_boundary[0],str(top_line_color),round(top_line_width,1)))
                    #Bot horizontal line
                    f.write('<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:rgb%s;stroke-width:%f" /> \n' % (500*similarity,bottom_boundary[0],bottom_boundary[1],bottom_boundary[0],str(bot_line_color),round(bot_line_width,1)))


                    #This is for disconnected SINGLE neurons (need to fix this proper at some point)
                    for neuron in c:
                        if neuron not in neurons_connected:
                            y_coord = neuron_offsets[neuron]                            
                            this_line_width = mid_line_width
                            f.write('<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:rgb%s;stroke-width:%f" /> \n' % (500*similarity,y_coord,500,y_coord,str(cluster_color),round(this_line_width,1)))
                            neurons_connected.append(neuron)
                    
                        previous_merges[neuron] = similarity
                        last_cluster_by_neuron[neuron] = c
                        clusters_by_neurons[neuron] = (center,500*similarity)

                previous_clusters = step

            f.write('</svg>')
            f.close()

        return 

class DisplayHelp(Operator):
    """Displays popup with additional help"""  
    bl_idname = "display.help"  
    bl_label = "Advanced Tooltip" 
    
    entry = StringProperty(name="which entry to show", default = '',options={'HIDDEN'})

    def execute (self, context):        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout 
        if self.entry == 'color.by_similarity':            
            layout.label(text='This function colors neurons based on how similar they are in respect ')
            layout.label(text='to either their morphology or their synapse placement.')
            layout.label(text='Morphological similarity is based on Kohl et al. (2013, Cell). ')
            layout.label(text='Synapse similarity is based on Schlegel et al (2016, bioRxiv).')
            layout.label(text='Dendrogram is created in the same directory as your blend file.')
        elif self.entry == 'color.by_pairs':
            layout.label(text='Gives paired neurons the same color. Pairing is based on annotations:')
            layout.label(text='Neuron needs to have a <paired with #skid> annotation. For example')
            layout.label(text='<paired with #1874652>')
        elif self.entry == 'color.by_spatial':
            layout.label(text='This function colors neurons based on spatial clustering of their somas.')
            layout.label(text='Uses the k-Mean algorithm. You need to set the number of clusters you')
            layout.label(text='expect and the algorithm finds clusters with smallest variance.')
        elif self.entry == 'retrieve.by_pairs':
            layout.label(text='Retrieves neurons paired with already the loaded neurons. Pairing is based')
            layout.label(text='on annotations: neuron needs to have a <paired with #skid> annotation.')
            layout.label(text='For example <paired with #1874652>')


    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self,width=400)
    

class ColorBySpatialDistribution(Operator):
    """Color neurons by spatial Distribution of their Somas"""  
    bl_idname = "color.by_spatial"  
    bl_label = "Color Neurons by Spatial Distribution of their Somas (k-Means algorithm)" 
    bl_options = {'UNDO'}
    
    ### 'radius' is used for determination of the #of neighbors for each soma
    radius = FloatProperty(name="Neighborhood Radius", default = 1.5)
    ### 'min_cluster_distance' is used for minimum distance of somas to other cluster centers to be 
    ###  considered a cluster of their own
    min_cluster_distance = FloatProperty(name="Min. Cluster Dist", default = 2)
    ### Number of clusters the algorithm tries to create
    n_clusters = IntProperty(name="# of Clusters", default = 4)
    ### If 'show_center' is True, a sphere will be created with a r of 'radius'
    show_centers = BoolProperty(    name="Show Cluster Centers", 
                                    default = True,
                                    description = 'If true, a sphere is used to indicate each cluster.' )
    
    
    def execute (self, context):
        neurons = []
        coords = []
        
        ### Set all Materials to Black first
        for material in bpy.data.materials:
            material.diffuse_color = (0,0,0)  
        
        for object in bpy.data.objects:
            if object.name.startswith('Soma'):
                neurons.append(copy.copy(object.name))
                coords.append((copy.copy(object.location),copy.copy(object.name)))
                mat = object.active_material
                
        neighbour_list = self.find_neighbours(coords)        
        bounding_boxes = self.find_top_cluster_centers(neighbour_list)        
        self.color_by_cluster(bounding_boxes)

        return{'FINISHED'}


    def color_by_cluster(self,bounding_box_centers):
        ### Assign unique hue to every cluster
        hues = []
                
        for i in range(len(bounding_box_centers)):
            hues.append((1/len(bounding_box_centers)) * i)
            
            if self.show_centers is True:
                center = bounding_box_centers[i]
                center_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, size=self.min_cluster_distance, \
                                                                 view_align=False, enter_editmode=False, location=center, \
                                                                 rotation=(0, 0, 0), layers=(True, False, False, False, \
                                                                 False, False, False, False, False, False, False, False, \
                                                                 False, False, False, False, False, False, False, False))                           
                bpy.context.active_object.name = 'Cluster Center %i' %i
                bpy.context.active_object.show_transparent = True
            
                ### Apply the same Material as for neuron tree
                Create_Mesh.assign_material (bpy.context.active_object, 'Mat of ' + bpy.context.active_object.name)
                bpy.context.active_object.active_material.diffuse_color = colorsys.hsv_to_rgb(hues[i],1,1) 
                bpy.context.active_object.active_material.alpha = 0.3
        
        for object in bpy.data.objects:
                        
            if object.name.startswith('Soma'):
                dist = 99999
                
                ### Find closest cluster center
                for i in range(len(bounding_box_centers)):
                    new_dist = self.calc_distance(copy.copy(object.location),bounding_box_centers[i])
                    if new_dist < dist:
                        dist = new_dist
                        hue = hues[i]
                
                ### Calculate Falloff for Value:
                falloff = 0.5/self.radius * dist
                value = 1 - falloff

                if value <= 0.5:
                    value = 0.3
                    
                saturation = 1
                object.active_material.diffuse_color = colorsys.hsv_to_rgb(hue,saturation,value)

    
    def find_neighbours(self, data):        
        neighbour_list = []
        
        for object in data:            
            ### Get number of neighbours within range 'radius'
            n_neighbours = 0
            
            print('Searching Partners of %s' % object[1])
            
            for other_object in data:
                dist = self.calc_distance(object[0],other_object[0])                
                print('.....Comparing to %s' % other_object[1])
                
                if dist <= self.radius:                    
                    n_neighbours += 1                    
                    print('Neighbour found (dist = %f)' % dist)
                    
            neighbour_list.append((object, n_neighbours))
                    
        return neighbour_list
     
        
    def find_top_cluster_centers(self,neighbour_list):
        bounding_box_centers = []
        
        ### Start off with sorted list of all neurons
        clusters = sorted(neighbour_list,key = lambda neighbours: neighbours[1], reverse = True)
        print('Sorted %s' % clusters[0][1])
        print(clusters)

        for i in range(self.n_clusters):
            if len(clusters) < i:
                print('WARNING: Cannot form any more clusters!')

                continue
            
            print('Searching for Cluster no. %i ...' % i)
            print('Starting neuron: %s' % clusters[0][0][1])   
            j = 0
            ### Take first neuron in list and pop it
            center = clusters[0][0][0]           
            clusters.pop(0) 
            vector_to_move = [0,0,0]
            n_vectors = 1            
            to_delete = [] 
            
            for j in range(len(clusters)):
                dist = self.calc_distance(center,clusters[j][0][0])
                if dist <= self.min_cluster_distance:
                    print('Found adjacent neighbour (dist = %f):' % dist)
                    print(clusters[j][0][1])
                    ### If within range: add vectors i cluster and remove j cluster                     
                    vector_to_move[0] += clusters[j][0][0][0] - center[0]
                    vector_to_move[1] += clusters[j][0][0][1] - center[1]
                    vector_to_move[2] += clusters[j][0][0][2] - center[2]
                    n_vectors += 1
                    to_delete.append(j)
            
            ### Remove neurons that have previously been associate with a top cluster
            to_delete.sort(reverse=True)
            
            for neuron in to_delete:        
                print('Removing neuron %s' % clusters[neuron][0][1])
                clusters.pop(neuron)                                    
            
            center[0] += vector_to_move[0]/n_vectors
            center[1] += vector_to_move[1]/n_vectors
            center[2] += vector_to_move[2]/n_vectors        
            bounding_box_centers.append(center)
        
            ### For Debugging only:
            #center_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, size=0.4, view_align=False, enter_editmode=False, location=center, rotation=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))                           
        
        return(bounding_box_centers)
                             
    
    def calc_distance(self, vecA,vecB):
        distX = (vecA[0] - vecB[0])**2  
        distY = (vecA[1] - vecB[1])**2
        distZ = (vecA[2] - vecB[2])**2        
        dist = math.sqrt(distX+distY+distZ)
        
        return(dist)
    
    
    def invoke(self, context, event):        
        return context.window_manager.invoke_props_dialog(self)
    
def calc_color (value, max_value, start_rgb, end_rgb,take_longest_route):
    """
    Calculates color along gradient based on value
    """      
    
    #Make sure value is capped at max_value
    if value > max_value:
        value = max_value
        print('WARNING! Value > Max_Value!')
        
    #Convert RGBs to HSVs
    start_hsv = colorsys.rgb_to_hsv(start_rgb[0],start_rgb[1],start_rgb[2])
    end_hsv = colorsys.rgb_to_hsv(end_rgb[0],end_rgb[1],end_rgb[2])
    
    if end_hsv[0] == start_hsv[0]:
        hue_range = 0
    elif take_longest_route is False:
        hue_range = end_hsv[0] - start_hsv[0]    
    elif math.fabs(end_hsv[0] - start_hsv[0]) > (1 - math.fabs(end_hsv[0] - start_hsv[0])):
        hue_range = end_hsv[0] - start_hsv[0]
    else:
        sign = -1 * (end_hsv[0] - start_hsv[0])/math.fabs(end_hsv[0] - start_hsv[0]) #sign makes sure we go the other way around the circle if this is the longer way
        hue_range = (1 - math.fabs(end_hsv[0] - start_hsv[0])) * sign    
        
    h = start_hsv[0] + (hue_range/max_value * value)
    
    if h < 0:
        h = 1 - h
    if h > 1:
        h = h - 1   
        
    s = start_hsv[1] + ((end_hsv[1]-start_hsv[1])/max_value * value)
    v = start_hsv[2] + ((end_hsv[2]-start_hsv[2])/max_value * value)
    
    rgb = colorsys.hsv_to_rgb(h,s,v)
    
    return rgb
        

def calc_hue (value, max_value, lut):
    """
    Tagged for removal
    """
    
    #Make sure value is capped at max_value
    if value > max_value:
        value = max_value

    #Get number of intervals
    n_intervals = (len(lut)-1)

    #Get interval for this value
    interval = math.ceil(n_intervals/max_value * value)

    #Set hue range based on interval
    if interval != 0:
        min_hue = lut[interval-1]
        max_hue = lut[interval]
    #Make sure that if value == 0 the first interval is choosen
    else:
        interval = 1
        min_hue = lut[0]
        max_hue = lut[1]

    this_interval_max_value = interval/n_intervals * max_value    
    
    #Hue range is always calculated as the shortest distance between the values    
    hue_range_cw = math.fabs(max_hue - min_hue)
    hue_range_cww = 360 - hue_range_cw
    
    if hue_range_cw < hue_range_cww:
        hue_range = max_hue - min_hue
    elif max_hue > min_hue:
        hue_range = 360 - max_hue + min_hue
    elif max_hue < min_hue:
        hue_range = -1 * (360 - max_hue + min_hue)
    
    hue = min_hue + (hue_range/this_interval_max_value * value)
    if hue < 0:
        hue = 360 - hue
    if hue > 360:
        hue = hue - 360

    #print('N_Intervals: %i; Interval: %i; Min/Max Hue: %i/%i; Value: %f;max_value: %f; Hue: %f/%f' % (n_intervals,interval,min_hue,max_hue,value,this_interval_max_value,hue_test,hue))

    return hue/360

class CATMAIDAddonPreferences(AddonPreferences):
    """
    Sets Addon preferences -> can be accessed via context.user_preferences.addons['CATMAIDImport'].preferences
    """
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    #bl_idname = __name__
    bl_idname = 'CATMAIDImport'

    server_url = StringProperty(
            name="CATMAID Server URL",
            default =  'https://neurocean.janelia.org/catmaidL1')
    project_id = IntProperty(
            name="Project ID",
            default=1,
            )
    http_user = StringProperty(
            name="HTTP User",
            default=''
            )
    http_pw = StringProperty(
            name="HTTP PW",
            default='',
            subtype='PASSWORD'
            )
    token = StringProperty(
            name="API Token",
            default='',
            subtype='PASSWORD',
            description = 'Retrieve your API token by logging into CATMAID and hovering over your username (top right) on the project selection screen'
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="CATMAID Import Preferences. Add your credentials to not have to enter them again after each restart.")
        layout.prop(self, "server_url")
        layout.prop(self, "project_id")
        layout.prop(self, "http_user")
        layout.prop(self, "http_pw")
        layout.prop(self, "token")

        
def register():
    bpy.utils.register_class(CATMAIDAddonPreferences)
    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(VersionManager)
    bpy.types.Scene.CONFIG_VersionManager = bpy.props.PointerProperty(type=VersionManager)


    """    
    bpy.utils.register_class(CATMAIDimportPanel)
    #bpy.utils.register_class(ImportFromTXT)
    #bpy.utils.register_class(ImportFromNeuroML)
    bpy.utils.register_class(Create_Mesh)
    bpy.utils.register_class(RandomMaterial)
    bpy.utils.register_class(RenderAllNeurons)
    bpy.utils.register_class(ExportAllToSVG)
    bpy.utils.register_class(ConnectToCATMAID)
    bpy.utils.register_class(RetrieveNeuron) 
    bpy.utils.register_class(RetrievePartners) 
    bpy.utils.register_class(RetrieveConnectors) 
    bpy.utils.register_class(ConnectorsToSVG) 
    bpy.utils.register_class(SetupMaterialsForRender) 
    bpy.utils.register_class(RetrieveByAnnotation)
    bpy.utils.register_class(UpdateNeurons)
    bpy.utils.register_class(ColorBySpatialDistribution)
    bpy.utils.register_class(ColorBySynapseCount)
    bpy.utils.register_class(TestHttpRequest)
    """
 
 
def unregister():
    bpy.utils.unregister_module(__name__)    
    bpy.utils.unregister_class(ExampleAddonPreferences) 
    """
    bpy.utils.unregister_class(CATMAIDimportPanel) 
    #bpy.utils.unregister_class(ImportFromTXT)
    bpy.utils.unregister_class(Create_Mesh)
    #bpy.utils.unregister_class(ImportFromNeuroML)
    bpy.utils.unregister_class(RandomMaterial)
    bpy.utils.unregister_class(RenderAllNeurons)
    bpy.utils.unregister_class(ExportAllToSVG)
    bpy.utils.unregister_class(ConnectToCATMAID)
    bpy.utils.unregister_class(RetrieveNeuron)
    bpy.utils.unregister_class(RetrievePartners)
    bpy.utils.unregister_class(RetrieveConnectors)  
    bpy.utils.unregister_class(ConnectorsToSVG)
    bpy.utils.unregister_class(SetupMaterialsForRender)
    bpy.utils.unregister_class(RetrieveByAnnotation)
    bpy.utils.unregister_class(UpdateNeurons)
    bpy.utils.unregister_class(ColorBySpatialDistribution) 
    bpy.utils.unregister_class(ColorBySynapseCount)
    bpy.utils.unregister_class(TestHttpRequest)
    """
    if bpy.context.scene.get('CONFIG_VersionManager') != None:     
        del bpy.context.scene['CONFIG_VersionManager']
    try:
        del bpy.types.Scene.CONFIG_VersionManager
    except:
        pass


if __name__ == "__main__":
    register()
 
