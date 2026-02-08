#!/usr/bin/env python3

import anywidget
import traitlets
from shapely.geometry import Point, LineString
import numpy as np


class ChooseLineWidget(anywidget.AnyWidget):
    # Traitlets for bidirectional communication
    data = traitlets.List([]).tag(sync=True)
    x_col = traitlets.Unicode("x").tag(sync=True)
    y_col = traitlets.Unicode("y").tag(sync=True)
    line_points = traitlets.List([]).tag(sync=True)  # In DATA coordinates

    _esm = """
    async function render({ model, el }) {
      // Import D3 from CDN
      const d3 = await import("https://cdn.jsdelivr.net/npm/d3@7/+esm");

      // Set up dimensions
      const width = 600;
      const height = 400;
      const margin = { top: 20, right: 20, bottom: 50, left: 60 };

      // Create SVG
      const svg = d3.select(el)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // Create main group for zoomable content
      const g = svg.append("g");

      // Get data and column names from Python
      const data = model.get("data");
      const xCol = model.get("x_col");
      const yCol = model.get("y_col");

      // Extract x and y values
      const xValues = data.map(d => d[xCol]);
      const yValues = data.map(d => d[yCol]);

      // Create scales with proper domains
      const xScale = d3.scaleLinear()
        .domain(d3.extent(xValues))
        .range([margin.left, width - margin.right]);

      const yScale = d3.scaleLinear()
        .domain(d3.extent(yValues))
        .range([height - margin.bottom, margin.top]);

      // Create axes
      const xAxis = d3.axisBottom(xScale);
      const yAxis = d3.axisLeft(yScale);

      // Add X axis
      const xAxisGroup = svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(xAxis);

      // Add Y axis
      const yAxisGroup = svg.append("g")
        .attr("class", "y-axis")
        .attr("transform", `translate(${margin.left},0)`)
        .call(yAxis);

      // Add axis labels
      svg.append("text")
        .attr("class", "x-label")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height - 10)
        .style("font-size", "12px")
        .text(xCol);

      svg.append("text")
        .attr("class", "y-label")
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .attr("y", 15)
        .attr("x", -height / 2)
        .style("font-size", "12px")
        .text(yCol);

      // Draw scatter points
      g.selectAll("circle")
        .data(data)
        .join("circle")
        .attr("cx", d => xScale(d[xCol]))
        .attr("cy", d => yScale(d[yCol]))
        .attr("r", 5)
        .attr("fill", "steelblue")
        .attr("opacity", 0.7);

      // Array to store line points (in pixel coordinates for drawing)
      let linePointsPixels = [];
      const lineGroup = g.append("g").attr("class", "line-group");

      // Function to update the polyline
      function updateLine() {
        lineGroup.selectAll("line").remove();
        lineGroup.selectAll("circle").remove();

        for (let i = 0; i < linePointsPixels.length - 1; i++) {
          lineGroup.append("line")
            .attr("x1", linePointsPixels[i].x)
            .attr("y1", linePointsPixels[i].y)
            .attr("x2", linePointsPixels[i + 1].x)
            .attr("y2", linePointsPixels[i + 1].y)
            .attr("stroke", "red")
            .attr("stroke-width", 2);
        }

        // Draw circles at click points
        lineGroup.selectAll("circle")
          .data(linePointsPixels)
          .join("circle")
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)
          .attr("r", 4)
          .attr("fill", "red");
      }

      // Function to convert pixel coordinates to data coordinates
      function pixelsToData(xPixel, yPixel) {
        return {
          x: xScale.invert(xPixel),
          y: yScale.invert(yPixel)
        };
      }

      // Function to convert data coordinates to pixel coordinates
      function dataToPixels(xData, yData) {
        return {
          x: xScale(xData),
          y: yScale(yData)
        };
      }

      // Keep track of current scales (updated with zoom)
      let currentXScale = xScale.copy();
      let currentYScale = yScale.copy();

      // Set up zoom behavior
      const zoom = d3.zoom()
        .scaleExtent([0.5, 10])
        .on("zoom", (event) => {
          const transform = event.transform;

          // Update the plot elements
          g.attr("transform", transform);

          // Update scales for axes
          currentXScale = transform.rescaleX(xScale);
          currentYScale = transform.rescaleY(yScale);

          // Update axes
          xAxisGroup.call(xAxis.scale(currentXScale));
          yAxisGroup.call(yAxis.scale(currentYScale));
        });

      svg.call(zoom);

      // Click handler to add points to line
      svg.on("click", function(event) {
        // Get mouse coordinates
        const transform = d3.zoomTransform(g.node());
        const [mouseX, mouseY] = d3.pointer(event, svg.node());

        // Transform coordinates back to original pixel scale
        const x = (mouseX - transform.x) / transform.k;
        const y = (mouseY - transform.y) / transform.k;

        // Store in pixel coordinates for drawing
        linePointsPixels = [...linePointsPixels, { x: x, y: y }];

        // Convert all points to data coordinates for Python
        const dataPoints = linePointsPixels.map(p =>
          pixelsToData(p.x, p.y)
        );

        // Sync to Python (in data coordinates)
        model.set("line_points", dataPoints);
        model.save_changes();

        updateLine();
      });

      // Double-click to clear the line
      svg.on("dblclick.clear", function(event) {
        event.preventDefault();

        // Clear both arrays
        linePointsPixels = [];

        // Sync to Python
        model.set("line_points", []);
        model.save_changes();

        updateLine();
      });

      // Prevent default zoom on double-click
      svg.on("dblclick.zoom", null);

      // Listen for changes from Python (convert data coords to pixels)
      model.on("change:line_points", () => {
        const dataPoints = model.get("line_points") || [];
        // Convert data coordinates to pixel coordinates
        linePointsPixels = dataPoints.map(p =>
          dataToPixels(p.x, p.y)
        );
        updateLine();  // CRITICAL: Call updateLine to redraw
      });

      // Initialize line from Python if present
      const initialDataPoints = model.get("line_points") || [];
      if (initialDataPoints.length > 0) {
        linePointsPixels = initialDataPoints.map(p =>
          dataToPixels(p.x, p.y)
        );
        updateLine();
      }
    }

    export default { render };
    """

    _css = """
    svg {
      border: 1px solid #ccc;
      background-color: #fafafa;
      cursor: crosshair;
    }
    .x-axis line, .y-axis line {
      stroke: #666;
    }
    .x-axis path, .y-axis path {
      stroke: #666;
    }
    .x-axis text, .y-axis text {
      fill: #333;
      font-size: 11px;
    }
    """

    def __init__(self, df=None, x_col="x", y_col="y", **kwargs):
        """
        Initialize widget with a Polars DataFrame.

        Parameters:
        -----------
        df : polars.DataFrame
            The dataframe containing scatter plot data
        x_col : str
            Name of the column to use for x-axis
        y_col : str
            Name of the column to use for y-axis
        """
        super().__init__(**kwargs)

        if df is not None:
            # Convert Polars DataFrame to list of dicts for JSON serialization
            self.data = df.select([x_col, y_col]).to_dicts()
            self.x_col = x_col
            self.y_col = y_col


def sort_along(line_points, data_df, threshold = None, x_col = "X", y_col = "Y"):
    polyline = LineString(  [ (d["x"], d["y"]) for  d in line_points])
    n, _ = data_df.shape
    dists_along = np.zeros(n, dtype= "float32")
    dists_from = np.zeros(n, dtype= "float32")
    for i, d in enumerate(data_df.to_dicts()):
        point = Point(d[x_col], d[y_col])
        dist_along = polyline.project(point)
        dist_from =  point.distance(polyline)
        dists_along[i] = dist_along
        dists_from[i] = dist_from
    idx = np.argsort(dists_along)
    if threshold is not None:
        idx = idx[dists_from < threshold]
    return idx
