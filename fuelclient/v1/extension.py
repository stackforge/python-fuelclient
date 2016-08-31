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

from fuelclient import objects
from fuelclient.v1 import base_v1


class ExtensionClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Extension

    def get_extensions(self, environment_id):
        ext = self._entity_wrapper(environment_id)
        return ext.get_env_extensions()

    def set_extensions(self, environment_id, extensions):
        ext = self._entity_wrapper(environment_id)
        return ext.set_env_extensions(extensions)

    def enable_extensions(self, environment_id, extensions):
        exts = self.get_extensions(environment_id)
        enabled_exts = set(exts + extensions)
        return self.set_extensions(environment_id, enabled_exts)

    def disable_extensions(self, environment_id, extensions):
        exts = self.get_extensions(environment_id)
        enabled_exts = set(exts) - set(extensions)
        return self.set_extensions(environment_id, enabled_exts)


def get_client(connection):
    return ExtensionClient(connection)