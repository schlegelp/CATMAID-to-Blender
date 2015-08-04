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

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper 
from bpy.props import FloatVectorProperty, FloatProperty, StringProperty, BoolProperty, EnumProperty, IntProperty

####
#Retrieve credentials from PW.txt
#Change file path as needed:
pw_file = 'c:\\Program Files\\Blender Foundation\\Blender\\2.68\\scripts\\addons\\PW.txt'

try:
    with open(pw_file,'r') as f:
        catmaid_user = f.readline()[:-1] #remove \n from readline
        http_user = f.readline()[:-1]
        catmaid_pw = f.readline()[:-1]
        http_pw = f.readline()  #no new line after this one
    f.close()
except:    
    print("No File containing credentials found! You will have to enter them by hand :(")
    catmaid_user = ''
    http_user = ''

    catmaid_pw = ''
    http_pw = ''    
###

remote_instance = None
connected = False
server_url = 'https://neurocean.janelia.org/catmaidL1'

bl_info = {
 "name": "Import/Export Neuron from CATMAID",
 "author": "Philipp Schlegel",
 "version": (3, 9, 0),
 "blender": (2, 7, 1),
 "location": "Properties > Scene > CATMAID Import",
 "description": "Imports Neuron from CATMAID server, Analysis tools, Export to SVG",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "Object"}
 
 
class CATMAIDimportPanel(bpy.types.Panel):
    """Creates Menu in Properties - scene """
    bl_label = "CATMAID Import"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"      
     
    def draw(self, context):       
        
        layout = self.layout   
        
        #Version Check
        config = bpy.data.scenes[0].CONFIG_VariableManager        
        layout.label(text="Your Script Version: %s" % str(round(config.current_version,3)))
        if config.latest_version == 0:
            layout.label(text="Latest Version on Github: Unable to Retrieve")
        else:
            layout.label(text="Latest Version on Github: %s" % str(round(config.latest_version,3))) 
            
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
        row = layout.row(align=True)
        row.alignment = 'EXPAND' 

        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("random.all_materials", text = "Randomize Color", icon ='COLOR')

        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_spatial", text = "By Spatial Distr.", icon ='COLOR')
        
        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_synapse_count", text = "By Synapse Count", icon ='COLOR')
        
        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("color.by_pairs", text = "By Pairs", icon ='COLOR')        

        row = layout.row(align=False)
        row.alignment = 'EXPAND'
        row.operator("for_render.all_materials", text = "Setup 4 Render", icon ='COLOR')

        layout.label('CATMAID Import')
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("connect.to_catmaid", text = "Connect 2 CATMAID", icon = 'EXTERNAL_DATA')#.number=1
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.neuron", text = "Retrieve by SkeletonID", icon = 'LOAD_FACTORY')#.number=1
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.by_annotation", text = "Retrieve by Annotation", icon = 'LOAD_FACTORY')#.number=1
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.partners", text = "Retrieve Partners", icon = 'LOAD_FACTORY')#.number=1
        row.alignment = 'EXPAND'
        row.operator("retrieve.by_pairs", text = "Retrieve Paired", icon = 'LOAD_FACTORY')#.number=1
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("reload.neurons", text = "Reload Neurons", icon = 'FILE_REFRESH')#.number=1
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("retrieve.connectors", text = "Retrieve Weighted Connectors", icon = 'LOAD_FACTORY')#.number=1
        
        layout.label(text="Export to SVG:")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("exportall.to_svg", text = 'Export Morphology')
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("connectors.to_svg", text = 'Export Connectors')        
        
        
class VariableManager(bpy.types.PropertyGroup):    
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
            latest_version = 0
            last_stable = 0
            new_features = ''
            message = ''

        config = bpy.data.scenes[0].CONFIG_VariableManager    
        config.current_version = current_version
        config.latest_version = float(latest_version)
        config.last_stable_version = float(last_stable)
        config.message = message
        config.new_features = new_features
        
    @classmethod
    def poll(cls, context):                
        return context.active_object is not None    

class CatmaidInstance:
    """ A class giving access to a CATMAID instance.
    """

    def __init__(self, srv, catmaid_usr, catmaid_pwd,
            http_usr=None, http_pwd=None):
        # Store server and user information
        self.server = srv
        self.user = catmaid_usr
        self.password = catmaid_pwd
        # Cookie storage
        self.cookies = cj.CookieJar()
        # Handlers
        handlers = []
        # Add redirect handler
        handlers.append( urllib.request.HTTPRedirectHandler() )
        # Add cookie handler
        handlers.append( urllib.request.HTTPCookieProcessor( self.cookies ) )
        # Add HTTP authentification if needed
        if http_usr and http_pwd:
            authinfo = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            authinfo.add_password(None, srv, http_usr, http_pwd)
            auth_handler = urllib.request.HTTPBasicAuthHandler(authinfo)
            # Add authentication handler
            handlers.append( auth_handler )
        # Create final opener
        self.opener = urllib.request.build_opener( *handlers )
        

    def mkurl(self, path):
        return self.server + path
    

    def login(self):
        url = self.mkurl("/accounts/login")
        opts = {
            'name': self.user,
            'pwd': self.password
        }

        data = urllib.parse.urlencode(opts)
        data = data.encode('utf-8')
        request = urllib.request.Request(url, data)
        response = self.opener.open(request)
        self.cookies.extract_cookies(response, request)

        return response.read()
    

    #Retrieves url from Server    
    def get_page(self, url, data=None):
        if data:
            data = urllib.parse.urlencode(data)
            data = data.encode('utf-8')
            request = urllib.request.Request(url, data)
        else:
            request = urllib.request.Request(url)

        response = self.opener.open(request)

        #Decode into array format
        return json.loads(response.read().decode("utf-8"))  #may have to adapt this depending on url requested

    #Use to parse url for retrieving stack infos
    def get_stack_info_url(self, pid, sid):
        return self.mkurl("/" + str(pid) + "/stack/" + str(sid) + "/info")

    #Use to parse url for retrieving skeleton nodes (no info on parents or synapses, does need post data)
    def get_skeleton_nodes_url(self, pid):
        return self.mkurl("/" + str(pid) + "/treenode/table/list")

    #ATTENTION: this url doesn't work properly anymore as of 07/07/14
    #use compact-skeleton instead
    #Used to parse url for retrieving all info the 3D viewer gets (does NOT need post data)
    #Format: name, nodes, tags, connectors, reviews 
    def get_skeleton_for_3d_viewer_url(self, pid, skid):
        return self.mkurl("/" + str(pid) + "/skeleton/" + str(skid) + "/compact-json")
    
    #Use to parse url for retrieving connectivity (does need post data)
    def get_connectivity_url(self, pid):
        return self.mkurl("/" + str(pid) + "/skeleton/connectivity" )
    
    #Use to parse url for retrieving info connectors (does need post data)
    def get_connectors_url(self, pid):
        return self.mkurl("/" + str(pid) + "/connector/skeletons" )
    
    #Use to parse url for retrieving annotated neurons (does need post data)
    def get_annotated_url(self, pid):
        return self.mkurl("/" + str(pid) + "/neuron/query-by-annotations" )
    
    #Use to parse url for retrieving list of all annotations (and their IDs) (does NOT need post data)
    def get_annotation_list(self, pid):
        return self.mkurl("/" + str(pid) + "/annotations/list" )
    
    #Use to get annotations for given neuron. DOES need skid as postdata
    def get_annotations_for_skid_list(self, pid):
        return self.mkurl("/" + str(pid) + "/annotations/skeletons/list" )     
    
    #Use to parse url for retrieving ancestry (e.g. name) of an id (does need post data: pid, skid)
    def get_ancestry(self, pid):
        return self.mkurl("/" + str(pid) + "/skeleton/ancestry" )
    
    #Use to parse url for names for a list of skeleton ids (does need post data: pid, skid)
    def get_neuronnames(self, pid):
        return self.mkurl("/" + str(pid) + "/skeleton/neuronnames" )   
    
    #Use to parse url for retrieving all info the 3D viewer gets (does NOT need post data)
    #Returns, in JSON, [[nodes], [connectors], [tags]], with connectors and tags being empty when 0 == with_connectors and 0 == with_tags, respectively
    def get_compact_skeleton_url(self, pid, skid, connector_flag = 1, tag_flag = 1):        
        return self.mkurl("/" + str(pid) + "/" + str(skid) + "/" + str(connector_flag) + "/" + str(tag_flag) + "/compact-skeleton") 
    
    
def get_annotations_from_list (skid_list, remote_instance):
    #Takes list of skids and retrieves annotations
    #Attention! It seems like this URL does not process more than 250 skids at a time!

    remote_get_annotations_url = remote_instance.get_annotations_for_skid_list( 1 )

    get_annotations_postdata = {}               

    for i in range(len(skid_list)):
        key = 'skids[%i]' % i
        get_annotations_postdata[key] = str(skid_list[i])

    print('Asking for %i skeletons annotations...' % len(get_annotations_postdata), end = ' ')   

    annotation_list_temp = remote_instance.get_page( remote_get_annotations_url , get_annotations_postdata )
    
    annotation_list = {}    

    for skid in annotation_list_temp['skeletons']:
        annotation_list[skid] = []        
        for annotation_id in annotation_list_temp['skeletons'][skid]:
            annotation_list[skid].append(annotation_list_temp['annotations'][str(annotation_id)])

    print('%i retrieved' % len(annotation_list))
    
    #Returns dictionary: annotation_list = {skid1 : [annotation1,annotation2,....], skid2: []}
   
    return(annotation_list)

def get_partners (skid_list, remote_instance, hops, upstream=True,downstream=True):

    #By seperating up and downstream retrieval we make sure that we don't go back in the second hop
    #E.g. we only want inputs of inputs and NOT inputs+outputs of inputs
    skids_upstream_to_retrieve = skid_list
    skids_downstream_to_retrieve = skid_list   

    partners = {}
    partners['incoming'] = []
    partners['outgoing'] = []    
    skids_already_seen = {}

    remote_connectivity_url = remote_instance.get_connectivity_url( 1 )        
    for hop in range(hops):  
        upstream_partners_temp = {}
        connectivity_post = {}
        connectivity_post['threshold'] = 1
        connectivity_post['boolean_op'] = 'logic_OR' 
        if upstream is True:        
            for i in range(len(skids_upstream_to_retrieve)):
                tag = 'source[%i]' % i
                connectivity_post[tag] = skids_upstream_to_retrieve[i]
                
            print( "Retrieving Upstream Partners for %i neurons [%i. hop]..." % (len(skids_upstream_to_retrieve),hop+1))
            connectivity_data = []
            connectivity_data = remote_instance.get_page( remote_connectivity_url , connectivity_post ) 
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
        connectivity_post['boolean_op'] = 'logic_OR'         
        downstream_partners_temp = {}
        if downstream is True:        
            for i in range(len(skids_downstream_to_retrieve)):
                tag = 'source[%i]' % i
                connectivity_post[tag] = skids_downstream_to_retrieve[i]
        
            print( "Retrieving Downstream Partners for %i neurons [%i. hop]..." % (len(skids_downstream_to_retrieve),hop+1))
            connectivity_data = []
            connectivity_data = remote_instance.get_page( remote_connectivity_url , connectivity_post )   
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
    
    
class TestHttpRequest(Operator):
    """Test Class for Debugging only"""

    bl_idname = "test.request" 
    bl_label = "Test Http Requests" 
    
    
    def execute(self,context):
        skids = [10418394,4453485]
        
        remote_get_names = remote_instance.get_neuronnames( 1 )
        
        get_names_postdata = {}
        get_names_postdata['pid'] = 1
        
        for i in range(len(skids)):
            key = 'skids[%i]' % i
            get_names_postdata[key] = skids[i]
        
        #get_names_postdata = {'pid' : 1 ,'skids[0]': '10418394', 'skids[1]': '4453485'}

        names = remote_instance.get_page( remote_get_names , get_names_postdata )
        
        print(names)
        
        return{'FINISHED'}
       
    
def get_neuronnames(skids):
    """Retrieves and Returns a list of names for a list of neurons"""
    
    ### Get URL to neuronnames function
    remote_get_names = remote_instance.get_neuronnames( 1 )
    
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
    neuron_names = remote_instance.get_page( remote_get_names , get_names_postdata )
    
    return(neuron_names)


class UpdateNeurons(Operator):      
    """Updates existing Neurons in Scene from CATMAID Server"""

    bl_idname = "reload.neurons"  
    bl_label = "Update Neurons from CATMAID Server"   
    bl_options = {'UNDO'}
    
    all_neurons = BoolProperty(name="Update All", default = True)
    keep_resampling = BoolProperty(name="Keep Old Resampling?", default = True)
    new_resampling = IntProperty(name="else: New Resampling Factor", default = 2, min = 1, max = 20)
    import_connectors = BoolProperty(name="Import Connectors", default = True)
    
    
    def execute(self,context):
        existing_neurons = {}
        resampling = 1
        
        ### Gather skeleton IDs
        if self.all_neurons is True:
            for neuron in bpy.data.objects:
                if neuron.name.startswith('#'):
                    try:
                        skid = re.search('#(.*?) -',neuron.name).group(1)
                        existing_neurons[neuron.name] = {}
                        existing_neurons[neuron.name]['skid'] = skid
                        if 'resampling' in neuron:
                            existing_neurons[neuron.name]['resampling'] = neuron['resampling']
                        else:
                            existing_neurons[neuron.name]['resampling'] = 1
                    except:
                        print('Unable to process neuron ', neuron.name)
    
            ### Select all Neuron-related objects (Skeletons, Inputs/Outputs) and deselect everything else                          
            for object in bpy.data.objects:
                if object.name.startswith('#') or object.name.startswith('Outputs of') or object.name.startswith('Inputs of') or object.name.startswith('Soma of'):
                    object.select = True
                else:
                    object.select = False
                    
            ### Delete selected objects
            bpy.ops.object.delete(use_global=False)
                    
        else:
            neuron = bpy.context.active_object
            if neuron.name.startswith('#'):
                skid = re.search('#(.*?) -',neuron.name).group(1)
                existing_neurons[neuron.name] = {}
                existing_neurons[neuron.name]['skid'] = skid
                if 'resampling' in neuron:
                    existing_neurons[neuron.name]['resampling'] = neuron['resampling']
                else:
                    existing_neurons[neuron.name]['resampling'] = 1  
                    
                for object in bpy.data.objects:
                    if object.name.startswith('#'+skid) or object.name.startswith("Outputs of " + skid) or object.name.startswith("Inputs of " + skid):
                        object.select = True
                    else:
                        object.select = False
                        
                ### Delete selected objects
                bpy.ops.object.delete(use_global=False)
                                      
            else:
                print('Active object not a neuron!')
                return{'FINISHED'}
        
        ### Get Neuron Names (in case they changed):
        print('Retrieving newest neuron names...')
        skids_to_retrieve = []
        for neuron in existing_neurons:
            skids_to_retrieve.append(existing_neurons[neuron]['skid'])
        neuron_names = get_neuronnames(skids_to_retrieve)

        ### Reload neurons
        for neuron in existing_neurons:
            skid = existing_neurons[neuron]['skid']            
            print('Updating Neuron %s' % neuron)
            if self.keep_resampling is True:       
                resampling = existing_neurons[neuron]['resampling']     
                RetrieveNeuron.add_skeleton(self, skid, neuron_names[skid], resampling, self.import_connectors) 
            else:
                RetrieveNeuron.add_skeleton(self, skid, neuron_names[skid], self.new_resampling, self.import_connectors) 
        
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
    
    skeleton_id = StringProperty(name="Skeleton ID(s)")  
    import_connectors = BoolProperty(name="Import Connectors", default = True)
    resampling = IntProperty(name="Resampling Factor", default = 2, min = 1, max = 20)
      
    
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
                error_temp = self.add_skeleton(skid,neuron_names[skid], self.resampling, self.import_connectors)
                self.count += 1
                
                if error_temp != '':
                    errors.append(error_temp)
                
        if len(errors) == 0:
            print('Success! %i neurons imported' % len(skeletons_to_retrieve))

        else:
            print('%i Error(s) while Importing:' % len(errors))

            for entry in errors:
                print(entry)
                        
        return {'FINISHED'}                  


    def add_skeleton(self, skeleton_id, neuron_name = '', resampling = 1, import_connectors = True):
        
        if neuron_name == '':
            print('Retrieving name of skeleton %s' % str(skeleton_id))
            neuron_name = get_neuronnames([neuron_name])[0]
        
        error = ''       
        
        cellname = skeleton_id + ' - ' + neuron_name  
        #truncated neuron name down to 63 letters if necessary
        if len(cellname) >= 60:
            cellname = cellname[0:56] +'...'
            print('Object name too long - truncated: ', cellname)
        
        object_name = '#' + cellname
            
        if object_name in bpy.data.objects:
            print('Neuron already exists! Skipping.')
            return error
        
        if import_connectors is True:
            remote_get_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , skeleton_id ,1,0)
        else:
            remote_get_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , skeleton_id ,0,0)            
        node_data = []
        node_data = remote_instance.get_page( remote_get_compact_skeleton_url )

        print("%i entries for neuron %s retrieved" % (len(node_data),skeleton_id) )
                
        ### Continue only of data retrieved contains 5 entries (if less there was an error while importing)
        if len(node_data) == 3 or len(node_data) == 2:             
            CATMAIDtoBlender.extract_nodes(node_data, skeleton_id, neuron_name, resampling, import_connectors)
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
    
    selected_neurons = BoolProperty(name="Of Selected Neurons", default = True)
    import_connectors = BoolProperty(name="Import Connectors", default = True)
    resampling = IntProperty(name="Resampling Factor", default = 2, min = 1, max = 20)
    
    
    def execute(self, context):  
        global remote_instance
        
        neurons = []
        
        if self.selected_neurons is True:
            print('Retrieving annotation of neurons')
            for neuron in bpy.context.selected_objects:    
                if neuron.name.startswith('#'):
                    try:                        
                        neurons.append(re.search('#(.*?) -',neuron.name).group(1))
                    except:
                        pass
        else:
            neurons = [re.search('#(.*?) -',bpy.context.active_object.name).group(1)]           

                
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
                            continue
                            
                        if paired_skid != None:
                            print('Warning - Multiple paired Annotations found for neuron %s! Neuron skipped!' % str(neuron))
                            paired_skid = None
                            continue
                            
                        paired_skid = skid
            except:
                pass
                    
            if paired_skid != None:
                if paired_skid in paired:
                    print('Warning - Neuron %s annotated as paired in multiple Neurons!' % str(paired_skid))                    
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
                
        for skid in paired:            
            print('Retrieving skeleton %s [%i of %i]' % (skid,count,len(paired)))
            try:
                RetrieveNeuron.add_skeleton(self,skid,neuron_names[skid], self.resampling, self.import_connectors)            
                count += 1         
            except:
                print('Error importing skid %s - wrong annotated skid?' %skid)
        
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
    
    annotation = StringProperty(name="Annotation")
    import_connectors = BoolProperty(name="Import Connectors", default = True)
    resampling = IntProperty(name="Resampling Factor", default = 2, min = 1, max = 20)
    
    
    def execute(self, context):  
        global remote_instance
        
        ### Get annotation ID of self.annotation
        annotation_id = self.retrieve_annotation_list()
        
        if annotation_id != 'not found':
            self.retrieve_annotated(self.annotation, annotation_id)
        else:
            print('Annotation not found in List! Import stopped!')
        
        return{'FINISHED'}
    
    
    def retrieve_annotation_list(self):
        print('Retrieving list of Annotations...')
        
        remote_annotation_list_url = remote_instance.get_annotation_list(1)
        list = remote_instance.get_page( remote_annotation_list_url )
        
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
        annotation_post = {'neuron_query_by_annotation': annotation_id, 'display_start': 0, 'display_length':500}
        remote_annotated_url = remote_instance.get_annotated_url( 1 )
        neuron_list = remote_instance.get_page( remote_annotated_url, annotation_post )
        count = 0        
        
        wm = bpy.context.window_manager
        ### Start progress bar at cursor (currently doesn't seem to work b/c window is not properly updated)
        wm.progress_begin(0, len(neuron_list['entities']))
        
        print('Retrieving names of annotated neurons...')
        annotated_skids = []
        for entry in neuron_list['entities']:
            annotated_skids.append(str(entry['skeleton_ids'][0]))
        neuron_names = get_neuronnames(annotated_skids)
        
        for entry in neuron_list['entities']:
            skid = str(entry['skeleton_ids'][0])
            print('Retrieving skeleton %s [%i of %i]' % (skid,count,len(neuron_list['entities'])))
            RetrieveNeuron.add_skeleton(self,skid,neuron_names[skid], self.resampling, self.import_connectors)
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
    """Retrieves Connectors of active/all Neuron from CATMAID database"""
    bl_idname = "retrieve.connectors"  
    bl_label = "Connectors will be created in Layer 3!!!"
     
    all_neurons = BoolProperty(name="Process All", default = False)
    selected_neurons = BoolProperty(name="Process Selected", default = False)
    random_colors = BoolProperty(name="Random Colors", default = False)
    basic_radius = FloatProperty(name="Basic Radius", default = 0.01)
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
        
        bpy.context.scene.layers[2] = True
        
        if self.all_neurons is False and self.selected_neurons is False:
            if bpy.context.active_object is None:
                print ('No Object Active')
            elif bpy.context.active_object is not None and '#' not in bpy.context.active_object.name:
                print ('Active Object not a Neuron') 
            else:                      
                active_skeleton = re.search('#(.*?) -',bpy.context.active_object.name).group(1)
                self.get_connectors(active_skeleton)   
        
        elif self.all_neurons is True:
            n = 0
            n_total = len(bpy.data.objects)
            for neuron in bpy.data.objects:
                n += 1
                if '#' in neuron.name:
                    print('Importing Connectors for Neuron %i [of %i]' % (n,n_total))
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    self.get_connectors(skid)
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)
        
        elif self.selected_neurons is True:
            n = 0
            n_total = len(bpy.context.selected_objects)
            for neuron in bpy.context.selected_objects:
                n += 1
                if '#' in neuron.name:
                    print('Importing Connectors for Neuron %i [of %i]' % (n,n_total))
                    skid = re.search('#(.*?) -',neuron.name).group(1)                    
                    self.get_connectors(skid)           
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)
                
            
        return {'FINISHED'}   
    
        
    def get_connectors(self, active_skeleton):
        node_data = []
        connector_ids = []
                        
        ### Retrieve compact json data and filter connector ids
        print('Retrieving connector data for skid %s...' % active_skeleton)
        remote_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , active_skeleton, 1, 0 )
        node_data = remote_instance.get_page( remote_compact_skeleton_url )

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
       
        print('%s Up- / %s Downstream connectors for skid %s found' % (len(connector_post_coords), len(connector_pre_coords), active_skeleton))

        remote_connector_url = remote_instance.get_connectors_url( 1 )

        if self.get_outputs is True:
            print( "Retrieving Postsynaptic Targets..." )
            ### Get connector data for all presynapses to determine number of postsynaptic targets and filter
            connector_data_post = remote_instance.get_page( remote_connector_url , connector_post_postdata )
        else:
            connector_data_post = []        
        
        if self.get_inputs is True:
            print( "Retrieving Presynaptic Targets..." )
            ### Get connector data for all presynapses to filter later           
            connector_data_pre = remote_instance.get_page( remote_connector_url , connector_pre_postdata ) 
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
            Create_Mesh.make_connector_spheres (active_skeleton, connector_post_coords, connector_pre_coords, number_of_targets, self.random_colors, self.basic_radius)
                
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
     
    all_neurons = BoolProperty(name="Process All", default = True)
    random_colors = BoolProperty(name="Use Random Colors", default = False)
    mesh_colors = BoolProperty(name="Use Mesh Colors", default = False)
    #gray_colors = BoolProperty(name="Use Gray Colors", default = False)
    merge = BoolProperty(name="Merge into One", default = True)
    color_by_input = BoolProperty(name="Color by Input", default = True)
    color_by_strength = BoolProperty(name="Color by Total # Connections", default = False)
    color_by_connections = StringProperty(name="Color by Connections to:", default = '',
                                     description="Count connections of neuron to this neuron and color connectors appropriately. Attention: whether up- and or downstream partners are counted is set by [export inputs] and [export outputs]")
    color_by_density = BoolProperty(name = "Color by Density", 
                                    default = False, 
                                    description = "Colors Edges between Nodes by # of Nodes of given Object (choose below)")                                    
    object_for_density = EnumProperty(name = "Object for Density", 
                                      items = availableObjects,
                                      description = "Choose Object for Coloring Edges by Density")
    proximity_radius_for_density = FloatProperty(name="Proximity Threshold", 
                                                 default = 0.25,
                                                 description = "Maximum allowed distance between Edge and a Node")        
    export_inputs = BoolProperty(name="Export Inputs", default = True)
    export_outputs = BoolProperty(name="Export Outputs", default = False)
    scale_outputs = BoolProperty(name="Scale Presynapses", default = False)    
    basic_radius = FloatProperty(name="Base Node Radius", default = 0.5) 
    use_arrows = BoolProperty(  name="Use Arrows", 
                                default = False,
                                description = "Use Arrows instead of Circles to indicate Incoming/Outgoing Synapses")
    export_ring_gland = BoolProperty(name="Export Ring Gland", default = False)
    export_neuron = BoolProperty(name="Include Neuron", default = True)
    filter_connectors = StringProperty(name="Filter Connector:", default = '',
                                     description="Filter Connectors by edges from/to neuron name(s)! (syntax: to exclude start with ! / to set synapse threshold start with > / applies to neuron names / case INsensitive / comma-separated -> ORDER MATTERS! ) ")
    #filter_downstream = StringProperty(name="Filter Outputs:", default = '')
    
    x_persp_offset = FloatProperty(name="Horizontal Perspective", default = 0.5, max = 2, min = -2)  
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
                                    description = "Choose which views should be included in final SVG")\
                    
    
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
        remote_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , active_skeleton, 1, 0 )

        node_data = remote_instance.get_page( remote_compact_skeleton_url )

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
        remote_connector_url = remote_instance.get_connectors_url( 1 )
    
        if self.export_outputs is True:        
            print( "Retrieving Target Connectors..." )        
            connector_data_post = remote_instance.get_page( remote_connector_url , connector_postdata_postsynapses )
            #print(connector_data_post)
        else:
            connector_data_post = []

        if self.export_inputs is True:    
            print( "Retrieving Source Connectors..." )
            connector_data_pre = remote_instance.get_page( remote_connector_url , connector_postdata_presynapses )
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
                print('Unable to create density data for object!')  
            
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
                f.write(line_to_write + '\n')                        
                
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
                                line_to_write='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.use_arrows is True:
                            line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-2,connector_y,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x-1,connector_y,
                                                connector_x-3,connector_y+1,
                                                connector_x-3,connector_y-1,                                                
                                                str(inputs_color)
                                               )                        
                            
                        else:                 
                            line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        f.write(line_to_write + '\n')

                line_to_write = '</g>' 
                f.write(line_to_write + '\n')   
          
                ### Export Outputs from front view
                line_to_write = '<g id="Outputs">' 
                f.write(line_to_write + '\n')                         
                
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
                        
                    if self.use_arrows is True:
                        line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x-9,connector_y,
                                            connector_x-2,connector_y,
                                            str(outputs_color),str(radius/3)
                                           )
                        line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                        % ( connector_x-10,connector_y,
                                            connector_x-8,connector_y+1,
                                            connector_x-8,connector_y-1,                                                
                                            str(outputs_color)
                                           )     
                    else:
                        line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                     % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(outputs_width_stroke))
                    f.write(line_to_write + '\n')

                line_to_write = '</g>' 
                f.write(line_to_write + '\n')

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
                line_to_write = '<g id="Inputs">' 
                f.write(line_to_write + '\n')
                
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
                                line_to_write='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.use_arrows is True:
                            line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x,connector_y-10,
                                                connector_x,connector_y-2,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x,connector_y-1,
                                                connector_x+1,connector_y-3,
                                                connector_x-1,connector_y-3,                                                
                                                str(inputs_color)
                                               )
                            
                        else:                 
                            line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        f.write(line_to_write + '\n')                

                line_to_write = '</g>' 
                f.write(line_to_write + '\n')   
                ### Export Outputs from lateral view
                line_to_write = '<g id="Outputs">' 
                f.write(line_to_write + '\n')                         
                
                for connector in connectors_post:
                    connector_x = round(connectors_post[connector]['coords'][1] * 10,1)
                    connector_y = round(connectors_post[connector]['coords'][2] * - 10,1)
                    
                    if self.color_by_density is True:
                        outputs_color = density_color_map[connector]
                    
                    if self.scale_outputs is True:
                        radius = basic_radius * (0.8 + connectors_weight[connector]/5) #connectors with 5 targets will be double the size
                    else:
                        radius = basic_radius
                        
                    if self.use_arrows is True:
                        line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x,connector_y-9,
                                            connector_x,connector_y-2,
                                            str(outputs_color),str(radius/3)
                                           )
                        line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                        % ( connector_x,connector_y-10,
                                            connector_x+1,connector_y-8,
                                            connector_x-1,connector_y-8,                                                
                                            str(outputs_color)
                                           )    
                    else:
                        line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                        % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(outputs_width_stroke))
                    f.write(line_to_write + '\n')

                line_to_write = '</g>' 
                f.write(line_to_write + '\n')

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
                f.write(line_to_write + '\n')
                
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
                                line_to_write='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.use_arrows is True:
                            line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-2,connector_y,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x-1,connector_y,
                                                connector_x-3,connector_y+1,
                                                connector_x-3,connector_y-1,                                                
                                                str(inputs_color)
                                               )  
                            
                        else:                 
                            line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        f.write(line_to_write + '\n')

                line_to_write = '</g>' 
                f.write(line_to_write + '\n')   
                ### Export Outputs from perspective view
                line_to_write = '<g id="Outputs">' 
                f.write(line_to_write + '\n')                         
                
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
                    
                    if self.use_arrows is True:
                        line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x-9,connector_y,
                                            connector_x-2,connector_y,
                                            str(outputs_color),str(radius/3)
                                           )
                        line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                        % ( connector_x-10,connector_y,
                                            connector_x-8,connector_y+1,
                                            connector_x-8,connector_y-1,                                                
                                            str(outputs_color)
                                           ) 
                    else:
                        line_to_write = '<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                        % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(outputs_width_stroke))
                    f.write(line_to_write + '\n')

                line_to_write = '</g>' 
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
                f.write(line_to_write + '\n')
                
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
                                line_to_write='<polygon points="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(shape_temp),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))                                                        
                            else:
                                line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                            % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                                str(inputs_color_stroke),str(inputs_width_stroke))
                                                
                        elif self.use_arrows is True:
                            line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                            % ( connector_x-10,connector_y,
                                                connector_x-2,connector_y,
                                                str(inputs_color),str(basic_radius/3)
                                               )
                            line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                            % ( connector_x-1,connector_y,
                                                connector_x-3,connector_y+1,
                                                connector_x-3,connector_y-1,                                                
                                                str(inputs_color)
                                               )                              
                        else:                 
                            line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="rgb%s" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y),str(basic_radius),str(inputs_color),\
                                      str(inputs_color_stroke),str(inputs_width_stroke))
                        f.write(line_to_write + '\n')    

                line_to_write = '</g>' 
                f.write(line_to_write + '\n')   
                ### Export Outputs from top view
                line_to_write = '<g id="Outputs">' 
                f.write(line_to_write + '\n')                         
                
                for connector in connectors_post:
                    connector_x = round(connectors_post[connector]['coords'][0] * 10,1)
                    connector_y = round(connectors_post[connector]['coords'][1] * - 10,1)
                    
                    if self.color_by_density is True:
                        outputs_color = density_color_map[connector]
                    
                    if self.scale_outputs is True:
                        radius = basic_radius * (0.8 + connectors_weight[connector]/5) #connectors with 5 targets will be double the size
                    else:
                        radius = basic_radius
                        
                    if self.use_arrows is True:
                        line_to_write='<path d="M%i,%i L%i,%i" stroke="rgb%s" stroke-width="%s"/> \n' \
                                        % ( connector_x-9,connector_y,
                                            connector_x-2,connector_y,
                                            str(outputs_color),str(radius/3)
                                           )
                        line_to_write+='<polygon points="%i,%i %i,%i %i,%i" fill="rgb%s" stroke-width="0"/>' \
                                        % ( connector_x-10,connector_y,
                                            connector_x-8,connector_y+1,
                                            connector_x-8,connector_y-1,                                                
                                            str(outputs_color)
                                           ) 
                    else:                    
                        line_to_write='<circle cx="%s" cy="%s" r="%s" fill="rgb%s" stroke="black" stroke-width="%s"  />' \
                                      % (str(connector_x),str(connector_y), str(radius),str(outputs_color),str(inputs_width_stroke))
                    f.write(line_to_write + '\n')

                line_to_write = '</g>' 
                f.write(line_to_write + '\n') 
                
                ### Add top brain shape
                if self.merge is False or first_neuron is True:
                    f.write('\n' + brain_shape_top_string + '\n') 
                
                    if self.export_ring_gland is True:
                        f.write('\n' + ring_gland_top + '\n')             

            offsetY_forLegend = -150
            ### Create legend for neurons if merged
            if self.merge is True and self.color_by_input is False and self.color_by_strength is False:
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
        
        return {'FINISHED'}
    
    
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
            print('Cannot create Scale for Synaptic Strength if Merged: heterogenous data')
            
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
                print('Invalid Neuron Name found: %s' % neuron )
        
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
        
        remote_connectivity_url = remote_instance.get_connectivity_url( 1 )  
        connectivity_post = {}
        connectivity_post['threshold'] = 1
        connectivity_post['boolean_op'] = 'logic_OR'                
        for i in range(len(neurons)):
            tag = 'source[%i]' % i
            connectivity_post[tag] = neurons[i]
            connection_count[neurons[i]] = 0
                
        print( "Retrieving Partners for %i neurons..." % len(neurons))
        connectivity_data = []
        connectivity_data = remote_instance.get_page( remote_connectivity_url , connectivity_post ) 
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
    
    selected = BoolProperty(name="From Selected Neurons?", default = False)   
    inputs = BoolProperty(name="Retrieve Upstream Partners?", default = True)          
    outputs = BoolProperty(name="Retrieve Downstream Partners?", default = True)
    minimum_synapses = IntProperty(name="Synapse Threshold", default = 5)
    import_connectors = BoolProperty(name="Import Connectors", default = True)   
    resampling = IntProperty(name="Resampling Factor", default = 2, min = 1, max = 20) 
    filter_by_annotation = StringProperty(name="Filter by Annotation", 
                                          default = '',
                                          description = 'Casesensitive. Must be exact. Separate multiple tags by comma' )   
    #Filter by annotation is case-sensitive and needs to be exact
    make_curve = False

    def execute(self, context):  
        global remote_instance
        
        if self.selected is True and len(bpy.context.selected_objects) != 0:
            count = 0
            to_process = []
            print('Loading partners for all selected neurons...')            
            for object in bpy.context.selected_objects:
                if object.name.startswith('#'):
                    to_process.append(object)   
            for neuron in to_process: 
                print('Retrieving partners for %s [%i of %i]...' % (neuron.name,count,len(to_process)))
                skid = re.search('#(.*?) -',neuron.name).group(1)
                self.get_partners(skid)
                count += 1
        elif bpy.context.active_object is None:
            print ('No Object Active')        
        elif '#' not in bpy.context.active_object.name:
            print ('Active Object not a Neuron')
        elif self.selected is False:
            active_skeleton = re.search('#(.*?) -',bpy.context.active_object.name).group(1)
            self.get_partners(active_skeleton)
        
                        
        return {'FINISHED'}  
    
    def get_partners(self, skid):
        connectivity_post = { 'source[0]': skid, 'threshold': 0 , 'boolean_op': 'logic_OR' }             
        remote_connectivity_url = remote_instance.get_connectivity_url( 1 )
        print( "Retrieving Partners..." )
        connectivity_data = []
        connectivity_data = remote_instance.get_page( remote_connectivity_url , connectivity_post )

        if connectivity_data:
            print("Connectivity successfully retrieved")
            self.extract_partners(skid, connectivity_data, self.inputs, self.outputs, self.make_curve)
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

    def extract_partners (self, source, connectivity_data, get_inputs, get_outputs, make_curve):
        partners = []
        number_of_inputs = str(len(connectivity_data['incoming']))      
        number_of_outputs = str(len(connectivity_data['outgoing']))
        
        print('%s Inputs detected' % number_of_inputs)
        print('%s Outputs detected' % number_of_outputs)
        
        neuron_names = {}    
        
        ### Cycle through connectivity data and retrieve skeleton ids
        if get_inputs is True:            
            for entry in connectivity_data['incoming']:
                total_synapses = 0
                for connection in connectivity_data['incoming'][entry]['skids']:
                    total_synapses += sum(connectivity_data['incoming'][entry]['skids'][connection])
                if total_synapses >= self.minimum_synapses:
                    partners.append(entry)                    
                
        if get_outputs is True:            
            for entry in connectivity_data['outgoing']:
                total_synapses = 0
                for connection in connectivity_data['outgoing'][entry]['skids']:
                    total_synapses += sum(connectivity_data['outgoing'][entry]['skids'][connection])
                if total_synapses >= self.minimum_synapses:
                    partners.append(entry)                     
                    
        neuron_names = get_neuronnames(list(set(partners)))
                
        ### Cycle over partner's skeleton ids and load neurons
        total_number = len(partners)
        i = 0
        
        if self.filter_by_annotation:
            annotations = get_annotations_from_list(partners,remote_instance)          
            tags = self.filter_by_annotation.split(',')
                            
        for skid in partners:            
            if self.filter_by_annotation:
                tag_found = False
                try:
                    for entry in annotations[skid]:
                        for tag in tags:
                            if entry == tag:
                                tag_found = True
                except:
                    print('%s has no annotations - not imported' % skid)
                    annotations[skid] = 'no annotations found'
            else:
                tag_found = True
            
            i += 1
            
            if tag_found == False:
                print('Tag not found for %s: %s' % (neuron_names[skid],str(annotations[skid])))
                continue           
                       
            print('Loading above-threshold partner: %s  [%i of %i]' % (neuron_names[skid],i,total_number))
            
            RetrieveNeuron.add_skeleton(self, skid, neuron_names[skid], self.resampling, self.import_connectors)        
            
            
            
class ColorCreator():
    """Class used to create distinctive colors"""  

    def random_colors (color_count,color_range='RGB'):
        ### Make count_color an even number
        if color_count % 2 != 0:
            color_count += 1
             
        colormap = []
        interval = 2/color_count 
        runs = int(color_count/2)
       
        ### Create first half with high saturation and low brightness; second half with low saturation and high brightness
        if color_range == 'RGB':
            for i in range(runs):
                ### High saturation
                h = interval * i
                s = 0.5
                v =  0.7
                hsv = colorsys.hsv_to_rgb(h,s,v)
                colormap.append((int(hsv[0]*255),int(hsv[1]*255),int(hsv[2]*255)))             
                ### Low saturation
                s = 1
                v =  1
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
    Class used to create distinctive shapes:
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
    
    def extract_nodes (node_data, skid, neuron_name = 'name unknown', resampling = 1, import_connectors = True):
        
        index = 1            
        cellname = skid + ' - ' + neuron_name                
        origin = (0,0,0)
        faces = []  
        XYZcoords = []
        connections = []
        edges = []
        soma = (0,0,0,0)
        connectors_post = []
        connectors_pre = []
        child_count = {}   
        nodes_list = {}    
        list_of_childs = {} 
        
        #Truncate object name is necessary 
        if len(cellname) >= 60:
            cellname = cellname[0:56] +'...'
            print('Object name too long - truncated: ', cellname)
        
        object_name = '#' + cellname     
        
        if object_name in bpy.data.objects:
            print('Neuron %s already exists!' % cellname)
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
                print('Soma found')
        
        ### Root node's entry is called 'None' because it has no parent
        ### This will be starting point for creation of the curves
        root_node = list_of_childs[None][0]        
        if resampling > 1:            
            resampled_child_list = CATMAIDtoBlender.resample_child_list(list_of_childs, root_node, resampling)

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
        
        if resampling > 1:
            Create_Mesh.make_curve_neuron (cellname, root_node, nodes_list, resampled_child_list, soma, skid, neuron_name, resampling)
        else:
            Create_Mesh.make_curve_neuron (cellname, root_node, nodes_list, list_of_childs, soma, skid, neuron_name, resampling)
            
        if import_connectors is True:    
            Create_Mesh.make_connectors(cellname, connector_pre, connector_post)
        
        return {'FINISHED'}
    
    def resample_child_list(list_of_childs,root_node,resampling_factor):
        
        print('Resampling Child List (Factor: %i)' % resampling_factor)        
        new_child_list = {}
        new_child_list[None] = root_node
        
        #Collect root node, end nodes and branching points in list: fix_nodes
        fix_nodes = []
        fix_nodes.append(root_node)
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


class ConnectToCATMAID(Operator):      
    """Connects to CATMAID database using given credentials"""
    bl_idname = "connect.to_catmaid"  
    bl_label = "Enter Credentials"    
    
    local_http_user = StringProperty(name="HTTP User")
    #subtype = 'PASSWORD' seems to be buggy in Blender 2.71
    #local_http_pw = StringProperty(name="HTTP Password", subtype = 'PASSWORD')
    local_http_pw = StringProperty(name="HTTP Password")
    local_catmaid_user = StringProperty(name="CATMAID User")
    #subtype = 'PASSWORD' seems to be buggy in Blender 2.71    
    #local_catmaid_pw = StringProperty(name="CATMAID Password", subtype = 'PASSWORD')
    local_catmaid_pw = StringProperty(name="CATMAID Password")
    
    def execute(self, context):               
        global remote_instance, server_url, connected
        
        #Check for latest version of the Script
        get_version_info.check_version(context)
        
        print('Connecting to CATMAID server')
        print('HTTP user: %s' % self.local_http_user)
        print('CATMAID user: %s' % self.local_catmaid_user)        

        remote_instance = CatmaidInstance( server_url, self.local_catmaid_user, self.local_catmaid_pw, self.local_http_user, \
                                           self.local_http_pw )        
        response = json.loads( remote_instance.login().decode( 'utf-8' ) )
        print( response ) 
        
        if  'error' in response:
            print ('Error while attempting 2 connect to CATMAID server')
            connected = False
        else:
            print ('Connection successful')
            connected = True
        
        return {'FINISHED'}
     
    
    def invoke(self, context, event):
        global catmaid_user, http_user, http_pw, catmaid_pw
        self.local_http_user = http_user
        self.local_catmaid_user = catmaid_user
        self.local_http_pw = http_pw
        self.local_catmaid_pw = catmaid_pw
        return context.window_manager.invoke_props_dialog(self)      
      
    
class ExportAllToSVG(Operator, ExportHelper):
    """Exports all neurons (only curves) to SVG File"""
    bl_idname = "exportall.to_svg"  
    bl_label = "Export neuron(s) (only curves!) to SVG"
    bl_options = {'PRESET'}
    
    all_neurons = BoolProperty(name="Process All Neurons", default = False)
    merge = BoolProperty(name="Merge into One", default = False)
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
                                    description ="Exports neurons as point cloud rather than edges (e.g. DCVs)")
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
                                   description='If checked, neuron name(s) will be included in figure',
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
            print('You need to connect to CATMAID server first to use <Color by Input/Output Ratio>!')                
            self.color_by_inputs_outputs = False
            
        if self.color_by_density is True and self.object_for_density == 'Synapses' and connected is False:
                print('You need to connect to CATMAID server first to use <Color by Synapse Density>!')                
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
                print('Unable to create density data for object!')  

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

        if self.merge is True or self.all_neurons is True:
            to_process = bpy.data.objects
            
        elif re.search('#.*',bpy.context.active_object.name) and bpy.context.active_object.type == 'CURVE':
            to_process = []
            to_process.append(bpy.context.active_object)
            
        elif self.merge is False:
            print('Error: Active Object is Not a Neuron')
            to_process = []
            return
        
        #Sort objects in to_process by color
        sorted_by_color = {}
        for object in to_process:           
            try:                
                color = str(object.active_material.diffuse_color)
            except:
                color = 'None'
            if color not in sorted_by_color:
                sorted_by_color[color] = []
            sorted_by_color[color].append(object)
        
        to_process_sorted = []
        for color in sorted_by_color:
            to_process_sorted += sorted_by_color[color]
        
        neuron_count = 0

        for neuron in to_process_sorted:            
            if re.search('#.*',neuron.name) and neuron.type == 'CURVE':
                neuron_count += 1
            
        colormap = ColorCreator.random_colors(neuron_count)
        print(str(neuron_count) + ' colors created')
        
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
                        print('Unable to retrieve color for ', neuron.name)
                        color = 'rgb' + str((0, 0, 0)) 
                else:
                    ### Standard color
                    color = 'rgb' + str((0, 0, 0)) 
                    
                if self.use_bevel is True:
                    self.line_width = neuron.data.bevel_depth/0.007 * base_line_width
                
                    
                if self.color_by_density is True and self.object_for_density == 'Synapses':   
                    print('Retrieving Connectors for Color by Density..')
                    skid = re.search('#(.*?) ',neuron.name).group(1)
                    remote_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , skid, 1, 0 )
                    node_data = remote_instance.get_page( remote_compact_skeleton_url )
                    
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
                           
                        remote_connector_url = remote_instance.get_connectors_url( 1 )
                        print( "Retrieving Info on Connectors for Filtering..." )        
                        connector_data = remote_instance.get_page( remote_connector_url , connector_postdata )                    
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
                    remote_compact_skeleton_url = remote_instance.get_compact_skeleton_url( 1 , skid, 1, 0 )
                    node_data = remote_instance.get_page( remote_compact_skeleton_url )
                    
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
        
        #Write back line_width in case it has been changed due to bevel_depth
        if self.use_bevel is True:
            self.line_width = base_line_width
        
        return{'FINISHED'} 
    

class Create_Mesh (Operator):
    """Class used to instance neurons"""  
    bl_idname = "create.new_neuron"  
    bl_label = "Create New Neuron"  

    def make_connector_spheres (neuron_name, connectors_post, connectors_pre, connectors_weight, random_colors = False, basic_radius = 0.01):
        ### Takes Connector data and create spheres in layer 3!!!
        ### For Downstream targets: sphere radius refers to # of targets
        print('Creating connector meshes')   
        start_creation = time.clock()
         
        for connector in connectors_post:
            #print('Creating connector %s' % connectors_post[connector]['id'])    
            co_size = basic_radius * connectors_weight[connectors_post[connector]['id']]    
            co_loc = connectors_post[connector]['coords']                
            connector_pre_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=6, size=co_size, view_align=False, \
                                                                    enter_editmode=False, location=co_loc, rotation=(0, 0, 0), \
                                                                    layers=(False, False, True, False, False, False, False, False, \
                                                                    False, False, False, False, False, False, False, False, False, \
                                                                    False, False, False))            
            bpy.context.active_object.name = 'Post_Connector %s of %s'  % (connectors_post[connector]['id'], neuron_name)            
            bpy.ops.object.shade_smooth()            
            #Create_Mesh.assign_material (bpy.context.active_object, 'PostSynapses_Mat', 0 , 0.8 , 0.8)

            if random_colors is True:
                Create_Mesh.assign_material (bpy.context.active_object, 'PreSynapses_Mat of' + neuron_name, random.randrange(0,100)/100 , \
                                            random.randrange(0,100)/100, random.randrange(0,100)/100)        
            else:
                Create_Mesh.assign_material (bpy.context.active_object, 'PreSynapses_Mat of' + neuron_name, 1 , 0 , 0)        

        for connector in connectors_pre:
            #print('Creating connector %s' % connectors_pre[connector]['id']) 
            co_size = basic_radius
            co_loc = connectors_pre[connector]['coords']                
            connector_pre_ob = bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=6, size=co_size, view_align=False, \
                                                                    enter_editmode=False, location=co_loc, rotation=(0, 0, 0), \
                                                                    layers=(False, False, True, False, False, False, False, False, \
                                                                    False, False, False, False, False, False, False, False, False, \
                                                                    False, False, False))            
            bpy.context.active_object.name = 'Pre_Connector %s of %s'  % (connectors_pre[connector]['id'], neuron_name)            
            bpy.ops.object.shade_smooth()            

            if random_colors is True:
                Create_Mesh.assign_material (bpy.context.active_object, 'PostSynapses_Mat of' + neuron_name, random.randrange(0,100)/100 , \
                                            random.randrange(0,100)/100, random.randrange(0,100)/100)        
            else:
                Create_Mesh.assign_material (bpy.context.active_object, 'PostSynapses_Mat of' + neuron_name, 0 , 0.8 , 0.8)       

        print('Done in ' + str(time.clock()-start_creation)+'s')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations = 10)


    def make_curve_neuron (neuron_name, root_node, nodes_dic, child_list, soma, skid = '', name = '', resampling = 1):
        ### Creates Neuron from Curve data that was imported from CATMAID
        start_creation = time.clock()        
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
            Create_Mesh.create_spline(root_node, child, nodes_dic, child_list, cu)

        print('Creating mesh done in ' + str(time.clock()-start_creation)+'s')        
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
        

    def create_spline (start_node, first_child, nodes_dic, child_list, cu):
        newSpline = cu.splines.new('POLY')
            
        ### Create start node            
        newPoint = newSpline.points[-1]
        newPoint.co = (nodes_dic[start_node][0], nodes_dic[start_node][1], nodes_dic[start_node][2], 0)
        active_node = first_child
        number_of_childs = len(child_list[active_node])
        ### nodes_created is a failsafe for while loop
        nodes_created = 0
            
        while nodes_created < 10000:
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
            
            ### If active node is branch point, start new splines for each child    
        if number_of_childs  > 1:
            for child in child_list[active_node]:
                Create_Mesh.create_spline(active_node, child, nodes_dic, child_list, cu)

    
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

        
    def assign_material (ob, material, diff_1=0.8, diff_2=0.8, diff_3=0.8):
        ###Checks if material exists, if not is is created and assigned
        if material not in bpy.data.materials:
            new_mat = bpy.data.materials.new(material)
            new_mat.diffuse_color[0] = diff_1
            new_mat.diffuse_color[1] = diff_2            
            new_mat.diffuse_color[2] = diff_3            
        else:
            new_mat = bpy.data.materials[material]
            
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
    """Assigns Random Materials to Neurons"""  
    bl_idname = "color.by_pairs"  
    bl_label = "Gives Paired Neurons the same Color (Annotation-based)"  
    bl_options = {'UNDO'}
    
    color_range = EnumProperty(name="Range",
                                   items = (('RGB','RGB','RGB'),
                                            ("Grayscale","Grayscale","Grayscale"),                                            
                                            ),
                                    default =  "RGB",
                                    description = "Choose mode of randomizing colors")
    
    unpaired_black = BoolProperty(  name="Color unpaired Neurons black",                                   
                                    default =  True,
                                    description = "If unchecked, unpaired neurons will be given random color"
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
                            print('Warning - Neuron %s paired with itself' % str(neuron))
                            continue
                            
                        if paired_skid != None:
                            print('Warning - Multiple paired Annotations found for neuron %s!' % str(neuron))
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
    """Prepares all Neuron's materials for Render"""  
    bl_idname = "for_render.all_materials"  
    bl_label = "Assign Properties to all Neurons Materials"  
    bl_options = {'UNDO'}

    def execute(self, context):
        for material in bpy.data.materials:
            if re.findall('#',material.name):
                print(material)
                material.emit = 1
                material.use_transparency = True
                
        return {'FINISHED'}           


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
    start_hue =         IntProperty(name="LUT - start hue", 
                                    description="Start Hue for Look up Table (standard = teal)",
                                    default = 110, min = 0, max = 360)                                     
    end_hue =           IntProperty(name="LUT - end Hue", 
                                    description="End Hue for Look up Table (standard = red)",
                                    default = 0, min = 0, max = 360)
    emit_max =          IntProperty(name="Emit", 
                                    description="Max Emit Value - set to 0 for no emit",
                                    default = 1, min = 0, max = 5)
    
    def execute (self, context):
        synapse_count = {}    
        connectivity_post = {} 
        connectivity_post['threshold'] = 0
        connectivity_post['boolean_op'] = 'logic_OR'         

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
                    print(object.name,synapse_count[skid])
                    if synapse_count[skid] > 0:
                        hue = calc_hue(synapse_count[skid],max_count,(self.start_hue,self.end_hue))
                        s = 1
                        v = 1
                        hsv = colorsys.hsv_to_rgb(hue,s,v)
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
                    print('Unable to process object: ', object.name)

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
    

class ColorBySpatialDistribution(Operator):
    """Color neurons by spatial Distribution of their Somas"""  
    bl_idname = "color.by_spatial"  
    bl_label = "Color Neurons by Spatial Distribution of their Somas!" 
    bl_options = {'UNDO'}
    
    ### 'radius' is used for determination of the #of neighbors for each soma
    radius = FloatProperty(name="Neighborhood Radius", default = 1.5)
    ### 'min_cluster_distance' is used for minimum distance of somas to other cluster centers to be 
    ###  considered a cluster of their own
    min_cluster_distance = FloatProperty(name="Min. Cluster Dist", default = 2)
    ### Number of clusters the algorithm tries to create
    n_clusters = IntProperty(name="# of Clusters", default = 4)
    ### If 'show_center' is True, a sphere will be created with a r of 'radius'
    show_centers = BoolProperty(name="Show Cluster Centers", default = True)
    
    
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
                print('Cannnot form any more clusters!')
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
        
            ### For Debugging:
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


def calc_hue (value, max_value, lut):
    
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
        
def register():
 bpy.utils.register_module(__name__)
 #bpy.utils.register_class(VariableManager)
 bpy.types.Scene.CONFIG_VariableManager = bpy.props.PointerProperty(type=VariableManager)       

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
 if bpy.context.scene.get('CONFIG_VariableManager') != None:     
    del bpy.context.scene['CONFIG_VariableManager']
 try:
    del bpy.types.Scene.CONFIG_VariableManager
 except:
    pass


if __name__ == "__main__":
 register()
 
