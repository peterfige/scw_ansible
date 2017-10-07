import os
import json
import argparse
from scaleway.apis import ComputeAPI


class ScwServer(object):
    def __init__(self, api_url):
        self.api = ComputeAPI(auth_token=os.environ['SCW_TOKEN'], base_url=api_url)
        self.session = self.api.make_requests_session()

    def get_servers(self, uri="/servers"):
        response = self.session.request(
            "GET", "{base}{uri}".format(
                base=self.api.base_url,
                uri=uri
            )
        )
        for item in response.json()["servers"]:
            yield item
        if 'next' in response.links:
            for item in self.get_servers(response.links['next']['url']):
                yield item


class ScwAnsible(object):
    DESTINATION_VARIABLE_PUBLIC_IP = 'public_ip'
    DESTINATION_VARIABLE_PRIVATE_IP = 'private_ip'

    def __init__(self):
        args = self.parse_args()

        region = self.get_region()
        self.destination_variable = self.get_destination_variable()

        self.hostgroups = {'_meta': {'hostvars': {}}}

        if args.host is not None:
            print json.dumps({})
        else:
            scw = ScwServer("https://cp-{}.scaleway.com".format(region))
            for server in scw.get_servers():
                name = server.get('name')
                if server.get('state') != 'running':
                    continue
                var = {}

                ansible_ssh_host = self.get_ansible_ssh_host(server)

                if ansible_ssh_host is None:
                    continue

                self.add_to_groups(server, ansible_ssh_host)
                self.add_key_value_pairs(server, var)

                var['ansible_ssh_host'] = ansible_ssh_host
                if ('public_ip' not in server) or (server.get('public_ip') is None):
                    var['ansible_ssh_host'] = server.get('private_ip')
                else:
                    var['ansible_ssh_host'] = server.get('public_ip').get('address')
                var['scw'] = server
                self.hostgroups['_meta']['hostvars'][name] = var

        if args.list:
            print json.dumps(self.hostgroups, indent=2)

        if args.cssh:
            for group, values in self.hostgroups.iteritems():
                if group == '_meta':
                    continue
                list_hosts = ["root@{0}".format(host) for host in values['hosts']]
                print "{0} = {1}".format(group, " ".join(list_hosts))

    @staticmethod
    def add_key_value_pairs(server, var):
        for tag in server.get('tags'):

            if tag.find(':') == -1:
                continue

            # tags formed as <key>:<value> are added as ansible variables
            (key, value) = tag.split(':', 1)
            var[key] = value

    def add_to_groups(self, server, ansible_ssh_host):
        for tag in server.get('tags'):

            if tag.find(':') == -1:
                # each tag without ':' forms a group on its own
                self.add_to_group('tag_' + tag, ansible_ssh_host)
            else:
                # tags formed as environment:<something> or ansible:<something> are added to group <something>
                (key, value) = tag.split(':', 1)
                if key == 'environment' or key == 'ansible':
                    self.add_to_group(value, ansible_ssh_host)

        self.add_to_group('commercial_type_' + server['commercial_type'], ansible_ssh_host)
        self.add_to_group('arch_' + server['arch'], ansible_ssh_host)
        self.add_to_group('hostname_' + server['hostname'], ansible_ssh_host)
        self.add_to_group('name_' + server['name'], ansible_ssh_host)
        self.add_to_group('security_group_' + server['security_group']['name'], ansible_ssh_host)

    def add_to_group(self, group, ansible_ssh_host):
        if group not in self.hostgroups:
            self.hostgroups[group] = {'hosts': []}
        self.hostgroups[group]['hosts'].append(ansible_ssh_host)

    def get_ansible_ssh_host(self, server):
        if self.destination_variable == self.DESTINATION_VARIABLE_PRIVATE_IP:
            if 'private_ip' not in server or server.get('private_ip') is None:
                return None
            return server.get('private_ip')
        if self.destination_variable == self.DESTINATION_VARIABLE_PUBLIC_IP:
            if 'public_ip' not in server or server.get('public_ip') is None:
                return None
            return server.get('public_ip').get('address')
        raise ValueError('Don\'t know how to handle destination_variable setting', self.destination_variable)

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="SCW inventory")
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--cssh', action='store_true')
        parser.add_argument('--host')
        return parser.parse_args()

    @staticmethod
    def get_region():
        if 'SCW_REGION' in os.environ:
            region = os.environ['SCW_REGION']
        else:
            region = 'par1'
        return region

    def get_destination_variable(self):
        if 'SCW_DESTINATION_VARIABLE' in os.environ:
            return os.environ['SCW_DESTINATION_VARIABLE']
        else:
            return self.DESTINATION_VARIABLE_PUBLIC_IP


def main():
    ScwAnsible()


if __name__ == '__main__':
    main()
