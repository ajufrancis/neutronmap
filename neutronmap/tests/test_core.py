# -*- coding: utf-8 -*-

import json
import mock
import unittest

from neutronmap import core

DEMO_SUB_RAW = {
    u'name': u'',
    u'enable_dhcp': True,
    u'network_id': u'00e871de-e297-4ac1-8270-241daefd5daf',
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'dns_nameservers': [u'8.8.8.8'],
    u'allocation_pools': [
        {
            u'start': u'10.5.5.1',
            u'end': u'10.5.5.253'
        }
    ],
    u'host_routes': [],
    u'ip_version': 4,
    u'gateway_ip': u'10.5.5.254',
    u'cidr': u'10.5.5.0/24',
    u'id': u'a2dee20c-9c52-41fd-95ce-580953f9b93a'
}

DEMO_NET_RAW = {
    u'status': u'ACTIVE',
    u'subnets': [u'a2dee20c-9c52-41fd-95ce-580953f9b93a'],
    u'name': u'demo-net',
    u'admin_state_up': True,
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'router:external': False,
    u'shared': False,
    u'id': u'00e871de-e297-4ac1-8270-241daefd5daf'
}

EXT_NET_RAW = {
    u'status': u'ACTIVE',
    u'subnets': [u'351d5210-dd84-40b4-a590-927c528f7394'],
    u'name': u'ext-net',
    u'admin_state_up': True,
    u'tenant_id': u'4515b04f663c403ba7402011e4a301d0',
    u'router:external': True,
    u'shared': False,
    u'id': u'2ca3fa80-e693-44ea-bc0c-5c030f1bd747'
}

ROUTER_PORT_RAW = {
    u'status': u'ACTIVE',
    u'name': u'',
    u'allowed_address_pairs': [],
    u'admin_state_up': True,
    u'network_id': u'00e871de-e297-4ac1-8270-241daefd5daf',
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'extra_dhcp_opts': [],
    u'device_owner': u'network:router_interface',
    u'mac_address': u'fa:16:3e:41:95:01',
    u'fixed_ips': [
        {
            u'subnet_id': u'a2dee20c-9c52-41fd-95ce-580953f9b93a',
            u'ip_address': u'10.5.5.254'
        }
    ],
    u'id': u'5bb24753-d826-486d-90e1-90f8df130f84',
    u'security_groups': [],
    u'device_id': u'a3628e26-3ee2-4cd7-bce1-b61d92b6b8a2'
}

ROUTER_RAW = {
    u'status': u'ACTIVE',
    u'external_gateway_info': {
        u'network_id': u'2ca3fa80-e693-44ea-bc0c-5c030f1bd747',
        u'enable_snat': True
    },
    u'name': u'ext-to-int',
    u'admin_state_up': True,
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'routes': [],
    u'id': u'a3628e26-3ee2-4cd7-bce1-b61d92b6b8a2'
}

DHCP_PORT_RAW = {
    u'status': u'ACTIVE',
    u'name': u'',
    u'allowed_address_pairs': [],
    u'admin_state_up': True,
    u'network_id': u'00e871de-e297-4ac1-8270-241daefd5daf',
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'extra_dhcp_opts': [],
    u'device_owner': u'network:dhcp',
    u'mac_address': u'fa:16:3e:31:1a:48',
    u'fixed_ips': [
        {
            u'subnet_id': u'a2dee20c-9c52-41fd-95ce-580953f9b93a',
            u'ip_address': u'10.5.5.2'
        }
    ],
    u'id': u'376830d1-95ec-4a77-a59c-efd85b49ac02',
    u'security_groups': [],
    u'device_id': u'dhcpd3377d3c-a0d1-5d71-9947-f17125c357bb-00e871de-e297-4ac'
                  '1-8270-241daefd5daf'
}

VM_PORT_RAW = {
    u'status': u'ACTIVE',
    u'name': u'',
    u'allowed_address_pairs': [],
    u'admin_state_up': True,
    u'network_id': u'00e871de-e297-4ac1-8270-241daefd5daf',
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'extra_dhcp_opts': [],
    u'device_owner': u'compute:None',
    u'mac_address': u'fa:16:3e:05:2f:7a',
    u'fixed_ips': [
        {
            u'subnet_id': u'a2dee20c-9c52-41fd-95ce-580953f9b93a',
            u'ip_address': u'10.5.5.1'
        }
    ],
    u'id': u'04ec9ade-5d37-4270-a323-0ff870cff1d4',
    u'security_groups': [u'e11b5f4a-de3a-4a75-b1f6-225a0304a89f'],
    u'device_id': u'bbf049ef-7a74-4668-8026-9c761be191eb'
}

VM_RAW = {
    u'OS-EXT-STS:task_state': None,
    u'addresses': {
        u'demo-net': [
            {
                u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:05:2f:7a',
                u'version': 4,
                u'addr': u'10.5.5.1',
                u'OS-EXT-IPS:type': u'fixed'
            },
            {
                u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:05:2f:7a',
                u'version': 4,
                u'addr': u'192.168.0.181',
                u'OS-EXT-IPS:type': u'floating'
            }
        ]
    },
    u'links': [
        {
            u'href': u'http://controller:8774/v2/c272f96891504bc4866525730796e'
            '6c5/servers/bbf049ef-7a74-4668-8026-9c761be191eb',
            u'rel': u'self'
        },
        {
            u'href': u'http://controller:8774/c272f96891504bc4866525730796e6c5'
                     '/servers/bbf049ef-7a74-4668-8026-9c761be191eb',
            u'rel': u'bookmark'
        }
    ],
    u'image': {
        u'id': u'54fd04b3-2adc-4fc4-be16-e2923a19dffc',
        u'links': [
            {u'href': u'http://controller:8774/c272f96891504bc4866525730796e6c'
                      '5/images/54fd04b3-2adc-4fc4-be16-e2923a19dffc',
             u'rel': u'bookmark'}
        ]
    },
    u'OS-EXT-STS:vm_state': u'stopped',
    u'OS-SRV-USG:launched_at': u'2014-04-12T17:04:28.000000',
    u'flavor': {
        u'id': u'1',
        u'links': [
            {
                u'href': u'http://controller:8774/c272f96891504bc4866525730796'
                'e6c5/flavors/1',
                u'rel': u'bookmark'
            }
        ]
    },
    u'id': u'bbf049ef-7a74-4668-8026-9c761be191eb',
    u'security_groups': [{u'name': u'default'}],
    u'user_id': u'd7e1d179eed14455a3ba44e5a5cf92a7',
    u'OS-DCF:diskConfig': u'MANUAL',
    u'accessIPv4': u'',
    u'accessIPv6': u'',
    u'OS-EXT-STS:power_state': 4,
    u'OS-EXT-AZ:availability_zone': u'nova',
    u'config_drive': u'',
    u'status': u'SHUTOFF',
    u'updated': u'2014-06-23T17:13:37Z',
    u'hostId': u'456ecc1ff4a2707a7cca0f5a25fec758847538a1383163e58d0be659',
    u'OS-SRV-USG:terminated_at': None,
    u'key_name': u'mykey',
    u'name': u'cirros1',
    u'created': u'2014-04-12T17:03:56Z',
    u'tenant_id': u'c272f96891504bc4866525730796e6c5',
    u'os-extended-volumes:volumes_attached': [],
    u'metadata': {}
}

DEMO_NET = {
    'status': 'ACTIVE',
    'subnets': [
        {
            'name': '',
            'dns_nameservers': ['8.8.8.8'],
            'id': 'a2dee20c-9c52-41fd-95ce-580953f9b93a',
            'allocation_pools': [
                {
                    'start': '10.5.5.1',
                    'end': '10.5.5.253'
                }
            ],
            'cidr': '10.5.5.0/24',
            'gateway_ip': '10.5.5.254'
        }
    ],
    'name': 'demo-net',
    'router_external': False,
    'type': 'network',
    'id': '00e871de-e297-4ac1-8270-241daefd5daf'
}

ROUTER = {
    'status': 'ACTIVE',
    'name': 'ext-to-int',
    'id': 'a3628e26-3ee2-4cd7-bce1-b61d92b6b8a2',
    'type': 'router',
    'external_gateway_info': {
        'network_id': '2ca3fa80-e693-44ea-bc0c-5c030f1bd747',
        'enable_snat': True
    },
    'ports': [
        {
            'network_id': '00e871de-e297-4ac1-8270-241daefd5daf',
            'status': 'ACTIVE',
            'vif': 'qr-5bb24753-d8',
            'ip_addresses': ['10.5.5.254'],
            'mac_address': 'fa:16:3e:41:95:01'
        }
    ]
}

DHCP = {
    'status': 'ACTIVE',
    'vif': 'tap376830d1-95',
    'network_id': '00e871de-e297-4ac1-8270-241daefd5daf',
    'ip_addresses': ['10.5.5.2'],
    'mac_address': 'fa:16:3e:31:1a:48',
    'type': 'dhcp',
    'device_id': 'dhcpd3377d3c-a0d1-5d71-9947-f17125c357bb-00e871de-e297-4ac1-'
                 '8270-241daefd5daf'
}

VM = {
    'ports': [
        {
            'network_id': '00e871de-e297-4ac1-8270-241daefd5daf',
            'status': 'ACTIVE',
            'vif': 'tap04ec9ade-5d',
            'ip_addresses': ['10.5.5.1'],
            'mac_address': 'fa:16:3e:05:2f:7a'
        }
    ],
    'floating_ips': {
        'demo-net': [
            ('192.168.0.181', 'fa:16:3e:05:2f:7a')
        ]
    },
    'type': 'vmoff',
    'id': 'bbf049ef-7a74-4668-8026-9c761be191eb',
    'name': 'cirros1',
    'status': 'SHUTOFF'
}

TOPOLOGY = {
    'nodes': [
        {
            'status': 'ACTIVE',
            'subnets': [
                {
                    'name': '',
                    'dns_nameservers': ['8.8.8.8'],
                    'id': 'a2dee20c-9c52-41fd-95ce-580953f9b93a',
                    'allocation_pools': [
                        {
                            'start': '10.5.5.1',
                            'end': '10.5.5.253'
                        }
                    ],
                    'cidr': '10.5.5.0/24',
                    'gateway_ip': '10.5.5.254'
                }
            ],
            'name': 'demo-net',
            'router_external': False,
            'type': 'network',
            'id': '00e871de-e297-4ac1-8270-241daefd5daf'
        },
        {
            'status': 'ACTIVE',
            'subnets': [],
            'name': 'ext-net',
            'router_external': True,
            'type': 'external',
            'id': '2ca3fa80-e693-44ea-bc0c-5c030f1bd747'
        },
        {
            'status': 'ACTIVE',
            'name': 'ext-to-int',
            'id': 'a3628e26-3ee2-4cd7-bce1-b61d92b6b8a2',
            'type': 'router',
            'external_gateway_info': {
                'network_id': '2ca3fa80-e693-44ea-bc0c-5c030f1bd747',
                'enable_snat': True
            },
            'ports': [
                {
                    'network_id': '00e871de-e297-4ac1-8270-241daefd5daf',
                    'status': 'ACTIVE',
                    'vif': 'qr-5bb24753-d8',
                    'ip_addresses': ['10.5.5.254'],
                    'mac_address': 'fa:16:3e:41:95:01'
                }
            ]
        },
        {
            'ports': [
                {
                    'network_id': '00e871de-e297-4ac1-8270-241daefd5daf',
                    'status': 'ACTIVE',
                    'vif': 'tap04ec9ade-5d',
                    'ip_addresses': ['10.5.5.1'],
                    'mac_address': 'fa:16:3e:05:2f:7a'
                }
            ],
            'floating_ips': {
                'demo-net': [('192.168.0.181', 'fa:16:3e:05:2f:7a')]
            },
            'type': 'vmoff',
            'id': 'bbf049ef-7a74-4668-8026-9c761be191eb',
            'name': 'cirros1',
            'status': 'SHUTOFF'
        },
        {
            'status': 'ACTIVE',
            'vif': 'tap376830d1-95',
            'network_id': '00e871de-e297-4ac1-8270-241daefd5daf',
            'ip_addresses': ['10.5.5.2'],
            'mac_address': 'fa:16:3e:31:1a:48',
            'type': 'dhcp',
            'device_id': 'dhcpd3377d3c-a0d1-5d71-9947-f17125c357bb-00e871de-e2'
                         '97-4ac1-8270-241daefd5daf'
        },
    ],
    'links': [
        {
            'source': 2,
            'target': 1
        },
        {
            'source': 2,
            'target': 0
        },
        {
            'source': 4,
            'target': 0
        },
        {
            'source': 3,
            'target': 0
        }
    ]
}


class TestCore(unittest.TestCase):

    def setUp(self):
        self.subnets = {'subnets': [DEMO_SUB_RAW]}
        self.networks = {'networks': [DEMO_NET_RAW, EXT_NET_RAW]}
        self.ports = {'ports': [ROUTER_PORT_RAW, DHCP_PORT_RAW, VM_PORT_RAW]}
        self.routers = {'routers': [ROUTER_RAW]}
        self.vms = (None, {'servers': [VM_RAW]})

    def test_network(self):
        subnet = core.Subnet(DEMO_SUB_RAW)
        network = core.Network(DEMO_NET_RAW)
        network.subnets = [subnet]
        self.assertDictEqual(network.data, DEMO_NET)

    def test_router(self):
        port = core.Port(ROUTER_PORT_RAW)
        router = core.Router(ROUTER_RAW)
        router.ports = [port]
        self.assertDictEqual(router.data, ROUTER)

    def test_dhcp(self):
        dhcp = core.DhcpPort(DHCP_PORT_RAW)
        self.assertDictEqual(dhcp.data, DHCP)

    def test_vm(self):
        port = core.Port(VM_PORT_RAW)
        vm = core.NovaInstance(VM_RAW)
        vm.ports = [port]
        self.assertDictEqual(vm.data, VM)

    def test_topology(self):
        topology = core.Topology()
        topology._neutron.list_subnets = mock.Mock(return_value=self.subnets)
        topology._neutron.list_networks = mock.Mock(return_value=self.networks)
        topology._neutron.list_ports = mock.Mock(return_value=self.ports)
        topology._neutron.list_routers = mock.Mock(return_value=self.routers)
        topology._nova.client.get = mock.Mock(return_value=self.vms)

        result = topology.build()
        expected = json.dumps(TOPOLOGY)

        self.assertDictEqual(json.loads(result), json.loads(expected))
