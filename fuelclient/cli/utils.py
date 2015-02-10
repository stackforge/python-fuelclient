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

from fuelclient.cli import error


def iterfiles(dir_path, file_patterns):
    """Returns generator where each item is a path to file, that satisfies
    file_patterns condtion

    :param dir_path: path to directory, e.g /etc/puppet/
    :param file_patterns: iterable with file name, e.g (tasks.yaml,)
    """
    for root, dirs, file_names in os.walk(dir_path):
        for file_name in file_names:
            if file_name in file_patterns:
                yield os.path.join(root, file_name)


def render_graph(input_path, output_path):
    """Renders DOT graph using pydot or pygraphviz depending on their presence.

    If none of the libraries is available and are fully functional it is not
    possible to render graphs.

    :param input_path: path to the file with DOT graph
    :param output_path: path to the rendered graph
    """
    render = None
    try:
        import pydot

        def render(input_path, output_path):
            graph = pydot.graph_from_dot_file(input_path)
            if not graph:
                raise error.BadDataException(
                    "File {0} do not contains graph in DOT format".format(
                        input_path))
            try:
                graph.write_png(output_path)
            except pydot.InvocationException as e:
                raise error.WrongEnvironmentError(
                    "There was an error with rendering graph:\n{0}".format(e))
    except ImportError:
        try:
            import pygraphviz as pgv

            def render(input_path, output_path):
                graph = pgv.AGraph(input_path)
                graph.draw(output_path, prog='dot', format='png')
        except ImportError:
            raise error.WrongEnvironmentError(
                "This action require Graphviz installed toghether with "
                "'pydot' or 'pygraphviz' Python library")

    return render(input_path, output_path)
