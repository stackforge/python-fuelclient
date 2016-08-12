# -*- coding: utf-8 -*-
#
#    Copyright 2016 Vitalii Kulanov
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

from fuelclient import objects
from fuelclient.v1 import base_v1


class SnapshotClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.SnapshotTask

    def create_snapshot(self, config):
        return self._entity_wrapper.start_snapshot_task(config)

    def get_default_config(self):
        return self._entity_wrapper.get_default_config()


def get_client(connection):
    return SnapshotClient(connection)
