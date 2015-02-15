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

from cliff import help as cliff_help

from fuelclient.cli import parser as obsolete_parser


class HelpAction(cliff_help.HelpAction):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.

    The reason for the class redefinition - customize help message
    processing so that it contains help not only for cliff defined
    commands but also for old code ones.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        app = self.default

        old_parser = obsolete_parser.get_parser()

        opt_args_action_group = [
            action_group for action_group in old_parser.parser._action_groups
            if action_group.title == 'optional arguments'
        ].pop()

        old_parser.parser.new_action_group = opt_args_action_group

        old_cmds_help = old_parser.parser.format_help()
        old_opt_args_help = old_parser.parser.opt_args_help

        # print help for optional args: both new and old version of client
        app.stdout.write(old_opt_args_help)

        try:
            super(HelpAction, self).__call__(parser, namespace,
                                             values, option_string)
        finally:
            # write help for old version of code
            app.stdout.write('\n' + old_cmds_help)
