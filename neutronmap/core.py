# -*- coding: utf-8 -*-

import json

from neutronclient.neutron import client as neutron_client
from novaclient import client as nova_client


class Network(object):
    """A graph node that represents a network."""

    def __init__(self, network):
        self.id = network.get('id')
        self.name = network.get('name')
        self.router_external = network.get('router:external')
        self.status = network.get('status')
        self.subnets = None

    def to_dict(self):
        attrs = ['id', 'name', 'router_external', 'status']
        d = {attr: getattr(self, attr) for attr in attrs}
        d['subnets'] = [subnet.to_dict() for subnet in self.subnets]
        d['type'] = 'external' if self.router_external else 'network'
        return d


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

    def to_dict(self):
        attrs = ['id', 'name', 'cidr', 'gateway', 'pools', 'nameservers']
        return {attr: getattr(self, attr) for attr in attrs}


class Router(object):
    """A graph node that represents a router."""

    def __init__(self, router):
        self.id = router.get('id')
        self.name = router.get('name')
        self.gateway = router.get('external_gateway_info')
        self.status = router.get('status')
        self.ports = None

    def to_dict(self):
        attrs = ['id', 'name', 'gateway', 'status']
        d = {attr: getattr(self, attr) for attr in attrs}
        d['ports'] = [port.to_dict() for port in self.ports]
        d['type'] = 'router'
        return d


class Port(object):
    """A Neutron port representation."""

    def __init__(self, port):
        self.id = port.get('id')
        self.network_id = port.get('network_id')
        self.mac_address = port.get('mac_address')
        self.fixed_ips = port.get('fixed_ips')
        self.status = port.get('status')

        # Attributes used to map the port to the
        # relevant device, and to set the vif name
        self.device_id = port.get('device_id')
        self.device_owner = port.get('device_owner')

    @property
    def vif(self):
        prefixes = {
            'network:router_interface': 'qr-',
            'network:router_gateway': 'qg-',
            'network:floatingip': 'qg-',
            'network:dhcp': 'tap',
            'compute:None': 'tap'
        }

        return prefixes[self.device_owner] + self.id[:11]

    def to_dict(self):
        attrs = ['vif', 'network_id', 'mac_address', 'status']
        d = {attr: getattr(self, attr) for attr in attrs}
        d['ips'] = [fixed_ip['ip_address'] for fixed_ip in self.fixed_ips]
        return d


class DhcpPort(object):
    """A graph node that represents the DHCP device binded to a subnet."""

    def __init__(self, port):
        self.id = port.get('id')
        self.network_id = port.get('network_id')
        self.mac_address = port.get('mac_address')
        self.fixed_ips = port.get('fixed_ips')
        self.device_id = port.get('device_id')
        self.status = port.get('status')

    @property
    def vif(self):
        return 'tap' + self.id[:11]

    def to_dict(self):
        attrs = ['vif', 'network_id', 'mac_address', 'device_id', 'status']
        d = {attr: getattr(self, attr) for attr in attrs}
        d['ips'] = [fixed_ip['ip_address'] for fixed_ip in self.fixed_ips]
        d['type'] = 'dhcp'
        return d


class NovaInstance(object):
    """A graph node that represents a compute instance."""

    def __init__(self, instance):
        self.id = instance.get('id')
        self.name = instance.get('name')
        self.addresses = instance.get('addresses')
        self.ports = None

    def to_dict(self):
        attrs = ['id', 'name']
        d = {attr: getattr(self, attr) for attr in attrs}
        d['ports'] = [port.to_dict() for port in self.ports]
        d['type'] = 'vm'

        # Floating IPs
        ips = {}
        for net in self.addresses:
            # Get an address list per network
            addresses = self.addresses[net]
            for a in addresses:
                if a['OS-EXT-IPS:type'] == 'floating':
                    ips.setdefault(net, []).append(
                        (a['addr'], a['OS-EXT-IPS-MAC:mac_addr']))
        d['floating_ips'] = ips if ips else None
        return d


class Topology(object):
    """A graph representation of a Neutron topology for a specific tenant."""

    def __init__(self, *args, **kwargs):
        self._nova = nova_client.Client('2', *args)
        self._neutron = neutron_client.Client('2.0', **kwargs)
        self._data = self._build()

    def _list_networks(self):
        return self._neutron.list_networks().get('networks')

    def _list_subnets(self):
        return self._neutron.list_subnets().get('subnets')

    def _list_routers(self):
        return self._neutron.list_routers().get('routers')

    def _list_ports(self):
        return self._neutron.list_ports().get('ports')

    def _list_vms(self):
        _, vms = self._nova.client.get('/servers/detail')
        return vms.get('servers')

    def _build(self):
        """Extract data and map the relevant elements together."""

        data = {}

        # Networks
        networks = self._list_networks()
        data['networks'] = [Network(item) for item in networks]

        # Subnets
        subnets = self._list_subnets()
        data['subnets'] = [Subnet(item) for item in subnets]

        # Routers
        routers = self._list_routers()
        data['routers'] = [Router(item) for item in routers]

        # Ports
        ports = self._list_ports()
        data['ports'] = [Port(item) for item in ports]

        # DHCP devices
        data['dhcp_ports'] = [DhcpPort(item) for item in ports
                              if item.get('device_owner') == 'network:dhcp']

        # Nova instances
        vms = self._list_vms()
        data['vms'] = [NovaInstance(item) for item in vms]

        # Subnet mapping
        for network in data['networks']:
            network.subnets = [subnet for subnet in data['subnets']
                               if subnet.network_id == network.id]

        # Router interface mapping
        for router in data['routers']:
            router.ports = [port for port in data['ports']
                            if port.device_id == router.id]

        # Nova instance interface mapping
        for vm in data['vms']:
            vm.ports = [port for port in data['ports']
                        if port.device_id == vm.id]

        return data

    def dump(self):
        """Returns a JSON representation of nodes and links that
           make up a Neutron topology.
        """

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
                # The current user may not have the required
                # permissions to see the target object
                if port.device_id in ids:
                    source = ids.index(port.device_id)
                    target = ids.index(port.network_id)
                    links.append({'source': source, 'target': target})

        return json.dumps({'nodes': nodes, 'links': links})
