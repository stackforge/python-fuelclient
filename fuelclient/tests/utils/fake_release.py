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


def get_fake_attributes_metadata(repos=None):
    return {
        'editable': {
            'repo_setup': {
                'repos': {
                    'value': repos or [
                        {
                            'name': 'upstream',
                            'type': 'deb',
                            'uri': 'fake_upstream_uri',
                            'suite': 'trusty',
                            'section': 'main restricted',
                            'priority': 1000
                        },
                        {
                            'name': 'mos',
                            'type': 'deb',
                            'uri': 'fake_mos_uri',
                            'suite': 'mos',
                            'section': 'main restricted',
                            'priority': 1050
                        }
                    ]
                }
            }
        }
    }


def get_fake_release(release_id=None, name=None, state=None,
                     operating_system=None, version=None, repos=None):
    """Create a random fake release

    Returns the serialized and parametrized representation of a dumped Fuel
    release. Represents the average amount of data.

    """
    return {
        'id': release_id or 1,
        'name': name or 'Mitaka on Ubuntu 14.04',
        'state': state or 'available',
        'operating_system': operating_system or 'environment',
        'version': version or 'mitaka-9.0',
        'attributes_metadata': get_fake_attributes_metadata(repos=repos),
    }


def get_fake_releases(release_count, **kwargs):
    """Create a random fake release list."""
    return [get_fake_release(release_id=i, **kwargs)
            for i in range(1, release_count + 1)]


def get_fake_release_component(name=None, requires=None, incompatible=None,
                               compatible=None, default=None):
    """Create a random fake component of release

    Returns the serialized and parametrized representation of a dumped Fuel
    component of release. Represents the average amount of data.

    """
    return {
        'name': name or 'network:neutron:ml2:vlan',
        'description':
            'dialog.create_cluster_wizard.network.neutron_vlan_description',
        'weight': 5,
        'requires': requires,
        'incompatible': incompatible,
        'compatible': compatible,
        'default': default,
        'label': 'common.network.neutron_vlan',
    }


def get_fake_release_components(component_count, **kwargs):
    """Create a random fake list of release components."""
    return [get_fake_release_component(**kwargs)
            for _ in range(component_count)]
