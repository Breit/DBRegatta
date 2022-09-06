$(document).ready(
    function() {
        window.setInterval(
            function() {
                $("#resultsCarousel").load(window.location.href + " #resultsCarousel");
            },
            displayDataRefresh);
    }
);
