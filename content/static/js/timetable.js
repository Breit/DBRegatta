function button_save_post(edit_id)
{
    $('#wait').removeClass('d-none').addClass('d-block');

    $('#editPost').prop('disabled', true);
    $('#cancelEditPost').prop('disabled', true);

    var enable = 'off';
    if ($(edit_id).find('#id_enable').prop('checked'))
    {
        enable = 'on';
    }

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: {
                'content': $(edit_id).find('#id_content').val(),
                'enable': enable
            },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('#timetable_post').html($(data).find('#timetable_post').html());
            }

            $('#wait').removeClass('d-block').addClass('d-none');

            $('#editPost').prop('disabled', false);
            $('#cancelEditPost').prop('disabled', false);

            $('#editPostModal').modal('toggle');
        }
    );
}

function focus_team(lane)
{
    const is_focused = $('#site_title > span').length > 0;
    $('#site_title > span').remove();
    for (let race of $('.timetable_race'))
    {
        $(race).removeClass('d-none');
        $(race).find('.timetable_lane > .col_team').each(
            function()
            {
                $(this).addClass('fw-bold');
            }
        );
    }

    if (is_focused <= 0)
    {
        const team = $(lane).find('.col_team').text();

        if (team !== undefined)
        {
            $('#site_title').append('<span>: ' + team + '</span>');

            for (let race of $('.timetable_race'))
            {
                var team_race = false;
                $(race).find('.timetable_lane > .col_team').each(
                    function()
                    {
                        if ($(this).text() === team)
                        {
                            team_race = true;
                        }
                        else
                        {
                            $(this).removeClass('fw-bold');
                        }
                    }
                );
                if (!team_race)
                {
                    $(race).addClass('d-none');
                }
            }
        }
    }

    $('.timetable_race')
        .removeClass('rounded-bottom')
        .addClass('border-bottom');
    $('.card-body').each(function()
        {
            $(this)
                .find('.timetable_race')
                .siblings()
                .not('.d-none')
                .last()
                .addClass('rounded-bottom')
                .removeClass('border-bottom');
        }
    );
}

$(document).ready(function()
{
    $('.timetable_lane').click(function()
    {
        focus_team(this);
    });
});
