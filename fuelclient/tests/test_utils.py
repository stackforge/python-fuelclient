# -*- coding: utf-8 -*-
#
#    Copyright 2014 Mirantis, Inc.
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

import os

import mock

from fuelclient.tests import base
from fuelclient import utils


class TestUtils(base.UnitTestCase):

    @mock.patch('fuelclient.cli.utils.os.walk')
    def test_iterfiles(self, mwalk):
        mwalk.return_value = [
            ('/some_directory/', [], ['valid.yaml', 'invalid.yml'])]

        pattern = '*.yaml'
        directory = '/some_directory'

        expected_result = [os.path.join(directory, 'valid.yaml')]
        files = list(utils.iterfiles(directory, pattern))

        mwalk.assert_called_once_with(directory)
        self.assertEqual(expected_result, files)
