<h3>Element details</h3>
<p>
  <strong>Nova instance:</strong><br/>
  id: {{:id}}<br/>
  name: {{:name}}<br/>
  {{for ports}}
    <strong>Interface:</strong><br/>
    name: {{:vif}}<br/>
    network id: {{:network_id}}<br/>
    mac: {{:mac_address}}<br/>
    ips:
    {{for ips ~count=ips.length}}
      {{:}}{{if #index < ~count-1}}, {{else #index === ~count-1}}<br/>{{/if}}
    {{/for}}
  {{/for}}
  <strong>Floating ips:</strong><br/>
  {{for floating_ips}}
    {{props}}
      {{for prop ~key=key}}
        {{:#data[0]}} - {{:#data[1]}} ({{:~key}})<br/>
      {{/for}}
    {{/props}}
  {{/for}}
</p>
