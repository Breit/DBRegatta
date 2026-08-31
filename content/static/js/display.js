var mouseTimer = null;
var cursorVisible = true;
var carouselRefreshInFlight = false;
var fallbackRefreshTimer = null;

function disappearCursor()
{
    mouseTimer = null;
    document.body.style.cursor = "none";
    cursorVisible = false;
}

function clearFallbackRefreshTimer()
{
    if (fallbackRefreshTimer)
    {
        window.clearTimeout(fallbackRefreshTimer);
        fallbackRefreshTimer = null;
    }
}

// with 0 or 1 slides Bootstrap never fires slide transition events, so fall back to a plain timer
function armFallbackRefreshIfNeeded()
{
    clearFallbackRefreshTimer();
    var slideCount = document.querySelectorAll("#resultsCarousel .carousel-item").length;
    if (slideCount <= 1)
    {
        fallbackRefreshTimer = window.setTimeout(refreshResultsCarousel, displayInterval);
    }
}

function refreshResultsCarousel()
{
    // skip instead of stacking a new request if the previous one is still pending
    if (carouselRefreshInFlight)
    {
        armFallbackRefreshIfNeeded();
        return;
    }
    carouselRefreshInFlight = true;

    $.ajax(
        {
            url: window.location.href,
            timeout: displayInterval,
            cache: false
        }
    ).done(
        function(html)
        {
            // plain DOM parsing avoids re-executing embedded <script> tags from the fetched page
            var scratch = document.createElement("div");
            scratch.innerHTML = html;
            var newCarousel = scratch.querySelector("#resultsCarousel");
            var oldCarousel = document.getElementById("resultsCarousel");
            if (newCarousel && oldCarousel)
            {
                // Bootstrap's Carousel instance caches references to the slide/indicator
                // nodes it was initialized with; swapping in fresh nodes without disposing
                // and recreating it leaves it cycling over detached elements, freezing the display
                var existingInstance = bootstrap.Carousel.getInstance(oldCarousel);
                if (existingInstance)
                {
                    existingInstance.dispose();
                }
                oldCarousel.innerHTML = newCarousel.innerHTML;
                new bootstrap.Carousel(oldCarousel);
            }
        }
    ).fail(
        function(jqXHR, textStatus)
        {
            console.error("Display refresh failed:", textStatus);
        }
    ).always(
        function()
        {
            carouselRefreshInFlight = false;
            armFallbackRefreshIfNeeded();
        }
    );
}

$(document).ready(
    function()
    {
        window.setInterval(
            function()
            {
                $("#liveClock").html(new Date().toLocaleTimeString('de-DE'));
            },
            1000
        );

        // refresh data right when the carousel completes a lap and lands back on the first slide
        $("#resultsCarousel").on(
            "slid.bs.carousel",
            function(event)
            {
                if (event.to === 0)
                {
                    clearFallbackRefreshTimer();
                    refreshResultsCarousel();
                }
            }
        );
        armFallbackRefreshIfNeeded();

        document.onmousemove = function()
        {
            if (mouseTimer)
            {
                window.clearTimeout(mouseTimer);
            }
            if (!cursorVisible)
            {
                document.body.style.cursor = "default";
                cursorVisible = true;
            }
            mouseTimer = window.setTimeout(disappearCursor, 1000);
        };

        window.setTimeout(disappearCursor, 100);
    }
);


