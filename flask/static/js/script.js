// Function to handle form submission using AJAX
function submitForm(event) {
    event.preventDefault(); // Prevent the default form submission behavior
    // Clear the response container before making the AJAX request
    $("#response-container").empty();
    var formData = $("#form_with_schedule").serialize();
    $.post("/solve", formData, function (data) {
        // Append the response data to the response container
        $("#response-container").append("<div class=" + "response" + ">" + data + "</div>");

        // Clear the input field after form submission
        $("#input_with_schedule").val("");

        // Scroll to the bottom to show the latest response
        $("#response-container").scrollTop($("#response-container")[0].scrollHeight);
    });
}

$(document).ready(function () {
    $("#clear_button").click(function () {
        $("#response-container").empty();
    });
});