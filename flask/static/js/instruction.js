$(document).ready(function () {
    $("#home").click(function () {
        window.location.href = "/";
    });
    $(".github").click(function () {
        var githubUrl = "https://github.com/Pancio-code/Project-Data-Management";
        window.open(githubUrl, "_blank");
    });
});