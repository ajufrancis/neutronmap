# -*- coding: utf-8 -*-

import json

from abc import ABCMeta, abstractmethod
from flask import current_app as app
from neutronclient.neutron import client as neutron_client
from novaclient import client as nova_client


class Network(object):
    """A graph node that represents a network."""

    def __init__(self, network):
        self.id = network.get('id')
        self.name = network.get('name')
        self.router_external = network.get('router:external')
        self.subnets = []

    def to_dict(self):
        d = {}
        d['type'] = 'external' if self.router_external else 'network'
        d['html'] = self.html
        return d

    @property
    def html(self):
        html = []
        html.extend(['<strong>Network:</strong>',
                     'id: ' + self.id,
                     'name: ' + self.name,
                     'router external: ' + str(self.router_external)])

        return ('<br>'.join(html) + '<br>' +
                '<br>'.join([s.html for s in self.subnets]))


class Subnet(object):
    """A Neutron subnet representation."""

    def __init__(self, subnet):
        self.id = subnet.get('id')
        self.name = subnet.get('name')
        self.cidr = subnet.get('cidr')
        self.gateway = subnet.get('gateway_ip')
        self.pools = subnet.get('allocation_pools')
        self.nameservers = subnet.get('dns_nameservers')

        # The network id is used to map the subnet to its network
        self.network_id = subnet.get('network_id')

    @property
    def html(self):
        html = []
        html.extend(['<strong>Subnet:</strong>',
                     'id: ' + self.id,
                     'name: ' + self.name,
                     'cidr: ' + self.cidr,
                     'gateway ip: ' + self.gateway])

        for pool in self.pools:
            html.append('pool: ' + pool['start'] + '/' + pool['end'])
        html.extend(['dns: ' + ns for ns in self.nameservers])

        return '<br>'.join(html)


class Router(object):
    """A graph node that represents a router."""

    def __init__(self, router):
        self.id = router.get('id')
        self.name = router.get('name')
        self.gateway = router.get('external_gateway_info')
        self.ports = []

    def to_dict(self):
        d = {}
        d['type'] = 'router'
        d['html'] = self.html
        return d

    @property
    def html(self):
        html = []
        html.extend(['<strong>Router:</strong>',
                     'id: ' + self.id,
                     'name: ' + self.name])
        if self.gateway:
            html.extend(['<strong>External gateway info:</strong>',
                         'network id: ' + self.gateway['network_id'],
                         'enable snat: ' + str(self.gateway['enable_snat'])])

        return ('<br>'.join(html) + '<br>' +
                '<br>'.join([p.html for p in self.ports]))


class Port(object):
    """A Neutron port representation."""

    def __init__(self, port):
        self.id = port.get('id')
        self.network_id = port.get('network_id')
        self.mac_address = port.get('mac_address')
        self.fixed_ips = port.get('fixed_ips')

        # Attributes used to map the port to the
        # relevant device, and to set the vif name
        self.device_id = port.get('device_id')
        self.device_owner = port.get('device_owner')

    @property
    def html(self):
        html = []
        html.extend(['<strong>Interface:</strong>',
                     'name: ' + self.vif,
                     'network id: ' + self.network_id,
                     'mac: ' + self.mac_address])

        ips = [fixed_ip['ip_address'] for fixed_ip in self.fixed_ips]
        html.append('ips: ' + ', '.join(ips))

        return '<br>'.join(html)

    @property
    def vif(self):
        prefixes = {'network:router_interface': 'qr-',
                    'network:router_gateway': 'qg-',
                    'network:floatingip': 'qg-',
                    'network:dhcp': 'tap',
                    'compute:None': 'tap'}

        return prefixes[self.device_owner] + self.id[:11]


class DhcpPort(object):
    """A graph node that represents the DHCP device binded to a subnet."""

    def __init__(self, port):
        self.id = port.get('id')
        self.network_id = port.get('network_id')
        self.mac_address = port.get('mac_address')
        self.fixed_ips = port.get('fixed_ips')
        self.device_id = port.get('device_id')

    def to_dict(self):
        d = {}
        d['type'] = 'dhcp'
        d['html'] = self.html
        return d

    @property
    def html(self):
        html = []
        html.extend(['<strong>DHCP device:</strong>',
                     'id: ' + self.device_id,
                     '<strong>Interface:</strong>',
                     'name: ' + self.vif,
                     'network id: ' + self.network_id,
                     'mac: ' + self.mac_address])

        ips = [fixed_ip['ip_address'] for fixed_ip in self.fixed_ips]
        html.append('ips: ' + ', '.join(ips))

        return '<br>'.join(html)

    @property
    def vif(self):
        return 'tap' + self.id[:11]


class NovaInstance(object):
    """A graph node that represents a compute instance."""

    def __init__(self, instance):
        self.id = instance.id
        self.name = instance.name
        self.addresses = instance.addresses
        self.ports = []

    def to_dict(self):
        d = {}
        d['type'] = 'vm'
        d['html'] = self.html
        return d

    @property
    def html(self):
        html = []
        html.extend(['<strong>Nova instance:</strong>',
                     'id: ' + self.id,
                     'name: ' + self.name])
        # Floating ip list
        ips = []
        for net in self.addresses:
            # Get an address list per network
            addresses = self.addresses[net]
            [ips.append('%s (%s)' % (a['addr'], a['OS-EXT-IPS-MAC:mac_addr']))
             for a in addresses if a['OS-EXT-IPS:type'] == 'floating']

        return ('<br>'.join(html) + '<br>' +
                '<br>'.join([p.html for p in self.ports]) + '<br>' +
                '<strong>Floating ips:</strong><br>' + '<br>'.join(ips))


class Topology(object):
    """A graph representation of a Neutron topology for a specific tenant."""

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self._nova = nova_client.Client('2', *args)
        self._neutron = neutron_client.Client('2.0', **kwargs)
        self._data = {}
        self._build()

    def _build(self):
        """Extract data and map the relevant elements together."""

        # Networks
        networks = self._neutron.list_networks().get('networks')
        self._data['networks'] = [Network(item) for item in networks]

        # Subnets
        subnets = self._neutron.list_subnets().get('subnets')
        self._data['subnets'] = [Subnet(item) for item in subnets]

        # Routers
        routers = self._neutron.list_routers().get('routers')
        self._data['routers'] = [Router(item) for item in routers]

        # Ports
        ports = self._neutron.list_ports().get('ports')
        self._data['ports'] = [Port(item) for item in ports]

        # DHCP devices
        self._data['dhcp_ports'] = \
            [DhcpPort(item) for item in ports
             if item.get('device_owner') == 'network:dhcp']

        # Nova instances
        vms = self._nova.servers.list()
        self._data['vms'] = [NovaInstance(item) for item in vms]

        # Subnet mapping
        for network in self._data['networks']:
            for subnet in self._data['subnets']:
                if subnet.network_id == network.id:
                    network.subnets.append(subnet)

        # Router interface mapping
        for router in self._data['routers']:
            for port in self._data['ports']:
                if port.device_id == router.id:
                    router.ports.append(port)

        # Nova instance interface mapping
        for vm in self._data['vms']:
            for port in self._data['ports']:
                if port.device_id == vm.id:
                    vm.ports.append(port)

    @abstractmethod
    def dumps():
        """Returns a JSON representation of the Neutron topology."""
        return


class LogicalTopology(Topology):
    """Returns a logical view of the Neutron network."""

    def __init__(self, *args, **kwargs):
        super(LogicalTopology, self).__init__(*args, **kwargs)

    def dumps(self):
        # We keep the IDs of the relevant elements
        # in order to generate the links
        ids = []
        nodes = []
        links = []

        for network in self._data['networks']:
            ids.append(network.id)
            nodes.append(network.to_dict())

        for router in self._data['routers']:
            ids.append(router.id)
            nodes.append(router.to_dict())

        for vm in self._data['vms']:
            ids.append(vm.id)
            nodes.append(vm.to_dict())

        for dhcp_port in self._data['dhcp_ports']:
            ids.append(dhcp_port.device_id)
            nodes.append(dhcp_port.to_dict())

        # For each router with an external gateway, we
        # add a link toward the external network
        for router in self._data['routers']:
            if router.gateway:
                source = ids.index(router.id)
                target = ids.index(router.gateway.get('network_id'))
                links.append({'source': source, 'target': target})

        # Links between networks and devices
        for port in self._data['ports']:
            if port.device_owner in ('compute:None',
                                     'network:dhcp',
                                     'network:router_interface'):
                source = ids.index(port.device_id)
                target = ids.index(port.network_id)
                links.append({'source': source, 'target': target})

        return json.dumps({'nodes': nodes, 'links': links})


class PhysicalTopology(Topology):
    pass
