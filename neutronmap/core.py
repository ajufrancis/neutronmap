# -*- coding: utf-8 -*-

import json

from neutronclient.neutron import client as neutron_client
from novaclient import client as nova_client


class Wrapper(object):
    """A basic wrapper for all Neutron objects."""

    def __init__(self, instance):
        for k, v in instance.iteritems():
            setattr(self, k, v)


class Network(Wrapper):
    """Network node wrapper."""

    def __init__(self, network):
        super(Network, self).__init__(network)
        self._subnets = None

    @property
    def router_external(self):
        return getattr(self, 'router:external')

    @property
    def subnets(self):
        return self._subnets

    @subnets.setter
    def subnets(self, value):
        self._subnets = value

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'router_external': self.router_external,
            'subnets': [subnet.data for subnet in self.subnets],
            'status': self.status,
            'type': 'external' if self.router_external else 'network'
        }


class Subnet(Wrapper):
    """Wrapper for a Neutron subnet."""

    def __init__(self, subnet):
        super(Subnet, self).__init__(subnet)

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'cidr': self.cidr,
            'gateway_ip': self.gateway_ip,
            'allocation_pools': self.allocation_pools,
            'dns_nameservers': self.dns_nameservers
        }


class Router(Wrapper):
    """Router node wrapper."""

    def __init__(self, router):
        super(Router, self).__init__(router)
        self._ports = None

    @property
    def ports(self):
        return self._ports

    @ports.setter
    def ports(self, value):
        self._ports = value

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'external_gateway_info': self.external_gateway_info,
            'ports': [port.data for port in self.ports],
            'status': self.status,
            'type': 'router'
        }


class Port(Wrapper):
    """Wrapper for a Neutron port."""

    def __init__(self, port):
        super(Port, self).__init__(port)

    @property
    def _vif(self):
        prefixes = {
            'network:router_interface': 'qr-',
            'network:router_gateway': 'qg-',
            'network:floatingip': 'qg-',
            'network:dhcp': 'tap',
            'compute:None': 'tap'
        }

        return prefixes[self.device_owner] + self.id[:11]

    @property
    def data(self):
        return {
            'vif': self._vif,
            'network_id': self.network_id,
            'mac_address': self.mac_address,
            'ip_addresses': [item['ip_address'] for item in self.fixed_ips],
            'status': self.status
        }


class DhcpPort(Wrapper):
    """DHCP device node wrapper."""

    def __init__(self, port):
        super(DhcpPort, self).__init__(port)

    @property
    def _vif(self):
        return 'tap' + self.id[:11]

    @property
    def data(self):
        return {
            'device_id': self.device_id,
            'vif': self._vif,
            'network_id': self.network_id,
            'mac_address': self.mac_address,
            'ip_addresses': [item['ip_address'] for item in self.fixed_ips],
            'status': self.status,
            'type': 'dhcp'
        }


class NovaInstance(Wrapper):
    """Nova instance node wrapper."""

    def __init__(self, instance):
        super(NovaInstance, self).__init__(instance)
        self._ports = None

    @property
    def ports(self):
        return self._ports

    @ports.setter
    def ports(self, value):
        self._ports = value

    @property
    def data(self):
        # Floating IPs
        ips = {}
        for net in self.addresses:
            # Get an address list per network
            addresses = self.addresses[net]
            for a in addresses:
                if a['OS-EXT-IPS:type'] == 'floating':
                    ips.setdefault(net, []).append(
                        (a['addr'], a['OS-EXT-IPS-MAC:mac_addr'])
                    )

        return {
            'id': self.id,
            'name': self.name,
            'floating_ips': ips,
            'ports': [port.data for port in self.ports],
            'status': self.status,
            'type': 'vmon' if self.status == 'ACTIVE' else 'vmoff'
        }


class Topology(object):
    """A graph representation of a Neutron topology for a specific tenant."""

    def __init__(self, *args, **kwargs):
        self._nova = nova_client.Client('2', *args)
        self._neutron = neutron_client.Client('2.0', **kwargs)

    @property
    def _networks(self):
        networks = self._neutron.list_networks().get('networks')
        return [Network(item) for item in networks]

    @property
    def _subnets(self):
        subnets = self._neutron.list_subnets().get('subnets')
        return [Subnet(item) for item in subnets]

    @property
    def _routers(self):
        routers = self._neutron.list_routers().get('routers')
        return [Router(item) for item in routers]

    @property
    def _ports(self):
        ports = self._neutron.list_ports().get('ports')
        return [Port(item) for item in ports]

    @property
    def _dhcp_ports(self):
        ports = self._neutron.list_ports().get('ports')
        return [DhcpPort(item) for item in ports
                if item['device_owner'] == 'network:dhcp']

    @property
    def _vms(self):
        _, vms = self._nova.client.get('/servers/detail')
        return [NovaInstance(item) for item in vms.get('servers')]

    def build(self):
        """Returns a JSON representation of the topology."""

        # Subnet to network mapping
        networks = self._networks
        for network in networks:
            network.subnets = [subnet for subnet in self._subnets
                               if subnet.network_id == network.id]

        # Router interface mapping
        routers = self._routers
        for router in routers:
            router.ports = [port for port in self._ports
                            if port.device_id == router.id]

        # Nova instance interface mapping
        vms = self._vms
        for vm in vms:
            vm.ports = [port for port in self._ports
                        if port.device_id == vm.id]

        # We keep the ID of each node added to the
        # topology in order to generate the links
        ids, nodes, links = [], [], []

        for network in networks:
            ids.append(network.id)
            nodes.append(network.data)

        for router in routers:
            ids.append(router.id)
            nodes.append(router.data)

        for vm in vms:
            ids.append(vm.id)
            nodes.append(vm.data)

        for dhcp_port in self._dhcp_ports:
            ids.append(dhcp_port.device_id)
            nodes.append(dhcp_port.data)

        # For each router with an external gateway, we
        # add a link toward the external network
        for router in routers:
            gateway = router.external_gateway_info
            if gateway:
                source = ids.index(router.id)
                target = ids.index(gateway.get('network_id'))
                links.append({'source': source, 'target': target})

        # Links between networks and devices
        for port in self._ports:
            if port.device_id in ids and port.device_owner in (
                    'compute:None',
                    'network:dhcp',
                    'network:router_interface'):
                source = ids.index(port.device_id)
                target = ids.index(port.network_id)
                links.append({'source': source, 'target': target})

        return json.dumps({'nodes': nodes, 'links': links})
