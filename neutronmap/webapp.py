# -*- coding: utf-8 -*-

from flask import Flask, json, render_template, request, Response

from forms import AuthenticationForm
from core import LogicalTopology


app = Flask(__name__)
app.config.from_object('config')


@app.route('/', methods=['GET'])
def index():
    """Application entry point."""
    return render_template('index.html')


@app.route('/topology', methods=['POST'])
def topology():
    """Returns a JSON representation of a Neutron topology."""
    form = AuthenticationForm(request.form)

    if request.method == 'POST' and form.validate():
        # We need positional arguments for nova client
        # and keywords arguments for neutron client
        keys = ['username', 'password', 'tenant_name', 'auth_url']
        args = [getattr(form, key).data for key in keys]
        kwargs = dict(zip(keys, args))

        return '{"nodes": [{"router_external": false, "subnets": [{"name": "", "nameservers": ["8.8.8.8"], "id": "a2dee20c-9c52-41fd-95ce-580953f9b93a", "pools": [{"start": "10.5.5.1", "end": "10.5.5.253"}], "cidr": "10.5.5.0/24", "gateway": "10.5.5.254"}], "type": "network", "id": "00e871de-e297-4ac1-8270-241daefd5daf", "name": "demo-net"}, {"router_external": true, "subnets": [], "type": "external", "id": "2ca3fa80-e693-44ea-bc0c-5c030f1bd747", "name": "ext-net"}, {"router_external": false, "subnets": [{"name": "test-net", "nameservers": [], "id": "3c93f8e4-3f85-4db3-ab3c-67d1643b92f8", "pools": [{"start": "10.5.9.1", "end": "10.5.9.253"}], "cidr": "10.5.9.0/24", "gateway": "10.5.9.254"}], "type": "network", "id": "4f58b56d-813a-459d-9abb-cb6b5d590fc0", "name": "test-net"}, {"ports": [{"network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.254"], "vif": "qr-5bb24753-d8", "mac_address": "fa:16:3e:41:95:01"}, {"network_id": "4f58b56d-813a-459d-9abb-cb6b5d590fc0", "ips": ["10.5.9.254"], "vif": "qr-64358f8f-9f", "mac_address": "fa:16:3e:68:6a:ad"}], "type": "router", "gateway": {"network_id": "2ca3fa80-e693-44ea-bc0c-5c030f1bd747", "enable_snat": true}, "id": "a3628e26-3ee2-4cd7-bce1-b61d92b6b8a2", "name": "ext-to-int"}, {"ports": [{"network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.7"], "vif": "tap8119bda6-9d", "mac_address": "fa:16:3e:16:e2:36"}], "floating_ips": {}, "type": "vm", "id": "e61df2ae-02ba-40ca-aa3a-ed168832126c", "name": "cirros5"}, {"ports": [{"network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.6"], "vif": "tap53df5238-a3", "mac_address": "fa:16:3e:de:da:af"}], "floating_ips": {}, "type": "vm", "id": "4c040eae-a051-4c78-983c-f29d6dab87ab", "name": "cirros4"}, {"ports": [{"network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.4", "10.5.5.5"], "vif": "tap6e1ba8c1-80", "mac_address": "fa:16:3e:66:33:0f"}, {"network_id": "4f58b56d-813a-459d-9abb-cb6b5d590fc0", "ips": ["10.5.9.3"], "vif": "tapcdeee58e-06", "mac_address": "fa:16:3e:e1:83:7f"}], "floating_ips": {"test-net": [["192.168.0.186", "fa:16:3e:e1:83:7f"]], "demo-net": [["192.168.0.187", "fa:16:3e:66:33:0f"], ["192.168.0.188", "fa:16:3e:66:33:0f"]]}, "type": "vm", "id": "a2ed6182-8307-416a-a00d-2378f3d16d89", "name": "cirros3"}, {"ports": [{"network_id": "4f58b56d-813a-459d-9abb-cb6b5d590fc0", "ips": ["10.5.9.2"], "vif": "tap2d96e1e2-a5", "mac_address": "fa:16:3e:f1:36:24"}], "floating_ips": {"test-net": [["192.168.0.183", "fa:16:3e:f1:36:24"]]}, "type": "vm", "id": "bd85ffb7-3193-42f2-8794-6c528f68ab2a", "name": "cirros2"}, {"ports": [{"network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.3"], "vif": "tapd5110a1d-6e", "mac_address": "fa:16:3e:e5:74:b6"}], "floating_ips": {"demo-net": [["192.168.0.182", "fa:16:3e:e5:74:b6"]]}, "type": "vm", "id": "acbf25f8-64a4-4c5f-85f4-a65d6e8f68cc", "name": "ubuntu1"}, {"ports": [{"network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.1"], "vif": "tap04ec9ade-5d", "mac_address": "fa:16:3e:05:2f:7a"}], "floating_ips": {"demo-net": [["192.168.0.181", "fa:16:3e:05:2f:7a"]]}, "type": "vm", "id": "bbf049ef-7a74-4668-8026-9c761be191eb", "name": "cirros1"}, {"vif": "tap376830d1-95", "network_id": "00e871de-e297-4ac1-8270-241daefd5daf", "ips": ["10.5.5.2"], "mac_address": "fa:16:3e:31:1a:48", "type": "dhcp", "device_id": "dhcpd3377d3c-a0d1-5d71-9947-f17125c357bb-00e871de-e297-4ac1-8270-241daefd5daf"}, {"vif": "tapdd3f7769-fa", "network_id": "4f58b56d-813a-459d-9abb-cb6b5d590fc0", "ips": ["10.5.9.1"], "mac_address": "fa:16:3e:7b:0f:7c", "type": "dhcp", "device_id": "dhcpd3377d3c-a0d1-5d71-9947-f17125c357bb-4f58b56d-813a-459d-9abb-cb6b5d590fc0"}], "links": [{"source": 3, "target": 1}, {"source": 9, "target": 0}, {"source": 7, "target": 2}, {"source": 10, "target": 0}, {"source": 5, "target": 0}, {"source": 3, "target": 0}, {"source": 3, "target": 2}, {"source": 6, "target": 0}, {"source": 4, "target": 0}, {"source": 6, "target": 2}, {"source": 8, "target": 0}, {"source": 11, "target": 2}]}'

        try:
            topology = LogicalTopology(*args, **kwargs)
            return Response(response=topology.dumps(),
                            mimetype='application/json',
                            status=200)
        except Exception as e:
            try:
                # Handle Neutron client exceptions first
                error = json.loads(e.message).pop('error')
                status = error.get('code', 500)
            except ValueError:
                # Wrap Nova client and other exceptions
                # into a serializable object
                status = e.http_status if hasattr(e, 'http_status') else 500
                error = {'title': type(e).__name__,
                         'message': str(e),
                         'code': status}
            return Response(response=json.dumps(error),
                            mimetype='application/json',
                            status=status)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
