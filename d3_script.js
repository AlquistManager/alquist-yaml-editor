var width = 1900,
    height = 1000,
    radius = 10,
    levelDist = 200,
    xRadiusScale = 5;

var fill = d3.scale.category20();

var force = d3.layout.force()
    .charge(-200) //-120 -200
    .linkDistance(200)
    .size([width, height]);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height)
          .call(d3.behavior.zoom().on("zoom", function () {
              if(panning){
                  child.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
              }
      }))
    .on(pan);

var child = svg.append("g");

//disables panning with left mouse button
svg.on("mousedown", function(){
    if(d3.event.buttons == 1){
        console.log("1");
        panning = false;
    }
});

//enables panning when left mouse is not pressed
svg.on("mouseup", function(){
    panning = true;
})


d3.json("graph.json", function(error, json) {
  if (error) throw error;


var edges = [];
json.links.forEach(function(e) {
    var sourceNode = json.nodes.filter(function(n) {
        return n.id === e.source;
    })[0],
        targetNode = json.nodes.filter(function(n) {
            return n.id === e.target;
        })[0];

    edges.push({
        source: sourceNode,
        target: targetNode
    });
});


  force
      .nodes(json.nodes)
      .links(edges)
      .on("tick", tick)
      .start();

  var link = child.selectAll("line")
      .data(edges)
    .enter().append("line");

    // build the arrow.
child.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
  .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 40)
    .attr("refY", 0) //-1.5
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
  .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");


var node = child.selectAll("g")
      .data(json.nodes)


var elemEnter = node.enter().append("g")

var circle = elemEnter.append("ellipse")
      //.attr("rx", radiusX) //radius - 0.75
      .attr("rx", function(d) {return d.name.length * xRadiusScale;})
      .attr("ry", radius)
      .style("fill", function(d) { return fill(d.group); })
      .style("stroke", function(d) { return d3.rgb(fill(d.group)).darker(); })
      .call(force.drag);

    /* Create the text for each block */
var text = elemEnter.append("text")
        .text(function(d){return d.name})
        .attr({
        "text-anchor": "middle",
        "dy": function(d) {
            return radius / ((radius * 25) / 100);
        }
        });


  function tick(e) {
    var k = 6 * e.alpha;

        //----------------------------------------------------
      //var q = d3.geom.quadtree(node),
      //i = 0,
      //n = node.length;

  //while (++i < n) q.visit(collide(node[i]));

    //for(i = 0; i < node.length; i++){
      //  collide(node[0][i], node[0]);
      //}
  //------------------------------------------------------------

    // Push sources up and targets down to form a weak tree.
    link
        .each(function(d) {

         })
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.level*levelDist; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.level*levelDist; })
        .attr("marker-end", "url(#end)");

    node
       // .attr("transform", function(d){return "translate("+d.x+", "+d.level*levelDist+")"});
            .attr("transform", function(d){return "translate("+collide2(d, node[0])+", "+d.level*levelDist+")"});

  }
});

//panning with middle mouse button
function pan() {
    current_translate = d3.transform(svg.attr("transform")).translate;
    dx = d3.event.wheelDeltaX + current_translate[0];
    dy = d3.event.wheelDeltaY + current_translate[1];

  child.attr("transform", "translate(" + [dx,dy] + ")");
  d3.event.stopPropagation();
}

function collide(n, node) {
    for(i = 0; i < node.length; i++){
        var currentNodeData = d3.select(n.firstChild).datum();
        var otherNodeData = d3.select(node[i].firstChild).datum();
        if(currentNodeData.level != otherNodeData.level || currentNodeData.id == otherNodeData.id){
            return;
        }

        var currentNodeRadius = (currentNodeData.name.length*xRadiusScale)/2;
        var otherNodeRadius = (currentNodeData.name.length*xRadiusScale)/2;

        var currentNodeCenter = currentNodeData.x + currentNodeRadius;
        var otherNodeCenter = otherNodeData.x + otherNodeRadius;

        if(currentNodeCenter  - otherNodeCenter < Math.max(currentNodeRadius, otherNodeRadius)){
            if(currentNodeCenter > otherNodeCenter){
                n.rx += 1;
                node[i].rx -= 1;
            }else{
                currentNodeData.x -= 1;
                otherNodeData.x += 1;
            }
        }
    }
}

function collide2(n, node) {
    for(i = 0; i < node.length; i++){
        var currentNodeData = n;
        var otherNodeData = d3.select(node[i].firstChild).datum();
        if(currentNodeData.level != otherNodeData.level || currentNodeData.id == otherNodeData.id){
            return n.x;
        }

        var currentNodeRadius = (currentNodeData.name.length*xRadiusScale)/2;
        var otherNodeRadius = (otherNodeData.name.length*xRadiusScale)/2;

        //var currentNodeCenter = currentNodeData.x + currentNodeRadius;
        //var otherNodeCenter = otherNodeData.x + otherNodeRadius;

        var currentNodeCenter = currentNodeData.x;
        var otherNodeCenter = otherNodeData.x;

        if(currentNodeCenter  - otherNodeCenter < Math.max(currentNodeRadius, otherNodeRadius)){
            if(currentNodeCenter > otherNodeCenter){
                //console.log(currentNodeData.x + 1);
                n.x = currentNodeData.x + 10;
            }else{
                n.x = currentNodeData.x - 10;
            }
        }

        return n.x
    }
}
