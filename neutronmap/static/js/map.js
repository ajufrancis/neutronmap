// d3.js code to generate the Neutron topology graph

var aspect = 0.5;
var svg;

function update(data) {
    var html = $.templates("#map").render();
    $("#content").empty().html(html);

    var width = $("#topology").width();
    var height = width * aspect;

    var force = d3.layout.force()
        .size([width, height])
        .charge(-1000)
        .friction(0.8)
        .linkDistance(50);

    svg = d3.select("#topology").append("svg")
        .attr("preserveAspectRatio", "xMinYMin")
        .attr("viewBox", "0 0 " + width + " " + height)
        .attr("width", width)
        .attr("height", height);

    var link = svg.selectAll(".link")
        .data(data.links)
        .enter().append("line")
        .attr("class", "link");

    var node = svg.selectAll(".node")
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

$(window).resize(function() {
    var width = $("#topology").width();
    svg.attr("width", width);
    svg.attr("height", width * aspect);
});


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
    var html = $.templates("#" + d.type).render(d);
    $("#details").empty().html(html);
    $("#details").show();
}
