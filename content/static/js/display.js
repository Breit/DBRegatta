var mouseTimer = null;
var cursorVisible = true;

function disappearCursor()
{
    mouseTimer = null;
    document.body.style.cursor = "none";
    cursorVisible = false;
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
        window.setInterval(
            function()
            {
                $("#resultsCarousel").load(window.location.href + " #resultsCarousel");
            },
            displayDataRefresh
        );

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


