var margin = {top: 20, right: 80, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d").parse;

var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.category10();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .ticks(7)
    .orient("left");

var line = d3.svg.line()
    .interpolate("linear")
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.points); });

var svg = d3.select("#plt").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var zoom = d3.behavior.zoom()
    .on("zoom", draw);    

svg.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")");

svg.append("g")
  .attr("class", "y axis")
.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 6)
  .attr("dy", ".71em")
  .style("text-anchor", "end")
  .text("points");
  
svg.append("rect")
    .attr("class", "pane")
    .attr("width", width)
    .attr("height", height)
    .call(zoom);
    

d3.json("data.json", function(error, data) {
  if (error) throw error;

  color.domain(d3.keys(data));
  
  var minDate;
  var maxDate;

  var players = color.domain().map(function(name) {
    return {
      name: name,
      values: data[name].map(function(d) {
          var date = parseDate(d[0])
          minDate = d3.min([date,minDate]);
          maxDate = d3.max([date,maxDate]);
        return {date: date, points: +d[1]};
      })
    };
  });

  x.domain([minDate,maxDate]);
  
  y.domain([
    d3.min(players, function(c) { return d3.min(c.values, function(v) { return v.points; }); }),
    d3.max(players, function(c) { return d3.max(c.values, function(v) { return v.points; }); })
  ]);
  
  zoom.x(x)
    .scaleExtent([1,16])
    //.xExtent(x.domain());



  var player = svg.selectAll(".player")
      .data(players)
    .enter().append("g")
      .attr("class", "player");

  player.append("path")
      .attr("class", "line")
     // .attr("d", function(d) { return line(d.values); })
      .style("stroke", function(d) { return color(d.name); });

  player.append("text")
      .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
      .attr("class","label")
      // .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.points) + ")"; })
      .attr("x", 3)
      .attr("dy", ".35em")
      .text(function(d) { return d.name; });
      
  draw()
      
});

function draw() {
  console.log("redrawing")
  svg.select("g.x.axis").call(xAxis);
  svg.select("g.y.axis").call(yAxis);
  svg.selectAll("path.line").attr("d", function(d) { return line(d.values); })
  svg.selectAll("text.label").attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.points) + ")"; })
}