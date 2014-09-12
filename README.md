Neutron Map
===========

A very simple web application to visualize OpenStack Neutron topologies.

Neutron networks are represented with the [D3.js][d3js] library. The goal is to provide a logical view of the virtual resources, as well as a representation of the way these resources are allocated on physical hosts (not implemented yet).

A quick way to test the application:

```
$ mkvirtualenv neutronmap
(neutronmap)$ git clone https://github.com/yannlambret/neutronmap.git
(neutronmap)$ cd neutronmap
(neutronmap)$ pip install -r requirements.txt
(neutronmap)$ python neutronmap/webapp.py
```

Depending on your client versions, you may also have to install oslo.config:

```
(neutronmap)$ pip install oslo.config
```

Use your browser to connect at http://localhost:5000, and submit Keystone credentials for a specific tenant. You can get detailed information by double-clicking on each topology element.

![Neutron Map screenshot](resources/demo.png?raw=true "Neutron Map")
![Neutron Map screenshot](resources/admin.png?raw=true "Neutron Map")

[d3js]: http://d3js.org/
