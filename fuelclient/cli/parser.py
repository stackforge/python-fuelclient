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

import argparse
import sys

from fuelclient.cli.actions import actions
from fuelclient.cli.arguments import substitutions
from fuelclient.cli.error import exceptions_decorator
from fuelclient.cli.error import ParserException
from fuelclient.cli.serializers import Serializer
from fuelclient import profiler


# TODO(aroma): remove this class when all commands will be moved to cliff
class FuelArgumentParser(argparse.ArgumentParser):
    """Designs to provide help string for old commands."""

    def format_help(self):
        """Builds summirized help only for subparsers."""
        formatter = self._get_formatter()

        for action_group in self._action_groups:
            if action_group.title == 'Namespaces':
                formatter.start_section(action_group.title)
                formatter.add_text(action_group.description)
                formatter.add_arguments(action_group._group_actions)
                formatter.end_section()

            elif action_group.title == 'optional arguments':
                # instantiate new formatter to keep optional args separately
                # from help string for subcommands
                formatter_for_opt_args = self._get_formatter()
                formatter_for_opt_args.start_section(action_group.title)
                formatter_for_opt_args.add_text(action_group.description)

                # the parser isntance has optional argument group attached
                # in order to make possible formatting action groups which
                # belong to different parsers using one formatter

                # also remove help action from old version parser to avoid
                # it apperance in help message
                #action_group_without_help_action = \
                #    filter(lambda a: not isinstance(a, argparse._HelpAction),
                #           action_group._group_actions)

                # formatter_for_opt_args.add_arguments(
                #     action_group_without_help_action +
                #     self.new_action_group._group_actions)

                formatter_for_opt_args.end_section()
                # save for further accessing where it is needed
                self.opt_args_help = formatter_for_opt_args.format_help()

        return formatter.format_help()


class Parser:
    """Parser for old commands' set. Will be removed after
    moving system to cliff
    """
    def __init__(self, argv):
        self.args = argv
        self.parser = FuelArgumentParser(
            usage="""
            Configuration for client you can find in
            /etc/fuel/client/config.yaml. If you don't have this file please
            create it i.e.:
            "SERVER_ADDRESS": "127.0.0.1",
            "LISTEN_PORT": "8000",
            "KEYSTONE_USER": "admin",
            "KEYSTONE_PASS": "admin"

            fuel [optional args] <namespace> [action] [flags]"""
        )
        self.subcommands_parsers = []
        self.universal_flags = []
        self.credential_flags = []
        self.subparsers = self.parser.add_subparsers(
            title="Namespaces",
            metavar="",
            dest="action",
            help='actions',
            parser_class=argparse.ArgumentParser
        )
        self.generate_actions()
        self.add_keystone_credentials_args()
        self.add_serializers_args()

    def generate_actions(self):
        for action, action_object in actions.iteritems():
            action_parser = self.subparsers.add_parser(
                action,
                prog="fuel {0}".format(action),
                help=action_object.__doc__,
                formatter_class=argparse.RawTextHelpFormatter,
                epilog=action_object.examples
            )
            for argument in action_object.args:
                if isinstance(argument, dict):
                    action_parser.add_argument(
                        *argument["args"],
                        **argument["params"]
                    )
                elif isinstance(argument, tuple):
                    required = argument[0]
                    group = action_parser.add_mutually_exclusive_group(
                        required=required)
                    for argument_in_group in argument[1:]:
                        group.add_argument(
                            *argument_in_group["args"],
                            **argument_in_group["params"]
                        )
            self.subcommands_parsers.append(action_parser)

    def parse(self):
        self.prepare_args()
        if len(self.args) < 2:
            self.parser.print_help()
            sys.exit(0)
        parsed_params, _ = self.parser.parse_known_args(self.args[1:])
        if parsed_params.action not in actions:
            self.parser.print_help()
            sys.exit(0)

        if profiler.profiling_enabled():
            handler_name = parsed_params.action
            method_name = ''.join([method for method in parsed_params.__dict__
                                   if getattr(parsed_params, method) is True])
            prof = profiler.Profiler(method_name, handler_name)

        actions[parsed_params.action].action_func(parsed_params)

        if profiler.profiling_enabled():
            prof.save_data()

    def add_serializers_args(self):
        for format_name in Serializer.serializers.keys():
            serialization_flag = "--{0}".format(format_name)
            self.universal_flags.append(serialization_flag)
            self.parser.add_argument(
                serialization_flag,
                dest=format_name,
                action="store_true",
                help="prints only {0} to stdout".format(format_name),
                default=False
            )

    def add_keystone_credentials_args(self):
        self.credential_flags.append('--user')
        self.credential_flags.append('--password')
        self.credential_flags.append('--tenant')
        self.parser.add_argument(
            "--user",
            dest="user",
            type=str,
            help="credentials for keystone authentication user",
            default=None
        )
        self.parser.add_argument(
            "--password",
            dest="password",
            type=str,
            help="credentials for keystone authentication password",
            default=None
        )
        self.parser.add_argument(
            "--tenant",
            dest="tenant",
            type=str,
            help="credentials for keystone authentication tenant",
            default="admin"
        )

    def prepare_args(self):
        # replace some args from dict substitutions
        self.args = map(
            lambda x: substitutions.get(x, x),
            self.args
        )

        # move general used flags before actions, otherwise they will be used
        # as a part of action by action_generator
        for flag in self.credential_flags:
            self.move_argument_before_action(flag)

        for flag in self.universal_flags:
            self.move_argument_before_action(flag, has_value=False)

        self.move_argument_after_action("--env",)

    def move_argument_before_action(self, flag, has_value=True):
        """We need to move general argument before action, we use them
        not directly in action but in APIClient.
        """
        for arg in self.args:
            if flag in arg:
                if "=" in arg or not has_value:
                    index_of_flag = self.args.index(arg)
                    flag = self.args.pop(index_of_flag)
                    self.args.insert(1, flag)
                else:
                    try:
                        index_of_flag = self.args.index(arg)
                        flag = self.args.pop(index_of_flag)
                        value = self.args.pop(index_of_flag)
                        self.args.insert(1, value)
                        self.args.insert(1, flag)
                    except IndexError:
                            raise ParserException(
                                'Corresponding value must follow "{0}" flag'
                                .format(arg)
                            )
                    break

    def move_argument_after_action(self, flag):
        for arg in self.args:
            if flag in arg:
                # if declaration with '=' sign (e.g. --env-id=1)
                if "=" in arg:
                    index_of_flag = self.args.index(arg)
                    flag = self.args.pop(index_of_flag)
                    self.args.append(flag)
                else:
                    try:
                        index_of_flag = self.args.index(arg)
                        self.args.pop(index_of_flag)
                        flag = self.args.pop(index_of_flag)
                        self.args.append(arg)
                        self.args.append(flag)
                    except IndexError:
                        raise ParserException(
                            'Corresponding value must follow "{0}" flag'
                            .format(arg)
                        )
                break


def get_parser(argv=sys.argv):
    return Parser(argv)


@exceptions_decorator
def main(argv=sys.argv):
    return get_parser(argv).parse()
