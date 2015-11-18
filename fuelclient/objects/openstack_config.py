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

import six
import urllib

from fuelclient.objects.base import BaseObject


class OpenstackConfig(BaseObject):

    class_api_path = 'openstack-config/'
    instance_api_path = 'openstack-config/{0}/'
    execute_api_path = 'openstack-config/execute/'

    @classmethod
    def _prepare_params(cls, filters):
        return dict((k, v) for k, v in six.iteritems(filters) if v is not None)

    @classmethod
    def create(cls, **kwargs):
        params = cls._prepare_params(kwargs)
        data = cls.connection.post_request(cls.class_api_path, params)
        return cls.init_with_data(data)

    def delete(self):
        return self.connection.delete_request(
            self.instance_api_path.format(self.id))

    @classmethod
    def execute(cls, **kwargs):
        params = cls._prepare_params(kwargs)
        return cls.connection.put_request(cls.execute_api_path, params)

    @classmethod
    def get_all_filtered_data(cls, **kwargs):
        url = cls.class_api_path
        query = urllib.urlencode(kwargs)
        if query:
            url = '{0}?{1}'.format(url, query)

        return cls.connection.get_request(url)

