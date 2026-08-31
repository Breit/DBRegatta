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
        fallbackRefreshTimer = window.setTimeout(
            function()
            {
                refreshResultsCarousel(0);
            },
            displayInterval
        );
    }
}

// targetIndex is where the carousel just landed with the (still stale) current content
function refreshResultsCarousel(targetIndex)
{
    // skip instead of stacking a new request if the previous one is still pending
    if (carouselRefreshInFlight)
    {
        armFallbackRefreshIfNeeded();
        return;
    }
    carouselRefreshInFlight = true;

    var oldCarousel = document.getElementById("resultsCarousel");
    var oldSlideCount = oldCarousel.querySelectorAll(".carousel-item").length;

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
            if (newCarousel && oldCarousel)
            {
                var newItems = newCarousel.querySelectorAll(".carousel-item");
                var newIndicators = newCarousel.querySelectorAll(".carousel-indicators button");
                // keep advancing normally unless the page count changed, then restart the loop
                var activeIndex = (newItems.length === oldSlideCount) ? targetIndex : 0;
                activeIndex = Math.min(Math.max(activeIndex, 0), Math.max(newItems.length - 1, 0));

                newItems.forEach(
                    function(item, idx)
                    {
                        item.classList.toggle("active", idx === activeIndex);
                    }
                );
                newIndicators.forEach(
                    function(button, idx)
                    {
                        button.classList.toggle("active", idx === activeIndex);
                    }
                );

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

        // refresh data on every page switch, continuing at the same position unless the page count changed
        $("#resultsCarousel").on(
            "slid.bs.carousel",
            function(event)
            {
                clearFallbackRefreshTimer();
                refreshResultsCarousel(event.to);
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


