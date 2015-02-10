# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import mock
import requests_mock

from fuelclient.cli.actions import graph
from fuelclient.tests import base


GRAPH_API_OUTPUT = "digraph G { A -> B -> C }"
TASKS_API_OUTPUT = [
    {'id': 'primary-controller'},
    {'id': 'sync-time'},
]


class TestGraphAction(base.UnitTestCase):

    def setUp(self):
        super(TestGraphAction, self).setUp()
        self.requests_mock = requests_mock.mock()
        self.requests_mock.start()
        self.m_tasks_api = self.requests_mock.get(
            '/api/v1/clusters/1/deployment_tasks',
            json=TASKS_API_OUTPUT)
        self.m_graph_api = self.requests_mock.get(
            '/api/v1/clusters/1/deploy_tasks/graph.gv',
            text=GRAPH_API_OUTPUT)

        self.m_full_path = mock.patch.object(graph.GraphAction,
                                             'full_path_directory').start()
        self.m_full_path.return_value = '/path'

    def tearDown(self):
        super(TestGraphAction, self).tearDown()
        self.requests_mock.stop()
        self.m_full_path.stop()

    def check_content_to_save(self, m_open, content):
        m_open().__enter__().write.assert_any_call(content)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_download_all_tasks(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1', '--download']
        )

        querystring = self.m_graph_api.last_request.qs
        for task in TASKS_API_OUTPUT:
            self.assertIn(task['id'], querystring['tasks'][0])
        self.check_content_to_save(m_open, GRAPH_API_OUTPUT)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_download_selected_tasks(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1',
             '--tasks', 'task-a', 'task-b']
        )

        querystring = self.m_graph_api.last_request.qs
        self.assertIn('task-a', querystring['tasks'][0])
        self.assertIn('task-b', querystring['tasks'][0])
        self.check_content_to_save(m_open, GRAPH_API_OUTPUT)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_download_with_skip(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1',
             '--skip', 'sync-time', 'task-b']
        )
        querystring = self.m_graph_api.last_request.qs
        self.assertIn('primary-controller', querystring['tasks'][0])
        self.assertNotIn('sync-time', querystring['tasks'][0])
        self.assertNotIn('task-b', querystring['tasks'][0])
        self.check_content_to_save(m_open, GRAPH_API_OUTPUT)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_download_with_end_and_start(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1', '--start', 'task-a',
             '--end', 'task-b']
        )

        tasks_qs = self.m_tasks_api.last_request.qs
        self.assertEqual('task-a', tasks_qs['start'][0])
        self.assertEqual('task-b', tasks_qs['end'][0])

        graph_qs = self.m_graph_api.last_request.qs
        for task in TASKS_API_OUTPUT:
            self.assertIn(task['id'], graph_qs['tasks'][0])
        self.check_content_to_save(m_open, GRAPH_API_OUTPUT)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_download_only_parents(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1',
             '--parents-for', 'task-z']
        )
        querystring = self.m_graph_api.last_request.qs
        self.assertEqual('task-z', querystring['parents_for'][0])

        self.check_content_to_save(m_open, GRAPH_API_OUTPUT)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_params_saved_in_dotfile(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1',
             '--parents-for', 'task-z',
             '--skip', 'task-a']
        )
        saved_params = ("# params:\n"
                        "# - start: None\n"
                        "# - end: None\n"
                        "# - skip: ['task-a']\n"
                        "# - tasks: []\n"
                        "# - parents-for: task-z\n")
        self.check_content_to_save(m_open, saved_params)

    @mock.patch('fuelclient.cli.actions.graph.open', create=True)
    def test_params_in_filename(self, m_open):
        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1',
             '--parents-for', 'task-z']
        )
        m_open.assert_called_with(
            '/path/deployment_graph_start_None_end_None_parents-for_task-z.gv',
            'w')

        self.execute_wo_auth(
            ['fuel', 'graph', '--download', '--env', '1',
             '--start', 'task-y']
        )
        m_open.assert_called_with(
            '/path/deployment_graph_start_task-y_end_None_parents-for_None.gv',
            'w')

    @mock.patch('fuelclient.cli.actions.graph.utils.render_graph')
    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    def test_render(self, m_exists, m_render):
        m_exists.return_value = True
        self.execute_wo_auth(
            ['fuel', 'graph', '--render', 'graph.gv']
        )
        m_render.assert_called_once_with('graph.gv', '/path/graph.gv.png')

    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    def test_render_no_file(self, m_exists):
        m_exists.return_value = False
        with self.assertRaises(SystemExit):
            self.execute_wo_auth(
                ['fuel', 'graph', '--render', 'graph.gv']
            )

    @mock.patch('fuelclient.cli.actions.graph.utils.render_graph')
    @mock.patch('fuelclient.cli.actions.graph.os.path.exists')
    def test_render_with_output_path(self, m_exists, m_render):
        output_dir = '/output/dir'
        m_exists.return_value = True
        self.m_full_path.return_value = output_dir
        self.execute_wo_auth(
            ['fuel', 'graph', '--render', 'graph.gv', '--dir', output_dir]
        )
        self.m_full_path.assert_called_once_with(output_dir, '')
        m_render.assert_called_once_with('graph.gv',
                                         '/output/dir/graph.gv.png')
