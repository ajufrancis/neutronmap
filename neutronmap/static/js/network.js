<h3>Element details</h3>
<p>
  <strong>Network:</strong><br/>
  id: {{:id}}<br/>
  name: {{:name }}<br/>
  router external: {{:router_external}}<br/>
  {{for subnets}}
    <strong>Subnet:</strong><br/>
    id: {{:id}}<br/>
    name: {{:name}}<br/>
    cidr: {{:cidr}}<br/>
    {{for pools}}
      pool: {{:start}} / {{:end}}<br/>
    {{/for}}
    gateway ip: {{:gateway}}<br/>
    {{for nameservers}}
      dns: {{:}}<br/>
    {{/for}}
  {{/for}}
</p>
