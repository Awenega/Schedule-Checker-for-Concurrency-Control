// Function to handle form submission using AJAX
function submitForm(event) {
    event.preventDefault(); // Prevent the default form submission behavior
    // Clear the response container before making the AJAX request
    $("#response-container").empty();
    $("#precedence-graph-container").empty();
    var formData = $("#form_with_schedule").serialize();
    $.post("/solve", formData, function (data) {

        if (data.precedence_graph === undefined) {
            // Precedence graph not available in the JSON data
            // Append the response data to the response container
            $("#response-container").append("<div class='response'>" + data + "</div>");

            // Clear the input field after form submission
            $("#input_with_schedule").val("");

            // Scroll to the bottom to show the latest response
            $("#response-container").scrollTop($("#response-container")[0].scrollHeight);

            // Update button states after receiving the response
            updateButtonStates();
            return;
        }
        // Extract the response data and precedence graph from the JSON data
        var responseData = data.data;
        var precedenceGraph = data.precedence_graph;

        // Append the response data to the response container
        $("#response-container").append("<div class='response'>" + responseData + "</div>");

        // Clear the input field after form submission
        $("#input_with_schedule").val("");

        // Scroll to the bottom to show the latest response
        $("#response-container").scrollTop($("#response-container")[0].scrollHeight);

        // Update button states after receiving the response
        updateButtonStates();
        // Display the precedence graph using d3.js
        drawPrecedenceGraph(precedenceGraph);
    });
}

$(document).ready(function () {
    // Initialize button states on page load
    updateButtonStates();

    // Handle Clear button click
    $("#clear_button").click(function () {
        $("#response-container").empty();
        $("#precedence-graph-container").empty();
        // Update button states after clearing the response
        updateButtonStates();
    });

    // Handle Instruction button click
    $(".tutorial").click(function () {
        // Replace the URL with the destination page URL
        window.location.href = "/instruction";
    });
});

function updateButtonStates() {
    const responseContainer = $("#response-container");
    const clearButton = $("#clear_button");

    // Enable/disable Clear button based on response container content
    if (responseContainer.text().trim() === "") {
        clearButton.prop("disabled", true);
    } else {
        clearButton.prop("disabled", false);
    }
}



function drawPrecedenceGraph(precedenceGraph) {

    // Update the title with the specified text
    $("#precedence-graph-container").html("<b>Precedence Graph</b>");
    // Extract unique IDs from the precedenceGraph
    const uniqueIds = [...new Set(precedenceGraph.flat())];

    // Create SVG
    const svgWidth = 400;
    const svgHeight = 200;
    const svg = d3.select("#precedence-graph-container")
        .append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight);

    // Add arrow marker
    svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("refX", 6)
        .attr("refY", 2)
        .attr("markerWidth", 6)
        .attr("markerHeight", 4)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,0 V4 L6,2 Z") // Arrowhead path
        .style("fill", "#000000");

    // Create links
    const links = [];
    for (let i = 0; i < precedenceGraph.length; i++) {
        const [source, target] = precedenceGraph[i];
        links.push({ source, target });
    }

    const linkElements = svg.append("g")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("x1", d => Math.cos((uniqueIds.indexOf(d.source) / uniqueIds.length) * 2 * Math.PI) * 50 + svgWidth / 2)
        .attr("y1", d => Math.sin((uniqueIds.indexOf(d.source) / uniqueIds.length) * 2 * Math.PI) * 50 + svgHeight / 2)
        .attr("x2", d => Math.cos((uniqueIds.indexOf(d.target) / uniqueIds.length) * 2 * Math.PI) * 50 + svgWidth / 2)
        .attr("y2", d => Math.sin((uniqueIds.indexOf(d.target) / uniqueIds.length) * 2 * Math.PI) * 50 + svgHeight / 2)
        .attr("marker-end", "url(#arrowhead)")
        .style("stroke", "#000000")
        .style("stroke-width", 2);

    const nodeElements = svg.append("g")
        .selectAll("circle")
        .data(uniqueIds)
        .enter().append("circle")
        .attr("r", 20)
        .attr("cx", d => Math.cos((uniqueIds.indexOf(d) / uniqueIds.length) * 2 * Math.PI) * 70 + svgWidth / 2)
        .attr("cy", d => Math.sin((uniqueIds.indexOf(d) / uniqueIds.length) * 2 * Math.PI) * 70 + svgHeight / 2)
        .style("fill", "#66ccff")
        .style("stroke", "#333")
        .style("stroke-width", 2)
        .style("pointer-events", "none");

    const labelElements = svg.append("g")
        .selectAll("text")
        .data(uniqueIds)
        .enter().append("text")
        .text(d => d)
        .attr("x", d => Math.cos((uniqueIds.indexOf(d) / uniqueIds.length) * 2 * Math.PI) * 70 + svgWidth / 2)
        .attr("y", d => Math.sin((uniqueIds.indexOf(d) / uniqueIds.length) * 2 * Math.PI) * 70 + svgHeight / 2 + 4)
        .style("text-anchor", "middle")
        .style("fill", "#333");

    // Center the SVG element within its container
    const containerWidth = $("#precedence-graph-container").width();
    const leftMargin = (containerWidth - svgWidth) / 2;
    $("svg").css("margin-left", `${leftMargin}px`);
}