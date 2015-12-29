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

from fuelclient.cli.actions.base import Action
import fuelclient.cli.arguments as Args
from fuelclient.objects.environment import Environment


class VIPAction(Action):
    """Download or upload VIP settings of specific environments.
    """
    action_name = "vip"
    acceptable_keys = ("id", "upload", "download", "network", "network-role",)

    def __init__(self):
        super(VIPAction, self).__init__()
        self.args = (
            Args.get_env_arg(required=True),
            Args.get_file_arg("File with vip data."),
            Args.get_upload_file_arg("Upload changed VIP configuration "
                                     "from given file"),
            Args.get_download_arg("Download VIP configuration"),
            Args.get_ip_arg("Ip address entity identifier"),
            Args.get_network_id_arg("Network identifier"),
            Args.get_network_role_arg("Network role string"),
            Args.get_dir_arg(
                "Select directory to which download VIP configuration"),
        )
        self.flag_func_map = (
            ("upload", self.upload),
            ("download", self.download)
        )

    def upload(self, params):
        """To upload VIP configuration from some
           directory for some environment:
                fuel --env 1 vip --upload --file vip.yaml
        """
        env = Environment(params.env)
        vips_data = env.read_vips_data_from_file(
            file_path=params.upload,
            serializer=self.serializer
        )
        env.set_vips_data(vips_data)
        print("VIP configuration uploaded.")

    def download(self, params):
        """To download VIP configuration in this
           directory for some environment:
                fuel --env 1 vip --download --dir ./vips_data
        """
        env = Environment(params.env)
        vips_data = env.get_vips_data(
            ip_addr_id=params.ip,
            network=getattr(params, 'network'),
            network_role=getattr(params, 'network-role')
        )
        vips_data_file_path = env.write_vips_data(
            vips_data,
            directory=params.dir,
            serializer=self.serializer
        )
        print(
            "VIP configuration for environment with id={0}"
            " downloaded to {1}".format(env.id, vips_data_file_path)
        )