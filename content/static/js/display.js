$(document).ready(
    function()
    {
        window.setInterval(
            function() {
                $("#liveClock").html(new Date().toLocaleTimeString('de-DE'));
            },
            1000
        );
        window.setInterval(
            function() {
                $("#resultsCarousel").load(window.location.href + " #resultsCarousel");
            },
            displayDataRefresh
        );
    }
);
