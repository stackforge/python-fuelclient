# -*- coding: utf-8 -*-
#
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

import json
import re

import requests_mock as rm

import fuelclient
from fuelclient.tests import utils
from fuelclient.tests.v2.unit.lib import test_api


class TestNodeFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestNodeFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/nodes/'.format(version=self.version)

        self.fake_node = utils.get_fake_node()
        self.fake_nodes = [utils.get_fake_node() for _ in range(10)]

        self.client = fuelclient.get_client('node', self.version)

    def test_node_list(self):
        matcher = self.m_request.get(self.res_uri,
                                     text=json.dumps(self.fake_nodes))
        self.client.get_all()

        self.assertTrue(matcher.called)

    def test_node_show(self):
        node_id = 42
        expected_uri = self.get_object_uri(self.res_uri, node_id)

        matcher = self.m_request.get(expected_uri,
                                     text=json.dumps(self.fake_node))

        self.client.get_by_id(node_id)

        self.assertTrue(matcher.called)

    def test_node_vms_list(self):
        node_id = 42
        expected_uri = "/api/v1/nodes/{0}/vms_conf/".format(node_id)

        fake_vms = json.dumps([{'id': 1, 'opt2': 'val2'},
                               {'id': 2, 'opt4': 'val4'}])
        matcher = self.m_request.get(expected_uri, text=fake_vms)

        self.client.get_node_vms_conf(node_id)

        self.assertTrue(matcher.called)

    def test_node_vms_create(self):
        config = [{'id': 1, 'opt2': 'val2'},
                  {'id': 2, 'opt4': 'val4'}]
        node_id = 42

        expected_uri = "/api/v1/nodes/{0}/vms_conf/".format(node_id)
        expected_body = json.dumps({'vms_conf': config})

        matcher = self.m_request.put(expected_uri,
                                     text=json.dumps(expected_body))

        self.client.node_vms_create(node_id, config)

        self.assertTrue(matcher.called)
        self.assertEqual(expected_body, matcher.last_request.body)

    def test_node_set_hostname(self):
        node_id = 42
        hostname = 'test-name'
        data = {"hostname": hostname}
        expected_uri = self.get_object_uri(self.res_uri, node_id)

        matcher = self.m_request.put(expected_uri,
                                     text=json.dumps(data))

        self.client.update(node_id, **data)

        self.assertTrue(matcher.called)
        self.assertEqual(data, matcher.last_request.json())
