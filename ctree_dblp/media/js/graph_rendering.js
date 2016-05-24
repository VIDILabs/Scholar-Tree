var color = d3.scale.category20(); // stander color scale

var color_cat = ["#f45e00","#e39ac5","#b04d84","#821b54",
                 "#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"];

var width, height, svg;

// var force = d3.layout.force()
//     .charge(-120)
//     .linkDistance(30)
//     .size([width, height]);




// var scale = d3.scale.linear()
//     .domain([0, 500])
//     .range([0,100]);

var force = d3.layout.force();
var nodes, links;


function get_graph_data(mydata){
  d3.select("svg").remove();
  width = $(window).width()*0.35;
  height = $(window).width()*0.35;
  svg = d3.select("#nl_canvas").append("svg")
    .attr("width", width)
    .attr("height", height);
  init();
  draw_graph(mydata.tree1);
}

function init(){
  force
    .charge(-120)
    .size([width, height])
    .linkDistance(80);
    // .start();

  var drag = force.drag()
    .on("dragstart", dragstart);
  
  // nodes = graph.nodes;
  // links = graph.links;
}

function draw_graph(graph){
  // graph = mydata.Wijk
  console.log(graph);
  force
    .nodes(graph.nodes)
    .links(graph.links)
    .start();

  var link = svg.selectAll(".link")
      .data(graph.links);
  link
    .enter().append("line")
      .attr("class", "link")
      .style("stroke", function(d) { return d.value; });
      // .style("stroke-width", 3);

  link.exit().remove();

  var node = svg.selectAll(".node")
      // .data(nodes);
      .data(graph.nodes);
    // .enter().append("circle")
  node
    .enter().append("g")
      .attr("class", "node")
      // .attr("r", function(d) { return d.size/10;} )
      // .style("fill", function(d) { return color(d.group); });
      // .style("fill", function(d) { return d.group;})
      .call(force.drag);
      // .call(drag);

  node.append("title")
      .text(function(d) { return d.label; });

  node.append("path")
      .attr("d", d3.svg.symbol()
        .size(function(d) { return d.size*50; })
        .type(function(d) { return d.type; }))
      .style("fill", function(d) { return color_cat[d.group];});

  node.exit().remove();

  
  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    // node.attr("cx", function(d) { return d.x; })
    //     .attr("cy", function(d) { return d.y; });
      node.attr("transform", function setPosition(d) {
        return "translate(" + d.x + "," + d.y +")";
      });
  });

}


function dragstart(d) {
  d3.select(this).classed("fixed", d.fixed = true);
}