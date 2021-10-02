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
import json
import requests
import six
import time
import urllib

import numpy as np

from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import (FloatVectorProperty, FloatProperty, StringProperty,
                       BoolProperty, EnumProperty, IntProperty,
                       CollectionProperty)

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
 "blender": (2, 9, 2),
 "location": "Properties > Scene > CATMAID Import",
 "description": "Imports Neuron from CATMAID server, Analysis tools, Export to SVG",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "Object"}

client = None

DEFAULTS = {
 "connectors": {0: {'color': (0, 0.8, 0.8, 1),  # postsynapses
                    'name': 'Presynapses'},
                1: {'color': (1, 0, 0, 1),  # presynapses
                    'name': 'Postsynapses'},
                2: {'color': (0, 1, 0, 1),  # gap junctions
                    'name': 'GapJunction'},
                3: {'color': (0.5, 0, 0.5, 1),  # abutting
                    'name': 'Abutting'},
               }
}

########################################
#  UI Elements
########################################


class CATMAID_PT_MAIN_PANEL(Panel):
    """Creates import menu in viewport side menu."""

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "CATMAID import"
    bl_category = "CATMAID import"

    def draw(self, context):
        layout = self.layout

        ver_str = '.'.join([str(i) for i in bl_info['version']])
        layout.label(text=f'CATMAID Import (v{ver_str})')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("catmaid.connect", text="Connect to CATMAID", icon='PLUGIN')

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("fetch.neuron", text="Import Neuron(s)", icon='ARMATURE_DATA')


########################################
#  Operators
########################################

class CATMAID_OP_connect(Operator):
    bl_idname = "catmaid.connect"
    bl_label = 'Connect CATMAID'
    bl_description = "Connect to given CATMAID server."

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

        #Retrieve user list, to test if PW was correct:
        try:
            _ = client.get_user_list()
            self.report({'INFO'}, 'Connection successful')
            print('Test call successful')
        except BaseException as e:
            self.report({'ERROR'}, 'Connection failed: see console')
            raise

        return {'FINISHED'}


class CATMAID_OP_fetch_neuron(Operator):
    bl_idname = "fetch.neuron"
    bl_label = 'Fetch neurons'
    bl_description = "Fetch given neurons from global server."

    names: StringProperty(name="Name(s)",
                          description="Search by neuron names. Separate "
                                      "multiple names by commas. For example: "
                                      "'neuronA,neuronB,neuronC'")
    partial_match: BoolProperty(name="Allow partial matches?", default=False,
                                description="Allow partial matches for neuron "
                                            "names and annotations! Will also "
                                            "become case-insensitive.")
    annotations: StringProperty(name="Annotations(s)",
                                description="Search by skeleton IDs. Separate "
                                            "multiple annotations by commas. For "
                                            "example: 'annotation 1,annotation2"
                                            ",annotation3'.")
    intersect: BoolProperty(name="Intersect", default=False,
                            description="If true, all identifiers (e.g. two "
                                        "annotations or name + annotation) "
                                        "have to be true for a neuron to be "
                                        "loaded")
    skeleton_ids: StringProperty(name="Skeleton ID(s)",
                                 description="Search by skeleton IDs. Separate "
                                             "multiple IDs by commas. "
                                             "Does not accept more than 400 "
                                             "characters in total!")
    minimum_nodes: IntProperty(name="Minimum node count", default=1, min=1,
                               description="Neurons with fewer nodes than this "
                                           " will be ignored.")
    import_synapses: BoolProperty(name="Synapses", default=True,
                                  description="Import chemical synapses (pre- "
                                              "and postsynapses), similarly to "
                                              "3D Viewer in CATMAID")
    import_gap_junctions: BoolProperty(name="Gap Junctions", default=False,
                                       description="Import gap junctions, "
                                                   "similarly to 3D Viewer in "
                                                   "CATMAID")
    import_abutting: BoolProperty(name="Abutting Connectors", default=False,
                                  description="Import abutting connectors.")
    downsampling: IntProperty(name="Downsampling Factor", default=2, min=1, max=20,
                              description="Will reduce number of nodes by given "
                                           "factor. Root, ends and forks are "
                                           "preserved.")
    use_radius: BoolProperty(name="Use node radii", default=False,
                             description="If true, neuron will use node radii "
                                         "for thickness. If false, radius is "
                                         "assumed to be 70nm (for visibility).")
    neuron_mat_for_connectors: BoolProperty(name="Connector color as neuron",
                                            default=False,
                                            description="If true, connectors "
                                                        "will have the same "
                                                        "color as the neuron.")
    skip_existing: BoolProperty(name="Skip existing", default=True,
                                description="If True, will not add neurons that "
                                            "are already in the scene.")

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

        ### Extract skeleton IDs from skeleton_id string
        print(f'{len(skeletons_to_retrieve)} neurons found - resolving names...')
        neuron_names = client.get_names(skeletons_to_retrieve)

        print("Collecting skeleton data...")
        start = time.time()
        skdata = client.get_skeletons(list(skeletons_to_retrieve),
                                      with_history=False,
                                      with_abutting=self.import_abutting)

        print(f"Importing for {len(skdata)} skeletons into Blender")

        for skid in skdata:
            import_skeleton(skdata[skid],
                            skeleton_id=str(skid),
                            neuron_name=neuron_names[str(skid)],
                            downsampling=self.downsampling,
                            import_synapses=self.import_synapses,
                            import_gap_junctions=self.import_gap_junctions,
                            import_abutting=self.import_abutting,
                            use_radii=self.use_radius,
                            neuron_mat_for_connectors=self.neuron_mat_for_connectors)

        print(f'Finished Import in {time.time()-start:.1f}s')

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
            abbutting[s] = [[e[7], e[1], 3, e[2], e[3], e[4]] for e in data if str(e[0]) == s]

        return abutting

    def get_annotation_list(self):
        """Return list with annotations."""
        url = self.make_url(f"{self.project_id}/annotations/")
        return self.fetch(url)['annotations']

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

########################################
#  Utility functions
########################################


def import_skeleton(compact_skeleton,
                    skeleton_id,
                    neuron_name='',
                    downsampling=None,
                    import_synapses=False,
                    import_gap_junctions=False,
                    import_abutting=False,
                    use_radii=False,
                    neuron_mat_for_connectors=False):
    """Import given skeleton into Blender."""
    # Create an object name
    object_name = f'#{skeleton_id} - {neuron_name}'
    #Truncate object name is necessary
    if len(object_name) >= 60:
        cellname = object_name[:56] + '...'

    # Extract nodes, connectors and tags from compact_skeleton
    nodes = np.array(compact_skeleton[0])
    connectors = np.array(compact_skeleton[1])
    tags = compact_skeleton[2]

    # Extract coords
    coords = nodes[:, 3:6].astype('float32')
    # Apply scaling
    coords /= get_pref('scale_factor', 10_000)
    # Invert y-axis
    coords *= [1, -1, 1]

    # Get node and parent IDs
    node_ids = nodes[:, 0].astype(int)
    parent_ids = nodes[:, 1]
    parent_ids[parent_ids == None] = -1
    parent_ids = parent_ids.astype(int)

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
    ob['CATMAID_object'] = True
    ob['id'] = str(skeleton_id)
    cu.dimensions = '3D'
    cu.fill_mode = 'FULL'
    cu.bevel_resolution = 5
    cu.resolution_u = 10

    if use_radii:
        cu.bevel_depth = 1
    else:
        cu.bevel_depth = 0.007

    # DO NOT touch this: lookup via dict is >10X faster!
    tn_coords = {n: co for n, co in zip(node_ids, coords)}
    radii = nodes[:, 6].astype(float) / get_pref('scale_factor', 10_000)
    tn_radii = {n: co for n, co in zip(node_ids, radii)}

    # Collect fix nodes
    if isinstance(downsampling, int) and downsampling > 1:
        fix_nodes = [root_node] + leafs
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

    # Take care of the material
    mat_name = (f'M#{skeleton_id}')[:59]
    mat = bpy.data.materials.get(mat_name,
                                 bpy.data.materials.new(mat_name))
    ob.active_material = mat

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
        bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, diameter=rad)
        bm.to_mesh(mesh)
        bm.free()

        mesh.polygons.foreach_set('use_smooth', [True] * len(mesh.polygons))

        soma_ob.name = f'Soma of #{skeleton_id}'
        soma_ob['type'] = 'SOMA'
        soma_ob['CATMAID_object'] = True
        soma_ob['id'] = str(skeleton_id)

        soma_ob.active_material = mat

        # Add the object into the scene
        bpy.context.scene.collection.objects.link(soma_ob)

    if len(connectors):
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
        cn_coords /= get_pref('scale_factor', 10_000)
        cn_coords *= [1, -1, 1]

        for t in to_add:
            # Load the default properties for this connector type
            settings = DEFAULTS['connectors'][t]

            # Which connectors are of this type
            is_this_type = cn_types == t

            # If none, just skip
            if not np.any(is_this_type):
                continue

            ob_name = f'{settings["name"]} of {skeleton_id}'

            # Only plot as lines if this is a TreeNeuron
            this_cn_coords = cn_coords[is_this_type]
            this_tn_coords = np.array([tn_coords[tn] for tn in cn_nodes[is_this_type]])

            # Add 4th coordinate for Blender
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
            bpy.context.scene.collection.objects.link(ob)

            ob['type'] = 'CONNECTORS'
            ob['CATMAID_object'] = True
            ob['cn_type'] = t
            ob['id'] = str(skeleton_id)
            ob.location = (0, 0, 0)
            ob.show_name = False

            mat_name = f'{settings["name"]} of #{skeleton_id}'
            mat = bpy.data.materials.get(mat_name,
                                         bpy.data.materials.new(mat_name))
            mat.diffuse_color = settings['color']
            ob.active_material = mat



def make_iterable(x, force_type=None):
    """Convert input into a np.ndarray, if it isn't already.

    For dicts, keys will be turned into array.

    """
    if not isinstance(x, collections.Iterable) or isinstance(x, six.string_types):
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

########################################
#  Preferences
########################################

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
    scale_factor: IntProperty(name="CATMAID to Blender unit conversion Factor",
                                   default=10000,
                                   description='CATMAID units will be divided '
                                               'by this factor when imported '
                                               'into Blender.')
    time_out: IntProperty(name="Time to Server Timeout [s]",
                          default=20,
                          description='Server requests will be timed out '
                                      'after this duration to prevent '
                                      'Blender from freezing indefinitely.')
    max_requests: IntProperty(name="Max parallel requests",
                              default=20, min=1,
                              description='Restricting the number of parallel '
                                          'requests can help if you get errors '
                                          'when loading loads of neurons.')

    def draw(self, context):
        layout = self.layout
        layout.label(text="CATMAID Import Preferences. Add your credentials "
                           "to not have to enter them again after each restart.")
        layout.prop(self, "server_url")
        layout.prop(self, "api_token")
        layout.prop(self, "project_id")
        layout.prop(self, "http_user")
        layout.prop(self, "http_pw")
        layout.prop(self, "scale_factor")
        layout.prop(self, "time_out")
        layout.prop(self, "max_requests")

########################################
#  Registeration stuff
########################################

classes = (CATMAID_PT_MAIN_PANEL,
           CATMAID_OP_connect,
           CATMAID_OP_fetch_neuron,
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
