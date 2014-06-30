<h3>Element details</h3>
<p>
  <strong>DHCP device:</strong><br/>
  id: {{:device_id}}<br/>
  <strong>Interface:</strong><br/>
  name: {{:vif}}<br/>
  network id: {{:network_id}}<br/>
  mac: {{:mac_address}}<br/>
  ips:
  {{for ips ~count=ips.length}}
    {{:}}{{if #index < ~count-1}}, {{else #index === ~count-1}}<br/>{{/if}}
  {{/for}}
</p>
