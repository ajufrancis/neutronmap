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
    $.ajax({
        url: $SCRIPT_ROOT + '/' + d.type,
        async: false,
        cache: true,
        dataType: "text",
        success: function(data) {
            $.templates({template: data});
            $("#hidden").empty().html(
                $.render.template(d)
            );
        }
    });
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
                $.ajax({
                    url: $SCRIPT_ROOT + '/exception',
                    async: false,
                    cache: true,
                    dataType: "text",
                    success: function(data) {
                        $.templates({template: data});
                        $("#hidden").html(
                            $.render.template(e)
                        );
                    }
                });
                $("#hidden").show();
            });
        $("form")[0].reset();
    });
});
