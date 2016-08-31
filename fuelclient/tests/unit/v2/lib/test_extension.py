# -*- coding: utf-8 -*-
#
#    Copyright 2016 Mirantis, Inc.
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

import fuelclient
from fuelclient.tests.unit.v2.lib import test_api
from fuelclient.tests import utils


class TestExtensionFacade(test_api.BaseLibTest):

    def setUp(self):
        super(TestExtensionFacade, self).setUp()

        self.version = 'v1'
        self.res_uri = '/api/{version}/extensions/'.format(
            version=self.version)
        self.res_env_uri = '/api/{version}/clusters/'.format(
            version=self.version)
        self.fake_ext = u'fake_ext1'
        self.fake_extension = utils.get_fake_extension(self.fake_ext)
        self.fake_extensions = utils.get_fake_extensions(10)
        self.fake_env_extensions = utils.get_fake_env_extensions()

        self.client = fuelclient.get_client('extension', self.version)

    def test_extension_list(self):
        expected_uri = self.get_object_uri(self.res_uri, '', '')
        matcher = self.m_request.get(expected_uri, json=self.fake_extensions)
        self.client.get_all()

        self.assertTrue(matcher.called)

    def test_env_extension_list(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_env_uri, env_id,
                                           '/extensions/')
        matcher = self.m_request.get(expected_uri,
                                     json=self.fake_env_extensions)
        self.client.get_extensions(env_id)

        self.assertTrue(matcher.called)

    def test_env_extension_enable(self):
        env_id = 42
        self.fake_ext = u'fake_ext4'
        expected_uri = self.get_object_uri(self.res_env_uri, env_id,
                                           '/extensions/')
        get_matcher = self.m_request.get(expected_uri,
                                         json=self.fake_env_extensions)
        put_matcher = self.m_request.put(expected_uri, json=[self.fake_ext])

        self.client.enable_extensions(env_id, [self.fake_ext])

        self.assertTrue(get_matcher.called)
        self.assertTrue(put_matcher.called)
        self.assertIn(self.fake_ext, put_matcher.last_request.json())

    def test_env_extension_disable(self):
        env_id = 42
        expected_uri = self.get_object_uri(self.res_env_uri, env_id,
                                           '/extensions/')
        get_matcher = self.m_request.get(expected_uri,
                                         json=self.fake_env_extensions)
        put_matcher = self.m_request.put(expected_uri, json=[self.fake_ext])

        self.client.disable_extensions(env_id, [self.fake_ext])

        self.assertTrue(get_matcher.called)
        self.assertTrue(put_matcher.called)
        self.assertNotIn(self.fake_ext, put_matcher.last_request.json())
