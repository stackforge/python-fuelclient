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

import os

import six

from fuelclient.cli import error
from fuelclient.cli.serializers import Serializer
from fuelclient.commands import base
from fuelclient.common import data_utils
from fuelclient import consts


class FileMethodsMixin(object):
    @classmethod
    def check_file_path(cls, file_path):
        if not os.path.exists(file_path):
            raise error.InvalidFileException(
                "File '{0}' doesn't exist.".format(file_path))

    @classmethod
    def check_dir(cls, directory):
        if not os.path.exists(directory):
            raise error.InvalidDirectoryException(
                "Directory '{0}' doesn't exist.".format(directory))
        if not os.path.isdir(directory):
            raise error.InvalidDirectoryException(
                "Error: '{0}' is not a directory.".format(directory))


class GraphUpload(base.BaseCommand, FileMethodsMixin):
    """Upload deployment graph configuration."""
    entity_name = 'graph'

    @classmethod
    def read_tasks_data_from_file(cls, file_path=None, serializer=None):
        """Read Tasks data from given path.

        :param file_path: path
        :type file_path: str
        :param serializer: serializer object
        :type serializer: object
        :return: data
        :rtype: list|object
        """
        cls.check_file_path(file_path)
        return (serializer or Serializer()).read_from_full_path(file_path)

    def get_parser(self, prog_name):
        parser = super(GraphUpload, self).get_parser(prog_name)
        graph_level = parser.add_mutually_exclusive_group(required=True)

        graph_level.add_argument('-e',
                                 '--env',
                                 type=int,
                                 required=False,
                                 help='Id of the environment')
        graph_level.add_argument('-r',
                                 '--release',
                                 type=int,
                                 required=False,
                                 help='Id of the release')
        graph_level.add_argument('-p',
                                 '--plugin',
                                 type=int,
                                 required=False,
                                 help='Id of the plugin')

        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Type of the deployment graph')
        parser.add_argument('-f',
                            '--file',
                            type=str,
                            required=True,
                            default=None,
                            help='YAML file that contains '
                                 'deployment graph data.')
        return parser

    def take_action(self, args):

        for parameter, graph_level in six.iteritems(
                consts.PARAMS_TO_GRAPH_CLASS_MAPPING):
            model_id = getattr(args, parameter)
            if model_id:
                self.client.upload(
                    data=self.read_tasks_data_from_file(args.file),
                    related_model=graph_level,
                    related_id=model_id,
                    graph_type=args.type
                )
                break

        self.app.stdout.write(
            "Deployment graph was uploaded from {0}\n".format(args.file)
        )


class GraphExecute(base.BaseCommand):
    """Start deployment with given graph type."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphExecute, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')
        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Type of the deployment graph')
        parser.add_argument('-n',
                            '--nodes',
                            type=int,
                            nargs='+',
                            required=False,
                            help='Ids of the nodes to use for deployment.')
        parser.add_argument('-d',
                            '--dry-run',
                            action="store_true",
                            required=False,
                            default=False,
                            help='Specifies to dry-run a deployment by '
                                 'configuring task executor to dump the '
                                 'deployment graph to a dot file.')
        return parser

    def take_action(self, args):
        result = self.client.execute(
            env_id=args.env,
            graph_type=args.type,
            nodes=args.nodes,
            dry_run=args.dry_run
        )
        msg = 'Deployment task with id {t} for the environment {e} ' \
              'has been started.\n'.format(t=result.data['id'],
                                           e=result.data['cluster'])
        self.app.stdout.write(msg)


class GraphDownload(base.BaseCommand):
    """Download deployment graph configuration."""
    entity_name = 'graph'

    def get_parser(self, prog_name):
        parser = super(GraphDownload, self).get_parser(prog_name)
        graph_level = parser.add_mutually_exclusive_group(required=True)

        graph_level.add_argument('-e',
                                 '--env',
                                 type=int,
                                 required=False,
                                 help='Id of the environment')

        graph_level.add_argument('-r',
                                 '--release',
                                 type=int,
                                 required=False,
                                 help='Id of the release')

        graph_level.add_argument('-p',
                                 '--plugin',
                                 type=int,
                                 required=False,
                                 help='Id of the plugin')

        # additional params for the env option
        cluster_level = parser.add_mutually_exclusive_group(required=False)
        cluster_level.add_argument('--merged-all',
                                   action="store_true",
                                   required=False,
                                   default=False,
                                   help='Download merged graph for the '
                                        'environment')
        cluster_level.add_argument('--merged-plugins',
                                   action="store_true",
                                   required=False,
                                   default=False,
                                   help='Download merged plugins graph for the'
                                        'environment')

        parser.add_argument('-t',
                            '--type',
                            type=str,
                            default=None,
                            required=False,
                            help='Graph type string')
        parser.add_argument('-f',
                            '--file',
                            type=str,
                            required=False,
                            default=None,
                            help='YAML file that contains tasks data.')
        return parser

    @classmethod
    def write_tasks_to_file(cls, tasks_data, file_path, serializer):
        serializer = serializer or Serializer()
        return serializer.write_to_full_path(
            file_path,
            tasks_data
        )

    def take_action(self, args):
        tasks_data = []
        default_file_name = 'graph'
        if args.env and (args.merged_all or args.merged_plugins):
            # if there is additional params for the env graph download
            if args.merged_plugins:
                default_file_name = 'graph_cluster_merged_plugins'
                self.app.stdout.write('WARNING: This tasks are merged from '
                                      'several graphs and not supposed to '
                                      'be uploaded back after editing until '
                                      'you are completely sure about what '
                                      'you are doing!\n')
                tasks_data = self.client.get_merged_plugins_tasks(
                    env_id=args.env,
                    graph_type=args.type)
            # args.merged_all flag is defined
            else:
                default_file_name = 'graph_cluster_merged_all'
                tasks_data = self.client.get_merged_cluster_tasks(
                    env_id=args.env,
                    graph_type=args.type)
        else:
            # get the tasks for the given model
            for parameter, graph_level in six.iteritems(
                    consts.PARAMS_TO_GRAPH_CLASS_MAPPING):
                model_id = getattr(args, parameter)
                if model_id:
                    default_file_name = 'graph_{}'.format(graph_level)
                    tasks_data = self.client.get_graph_for_model(
                        related_model=graph_level,
                        related_model_id=model_id,
                        graph_type=args.type
                    )[0].get('tasks', [])
                    break

        # write to file
        graph_data_file_path = self.write_tasks_to_file(
            tasks_data=tasks_data,
            file_path=args.file or default_file_name,
            serializer=Serializer()
        )

        self.app.stdout.write(
            "Tasks were downloaded to {0}\n".format(graph_data_file_path)
        )


class GraphList(base.BaseListCommand):
    """List deployment graphs."""
    entity_name = 'graph'
    columns = ("id",
               "name",
               "tasks",
               "relations")

    def get_parser(self, prog_name):
        parser = super(GraphList, self).get_parser(prog_name)
        parser.add_argument('-e',
                            '--env',
                            type=int,
                            required=True,
                            help='Id of the environment')
        return parser

    def take_action(self, parsed_args):
        data = self.client.list(
            env_id=parsed_args.env
        )
        # format fields
        for d in data:
            d['relations'] = "\n".join(
                'as "{type}" to {model}(ID={model_id})'
                .format(**r) for r in d['relations']
            )
            d['tasks'] = ', '.join(sorted(t['id'] for t in d['tasks']))
        data = data_utils.get_display_data_multi(self.columns, data)
        scolumn_ids = [self.columns.index(col)
                       for col in parsed_args.sort_columns]
        data.sort(key=lambda x: [x[scolumn_id] for scolumn_id in scolumn_ids])
        return self.columns, data
