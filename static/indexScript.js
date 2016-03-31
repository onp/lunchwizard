//Display this month's graph on the main page.

// Establish dimensions and margins for the plot
var margin = {top: 20, right: 80, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// Parser for dates coming from the json data.
var parseDate = d3.time.format("%Y-%m-%d").parse;

// scales (used to project data domains onto axes.)
var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

// axes (the svg elements that are displayed)
var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .ticks(7)
    .orient("left");

// color set used for players.
var color = d3.scale.category10();
    
// line function that parses player data.
var line = d3.svg.line()
    .interpolate("linear")
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.points); });

// create the main chart element
var svg = d3.select("#plt").append("svg")
    .attr("width", width + margin.left + margin.right) // chart is padded by the width of the margins
    .attr("height", height + margin.top + margin.bottom) 
  .append("g") // this is the base element that actually gets attached to the svg handle
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");   // add padding


svg.append("g") // element to hold x axis
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")") // place x axis container at bottom of chart
    .call(xAxis); // draw the axis
  

svg.append("g") // element to hold y axis
  .attr("class", "y axis")
  .call(yAxis)  // draw the axis
.append("text") // y axis label
  .attr("text-anchor", "middle") // tranforms will move the center of the element
  .attr("transform", "translate("+ (margin.left/2) +","+(height/2)+")rotate(-90)")
  .attr("y", 6)
  .attr("dy", ".71em")
  .style("text-anchor", "end")
  .text("points");
  
svg.append("rect")
    .attr("class", "pane")
    .attr("width", width)
    .attr("height", height)
    .call(zoom);
    
var minDate,maxDate;
    

d3.json("data.json", function(error, data) {
  if (error) throw error;

  color.domain(d3.keys(data));
  
  //var minDate;
  //var maxDate;

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


  var player = svg.selectAll(".player")
      .data(players)
    .enter().append("g")
      .attr("class", "player");

  player.append("path")
      .attr("class", "line")
     // .attr("d", function(d) { return line(d.values); })
      .style("stroke", function(d) { return color(d.name); });
      
  svg.selectAll("path.line").attr("d", function(d) { return line(d.values); })    
   
});