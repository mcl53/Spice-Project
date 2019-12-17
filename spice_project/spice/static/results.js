// set the dimensions and margins of the graph
var margin = {top: 10, right: 30, bottom: 30, left: 40},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#data-vis")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// read data
var url = "/fingerprints/" + file_name
d3.csv(url, function(data) {
  // Add X axis
  var x = d3.scaleLinear()
    .domain([data[0]['x'], data[data.length - 1]['x']])
    .range([ margin.left, width - margin.right ]);
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

  // Add Y axis
  var y = d3.scaleLinear()
    .domain([data[0]['y'], data[data.length - 1]['y']])
    .range([ height - margin.bottom, margin.top ]);
  svg.append("g")
    .call(d3.axisLeft(y));

  // Get intensities
  var zData = data.map(function(d) { return parseFloat(d.z) })

  var max = zData.reduce(function(a, b) { return Math.max(a, b); });
  var min = zData.reduce(function(a, b) { return Math.min(a, b); });
  var z = d3.scaleLinear()
    .domain([min, max])
    .range([0, 100])
  // Prepare a color palette
  var color = d3.scaleLinear()
      .domain([0, 5]) // Points per square pixel.
      .range(["white", "#69b3a2"])
  // compute the density data
  var densityData = d3.contourDensity()
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); })
    .weight(function(d) { return z(d.z)})
    .size([width, height])
    .bandwidth(15)
    (data)

  // show the shape!
  svg.insert("g", "g")
    .selectAll("path")
    .data(densityData)
    .enter().append("path")
      .attr("d", d3.geoPath())
      .attr("fill", function(d) { return color(d.value); })
})