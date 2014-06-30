<h3>Element details</h3>
<p>
  <strong>Router:</strong><br/>
  id: {{:id}}<br/>
  name: {{:name}}<br/>
  {{if gateway}}
    <strong>External gateway info:</strong><br/>
    network id: {{:gateway.network_id}}<br/>
    enable snat: {{:gateway.enable_snat}}<br/>
  {{/if}}
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
</p>
