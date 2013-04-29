TEMPLATE = '''<!DOCTYPE html>
<meta charset="utf-8">
<style>

.place {
  stroke: #fff;
  stroke-width: 1.5px;
  fill:grey;
}


.transition {
  stroke: #fff;
  stroke-width: 1.5px;
  fill:grey;
}

.attack {
  stroke: red;
}

.arc {
  stroke:#bbb;
  stroke-opacity: .6;
  stroke-width: 2;
}

.input, .output {
    marker-end:url(#normal-arc);
}

.inhibitor {
    marker-start:url(#inhibitor-start-arc);
    marker-end:url(#inhibitor-end-arc);
}

.attack.enabled {
    fill: red;
}
.enabled {
    fill: green;
}

.label {
    font-family:Verdana;
    font-size:8px;
    fill:blue;
}

.transition-name.label {
  fill:blue;
}
.transition-guard.label {
  fill:blue;
}
.place-tokens.label {
  font-size:12px;
  fill:green;
}

#tokens {
    font-family:Verdana;
    font-size:12px;
    fill:gray;
}
</style>
<body>
<svg width='960' height='500' xmlns="http://www.w3.org/2000/svg" version="1.1">
    <defs>
        <marker id="normal-arc"
          viewBox="0 0 10 10" refX="30" refY="5" 
          markerUnits="strokeWidth"
          markerWidth="4" markerHeight="3"
          orient="auto">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#bbb"/>
        </marker>
        <marker id="inhibitor-end-arc"
          viewBox="0 0 10 10" refX="30" refY="5" 
          markerUnits="strokeWidth"
          markerWidth="4" markerHeight="3"
          orient="auto">
          <path d="M 0 5 L 5 0 L 10 5 L 5 10 z" fill="#bbb"/>
        </marker>
        <marker id="inhibitor-start-arc"
          viewBox="0 0 10 10" refX="-25" refY="5" 
          markerUnits="strokeWidth"
          markerWidth="4" markerHeight="3"
          orient="auto">
          <path d="M 0 5 L 5 0 L 10 5 L 5 10 z" fill="#bbb"/>
        </marker>
        %(markers)s
      </defs>

      <g id='net'/>
      <g id='tokens-widget'>
        <text x='10' y='20' id='tokens'>
        %(tokens)s
        </text>
      </g>
</svg>

<script src="http://d3js.org/d3.v3.min.js"></script>
<script>graph=%(graph)s</script>
<script>
    function calc_arc(d){
        if (d.curved==0){
            return 'M0,0 l50,0 l50,0'
        }else{
            return 'M0,0 A100,50 0 0,0 50,15 A100,50 0 0,0 100,0'
        }
        
    }
    function transform_arc(d){
      var Ly = d.target.y-d.source.y
      var Lx = d.target.x-d.source.x
      var G = Math.sqrt(Lx*Lx + Ly*Ly)
      scale = G/100;
      var sin = Ly/G;
      var cos = Lx/G;
      return "translate("+d.source.x+","+d.source.y+") scale("+scale+","+scale+") matrix("+cos+","+sin+","+-1*sin+","+cos+",0,0)"

    }
</script>
<script>

var width = 960,
    height = 500;

var color = d3.scale.category20();
var linkDistance = 120
var force = d3.layout.force()
    .charge(-1320)
    .linkDistance(linkDistance)
    .size([width, height]);

var svg = d3.select("#net")
  force
      .nodes(graph.places.concat(graph.transitions))
      .links(graph.arcs)
      .start();

  var link = svg.selectAll(".arc")
      .data(graph.arcs)
    .enter().append("path")
      .attr("class", function(d){return 'arc ' + d['class']})
      .attr("d", calc_arc)
      .attr("fill", "#fff")
      .attr("marker-mid", function(d){return 'url(#marker_mid_'+d.id+')'})
      

  var place = svg.selectAll(".place")
      .data(graph.places)
    .enter()
      .append('path')
      .attr("class", 'place')
      .attr("onmouseover", function(d){return "document.getElementById('place-text-"+d.id+"').setAttribute('font-weight','bold')"})
      .attr("onmouseout", function(d){return "document.getElementById('place-text-"+d.id+"').setAttribute('font-weight','normal')"})      
      .attr("marker-start", function(d){return 'url(#marker_start_'+d.id+')'})
      .attr("marker-mid", function(d){return 'url(#marker_mid_'+d.id+')'})
      .attr("marker-end", function(d){return 'url(#marker_end_'+d.id+')'})      
      .call(force.drag);

  place.append("desc")
      .text(function(d) { return d.name; });

  var transition = svg.selectAll(".transition")
      .data(graph.transitions)
    .enter()
      .append('path')
      .attr("class", function(d){return d['class']})
      .attr("width", 30)
      .attr("height", 15)
      .attr("marker-start", function(d){return 'url(#marker_start_'+d.id+')'})
      .attr("marker-mid", function(d){return 'url(#marker_mid_'+d.id+')'})
      .attr("marker-end", function(d){return 'url(#marker_end_'+d.id+')'})      

      .call(force.drag);

  transition.append("desc")
      .text(function(d) { return d.name; });
  
  force.on("tick", function() {
    link.attr("transform", transform_arc)

    place.attr("d", function(d) { return 'M'+ d.x + ',' + d.y + ' m -15,0 a 15,15 0 1,0 30,0 a 15,15 0 1,0 -30,0 z'})

    transition.attr("d", function(d) { return 'M' + (d.x-15) + ',' + (d.y-7) + ' l30,0 l0,15 l-30,0 z'});

  });

</script>

</body>
'''

PLACE_MARKER = '''<marker id="%s"
  viewBox="0 0 52 18" refX="-20" refY="10" 
  markerUnits="strokeWidth"
  markerWidth="52" markerHeight="18"
  orient="0">
    <text x="1" y="10" font-family="Verdana" font-size="10" fill="black" opacity='0.6'>%s</text>
</marker>'''

ARC_MARKER = '''<marker id="%s"
          viewBox="0 0 60 20" refX="20" refY="0" 
          markerUnits="strokeWidth"
          markerWidth="36" markerHeight="36"
          orient="0">
            <text class='label'>%s</text>
        </marker>'''

TRANSITION_NAME_MARKER = '''<marker id="%s"
          viewBox="0 0 60 20" refX="0" refY="0" 
          markerUnits="strokeWidth"
          markerWidth="36" markerHeight="36"
          orient="auto">
            <text class="transition-name label">%s</text>
        </marker>'''
TRANSITION_GUARD_MARKER = '''<marker id="%s"
          viewBox="0 0 80 20" refX="0" refY="-10" 
          markerUnits="strokeWidth"
          markerWidth="46" markerHeight="46"
          orient="auto">
            <text class="transition-guard label">%s</text>
        </marker>'''

PLACE_TOKENS = '''<marker id="%s"
  viewBox="0 0 52 18" refX="4" refY="6" 
  markerUnits="strokeWidth"
  markerWidth="52" markerHeight="18"
  orient="0">
    <text x="1" y="10" class='place-tokens label'>%s</text>
</marker>'''


PLACE_INFO = '''<tspan id='%(id)s' x='10' dy='25' class='tokens-group'>%(name)s
            %(tokens)s
        </tspan> 
'''

TOKEN_INFO = '''
  <tspan id='%s' x='20' dy='16'>%s</tspan>
'''