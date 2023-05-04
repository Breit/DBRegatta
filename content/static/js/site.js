function getCookie(name)
{
    let cookieValue = null;
    if (document.cookie && document.cookie !== '')
    {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++)
        {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '='))
            {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleFoldMenu()
{
    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: { menu_fold_toggle: true },
            headers: { 'X-CSRFToken': csrftoken }
        }
    );

    var listItems = $("#folded li");
    if (listItems.length === 0)
    {
        var listItems = $("#full li");
        listItems.each(
            function(idx, li)
            {
                $(li).find("a span.item_title").addClass("d-none");
                $(li).find("a div.item_badges").addClass("d-none");
            }
        );
        $("#full").attr("id", "folded");
    }
    else
    {
        listItems.each(
            function(idx, li)
            {
                $(li).find("a span.item_title").removeClass("d-none");
                $(li).find("a div.item_badges").removeClass("d-none");
            }
        );
        $("#folded").attr("id", "full");
    }
}

function registerTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-tooltip]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    var tooltipExTriggerList = [].slice.call(document.querySelectorAll('[data-bs-tooltip-ex]'))
    var tooltipExList = tooltipExTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            html: true,
            customClass: 'tooltip-text-left'
        })
    });
}

$(document).ready(function()
{
    registerTooltips();

    $('.card-body.collapse').on('show.bs.collapse', function () {
        $(this).siblings('.card-header').removeClass('card-header-collapsed');
    });

    $('.card-body.collapse').on('hidden.bs.collapse', function () {
        $(this).siblings('.card-header').addClass('card-header-collapsed');
    });
});
