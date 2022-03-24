"""CATMAID to Blender Import Script.

Connects to CATMAID servers and retrieves skeleton data.
Copyright (C) Philipp Schlegel, 2014.

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
"""

import bmesh
import bpy
import collections
import colorsys
import json
import math
import re
import requests
import time
import urllib

import numpy as np

from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import (FloatVectorProperty, FloatProperty, StringProperty,
                       BoolProperty, EnumProperty, IntProperty,
                       CollectionProperty)
from bpy_extras.io_utils import orientation_helper, axis_conversion
from mathutils import Matrix

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import HTTPError


########################################
#  Settings
########################################


bl_info = {
 "name": "CATMAID Import",
 "author": "Philipp Schlegel",
 "version": (7, 0, 0),
 "for_catmaid_version": '2020.02.15-684-gcbe37bd',
 "blender": (2, 80, 0),  # this MUST be 2.80.0 (i.e. not 2.9x)
 "location": "View3D > Sidebar (N) > CATMAID",
 "description": "Imports Neuron from CATMAID server, Analysis tools, Export to SVG",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "Object"}

client = None

# Will populate this later
catmaid_volumes = [('None', 'None', 'Do not import volume from this list')]

DEFAULTS = {
 "connectors": {
                0: {'color': (0, 0.8, 0.8, 1),  # postsynapses
                    'name': 'Presynapses'},
                1: {'color': (1, 0, 0, 1),  # presynapses
                    'name': 'Postsynapses'},
                2: {'color': (0, 1, 0, 1),  # gap junctions
                    'name': 'GapJunctions'},
                3: {'color': (0.5, 0, 0.5, 1),  # abutting
                    'name': 'Abutting'},
               }
}

########################################
#  UI Elements
########################################


class CATMAID_PT_import_panel(Panel):
    """Creates import menu in viewport side menu."""

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Import"
    bl_category = "CATMAID"

    def draw(self, context):
        layout = self.layout

        ver_str = '.'.join([str(i) for i in bl_info['version']])
        layout.label(text=f'CATMAID plugin v{ver_str}')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("catmaid.connect", text="Connect to CATMAID", icon='PLUGIN')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("fetch.neuron", text="Import Neuron(s)", icon='ARMATURE_DATA')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("fetch.connectors", text="Import Connectors", icon='PMARKER_SEL')
        row.operator("display.help", text="", icon='QUESTION').entry = 'retrieve.connectors'

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("import.volume", text='Import Volume', icon='IMPORT')


class CATMAID_PT_export_panel(Panel):
    """Creates export menu in viewport side menu."""

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Export"
    bl_category = "CATMAID"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("export.volume", text='Export Volume', icon='EXPORT')


class CATMAID_PT_properties_panel(Panel):
    """Creates properties menu in viewport side menu."""

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Neuron Properties"
    bl_category = "CATMAID"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("curve.change", text="Curve properties",
                     icon='COLOR_BLUE')
        row.operator("display.help", text="", icon='QUESTION').entry = 'curve.change'

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("material.change", text="Set colors",
                     icon='COLOR_BLUE')
        row.operator("display.help", text="", icon='QUESTION').entry = 'change.material'

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("material.randomize", text="Randomize colors", icon='COLOR')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("material.kmeans", text="Color by clusters", icon='LIGHT_SUN')
        row.operator("display.help", text="", icon='QUESTION').entry = 'material.kmeans'

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("color.by_annotation", text="Color by Annotation", icon='SORTALPHA')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("color.by_strahler", text="Color by Strahler Index", icon='MOD_ARRAY')
        row.operator("display.help", text="", icon='QUESTION').entry = 'color.by_strahler'

########################################
#  Operators
########################################

class CATMAID_OP_connect(Operator):
    bl_idname = "catmaid.connect"
    bl_label = 'Connect CATMAID'
    bl_description = "Connect to given CATMAID server"

    local_http_user: StringProperty(name="HTTP User")
    local_http_pw: StringProperty(name="HTTP Password",
                                  subtype='PASSWORD')
    local_token: StringProperty(name="API token",
                                description='How to retrieve Token: '
                                            'http://catmaid.github.io/dev/api.html#api-token')
    local_server_url: StringProperty(name="Server Url")
    local_project_id: IntProperty(name='Project ID', default=0)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "local_server_url")
        row = layout.row(align=True)
        row.prop(self, "local_token")
        row = layout.row(align=True)
        row.prop(self, "local_project_id")
        row = layout.row(align=True)
        row.prop(self, "local_http_user")
        row = layout.row(align=True)
        row.prop(self, "local_http_pw")
        layout.label(text="Use Addon preferences to set peristent server url, credentials, etc.")

    def invoke(self, context, event):
        self.local_http_user = get_pref('http_user', '')
        self.local_token = get_pref('api_token', '')
        self.local_http_pw = get_pref('http_pw', '')
        self.local_project_id = get_pref('project_id', 0)
        self.local_server_url = get_pref('server_url', '')
        self.max_threads = get_pref('max_threads', 20)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        print('Connecting to CATMAID server')
        print('URL: %s' % self.local_server_url)
        print('HTTP user: %s' % self.local_http_user)
        print('Token: %s' % self.local_token)

        global client
        client = CatmaidClient(server=self.local_server_url,
                               api_token=self.local_token,
                               http_user=self.local_http_user,
                               http_password=self.local_http_pw,
                               project_id=self.local_project_id,
                               max_threads=self.max_threads)

        # Retrieve volumes, to test if connection is good:
        try:
            volumes = client.get_volume_list()
            self.report({'INFO'}, 'Connection successful')
            print('Test call successful')
        except BaseException:
            self.report({'ERROR'}, 'Connection failed: see console')
            raise

        global catmaid_volumes
        catmaid_volumes = [('None', 'None', 'Do not import volume from list')]
        catmaid_volumes += [(str(e[0]), e[1], str(e[2])) for e in volumes]

        return {'FINISHED'}


class CATMAID_OP_fetch_neuron(Operator):
    """Fetch neurons."""

    bl_idname = "fetch.neuron"
    bl_label = 'Fetch neurons'
    bl_description = "Fetch given neurons from global server"

    names: StringProperty(name="Name(s)",
                          description="Search by neuron names. Separate "
                                      "multiple names by commas. For example: "
                                      "'neuronA,neuronB,neuronC'")
    partial_match: BoolProperty(name="Allow partial matches?", default=False,
                                description="Allow partial matches for neuron "
                                            "names and annotations! Will also "
                                            "become case-insensitive")
    annotations: StringProperty(name="Annotations(s)",
                                description="Search by skeleton IDs. Separate "
                                            "multiple annotations by commas. For "
                                            "example: 'annotation 1,annotation2"
                                            ",annotation3'")
    intersect: BoolProperty(name="Intersect", default=False,
                            description="If true, all identifiers (e.g. two "
                                        "annotations or name + annotation) "
                                        "have to be true for a neuron to be "
                                        "loaded")
    skeleton_ids: StringProperty(name="Skeleton ID(s)",
                                 description="Search by skeleton IDs. Separate "
                                             "multiple IDs by commas. "
                                             "Does not accept more than 400 "
                                             "characters in total")
    minimum_nodes: IntProperty(name="Minimum node count", default=1, min=1,
                               description="Neurons with fewer nodes than this "
                                           " will be ignored")
    import_synapses: BoolProperty(name="Synapses", default=True,
                                  description="Import chemical synapses (pre- "
                                              "and postsynapses), similarly to "
                                              "3D Viewer in CATMAID")
    import_gap_junctions: BoolProperty(name="Gap Junctions", default=False,
                                       description="Import gap junctions, "
                                                   "similarly to 3D Viewer in "
                                                   "CATMAID")
    import_abutting: BoolProperty(name="Abutting Connectors", default=False,
                                  description="Import abutting connectors")
    cn_spheres: BoolProperty(name="Connectors as spheres", default=False,
                             description="Import connectors as spheres instead "
                                         "of curves")
    downsampling: IntProperty(name="Downsampling Factor", default=2, min=1, max=20,
                              description="Will reduce number of nodes by given "
                                          "factor. Root, ends and forks are "
                                          "preserved")
    use_radius: BoolProperty(name="Use node radii", default=False,
                             description="If true, neuron will use node radii "
                                         "for thickness. If false, radius is "
                                         "assumed to be 70nm (for visibility)")
    neuron_mat_for_connectors: BoolProperty(name="Connectors same color as neuron",
                                            default=False,
                                            description="If true, connectors "
                                                        "will have the same "
                                                        "color as the neuron")
    skip_existing: BoolProperty(name="Skip existing", default=True,
                                description="If True, will not add neurons that "
                                            "are already in the scene")

    # ATTENTION:
    # using check() in an operator that uses threads, will lead to segmentation faults!
    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        if client:
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=False)
        row.prop(self, "names")
        row = box.row(align=False)
        row.prop(self, "annotations")

        row = box.row(align=False)
        row.prop(self, "skeleton_ids")

        row = box.row(align=False)
        row.prop(self, "partial_match")
        row.enabled = True if self.names or self.annotations else False
        row.prop(self, "intersect")
        row.enabled = True if self.names or self.annotations else False

        row = box.row(align=False)
        row.prop(self, "minimum_nodes")
        layout.label(text="Import Options")
        box = layout.box()
        row = box.row(align=False)
        row.prop(self, "import_synapses")
        row.prop(self, "import_gap_junctions")
        row.prop(self, "import_abutting")

        row = box.row(align=False)
        row.prop(self, "cn_spheres")
        row.enabled = True if self.import_synapses or self.import_gap_junctions or self.import_abutting else False

        row = box.row(align=False)
        row.prop(self, "neuron_mat_for_connectors")
        row.enabled = True if self.import_synapses or self.import_gap_junctions or self.import_abutting else False

        row = box.row(align=False)
        row.prop(self, "downsampling")

        row = box.row(align=False)
        row.prop(self, "use_radius")
        row.prop(self, "skip_existing")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        retrieve_by_names = []
        if self.names:
            retrieve_by_names = client.search_names(self.names, self.partial_match)

            if not len(retrieve_by_names):
                print('ERROR: Search name(s) not found! Import stopped')
                self.report({'ERROR'}, 'Search tag(s) not found! Import stopped')
                return{'FINISHED'}

        retrieve_by_skids = []
        if self.skeleton_ids:
            retrieve_by_skids = np.array([x.strip() for x in self.skeleton_ids.split(',')])

        retrieve_by_annotations = []
        if self.annotations:
            # In case there are commas in the annotation, we use quotation marks
            if self.annotations.startswith('"') and self.annotations.endswith('"'):
                annotations = [self.annotations[1:-1]]
            else:
                annotations = [x.strip() for x in self.annotations.split(',')]
            retrieve_by_annotations = client.search_annotations(annotations,
                                                                allow_partial=self.partial_match,
                                                                intersect=self.intersect)

            if not len(retrieve_by_annotations):
                print('ERROR: No matching annotation(s) found! Import stopped')
                self.report({'ERROR'}, 'No matching annotation(s) found! Import stopped')
                return{'FINISHED'}

        if self.intersect:
            skeletons_to_retrieve = set.intersection(set(retrieve_by_annotations),
                                                     set(retrieve_by_names))

            if not skeletons_to_retrieve:
                print('WARNING: No neurons left after intersection! Import stopped')
                self.report({'ERROR'}, 'Intersection empty! Import stopped')
                return{'FINISHED'}
        else:
            skeletons_to_retrieve = set.union(set(retrieve_by_annotations),
                                              set(retrieve_by_names),
                                              set(retrieve_by_skids))

        if self.skip_existing:
            existing_skids = {ob['skeleton_id'] for ob in bpy.data.objects if 'skeleton_id' in ob}
            skeletons_to_retrieve = skeletons_to_retrieve - existing_skids

        if self.minimum_nodes > 1 and skeletons_to_retrieve:
            print(f'Filtering {{len(skeletons_to_retrieve)}} neurons for size')
            counts = client.get_node_counts(skeletons_to_retrieve)
            skeletons_to_retrieve = [e for e in skeletons_to_retrieve if counts.get(str(e), 0) >= self.minimum_nodes]

        # Extract skeleton IDs from skeleton_id string
        print(f'{len(skeletons_to_retrieve)} neurons found - resolving names...')
        neuron_names = client.get_names(skeletons_to_retrieve)

        print("Collecting skeleton data...")
        start = time.time()
        skdata = client.get_skeletons(list(skeletons_to_retrieve),
                                      with_history=False,
                                      with_abutting=self.import_abutting)

        print(f"Importing for {len(skdata)} skeletons into Blender")

        for skid in skdata:
            # Create an object name
            object_name = f'#{skid} - {neuron_names[str(skid)]}'
            import_skeleton(skdata[skid],
                            skeleton_id=str(skid),
                            object_name=object_name,
                            downsampling=self.downsampling,
                            import_synapses=self.import_synapses,
                            import_gap_junctions=self.import_gap_junctions,
                            import_abutting=self.import_abutting,
                            use_radii=self.use_radius,
                            cn_as_curves=not self.cn_spheres,
                            neuron_mat_for_connectors=self.neuron_mat_for_connectors)

        print(f'Finished Import in {time.time()-start:.1f}s')

        return {'FINISHED'}


def _get_available_volumes(self, context):
    """Simply returns parsed list of available volumes."""
    # Must be defined before CATMAID_OP_fetch_volume
    return catmaid_volumes


class CATMAID_OP_fetch_volume(Operator):
    """Imports a volume as mesh from CATMAID."""

    bl_idname = "import.volume"
    bl_label = "Import volumes from CATMAID"
    bl_description = "Fetch volume from server"

    volume: EnumProperty(name='Import from List',
                         items=_get_available_volumes,
                         description='Select volume to be imported. List will '
                                     'refresh on (re-)connecting to CATMAID '
                                     'server.')
    by_name: StringProperty(name='Import by Name', default='',
                            description='Name of volume to import.')
    allow_partial: BoolProperty(name='Allow partial match', default=True,
                                description='If True, name can be a partial match.')

    @classmethod
    def poll(cls, context):
        if client:
            return True
        return False

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Reconnect to CATMAID server to refresh list")
        row = layout.row()
        row.prop(self, "volume")
        row = layout.row()
        row.prop(self, "by_name")
        row = layout.row()
        row.prop(self, "allow_partial")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        volumes_to_retrieve = []

        if self.volume != 'None':
            volumes_to_retrieve.append(self.volume)

        if self.by_name:
            if self.allow_partial:
                volumes_to_retrieve += [v[0] for v in catmaid_volumes if self.by_name.lower() in v[1].lower()]
            else:
                volumes_to_retrieve += [v[0] for v in catmaid_volumes if self.by_name.lower() == v[1].lower()]

        for k, vol in enumerate(volumes_to_retrieve):
            vertices, faces, name = client.get_volume(vol)

            print(f'Importing volume {k} of {len(volumes_to_retrieve)}: '
                  f'{name} (ID {vol}) - {len(vertices)} vertices/'
                  f'{len(faces)} faces after clean-up')

            import_mesh(vertices, faces, name=name)

        return{'FINISHED'}


class CATMAID_OP_upload_volume(Operator):
    """Export a mesh as volume to CATMAID."""

    bl_idname = "export.volume"
    bl_label = "Export mesh to CATMAID"
    bl_description = "Export mesh to CATMAID as volume"

    volume_name: StringProperty(name='Name', default='',
                                description='If not explicitly provided, will '
                                            'use the Blender object name.')
    comment: StringProperty(name='Comment', default='',
                            description='Add comment to volume.')

    @classmethod
    def poll(cls, context):
        if client:
            return True
        return False

    def draw(self, context):
        layout = self.layout
        if not len(self.selected):
            layout.label(text='Must have one or more meshes selected!')
            return
        elif len(self.selected) == 1:
            layout.label(text='Single mesh selected for export:')
            layout.prop(self, "volume_name")
        else:
            layout.label(text=f"{len(self.selected)} meshes selected: using objects' names for export:")
        layout.prop(self, "comment")
        layout.label(text="Meshes will show up in CATMAID 3D viewer and volume manager.")
        layout.label(text="Requires CATMAID version 2016.04.18 or higher.")
        layout.label(text="Polygon faces will be converted into triangles - please save Blender file before clicking OK!")

    def invoke(self, context, event):
        # Set selected objects at draw time
        self.selected = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        if len(self.selected) == 1:
            self.volume_name = self.selected[0].name

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if not self.selected:
            print("No meshes selected!")
            return{'FINISHED'}

        for i, obj in enumerate(self.selected):
            if self.volume_name == '':
                vol_name = obj.name
            else:
                vol_name = self.volume_name

            # Make this object the active one
            bpy.context.view_layer.objects.active = obj

            # Check if mesh is trimesh:
            is_trimesh = np.all([len(f.vertices) == 3 for f in obj.data.polygons])
            if not is_trimesh:
                print('Mesh not a trimesh - trying to convert')
                # First go out of edit mode and select all vertices while in object mode
                if obj.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')

                # Select all vertices
                for v in obj.data.vertices:
                    v.select = True

                # Now go to edit mode and convert to trimesh
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.quads_convert_to_tris()
                bpy.ops.object.mode_set(mode='OBJECT')

                # Check if again mesh is trimesh:
                is_trimesh = np.all([len(f.vertices) == 3 for f in obj.data.polygons])
                if all(is_trimesh):
                    print(f"{i} of {len(self.selected)}: Mesh '{vol_name}"
                          'successfully converted to trimesh!')
                else:
                    print(f"{i} of {len(self.selected)}: Error during "
                          f"conversion of '{vol_name}' to trimesh "
                          "- try manually!")
                    continue

            # Now create postdata
            verts = np.empty(len(obj.data.vertices) * 3)
            obj.data.vertices.foreach_get('co', verts)  # this fills above array
            verts = verts.reshape(len(obj.data.vertices), 3)

            faces = np.empty(len(obj.data.polygons) * 3)
            obj.data.polygons.foreach_get('vertices', faces)
            faces = faces.reshape(len(obj.data.polygons), 3)

            resp = client.upload_volume(verts, faces,
                                        name=vol_name, comment=self.comment)

            if 'success' in resp and resp['success'] is True:
                print(f"{i} of {len(self.selected)}: Export of mesh '{vol_name}' "
                      "successful")
                self.report({'INFO'}, 'Success!')
            else:
                print(f"{i} of {len(self.selected)}: Export of mesh '{vol_name}' "
                      "failed!")
                self.report({'ERROR'}, 'See console for details!')
                print(resp)
        return{'FINISHED'}


class CATMAID_OP_display_help(Operator):
    """Displays popup with additional help."""

    bl_idname = "display.help"
    bl_label = "Advanced Tooltip"
    bl_description = "Display help tooltip"

    entry: StringProperty(name="which entry to show",
                          default='', options={'HIDDEN'})

    def execute (self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        if self.entry == 'color.by_similarity':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Color Neurons by Similarity - Tooltip')
            box = layout.box()
            box.label(text='This function colors neurons based on how similar they are with respect to either: morphology, synapse placement, connectivity or paired connectivity.')
            box.label(text='It is highly recommended to have SciPy installed - this will increase speed of calculation a lot!')
            box.label(text='See https://github.com/schlegelp/CATMAID-to-Blender on how to install SciPy in Blender.')
            box.label(text='Use <Settings> button to set parameters, then <Start Calculation>.')
            layout.label(text='Morphology:')
            box = layout.box()
            box.label(text='Neurons that have close-by projections with similar orientation are')
            box.label(text='similar. See Kohl et al. (2013, Cell).')
            layout.label(text='Synapses:')
            box = layout.box()
            box.label(text='Neurons that have similar numbers of synapses in the same area')
            box.label(text='are similar. See Schlegel et al. (2016, eLife).')
            layout.label(text='Connectivity:')
            box = layout.box()
            box.label(text='Neurons that connects with similar number of synapses to the same')
            box.label(text='partners are similar. See Schlegel et al. (2016, eLife).')
            layout.label(text='Paired Connectivity:')
            box = layout.box()
            box.label(text='Neurons that mirror (left/right comparison) each others connectivity')
            box.label(text='are similar. This requires synaptic partners to be paired with a')
            box.label(text='<paired with #skeleton_id> annotation.')
        elif self.entry == 'color.by_pairs':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Color Neurons by Pairs - Tooltip')
            box = layout.box()
            box.label(text='Gives paired neurons the same color. Pairing is based on annotations:')
            box.label(text='Neuron needs to have a <paired with #skeleton_id> annotation.')
            box.label(text='For example <paired with #1874652>.')
        elif self.entry == 'material.kmeans':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Color by Spatial Distribution - Tooltip')
            box = layout.box()
            box.label(text='This function colors neurons based on spatial clustering of their somas.')
            box.label(text='Uses the k-Mean algorithm. You need to set the number of clusters you')
            box.label(text='expect and the algorithm finds clusters with smallest variance.')
        elif self.entry == 'retrieve.by_pairs':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Retrieve Pairs of Neurons - Tooltip')
            box = layout.box()
            box.label(text='Retrieves neurons paired with already the loaded neurons. Pairing is')
            box.label(text='based on annotations: neuron needs to have a <paired with #skeleton_id>')
            box.label(text='annotation. For example neuron #1234 has annotation')
            box.label(text='<paired with #5678> and neuron 5678 has annotation')
            box.label(text='<paired with #1234>.')
        elif self.entry == 'retrieve.connectors':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Retrieve Connectors - Tooltip')
            box = layout.box()
            box.label(text='Retrieves connectors as spheres. Outgoing (presynaptic) connectors can be')
            box.label(text='scaled (weighted) based on the number of postsynaptically connected')
            box.label(text='neurons. Incoming (postsynaptic) connectors always have base radius.')
        elif self.entry == 'change.material':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Change Materials - Tooltip')
            box = layout.box()
            box.label(text='By default, all imported neurons have a standard material with random')
            box.label(text='color. You can change the material of individual neurons in the ')
            box.label(text='material tab or in bulk using this function. For more options')
            box.label(text='see material tab.')
        elif self.entry == 'color.by_strahler':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Color by Strahler - Tooltip')
            box = layout.box()
            box.label(text='Colors neurons by Strahler index. Result may will look odd')
            box.label(text='in the viewport unless viewport shading is set to <render> or')
            box.label(text='<material>. In any case, if you render it will look awesome!')
        elif self.entry == 'animate.history':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Animate history - Tooltip')
            box = layout.box()
            box.label(text='This works essentially like the corresponding function of CATMAIDs 3D viewer: nodes and connectors pop into existence ')
            box.label(text='as they were traced originally. Attention: using the <Skip idle phases> option will compromise relation between neurons')
            box.label(text='because idle phases are currently calculated for each neuron individually. The <Show timer> will also be affected!')
        elif self.entry == 'curve.change':
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Change Curve Properties - Tooltip')
            box = layout.box()
            box.label(text='Skeletons are created using curves. Bevel depth determines the ')
            box.label(text='thickness of the curves. Radial (bevel) and curve resolution ')
            box.label(text='determine how detailed the curves are - lower to improve ')
            box.label(text='render performance.')


    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)


class CATMAID_OP_material_change(Operator):
    """Change colors."""

    bl_idname = "material.change"
    bl_label = "Change colors"
    bl_options = {'UNDO'}
    bl_description = "Change color"

    which_neurons: EnumProperty(name="Which Objects?",
                                items=[('Selected', 'Selected', 'Selected'),
                                       ('All', 'All', 'All')],
                                default='Selected',
                                description="Assign common material to which neurons")
    to_neurons: BoolProperty(name='Neurons',
                             default=True,
                             description='Include neurons?')
    to_outputs: BoolProperty(name='Presynapses',
                             default=False,
                             description='Include presynaptic sites (outgoing)?')
    to_inputs: BoolProperty(name='Postsynapses',
                            default=False,
                            description='Include postsynaptic sites (incoming)?')
    change_color: BoolProperty(name='Color', default=True, description='Change color?')
    new_color: FloatVectorProperty(name="", description="Set new color",
                                   default=(0.0, 1, 0.0), min=0.0, max=1.0,
                                   subtype='COLOR')

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.label(text="Apply to")
        box = layout.box()
        row = box.row(align=False)
        row.prop(self, "which_neurons")
        row = box.row(align=False)
        row.prop(self, "to_neurons")
        row.prop(self, "to_outputs")
        row.prop(self, "to_inputs")

        layout.label(text="Change")
        box = layout.box()

        row = box.row(align=False)
        col = row.column()
        col.prop(self, "change_color")
        if self.change_color:
            col = row.column()
            col.prop(self, "new_color")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.which_neurons == 'Selected':
            ob_list = bpy.context.selected_objects
        elif self.which_neurons == 'All':
            ob_list = bpy.data.objects

        filtered_ob_list = []

        # First find the objects
        for ob in ob_list:
            if 'subtype' not in ob:
                continue
            if ob['subtype'] in ('NEURITES', 'SOMA') and not self.to_neurons:
                continue
            if ob['subtype'] in ('CONNECTORS'):
                if ob['cn_type'] == 'Presynapses' and not self.to_outputs:
                    continue
                if ob['cn_type'] == 'Postsynapses' and not self.to_inputs:
                    continue

            filtered_ob_list.append(ob)

        # Now apply cahnges
        for ob in filtered_ob_list:
            if self.change_color:
                ob.active_material.diffuse_color = (self.new_color[0],
                                                    self.new_color[1],
                                                    self.new_color[2],
                                                    1)

        self.report({'INFO'}, f'{len(filtered_ob_list)} materials changed')

        return {'FINISHED'}


class CATMAID_OP_curve_change(Operator):
    """Change curve settings."""

    bl_idname = "curve.change"
    bl_label = "Change curve properties"
    bl_options = {'UNDO'}
    bl_description = "Change curve properties"

    which_neurons: EnumProperty(name="Which Objects?",
                                items=[('Selected', 'Selected', 'Selected'),
                                       ('All', 'All', 'All')],
                                default='Selected',
                                description="Assign common material to which neurons")
    to_neurons: BoolProperty(name='Neurons',
                             default=True,
                             description='Include neurons?')
    to_outputs: BoolProperty(name='Presynapses',
                             default=False,
                             description='Include presynaptic sites (outgoing)?')
    to_inputs: BoolProperty(name='Postsynapses',
                            default=False,
                            description='Include postsynaptic sites (incoming)?')
    change_bevel: BoolProperty(name='Thickness', default=False,
                               description='Change neuron thickness (bevel)?')
    new_bevel: FloatProperty(name="", description="Set new thickness.",
                             default=0.015, min=0)
    change_bevel_res: BoolProperty(name='Radial resolution', default=False,
                                   description='Change radial (bevel) resolution?')
    new_bevel_res: IntProperty(name="", description="Set new resolution.",
                               default=5, min=0)
    change_curve_res: BoolProperty(name='Curve resolution', default=False,
                                   description='Change curve resolution?')
    new_curve_res: IntProperty(name="", description="Set new resolution.",
                               default=10, min=0)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.label(text="Apply to")
        box = layout.box()
        row = box.row(align=False)
        row.prop(self, "which_neurons")
        row = box.row(align=False)
        row.prop(self, "to_neurons")
        row.prop(self, "to_outputs")
        row.prop(self, "to_inputs")

        layout.label(text="Change")
        box = layout.box()

        row = box.row(align=False)
        col = row.column()
        col.prop(self, "change_bevel")
        if self.change_bevel:
            col = row.column()
            col.prop(self, "new_bevel")

        row = box.row(align=False)
        col = row.column()
        col.prop(self, "change_bevel_res")
        if self.change_bevel_res:
            col = row.column()
            col.prop(self, "new_bevel_res")

        row = box.row(align=False)
        col = row.column()
        col.prop(self, "change_curve_res")
        if self.change_curve_res:
            col = row.column()
            col.prop(self, "new_curve_res")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.which_neurons == 'Selected':
            ob_list = bpy.context.selected_objects
        elif self.which_neurons == 'All':
            ob_list = bpy.data.objects

        filtered_ob_list = []

        # First find the objects
        for ob in ob_list:
            if 'subtype' not in ob:
                continue
            if ob['subtype'] in ('NEURITES', 'SOMA') and not self.to_neurons:
                continue
            if ob['subtype'] in ('CONNECTORS'):
                if ob['cn_type'] == 'Presynapses' and not self.to_outputs:
                    continue
                if ob['cn_type'] == 'Postsynapses' and not self.to_inputs:
                    continue

            filtered_ob_list.append(ob)

        # Now apply cahnges
        for ob in filtered_ob_list:
            if self.change_bevel and ob.type == 'CURVE':
                ob.data.bevel_depth = self.new_bevel
            if self.change_bevel_res and ob.type == 'CURVE':
                ob.data.bevel_resolution = self.new_bevel_res
            if self.change_curve_res and ob.type == 'CURVE':
                ob.data.resolution_u = self.new_curve_res

        self.report({'INFO'}, f'{len(filtered_ob_list)} curves changed')

        return {'FINISHED'}


class CATMAID_OP_material_randomize(Operator):
    """Assigns new semi-random colors to neurons"""
    bl_idname = "material.randomize"
    bl_label = "Assign (semi-) random colors"
    bl_description = "Assign (semi-) random colors"
    bl_options = {'UNDO'}

    which_neurons: EnumProperty(name="Which Neurons?",
                                items=[('Selected', 'Selected', 'Selected'),
                                       ('All', 'All', 'All')],
                                description="Choose which neurons to give random color.",
                                default='All')
    color_range: EnumProperty(name="Range",
                              items=(('RGB', 'RGB', 'RGB'),
                                     ("Grayscale", "Grayscale", "Grayscale"),),
                              default="RGB",
                              description="Choose mode of randomizing colors")
    start_color: FloatVectorProperty(name="Color range start",
                                     description="Set start of color range (for RGB). Keep start and end the same to use full range.",
                                     default=(1, 0.0, 0.0), min=0.0, max=1.0,
                                     subtype='COLOR')
    end_color: FloatVectorProperty(name="Color range end",
                                   description="Set end of color range (for RGB). Keep start and end the same to use full range.",
                                   default=(1, 0.0, 0.0), min=0.0, max=1.0,
                                   subtype='COLOR')


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.which_neurons == 'All':
            to_process = bpy.data.objects
        elif self.which_neurons == 'Selected':
            to_process = bpy.context.selected_objects

        to_process = [o for o in to_process if 'type' in o]
        to_process = [o for o in to_process if o['type'] == 'NEURON']

        neurons = set([o['id'] for o in to_process])

        colors = random_colors(len(neurons),
                               color_range=self.color_range,
                               start_rgb=self.start_color,
                               end_rgb=self.end_color,
                               alpha=1)
        colormap = dict(zip(neurons, colors))

        for ob in to_process:
            ob.active_material.diffuse_color = colormap[ob['id']]
        return {'FINISHED'}


class CATMAID_OP_material_spatial(Operator):
    """Color neurons by spatially clustering their somas."""
    bl_idname = "material.kmeans"
    bl_label = "Color neurons by spatially clustering of their somas (k-Means algorithm)"
    bl_description = "Color neurons by spatially clustering of their somas (k-Means algorithm)"
    bl_options = {'UNDO'}

    # Number of clusters the algorithm tries to create
    n_clusters: IntProperty(name="# of clusters", default=4)
    # Fade colours by distance to cluster center
    fade_color: BoolProperty(name="Fade colors", default=True,
                             description='If true, neuron color will fade with distance from cluster center.')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute (self, context):
        neurons = []
        coords = []
        for obj in bpy.data.objects:
            if 'subtype' not in obj:
                continue
            if obj['subtype'] != 'SOMA':
                continue
            neurons.append(obj)
            coords.append(obj.location)
            # Set color to black -> this means that all neurons without somata
            # will remain black
            obj.active_material.diffuse_color = (0, 0, 0, 1)

        clusters, centers, dists = cluster_kmeans(coords, n_clusters=self.n_clusters)
        max_dist = dists.max()

        colors = random_colors(self.n_clusters)

        for obj, cl, d in zip(neurons, clusters, dists):
            c = colors[cl]

            if self.fade_color:
                c = list(colorsys.rgb_to_hsv(*c[:3]))
                c[2] = 1 - (0.5 * d / max_dist)
                c = list(colorsys.hsv_to_rgb(*c))
                c.append(1)  # add alpha

            obj.active_material.diffuse_color = c

        return{'FINISHED'}


class CATMAID_OP_material_annotation(Operator):
    """Color neurons by annotation."""

    bl_idname = "color.by_annotation"
    bl_label = "Color Neurons based on whether they have given annotation"
    bl_description = "Color neurons by annotation"
    bl_options = {'UNDO'}

    annotation: StringProperty(name="Annotation",
                               description="Seperate multiple annotations by "
                                           "comma without space. Must be exact! "
                                           "Case-sensitive!")
    exclude_annotation: StringProperty(name="Exclude",
                                       description="Seperate multiple annotations "
                                                   " by comma without space. "
                                                   "Must be exact! Case-sensitive!")
    color: FloatVectorProperty(name="Color",
                               description="Color value.",
                               default=(1, 0.0, 0.0),
                               min=0.0, max=1.0, subtype='COLOR')
    variation: BoolProperty(name="Vary color",
                            description="Add small variation in color to each "
                                        "individual neuron.",
                            default=False)
    make_non_matched_grey: BoolProperty(name="Color others grey",
                                        description="If unchecked, color of "
                                                    "neurons without given "
                                                    "annotation(s) will not be "
                                                    "changed.",
                                        default=False)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    @classmethod
    def poll(cls, context):
        if client:
            return True
        return False

    def execute(self, context):
        skids = get_skids()

        annotations = client.get_annotations(skids)

        include_annotations = [a.strip() for a in self.annotation.split(',')]
        exclude_annotations = [a.strip() for a in self.exclude_annotation.split(',')]

        for s in skids:
            objects = skeleton_id_objects(s)

            include = False
            exclude = False
            for an in annotations.get(s, []):
                if an in include_annotations:
                    include = True
                if an in exclude_annotations:
                    exclude = True
            if not include or exclude:
                if self.make_non_matched_grey:
                    for obj in objects:
                        obj.active_material.diffuse_color = (0.4, 0.4, 0.4, 1)
                continue

            if self.variation is False:
                color = self.color
            elif self.variation is True:
                color = list(self.color)
                for i in range(3):
                    color[i] += np.random.randint(-10, 10) / 100

            if len(color) == 3:
                color = list(color) + [1]

            for obj in objects:
                obj.active_material.diffuse_color = color

        return{'FINISHED'}


class CATMAID_OP_material_strahler(Operator):
    """Colors a neuron by strahler index.

    This essentially just triggers a reload a reload of these neurons with
    Strahler coloring.
    """

    bl_idname = "color.by_strahler"
    bl_label = "Color neuron(s) by strahler index"
    bl_description = "Color neuron(s) by strahler index"
    bl_options = {'UNDO'}

    which_neurons:  EnumProperty(name="Which Neurons?",
                                 items=[('All', 'All', 'All'),
                                        ('Selected', 'Selected', 'Selected')],
                                 description="Choose which neurons to color by similarity",
                                 default='All')
    color_code: EnumProperty(name="Color code",
                             items=(('grey_alpha', 'Shades of grey', 'use shades of grey + alpha values'),
                                    ('color_alpha', 'New random color', 'use shades of a random color + alpha values'),
                                    ('this_color', 'Use current color', 'use shades of current color + alpha values')),
                             default="this_color",
                             description="Choose how Strahler index is encoded")
    white_background: BoolProperty(name="White background", default=False,
                                   description="Inverts color scheme for white background")


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    @classmethod
    def poll(cls, context):
        if client:
            return True
        return False

    def execute(self, context):
        # Gather skeleton IDs
        if self.which_neurons == 'All':
            skids = get_skids()
        elif self.which_neurons == 'Selected':
            skids = get_skids(selected_only=True)
        elif self.which_neurons == 'Active':
            ob = bpy.context.active_object
            skids = []
            if 'type' in ob and 'id' in ob:
                skids.append(ob['id'])

        # Collect current colors and downsampling factors
        downsampling = {}
        current_colors = {}
        names = {}
        use_radii = {}
        for s in skids:
            objects = skeleton_id_objects(s, somas=False, neurites=True, connectors=False)
            downsampling[s] = 2
            for obj in objects:
                downsampling[s] = obj.get('downsampling', 2)
                current_colors[s] = tuple(obj.active_material.diffuse_color)
                names[s] = obj.name

                if any([p.radius != 1 for p in obj.data.splines[0].points]):
                    use_radii[s] = True
                else:
                    use_radii[s] = False

        # Delete these neurons
        delete_neuron_objects(skids, connectors=False)

        skdata = client.get_skeletons(list(skids),
                                      with_history=False,
                                      with_abutting=False)

        for s in skdata:
            if self.color_code == 'this_color':
                color = current_colors[s]
            elif self.color_code == 'grey_alpha':
                if self.white_background:
                    color = (0, 0, 0, 1)
                else:
                    color = (1, 1, 1, 1)
            else:
                color = (np.random.randint(0, 255, 4) / 255).tolist()

            import_skeleton(skdata[s],
                            skeleton_id=str(s),
                            object_name=names[s],
                            downsampling=downsampling[s],
                            import_synapses=False,
                            import_gap_junctions=False,
                            import_abutting=False,
                            color_by_strahler=color,
                            use_radii=use_radii[s])

        return {'FINISHED'}


class CATMAID_OP_fetch_connectors(Operator):
    """Retrieves connectors of given neuron(s)."""
    bl_idname = "fetch.connectors"
    bl_label = "Retrieve Connectors"
    bl_description = "Import connectors for given neurons/connections."

    which_neurons: EnumProperty(name="For which neuron(s)?",
                                items=[('Selected', 'Selected', 'Selected'),
                                       ('All', 'All', 'All')],
                                description="Choose for which neurons to retrieve connectors")
    color_prop: EnumProperty(name="Colors",
                             items=[('Black', 'Black', 'Black'),
                                    ('Mesh-color', 'Mesh-color', 'Mesh-color'),
                                    ('Random', 'Random', 'Random')],
                             description="How to color the connectors")
    create_as: EnumProperty(name="Create as",
                            items=[('Spheres', 'Spheres', 'Spheres'),
                                   ('Curves', 'Curves', 'Curves')],
                            description="As what to create them")
    base_radius: FloatProperty(name="Base radius", default=0.05,
                               description="Base radius for connector spheres")
    get_inputs: BoolProperty(name="Retrieve inputs", default=True)
    get_outputs: BoolProperty(name="Retrieve outputs", default=True)
    restr_sources: StringProperty(name="Restrict sources",
                                  description='Use e.g. "12345,6789" or "annotation:glomerulus DA1" to restrict connectors to those that target this set of neurons')
    restr_targets: StringProperty(name="Restrict targets",
                                  description='Use e.g. "12345,6789" or "annotation:glomerulus DA1" to restrict connectors to those coming from this set of neurons')

    @classmethod
    def poll(cls, context):
        if client:
            return True
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.which_neurons == 'All':
            to_search = bpy.data.objects
        elif self.which_neurons == 'Selected':
            to_search = bpy.context.selected_objects

        filtered_ob_list = []
        filtered_skids = set()
        for ob in to_search:
            if 'type' in ob and ob['type'] == 'NEURON':
                if 'id' in ob:
                    filtered_skids.add(ob['id'])
                    filtered_ob_list.append(ob)

        if not filtered_skids:
            print('Error - no neurons found! Cancelled')
            self.report({'ERROR'}, 'No neurons found!')
            return {'FINISHED'}

        print(f"Retrieving connector data for {len(filtered_ob_list)} neurons")

        # First get the connector IDs for each neuron
        skdata = client.get_skeletons(filtered_skids)

        # Extract connectors
        all_cn_ids = []
        for s in skdata:
            if not skdata[s] or not len(skdata[s]) >= 2:
                print(f'Neuron {s} has no connectors! Import cancelled.')
                self.report({'ERROR'}, f'Neuron {s} has no connectors! Import cancelled.')
                return {'FINISHED'}

            for c in skdata[s][1]:
                if c[2] == 1 and self.get_inputs:
                    all_cn_ids.append(c[1])
                elif c[2] == 0 and self.get_outputs:
                    all_cn_ids.append(c[1])
        all_cn_ids = set(all_cn_ids)

        if self.restr_sources or self.restr_targets:
            # Get connector details.
            # Data: [[2211855,  # connector ID
            #         {'presynaptic_to': 16,
            #          'postsynaptic_to': [15614, 10474885],
            #          'presynaptic_to_node': 124396,
            #          'postsynaptic_to_node': [2211846, 32891740]}], ...]
            cn_details = client.get_connector_details(all_cn_ids)

            if self.restr_sources:
                source_skids = eval_skids(self.restr_sources)
                source_skids = set([int(s) for s in source_skids])
                source_allowed = set()
                for cn in cn_details:
                    if set(cn[1]['postsynaptic_to']) & source_skids:
                        source_allowed.add(cn[0])
                all_cn_ids = all_cn_ids & source_allowed

            if self.restr_targets:
                target_skids = set(eval_skids(self.restr_targets))
                target_skids = set([int(s) for s in target_skids])
                target_allowed = set()
                for cn in cn_details:
                    if cn[1]['presynaptic_to'] in target_skids:
                        target_allowed.add(cn[0])
                all_cn_ids = all_cn_ids & target_allowed

        if not len(all_cn_ids):
            self.report({'ERROR'}, 'No connectors left after filtering!')
            return {'FINISHED'}

        # Drop connectors that didn't meet the criteria
        for s in skdata:
            skdata[s][1] = [cn for cn in skdata[s][1] if cn[1] in all_cn_ids]

        for s in skdata:
            # Extract nodes, connectors and tags from compact_skeleton
            nodes = np.array(skdata[s][0])
            connectors = np.array(skdata[s][1])

            # Extract coords
            coords = nodes[:, 3:6].astype('float32')

            # Apply global transforms
            coords = apply_global_xforms(coords)

            # Get node and parent IDs
            node_ids = nodes[:, 0].astype(int)

            tn_coords = {n: co for n, co in zip(node_ids, coords)}

            if self.color_prop == 'Random':
                color = (np.random.randint(0, 255, 3) / 255).tolist()
            elif self.color_prop == 'Mesh-color':
                obj = skeleton_id_objects(s, neurites=True, somas=False, connectors=False)[0]
                color = list(obj.active_material.diffuse_color)
            else:
                color = [0, 0, 0]

            if not len(connectors):
                continue

            import_connectors(connectors,
                              tn_coords,
                              skeleton_id=s,
                              color=color,
                              import_synapses=True,
                              import_gap_junctions=True,
                              import_abutting=True,
                              base_radius=self.base_radius,
                              as_curves=self.create_as == 'Curves')

        return {'FINISHED'}


########################################
#  CATMAID/neuron-related functions
########################################

class CatmaidClient:
    """Class representing connection to a CATMAID project."""
    def __init__(self, server, api_token, http_user=None, http_password=None,
                 project_id=1, max_threads=100):
        # Catch too many backslashes in server URL
        while server.endswith('/'):
            server = server[:-1]

        self.server = server
        self.project_id = project_id
        self.http_user = http_user
        self.http_password = http_password
        self.api_token = api_token
        self.max_threads = max_threads

        self.session = requests.Session()

        self.update_credentials()

    def update_credentials(self):
        """Update session headers."""
        if self.http_user and self.http_password:
            self.session.auth = (self.http_user, self.http_password)

        if self.api_token:
            self.session.headers['X-Authorization'] = 'Token ' + self.api_token
        else:
            # If no api token, we have to get a CSRF token instead
            r = self.session.get(self.server)
            r.raise_for_status()
            # Extract token
            key = [k for k in r.cookies.keys() if 'csrf' in k.lower()]

            if not key:
                print("No CSRF Token found. You won't be able to "
                      "do POST requests to this server.")
            else:
                csrf = r.cookies[key[0]]
                self.session.headers['referer'] = self.server
                self.session.headers['X-CSRFToken'] = csrf

    def fetch(self, url, post=None, files=None, on_error='raise', desc='Fetching',
              disable_pbar=False, leave_pbar=True, return_type='json'):
        """Fetch data from given URL(s).

        Parameters
        ----------
        url :           str, list of str
                        URL or list of URLs to fetch data from.
        post :          None | dict | list of dict
                        If provided, will send POST request. Must provide one
                        dictionary for each url.
        files :         str, optional
                        Files to be sent alongside POST request.
        on_error :      "raise" | "log" | "pass"
                        What to do if request returns an error code: raise
                        an exception, log the error but continue or silently
                        pass.
        desc :          str, optional
                        Message for progress bar.
        disable_pbar :  bool, optional
                        If True, won't show progress bar.
        leave_pbar :    bool, optional
                        If True, will not remove pbar after finishing.
        return_type :   "json" | "raw" | "request"
                        Set how to return data::

                          json: return json parsed data (default)
                          raw: return unparsed response content
                          request: return request object

        """
        assert on_error in ['raise', 'log', 'pass']
        assert return_type in ['json', 'raw', 'request']

        # Make sure url and post are iterables
        was_single = isinstance(url, str)
        url = make_iterable(url)
        # Do not use _make_iterable here as it will turn dictionaries into keys
        post = [post] * len(url) if isinstance(post, (type(None), dict, bool)) else post

        if len(url) != len(post):
            raise ValueError('POST needs to be provided for each url.')

        # Generate futures
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for u, p in zip(url, post):
                # Generate requests
                if not isinstance(p, type(None)):
                    f = executor.submit(self.session.post, u, data=p,
                                        files=files,
                                        timeout=get_pref('time_out', 20))
                else:
                    f = executor.submit(self.session.get, u, params=None,
                                        timeout=get_pref('time_out', 20))
                futures.append(f)

        # Get the responses
        resp = [f.result() for f in futures]

        # Check responses for errors
        errors = []
        details = []
        if on_error in ['raise', 'log']:
            for r in resp:
                # Skip if all is well
                if r.status_code == 200:
                    continue
                # CATMAID internal server errors return useful error messages
                if str(r.status_code).startswith('5'):
                    # Try extracting error:
                    try:
                        msg = r.json().get('error', 'No error message.')
                        det = r.json().get('detail', 'No details provided.')
                    except BaseException:
                        msg = r.reason
                        det = 'No details provided.'
                    errors.append('{} Server Error: {} for url: {}'.format(r.status_code,
                                                                           msg,
                                                                           r.url))
                    details.append(det)
                # Parse all other errors
                else:
                    errors.append('{} Server Error: {} for url: {}'.format(r.status_code,
                                                                           r.reason,
                                                                           r.url))
                    details.append('')

        if errors:
            if on_error == 'raise':
                raise HTTPError('{} errors encountered: {}'.format(len(errors),
                                                                   '\n'.join(errors)))
            else:
                for e, d in zip(errors, details):
                    print(e)
                    print('{}. Details: {}'.format(e, d))

        # Return requested data
        if return_type.lower() == 'json':
            parsed = []
            for r in resp:
                content = r.content
                if isinstance(content, bytes):
                    content = content.decode()
                try:
                    parsed.append(json.loads(content))
                except BaseException:
                    print('Error decoding json in response:\n{}'.format(content))
                    raise
        elif return_type.lower() == 'raw':
            parsed = [r.content for r in resp]
        else:
            parsed = resp

        return parsed[0] if was_single else parsed

    def make_url(self, *args, **GET):
        """Generate URL.

        Parameters
        ----------
        *args
                    Will be turned into the URL. For example::

                        >>> remote_instance.make_url('skeleton', 'list')
                        'http://my-server.com/skeleton/list'

        **GET
                    Keyword arguments are assumed to be GET request queries
                    and will be encoded in the url. For example::

                        >>> remote_instance.make_url('skeleton', node_gt: 100)
                        'http://my-server.com/skeleton?node_gt=100'

        Returns
        -------
        url :       str

        """
        # Generate the URL
        url = self.server
        for arg in args:
            arg_str = str(arg)
            joiner = '' if url.endswith('/') else '/'
            relative = arg_str[1:] if arg_str.startswith('/') else arg_str
            url = requests.compat.urljoin(url + joiner, relative)
        if GET:
            url += '?{}'.format(urllib.parse.urlencode(GET))
        return url

    @property
    def catmaid_version(self):
        """Version of CATMAID your server is running."""
        return self.fetch(self._get_catmaid_version())['SERVER_VERSION']

    @property
    def user_permissions(self):
        """List per-project permissions and groups of user with given token."""
        return self.fetch(self.make_url('permission'))

    @property
    def available_projects(self):
        """List of projects hosted on your server.

        This depends on your user's permission!
        """
        return self.fetch(self._get_projects_url())

    @property
    def image_stacks(self):
        """Image stacks available under this project id."""
        stacks = self.fetch(self._get_stacks_url())
        details = self.fetch([self._get_stack_info_url(s['id']) for s in stacks])

        # Add details to stacks
        for s, d in zip(stacks, details):
            s.update(d)

        return stacks

    def _get_catmaid_version(self, **GET):
        """Generate url for retrieving CATMAID server version."""
        return self.make_url('version', **GET)

    def _get_stack_info_url(self, stack_id, **GET):
        """Generate url for retrieving stack infos."""
        return self.make_url(self.project_id, 'stack', stack_id, 'info', **GET)

    def _get_projects_url(self, **GET):
        """Generate URL to get list of available projects on server."""
        return self.make_url('projects', **GET)

    def _get_stacks_url(self, **GET):
        """Generate URL to get list of available image stacks for the project."""
        return self.make_url(self.project_id, 'stacks', **GET)

    def get_abutting(self, skeleton_ids):
        """Get abutting connectors for given skeleton IDs."""
        skeleton_ids = make_iterable(skeleton_ids, force_type=str)
        get = {f'skeleton_ids[{i}]': s for i, s in enumerate(skeleton_ids)}
        get['with_tags'] = 'false'
        get['relation_type'] = 'abutting'

        url = self.make_url(f'{self.project_id}/connectors/', **get)
        data = self.fetch(url)['links']
        #data format: [skeleton_id, connector_id, x, y, z, confidence, creator, treenode_id, creation_date]

        #Now sort to skeleton data -> give abutting connectors relation type 3 (0 = pre, 1 = post, 2 = gap)
        #and put into standard compact-skeleton format: [treenode_id, connector_id, relation_type, x, y, z]
        abutting = {}
        for s in skeleton_ids:
            abutting[s] = [[e[7], e[1], 3, e[2], e[3], e[4]] for e in data if str(e[0]) == s]

        return abutting

    def get_annotation_list(self):
        """Return list with annotations."""
        url = self.make_url(f"{self.project_id}/annotations/")
        return self.fetch(url)['annotations']

    def get_annotations(self, skeleton_ids):
        """Return dictionary with annotations for given skeleton IDs."""
        skeleton_ids = make_iterable(skeleton_ids, force_type=str)

        url = self.make_url(f'{self.project_id}/skeleton/annotationlist')

        post = {'metaannotations': 0, 'neuronnames': 0}
        post.update({f'skeleton_ids[{i}]': s for i, s in enumerate(skeleton_ids)})

        response = self.fetch(url, post=post)

        annotations = {}
        for skid in response['skeletons']:
            annotations[skid] = []
            # for entry in annotation_list_temp['skeletons'][skid]:
            for entry in response['skeletons'][skid]['annotations']:
                annotation_id = entry['id']
                annotations[skid].append(
                    response['annotations'][str(annotation_id)])

        return annotations

    def get_connector_details(self, connector_ids):
        """Return details for given connectors."""
        connector_ids = make_iterable(connector_ids, force_type=str)
        connector_ids = list(set(connector_ids))

        url = self.make_url(f'{self.project_id}/connector/skeletons')

        CHUNK_SIZE = min(50000, len(connector_ids))

        connectors = []
        for ch in range(0, len(connector_ids), CHUNK_SIZE):
            post = {}
            for i, s in enumerate(connector_ids[ch:ch + CHUNK_SIZE]):
                post[f'connector_ids[{i}]'] = s

            connectors += self.fetch(url, post=post)

        # Data: [[2211855,  # connector ID
        #         {'presynaptic_to': 16,
        #          'postsynaptic_to': [15614, 10474885],
        #          'presynaptic_to_node': 124396,
        #          'postsynaptic_to_node': [2211846, 32891740]}], ...]
        return connectors

    def get_user_list(self):
        """Fetch list of CATMAID users."""
        url = self.make_url('user-list')
        return self.fetch(url)

    def get_names(self, skeleton_ids):
        """Fetch names for given skeleton IDs."""
        skeleton_ids = make_iterable(skeleton_ids, force_type=str)
        url = self.make_url(f"{self.project_id}/skeleton/neuronnames")
        post = {f'skids[{i}]': s for i, s in enumerate(skeleton_ids)}
        post['self.project_id'] = self.project_id
        return self.fetch(url, post=post)

    def get_node_counts(self, skeleton_ids):
        """Fetch node counts for given skeleton IDs."""
        skeleton_ids = make_iterable(skeleton_ids, force_type=str)
        url = self.make_url(f"{self.project_id}/skeletons/review-status")
        post = {f'skeleton_ids[{i}]': s for i, s in enumerate(skeleton_ids)}
        review_status = self.fetch(url, post=post)

        return {k: v[0] for k, v in review_status.items()}

    def get_skeletons(self, skeleton_ids, with_history=False, with_abutting=False):
        """Fetch skeletons for given IDs."""
        skeleton_ids = make_iterable(skeleton_ids, force_type=str)
        urls = [self.make_url(f'{self.project_id}/skeletons/{skid}/compact-detail',
                              with_tags='true',
                              with_connectors='true',
                              with_merge_history='false',
                              with_history=str(with_history).lower()) for skid in skeleton_ids]
        responses = self.fetch(urls, on_error='log')
        print(f'Data for {len(responses)} neurons retrieved')
        skdata = {s: r for s, r in zip(skeleton_ids, responses)}

        if with_abutting:
            abutting = self.get_abutting(skeleton_ids)
            for s in skdata:
                skdata[s][1] += abutting.get(s, [])

        return skdata

    def get_volume_list(self):
        """Retrieves list of available volumes."""
        url = self.make_url(f"/{self.project_id}/volumes/")
        response = self.fetch(url)
        # Data is list of lists:
        # id, name, comment, user_id, editor_id, project_id, creation_time,
        # edition_time, annotations, area, volume, watertight, meta_computed
        return sorted(response['data'], key=lambda x: x[1])

    def get_volume(self, volume_id):
        """Fetch given volume."""
        url = self.make_url(f"/{self.project_id}/volumes/{volume_id}")
        r = self.fetch(url)

        mesh_str = r['mesh']
        mesh_name = r['name']
        mesh_type = re.search('<(.*?) ', mesh_str).group(1)

        # Now reverse engineer the mesh
        if mesh_type == 'IndexedTriangleSet':
            t = re.search("index='(.*?)'", mesh_str).group(1).split(' ')
            faces = [(int(t[i]), int(t[i + 1]), int(t[i + 2]))
                     for i in range(0, len(t) - 2, 3)]

            v = re.search("point='(.*?)'", mesh_str).group(1).split(' ')
            vertices = [(float(v[i]), float(v[i + 1]), float(v[i + 2]))
                        for i in range(0, len(v) - 2, 3)]

        elif mesh_type == 'IndexedFaceSet':
            # For this type, each face is indexed and an index of -1 indicates
            # the end of this face set
            t = re.search("coordIndex='(.*?)'", mesh_str).group(1).split(' ')
            faces = []
            this_face = []
            for f in t:
                if int(f) != -1:
                    this_face.append(int(f))
                else:
                    faces.append(this_face)
                    this_face = []

            # Make sure the last face is also appended
            faces.append(this_face)

            v = re.search("point='(.*?)'", mesh_str).group(1).split(' ')
            vertices = [(float(v[i]), float(v[i + 1]), float(v[i + 2]))
                        for i in range(0, len(v) - 2, 3)]
        else:
            print(f"Unknown volume type: {mesh_type}")
            raise TypeError(f"Unknown volume type: {mesh_type}")

        # Collapse to unique vertices
        verts, inv = np.unique(vertices, return_inverse=True, axis=0)
        faces = np.array(faces)
        faces_new = faces.copy()
        for i in range(inv.shape[0]):
            faces_new[faces == i] = inv[i]

        # Scale vertices
        verts = apply_global_xforms(verts)

        return verts, faces_new, mesh_name

    def search_annotations(self, annotations, allow_partial=False, intersect=False):
        """Find skeleton IDs by annotation(s)."""
        annotations = make_iterable(annotations, force_type=str)
        all_ann = self.get_annotation_list()

        if not allow_partial:
            matches = [x for x in all_ann if x['name'] in annotations]
        else:
            matches = [x for x in all_ann if True in [y.lower() in x['name'].lower() for y in annotations]]

        if not matches:
            return []

        url = self.make_url(f"{self.project_id}/annotations/query-targets")
        if intersect:
            post = {'rangey_start': 0,
                    'range_length': 500,
                    'with_annotations': False}
            for i, m in enumerate(matches):
                post[f'annotated_with[{i}]'] = m['id']
            resp = self.fetch(url, post=post)['entities']
            skids = [n['skeleton_ids'][0] for n in resp if n['type'] == 'neuron']
        else:
            skids = []
            for i, m in enumerate(matches):
                post = {'rangey_start': 0,
                        'range_length': 500,
                        'with_annotations': False,
                        'annotated_with[0]': m['id']}
                resp = self.fetch(url, post=post)['entities']
                skids += [n['skeleton_ids'][0] for n in resp if n['type'] == 'neuron']

        skids = np.unique(skids).astype(str)

        print(f'Found {len(skids)} neurons with matching annotation(s)')
        return skids

    def search_names(self, names, allow_partial=False):
        """Find skeleton IDs by neuron name(s)."""
        names = make_iterable(names)
        url = self.make_url(f"{self.project_id}/annotations/query-targets")
        matches = []
        for n in names:
            assert isinstance(n, str)
            post = {'name': str(n.strip()),
                    'rangey_start': 0,
                    'range_length': 500,
                    'with_annotations': False}
            results = self.fetch(url, post)['entities']
            for e in results['entities']:
                if allow_partial and e['type'] == 'neuron' and n.lower() in e['name'].lower():
                    matches += e['skeleton_ids']
                if not allow_partial and e['type'] == 'neuron' and e['name'] == n:
                    matches += e['skeleton_ids']

        return np.unique(matches).astype(str)

    def upload_volume(self, vertices, faces, name, comment):
        """Upload volume to CATMAID."""
        vertices = np.asarray(vertices)

        # Invert global transforms
        vertices = apply_global_xforms(vertices, inverse=True).round()

        faces = np.asarray(faces).astype(int)

        postdata = {'title': name,
                    'type': 'trimesh',
                    'mesh': json.dumps([vertices.tolist(), faces.tolist()]),
                    'comment': comment
                    }

        url = self.make_url(f"/{self.project_id}/volumes/add")
        return self.fetch(url, postdata)

########################################
#  Utility functions
########################################


def import_skeleton(compact_skeleton,
                    skeleton_id,
                    object_name,
                    downsampling=None,
                    import_synapses=False,
                    import_gap_junctions=False,
                    import_abutting=False,
                    use_radii=False,
                    color_by_strahler=False,
                    cn_as_curves=False,
                    neuron_mat_for_connectors=False):
    """Import given skeleton into Blender."""
    # Truncate object name is necessary
    if len(object_name) >= 60:
        object_name = object_name[:55] + '[..]'

    # Extract nodes, connectors and tags from compact_skeleton
    nodes = np.array(compact_skeleton[0])
    connectors = np.array(compact_skeleton[1])
    tags = compact_skeleton[2]

    # Extract coords
    coords = nodes[:, 3:6].astype('float32')

    # Apply global transforms
    coords = apply_global_xforms(coords)

    # Get node and parent IDs
    node_ids = nodes[:, 0].astype(int)
    parent_ids = nodes[:, 1]
    parent_ids[parent_ids == None] = -1
    parent_ids = parent_ids.astype(int)

    if color_by_strahler:
        segments = extract_short_segments(node_ids, parent_ids)
        SI = strahler_index(node_ids, parent_ids)
        prepare_strahler_mats(skeleton_id,
                              max_strahler_index=max(SI.values()),
                              color=color_by_strahler)
    else:
        segments = extract_long_segments(node_ids, parent_ids)

    # Find soma
    soma_node = None
    if 'soma' in tags:
        soma_node = tags['soma'][-1]

    # Find root node
    # -> this will be starting point for creation of the curves
    root_node = node_ids[parent_ids < 0][0]

    # Create the object
    cu = bpy.data.curves.new(f"{object_name} curve", 'CURVE')
    ob = bpy.data.objects.new(object_name, cu)
    ob.location = (0, 0, 0)
    ob.show_name = True
    ob['type'] = 'NEURON'
    ob['subtype'] = 'NEURITES'
    ob['CATMAID_object'] = True
    ob['downsampling'] = downsampling if downsampling else 0
    ob['id'] = str(skeleton_id)
    cu.dimensions = '3D'
    cu.fill_mode = 'FULL'
    cu.bevel_resolution = 5
    cu.resolution_u = 10

    if use_radii:
        cu.bevel_depth = 1
    else:
        cu.bevel_depth = 0.015

    # DO NOT touch this: lookup via dict is >10X faster!
    tn_coords = {n: co for n, co in zip(node_ids, coords)}
    radii = nodes[:, 6].astype(float) / get_pref('scale_factor', 10_000)
    tn_radii = {n: co for n, co in zip(node_ids, radii)}

    # Collect fix nodes
    if isinstance(downsampling, int) and downsampling > 1:
        leafs = node_ids[~np.isin(node_ids, parent_ids)]
        fix_nodes = [root_node] + leafs.tolist()
        _nodes, _counts = np.unique(parent_ids, return_counts=True)
        branch_points = _nodes[_counts > 1]
        fix_nodes += branch_points.tolist()

    for seg in segments:
        if isinstance(downsampling, int) and downsampling > 1:
            mask = np.zeros(len(seg), dtype=bool)
            mask[downsampling::downsampling] = True

            keep = np.isin(seg, fix_nodes)

            seg = np.array(seg)[mask | keep]

        sp = cu.splines.new('POLY')

        coords = np.array([tn_coords[tn] for tn in seg])

        # Add points
        sp.points.add(len(coords) - 1)

        # Add this weird fourth coordinate
        coords = np.c_[coords, [0] * coords.shape[0]]

        # Set point coordinates
        sp.points.foreach_set('co', coords.ravel())
        sp.points.foreach_set('weight', seg)

        if use_radii:
            r = [tn_radii[tn] for tn in seg]
            sp.points.foreach_set('radius', r)

        if color_by_strahler:
            # This Strahler's material name
            mat_name = f'#{skeleton_id} StrahlerMat {SI[seg[0]]}'
            # Grab the corresponding material
            mat = bpy.data.materials[mat_name]

            if mat_name not in ob.data.materials:
                ob.data.materials.append(bpy.data.materials[mat_name])
                slot = len(ob.data.materials)
            else:
                slot = [mat.name for mat in ob.data.materials].index(mat_name)

            # Set this material for this spline
            sp.material_index = slot

    # Take care of the material
    if not color_by_strahler:
        mat_name = f'M#{skeleton_id}'[:59]
        mat = bpy.data.materials.get(mat_name,
                                     bpy.data.materials.new(mat_name))
        ob.active_material = mat
    elif 'soma' in tags:
        # Select the appropriate material for use at soma
        soma_node = tags['soma'][0]
        mat_name = f'#{skeleton_id} StrahlerMat {SI[soma_node]}'
        mat = bpy.data.materials[mat_name]

    # Link curve to scene
    bpy.context.scene.collection.objects.link(ob)

    # Take care of the soma
    if 'soma' in tags:
        soma_node = tags['soma'][0]
        loc = tn_coords[soma_node]
        rad = tn_radii[soma_node]

        mesh = bpy.data.meshes.new(f'Soma of #{skeleton_id} - mesh')
        soma_ob = bpy.data.objects.new(f'Soma of #{skeleton_id}', mesh)

        soma_ob.location = loc

        # Construct the bmesh cube and assign it to the blender mesh.
        bm = bmesh.new()
        try:
            bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, diameter=rad)
        except TypeError:
            bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=rad)
        bm.to_mesh(mesh)
        bm.free()

        mesh.polygons.foreach_set('use_smooth', [True] * len(mesh.polygons))

        soma_ob.name = f'Soma of #{skeleton_id}'
        soma_ob['type'] = 'NEURON'
        soma_ob['subtype'] = 'SOMA'
        soma_ob['CATMAID_object'] = True
        soma_ob['id'] = str(skeleton_id)

        soma_ob.active_material = mat

        # Add the object into the scene
        bpy.context.scene.collection.objects.link(soma_ob)

    if len(connectors):
        import_connectors(connectors,
                          tn_coords,
                          skeleton_id,
                          color=None,
                          as_curves=cn_as_curves,
                          import_synapses=import_synapses,
                          import_gap_junctions=import_gap_junctions,
                          import_abutting=import_abutting)


def import_connectors(connectors,
                      tn_coords,
                      skeleton_id,
                      color=None,
                      import_synapses=True,
                      import_gap_junctions=True,
                      import_abutting=True,
                      base_radius=0.1,
                      as_curves=True):
    """Import connectors."""
    # Compile the connector types to plot
    to_add = []
    if import_synapses:
        to_add += [0, 1]
    if import_gap_junctions:
        to_add += [2]
    if import_abutting:
        to_add += [3]

    # Parse the actual data
    cn_types = connectors[:, 2].astype(int)
    cn_nodes = connectors[:, 0].astype(int)
    cn_coords = connectors[:, 3:6].astype('float32')

    # Apply global transforms
    cn_coords = apply_global_xforms(cn_coords)

    for t in to_add:
        # Load the default properties for this connector type
        settings = DEFAULTS['connectors'][t]

        # Which connectors are of this type
        is_this_type = cn_types == t

        # If none, just skip
        if not np.any(is_this_type):
            continue

        ob_name = f'{settings["name"]} of {skeleton_id}'

        # Get this subtype's coordinates
        this_cn_coords = cn_coords[is_this_type]
        this_tn_coords = np.array([tn_coords[tn] for tn in cn_nodes[is_this_type]])

        if as_curves:
            # Add 4th coordinate for Blender's curves
            this_cn_coords = np.c_[this_cn_coords, [0] * this_cn_coords.shape[0]]
            this_tn_coords = np.c_[this_tn_coords, [0] * this_tn_coords.shape[0]]

            # Combine cn and tn coords in pairs
            # This will have to be transposed to get pairs of cn and tn
            # (see below)
            coords = np.dstack([this_cn_coords, this_tn_coords])
            cu = bpy.data.curves.new(ob_name + ' mesh', 'CURVE')
            ob = bpy.data.objects.new(ob_name, cu)
            cu.dimensions = '3D'
            cu.fill_mode = 'FULL'
            cu.bevel_resolution = 0
            cu.bevel_depth = 0.007
            cu.resolution_u = 0

            for cn in coords:
                sp = cu.splines.new('POLY')

                # Add a second point
                sp.points.add(1)

                # Move points
                sp.points.foreach_set('co', cn.T.ravel())
        else:
            coords = this_cn_coords

            # Generate a base sphere
            base_mesh = bpy.data.meshes.new(f'_connector base mesh')
            bm = bmesh.new()
            try:
                bmesh.ops.create_icosphere(bm, subdivisions=2, diameter=base_radius)
            except TypeError:
                bmesh.ops.create_icosphere(bm, subdivisions=2, radius=base_radius)
            bm.to_mesh(base_mesh)
            bm.free()

            base_verts = np.vstack([v.co for v in base_mesh.vertices])
            base_faces = np.vstack([list(v.vertices) for v in base_mesh.polygons])

            # Repeat sphere vertices
            sp_verts = np.tile(base_verts.T, coords.shape[0]).T
            # Add coords offsets to each sphere
            offsets = np.repeat(coords, base_verts.shape[0], axis=0)
            sp_verts += offsets

            # Repeat sphere faces and offset vertex indices
            sp_faces = np.tile(base_faces.T, coords.shape[0]).T
            face_offsets = np.repeat(np.arange(coords.shape[0]),
                                     base_faces.shape[0], axis=0)
            face_offsets *= base_verts.shape[0]
            sp_faces += face_offsets.reshape((face_offsets.size, 1))

            # Generate mesh
            mesh = bpy.data.meshes.new(ob_name + ' mesh')
            mesh.from_pydata(sp_verts, [], sp_faces.tolist())
            mesh.polygons.foreach_set('use_smooth', [True] * len(mesh.polygons))
            ob = bpy.data.objects.new(ob_name, mesh)

        bpy.context.scene.collection.objects.link(ob)

        ob['type'] = 'NEURON'
        ob['subtype'] = 'CONNECTORS'
        ob['CATMAID_object'] = True
        ob['cn_type'] = t
        ob['id'] = str(skeleton_id)
        ob.location = (0, 0, 0)
        ob.show_name = False

        mat_name = f'{settings["name"]} of #{skeleton_id}'
        mat = bpy.data.materials.get(mat_name,
                                     bpy.data.materials.new(mat_name))

        if not color:
            color = settings['color']
        elif len(color) == 3:
            color = list(color) + [1]

        mat.diffuse_color = color
        ob.active_material = mat


def extract_short_segments(node_ids, parent_ids):
    """Extract linear segments for given neuron.

    This only goes from branches/leafs to the next branch or leaf - hence
    "short segments".
    """
    # 1. Find leafs and branch points
    leafs = node_ids[~np.isin(node_ids, parent_ids)]
    _parents, counts = np.unique(parent_ids, return_counts=True)
    branch_points = _parents[counts > 1]
    # Combine into seeds
    seeds = np.append(leafs, branch_points)

    # Add root to stop condition
    root = node_ids[parent_ids < 0]
    stops = set(np.append(seeds, root))

    segments = []
    lop = dict(zip(node_ids, parent_ids))
    for node in seeds:
        this_seg = [node]
        parent = lop[node]
        while parent not in stops:
            this_seg.append(parent)
            parent = lop[parent]
        segments.append(this_seg)

    return sorted(segments, key=lambda x: len(x), reverse=True)


def extract_long_segments(node_ids, parent_ids):
    """Extract linear segments for given neuron maximizing length."""
    # Create child -> parent dict
    lop = dict(zip(node_ids, parent_ids))

    # Create segments:
    # 1. Find leafs
    leafs = node_ids[~np.isin(node_ids, parent_ids)]
    # 2. For each leaf get the distance to root
    dists = dict()
    for l in leafs:
        d = 1
        p = lop[l]
        while p >= 0:
            d += 1
            p = lop[p]
        dists[l] = d
    # 3. Sort leafs by distance to roots
    leafs = sorted(leafs, key=lambda x: dists.get(x, 0), reverse=True)
    # 4. Extract segments
    seen: set = set()
    segments = []
    for node in leafs:
        segment = [node]
        parent = lop[node]
        while parent >= 0:
            segment.append(parent)
            if parent in seen:
                break
            seen.add(parent)
            parent = lop[parent]

        if len(segment) > 1:
            segments.append(segment)

    segments = sorted(segments, key=lambda x: len(x), reverse=True)

    return segments


def import_mesh(vertices, faces, name='mesh'):
    """Import mesh into scene."""
    if isinstance(vertices, np.ndarray):
        vertices = vertices.tolist()

    if isinstance(faces, np.ndarray):
        faces = faces.tolist()

    # Now create the mesh
    me = bpy.data.meshes.new(name + '_mesh')
    ob = bpy.data.objects.new(name, me)

    bpy.context.scene.collection.objects.link(ob)

    me.from_pydata(vertices, [], faces)
    me.update()


def make_iterable(x, force_type=None):
    """Convert input into a np.ndarray, if it isn't already.

    For dicts, keys will be turned into array.

    """
    if not isinstance(x, collections.Iterable) or isinstance(x, str):
        x = [x]

    if isinstance(x, dict) or isinstance(x, set):
        x = list(x)

    if force_type:
        return np.array(x).astype(force_type)
    else:
        return np.array(x)


def get_pref(key, default=None):
    """Fetch given key from preferences."""
    if 'CATMAIDImport' in bpy.context.preferences.addons:
        prefs = bpy.context.preferences.addons['CATMAIDImport'].preferences

        if hasattr(prefs, key):
            return getattr(prefs, key)
        elif default:
            return default
        else:
            raise KeyError(f'`CatmaidImport` has no preference "{key}"')
    else:
        if default:
            return default
        else:
            raise KeyError(f'Could not find `CatmaidImport` preferences.')


def random_colors(color_count, color_range='RGB',
                  start_rgb=None, end_rgb=None, alpha=1):
    """Create evenly spaced colors in given color space."""
    # Make count_color an even number
    if color_count % 2 != 0:
        color_count += 1

    if start_rgb and end_rgb and start_rgb != end_rgb:
        # Convert RGBs to HSVs
        start_hue = colorsys.rgb_to_hsv(*start_rgb)[0]
        end_hue = colorsys.rgb_to_hsv(*end_rgb)[0]
    else:
        start_hue = 0
        end_hue = 1

    colors = []
    if color_range == 'RGB':
        interval = (end_hue - start_hue) / color_count
        for i in range(color_count):
            saturation = 1
            brightness = 1
            hue = start_hue + (interval * i)
            colors.append(colorsys.hsv_to_rgb(hue, saturation, brightness))

            if brightness == 1:
                brightness = .5
            else:
                brightness = 1
    elif color_range == 'Grayscale':
        saturation = 1
        brightness = 1
        hue = 0
        for i in range(color_count):
            v = 1 / color_count * i
            colors.append(colorsys.hsv_to_rgb(hue, saturation, v))

    if not isinstance(alpha, type(None)):
        colors = [[c[0], c[1], c[2], alpha] for c in colors]

    print(f'{len(colors)} random colors created')

    return colors


def cluster_kmeans(points, n_clusters):
    """Produce a k-means clustering for given coordinates."""
    points = np.asarray(points)
    # Assign each point to a random cluster but make sure each cluster shows
    # up at least once
    clust = list(range(n_clusters)) * math.ceil(len(points) / n_clusters)
    clust = np.array(clust)[:len(points)]
    np.random.shuffle(clust)

    while True:
        # Get cluster centers
        centers = np.array([points[clust == i].mean(axis=0) for i in np.unique(clust)])

        # For each point get the distance to the cluster centers
        dists = [np.linalg.norm(points - centers[i], axis=1) for i in np.unique(clust)]
        dists = np.array(dists).T

        new_clust = np.argmin(dists, axis=1)

        if np.all(new_clust == clust):
            break

        clust = new_clust

    return clust, centers, dists.min(axis=1)


def get_skids(selected_only=False):
    """Return all unique skeleton IDs in the scene."""
    if selected_only:
        to_check = bpy.context.selected_objects
    else:
        to_check = bpy.data.objects

    skids = set()
    for obj in to_check:
        if 'type' in obj and obj['type'] == 'NEURON':
            skids.add(obj['id'])
    return skids


def get_neuron_objects(neurites=True, somas=True, connectors=False,
                       selected_only=False):
    """Return all neuron objects in the scene."""
    if selected_only:
        to_check = bpy.context.selected_objects
    else:
        to_check = bpy.data.objects

    objects = []
    for obj in to_check:
        if 'CATMAID_object' not in obj:
            continue
        if 'type' not in obj:
            continue
        if obj['type'] == 'NEURON':
            if obj['subtype'] == 'NEURITES' and not neurites:
                continue
            if obj['subtype'] == 'SOMA' and not somas:
                continue
            if obj['subtype'] == 'CONNECTORS' and not connectors:
                continue
        objects.append(obj)
    return objects


def delete_neuron_objects(skeleton_ids, neurites=True, somas=True, connectors=True):
    """Delete neuron objects for given skeleton ID(s)."""
    skeleton_ids = make_iterable(skeleton_ids)

    # First deselect all objects
    for obj in bpy.data.objects:
        obj.select_set(False)

    # Now select objects to delete
    for skid in skeleton_ids:
        to_delete = skeleton_id_objects(skid,
                                        neurites=neurites,
                                        somas=somas,
                                        connectors=connectors)
        for obj in to_delete:
            obj.select_set(True)

    print(f'Deleting {len(bpy.context.selected_objects)} from scene')

    # Delete selected objects
    bpy.ops.object.delete(use_global=False)


def skeleton_id_objects(skeleton_id, neurites=True, somas=True, connectors=False,
                        selected_only=False):
    """Get all objects matching the given skeleton ID."""
    skeleton_id = str(skeleton_id)
    objects = get_neuron_objects(neurites=neurites,
                                 somas=somas,
                                 connectors=connectors,
                                 selected_only=selected_only)

    matches = []
    for obj in objects:
        if 'id' not in obj:
            continue
        if obj['id'] != skeleton_id:
            continue
        matches.append(obj)
    return matches


def strahler_index(node_ids, parent_ids):
    """Calculate Strahler index for all treenodes

    - starts with index of 1 at each leaf
    - at forks with varying incoming strahler index, the highest index
      is continued
    - at forks with the same incoming strahler index, highest index + 1 is
      continued
    """
    node_ids = np.asarray(node_ids)
    parent_ids = np.asarray(parent_ids)

    # Find leaf and branch points
    leafs = node_ids[~np.isin(node_ids, parent_ids)]

    _parents, counts = np.unique(parent_ids, return_counts=True)
    branch_points = _parents[counts > 1]

    list_of_parents = dict(zip(node_ids, parent_ids))
    list_of_childs = defaultdict(list)
    for n, p in zip(node_ids, parent_ids):
        list_of_childs[p].append(n)

    strahler_index = {}
    seeds = set(np.append(leafs, branch_points).tolist())
    while seeds:
        seen = set()
        for i, node in enumerate(seeds):

            # First check, if all childs of this starting point have already
            # been processed and skip this node for now if that's not yet the
            # case
            skip = False
            for child in list_of_childs[node]:
                if child not in strahler_index:
                    skip = True
                    break
            if skip:
                continue

            # Calculate index for this branch
            previous_indices = []
            for child in list_of_childs[node]:
                previous_indices.append(strahler_index[child])

            if len(previous_indices) == 0:
                this_branch_index = 1
            elif len(previous_indices) == 1:  # this actually should not happen
                this_branch_index = previous_indices[0]
            elif len(set(previous_indices)) == 1:
                this_branch_index = previous_indices[0] + 1
            else:
                this_branch_index = max(previous_indices)

            strahler_index[node] = this_branch_index
            seen.add(node)

            # Now propagate Strahler indices
            parent = list_of_parents.get(node, -1)
            while parent >= 0 and parent not in seeds:
                strahler_index[parent] = this_branch_index
                parent = list_of_parents.get(parent, -1)

        # Drop those seeds that we were able to process in this run
        for node in seen:
            seeds.remove(node)

    return strahler_index


def prepare_strahler_mats(skid, max_strahler_index, color):
    """Create set of Strahler index materials for this neuron."""
    for i in range(1, (max_strahler_index + 1)):
        mat_name = f'#{skid} StrahlerMat {i}'

        cfactor = i / max_strahler_index
        this_color = [c * cfactor for c in color]

        if len(this_color) == 3:
            this_color.append(1)

        mat = bpy.data.materials.get(mat_name,
                                     bpy.data.materials.new(mat_name))
        mat.diffuse_color = this_color


def eval_skids(x):
    """Evalutate parameters passed as skeleton IDs.

    Will turn annotations and neuron names into skeleton IDs.

    Parameters
    ----------
    x :             int | str | list thereof
                    Your options are either:
                     1. int or list of ints will be assumed to be skeleton IDs
                     2. str or list of str:
                         - if convertible to int, will be interpreted as skid
                         - if starts with 'annotation:' will be assumed to be
                           annotations
                         - else, will be assumed to be neuron names

    Returns
    -------
    skeleton_ids :  list
                    List containing skeleton IDs as strings.

    """
    if ',' in x:
        x = x.split(',')

    if isinstance(x, (int, np.int64, np.int32, np.int16)):
        return [str(x)]
    elif isinstance(x, (str, np.str)):
        try:
            return [str(int(x))]
        except ValueError:
            if x.startswith('annotation:'):
                return client.search_annotations(x[11:])
            elif x.startswith('name:'):
                return client.search_names(x[5:], allow_partial=False)
            else:
                return client.search_names(x, allow_partial=False)
    elif isinstance(x, (list, np.ndarray)):
        skids = []
        for e in x:
            temp = eval_skids(e)
            if isinstance(temp, (list, np.ndarray)):
                skids += temp
            else:
                skids.append(temp)
        return list(set(skids))
    else:
        raise TypeError(f'Unable to parse skeleton IDs from type "{type(x)}"')


def apply_global_xforms(points, inverse=False):
    """Apply globally defined transforms to coordinates."""
    global_scale = 1 / get_pref('scale_factor', 10_000)
    up = get_pref('axis_up', 'Z')
    forward = get_pref('axis_forward', 'Y')

    # Note: `Matrix` is available at global namespace in Blender
    global_matrix = axis_conversion(from_forward=forward,
                                    from_up=up,
                                    ).to_4x4() @ Matrix.Scale(global_scale, 4)

    if inverse:
        global_matrix = np.linalg.inv(global_matrix)

    # Add a fourth column to points
    points_mat = np.ones((points.shape[0], 4))
    points_mat[:, :3] = points

    return np.dot(global_matrix, points_mat.T).T[:, :3]


########################################
#  Preferences
########################################


@orientation_helper(axis_forward='-Z', axis_up='-Y')
class CATMAID_preferences(AddonPreferences):
    bl_idname = 'CATMAIDImport'

    server_url: StringProperty(name="CATMAID Server URL",
                               default='https://fafb.catmaid.virtualflybrain.org/')
    project_id: IntProperty(name="Project ID", default=1)
    http_user: StringProperty(name="HTTP user", default='',
                              description="In case your CATMAID server "
                                          "requires an additional HTTP "
                                          "authentication (i.e. before you) "
                                          "even get to the CATMAID page.")
    http_pw: StringProperty(name="HTTP password", default='', subtype='PASSWORD',
                            description="In case your CATMAID server "
                                        "requires an additional HTTP "
                                        "authentication (i.e. before you) "
                                        "even get to the CATMAID page.")
    api_token:  StringProperty(name="API Token", default='', subtype='PASSWORD',
                               description="Retrieve your API token by logging "
                                           "into CATMAID and hovering over your "
                                           "username (top right) on the project "
                                           "selection screen. Leave empty if "
                                           "no token required.")

    time_out: IntProperty(name="Time to Server Timeout [s]",
                          default=30,
                          description='Server requests will be timed out '
                                      'after this duration to prevent '
                                      'Blender from freezing indefinitely.')
    max_requests: IntProperty(name="Max parallel requests",
                              default=20, min=1,
                              description='Restricting the number of parallel '
                                          'requests can help if you get errors '
                                          'when loading loads of neurons.')

    scale_factor: IntProperty(name="CATMAID to Blender unit conversion Factor",
                              default=10000,
                              description='CATMAID units will be divided '
                                          'by this factor when imported '
                                          'into Blender.')

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="CATMAID credentials:")
        box.prop(self, "server_url")
        box.prop(self, "api_token")
        box.prop(self, "project_id")
        box.prop(self, "http_user")
        box.prop(self, "http_pw")

        box = layout.box()
        box.label(text="Connection settings:")
        box.prop(self, "time_out")
        box.prop(self, "max_requests")

        box = layout.box()
        box.label(text="Import options:")
        box.prop(self, "scale_factor")
        box.prop(self, "axis_forward")
        box.prop(self, "axis_up")


########################################
#  Registration stuff
########################################


classes = (CATMAID_PT_import_panel,
           CATMAID_PT_export_panel,
           CATMAID_PT_properties_panel,
           CATMAID_OP_connect,
           CATMAID_OP_fetch_connectors,
           CATMAID_OP_fetch_neuron,
           CATMAID_OP_fetch_volume,
           CATMAID_OP_upload_volume,
           CATMAID_OP_display_help,
           CATMAID_OP_material_change,
           CATMAID_OP_material_randomize,
           CATMAID_OP_material_spatial,
           CATMAID_OP_material_annotation,
           CATMAID_OP_curve_change,
           CATMAID_OP_material_strahler,
           CATMAID_preferences)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


# This allows us to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
