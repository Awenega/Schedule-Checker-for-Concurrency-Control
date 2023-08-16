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
        else if (data.precedence_graph == null) {
            var responseData = data.data;

            // Precedence graph not available in the JSON data
            // Append the response data to the response container
            $("#response-container").append("<div class='response'>" + responseData + "</div>");

            // Clear the input field after form submission
            $("#input_with_schedule").val("");

            // Scroll to the bottom to show the latest response
            $("#response-container").scrollTop($("#response-container")[0].scrollHeight);

            // Update button states after receiving the response
            updateButtonStates();
        } else {
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
        }

        var schedulesJson = localStorage.getItem("schedules") || [];
        if (schedulesJson.length !== 0) {
            console.log()
            var schedulesList = JSON.parse(schedulesJson);
        } else {
            var schedulesList = schedulesJson;
        }

        var schedule = data.schedule;
        schedulesList.unshift(schedule);

        var updatedSchedulesJson = JSON.stringify(schedulesList);

        localStorage.setItem("schedules", updatedSchedulesJson);
    });
}

$(document).ready(function () {
    // Initialize button states on page load
    updateButtonStates();

    $("#solve_button").prop("disabled", true);

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Show tooltip on hover when the button is disabled
    $("#solve_button").hover(
        function () {
            if ($(this).prop("disabled")) {
                $(this).tooltip("show");
            }
        },
        function () {
            if ($(this).prop("disabled")) {
                $(this).tooltip("hide");
            }
        }
    );

    $("#empty_button").click(function () {
        localStorage.removeItem('schedules');
        $("#list_schedules").html("No schedule submitted!");
    }
    );

    // Add event listener to checkboxes
    $("input[name='possibility']").on("change", function () {
        // Check if any checkbox is checked
        if ($("input[name='possibility']:checked").length > 0) {
            // Enable the Solve button
            $("#solve_button").prop("disabled", false);
        } else {
            // Disable the Solve button
            $("#solve_button").prop("disabled", true);
        }
    });

    // Handle Clear button click
    $("#clear_button").click(function () {
        $("#response-container").empty();
        $("#precedence-graph-container").empty();
        // Update button states after clearing the response
        updateButtonStates();
    });

    $("#history_button").click(function () {
        var schedulesJson = localStorage.getItem("schedules") || [];
        if (schedulesJson.length !== 0) {
            $("#list_schedules").html("");
            var schedulesList = JSON.parse(schedulesJson);
            var listSchedules = $("#list_schedules")
            var i = 0;
            schedulesList.forEach(function (value) {
                const div = $("<div>").addClass("pastSchedule");
                const p = $("<p>").addClass("textPastSchedule").text(value).attr("id", "Schedule" + i);
                div.append(p);

                const divInner = $("<div>").addClass("copy-button-container");

                const button = $("<button>").attr("id", "copy_button " + i).addClass("btn btn-default px-3 sapienza-button copy-button");
                button.on("click", function () {
                    copyValue(this.id.split(" ")[1]);
                });

                const icon = $("<i>").addClass("fa-solid fa-copy icon-of-page");
                button.append(icon);
                divInner.append(button);
                div.append(divInner);

                i++;

                listSchedules.append(div);
            });
        } else {
            $("#list_schedules").html("No schedule submitted!");
        }
        $("#popupContainer").css("display", "flex");
    });

    $("#close_button").click(function () {
        $("#popupContainer").css("display", "none");
        $("#list_schedules").html("");
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
    $("#precedence-graph-container").html("<h4>Precedence Graph:</h4>");
    // Extract unique IDs from the precedenceGraph

    if (precedenceGraph.length > 0) {
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
    } else {
        $("#precedence-graph-container").append("<p>There are no conflicting actions, the Precedence graph is empty!")
    }
}

function copyValue(value) {
    var textToCopy = $("#Schedule" + value).text();

    // Create a temporary textarea element to hold the text
    var tempTextArea = $("<textarea>");
    tempTextArea.val(textToCopy);
    $("body").append(tempTextArea);

    // Select and copy the text from the temporary textarea
    tempTextArea.select();
    document.execCommand("copy");

    // Remove the temporary textarea
    tempTextArea.remove();

    alert("Text copied to clipboard: " + textToCopy);
}