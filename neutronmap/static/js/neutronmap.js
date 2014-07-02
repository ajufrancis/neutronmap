// d3.js code to generate the Neutron topology graph

var width = 825,
    height = 560,
    root;

var force = d3.layout.force()
    .size([width, height])
    .charge(-1000)
    .friction(0.8)
    .linkDistance(50);

var svg = d3.select("#topology").append("svg")
    .attr("width", width)
    .attr("height", height);

function update(data) {
    d3.select("#topology > svg").remove();

    var newsvg = d3.select("#topology").append("svg")
        .attr("width", width)
        .attr("height", height);

    var link = newsvg.selectAll(".link")
        .data(data.links)
        .enter().append("line")
        .attr("class", "link");

    var node = newsvg.selectAll(".node")
        .data(data.nodes)
        .enter().append("g")
        .attr("class", "node")
        .on("dblclick", dblclick)
        .call(force.drag);

    node.append("circle")
        .attr("class", function(d) { return d.type + "-inner"; })
        .attr("r", function(d) { return Math.sqrt(size(d)) / 18; });

    node.append("circle")
        .attr("class", function(d) { return d.type + "-outer"; })
        .attr("r", function(d) { return Math.sqrt(size(d)) / 6; })

    force
        .nodes(data.nodes)
        .links(data.links)
        .start();

    force.on("tick", function() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });
}


// Get a specific size for each network element

function size(d) {
    var sizes = [];
    sizes["external"] = 12000;
    sizes["network"] = 12000;
    sizes["router"] = 8000;
    sizes["dhcp"] = 6000;
    sizes["vm"] = 6000;
    return sizes[d.type];
}


// Display node info on dblclick.

function dblclick(d) {
    d3.selectAll(".node").classed({"highlighted": false});
    d3.select(this).classed({"highlighted": true});
    var html = $.templates[d.type].render(d);
    $("#hidden").empty().html(html);
    $("#hidden").show();
}


// Authentication form submission

$(function() {
    $("form").on("submit", function(event) {
        event.preventDefault();
        $("#hidden").empty();
        var data = $(this).serialize();
        $.post($SCRIPT_ROOT + '/topology', data, update, "json")
            .fail(function(jqXHR, textStatus, errorThrown) {
                var e = jqXHR.responseJSON;
                var html = $.templates.exception.render(e);
                $("#hidden").html(html);
                $("#hidden").show();
            });
        $("form")[0].reset();
    });
});


// JSRender templates

$.templates({
    exception: '<div class="alert alert-danger alert-dismissable">' +
               '  <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
               '  <strong>Title:</strong> {{:title}}<br/>' +
               '  <strong>Message:</strong> {{:message}}<br/>' +
               '  <strong>Code:</strong> {{:code}}<br/>' +
               '</div>',
    external: '<h3>Element details</h3>' +
              '<p>' +
              '  <strong>Network:</strong><br/>' +
              '  id: {{:id}}<br/>' +
              '  name: {{:name }}<br/>' +
              '  router external: {{:router_external}}<br/>' +
              '  {{for subnets}}' +
              '    <strong>Subnet:</strong><br/>' +
              '    id: {{:id}}<br/>' +
              '    name: {{:name}}<br/>' +
              '    cidr: {{:cidr}}<br/>' +
              '    {{for pools}}' +
              '      pool: {{:start}} / {{:end}}<br/>' +
              '    {{/for}}' +
              '    gateway ip: {{:gateway}}<br/>' +
              '    {{for nameservers}}' +
              '      dns: {{:}}<br/>' +
              '    {{/for}}' +
              '  {{/for}}' +
              '</p>',
    network: '<h3>Element details</h3>' +
             '<p>' +
             '  <strong>Network:</strong><br/>' +
             '  id: {{:id}}<br/>' +
             '  name: {{:name }}<br/>' +
             '  router external: {{:router_external}}<br/>' +
             '  {{for subnets}}' +
             '    <strong>Subnet:</strong><br/>' +
             '    id: {{:id}}<br/>' +
             '    name: {{:name}}<br/>' +
             '    cidr: {{:cidr}}<br/>' +
             '    {{for pools}}' +
             '      pool: {{:start}} / {{:end}}<br/>' +
             '    {{/for}}' +
             '    gateway ip: {{:gateway}}<br/>' +
             '    {{for nameservers}}' +
             '      dns: {{:}}<br/>' +
             '    {{/for}}' +
             '  {{/for}}' +
             '</p>',
    router: '<h3>Element details</h3>' +
            '<p>' +
            '  <strong>Router:</strong><br/>' +
            '  id: {{:id}}<br/>' +
            '  name: {{:name}}<br/>' +
            '  {{if gateway}}' +
            '    <strong>External gateway info:</strong><br/>' +
            '    network id: {{:gateway.network_id}}<br/>' +
            '    enable snat: {{:gateway.enable_snat}}<br/>' +
            '  {{/if}}' +
            '  {{for ports}}' +
            '    <strong>Interface:</strong><br/>' +
            '    name: {{:vif}}<br/>' +
            '    network id: {{:network_id}}<br/>' +
            '    mac: {{:mac_address}}<br/>' +
            '    ips:' +
            '    {{for ips ~count=ips.length}}' +
            '      {{:}}{{if #index < ~count-1}}, {{else #index === ~count-1}}<br/>{{/if}}' +
            '    {{/for}}' +
            '  {{/for}}' +
            '</p>',
    dhcp: '<h3>Element details</h3>' +
          '<p>' +
          '  <strong>DHCP device:</strong><br/>' +
          '  id: {{:device_id}}<br/>' +
          '  <strong>Interface:</strong><br/>' +
          '  name: {{:vif}}<br/>' +
          '  network id: {{:network_id}}<br/>' +
          '  mac: {{:mac_address}}<br/>' +
          '  ips:' +
          '  {{for ips ~count=ips.length}}' +
          '    {{:}}{{if #index < ~count-1}}, {{else #index === ~count-1}}<br/>{{/if}}' +
          '  {{/for}}' +
          '</p>',
    vm: '<h3>Element details</h3>' +
        '<p>' +
        '  <strong>Nova instance:</strong><br/>' +
        '  id: {{:id}}<br/>' +
        '  name: {{:name}}<br/>' +
        '  {{for ports}}' +
        '    <strong>Interface:</strong><br/>' +
        '    name: {{:vif}}<br/>' +
        '    network id: {{:network_id}}<br/>' +
        '    mac: {{:mac_address}}<br/>' +
        '    ips:' +
        '    {{for ips ~count=ips.length}}' +
        '      {{:}}{{if #index < ~count-1}}, {{else #index === ~count-1}}<br/>{{/if}}' +
        '    {{/for}}' +
        '  {{/for}}' +
        '  <strong>Floating ips:</strong><br/>' +
        '  {{for floating_ips}}' +
        '    {{props}}' +
        '      {{for prop ~key=key}}' +
        '        {{:#data[0]}} - {{:#data[1]}} ({{:~key}})<br/>' +
        '      {{/for}}' +
        '    {{/props}}' +
        '  {{/for}}' +
        '</p>'
});
