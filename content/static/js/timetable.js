function button_save_post(edit_id)
{
    $('#wait_post').removeClass('d-none').addClass('d-block');

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

            $('#wait_post').removeClass('d-block').addClass('d-none');

            $('#editPost').prop('disabled', false);
            $('#cancelEditPost').prop('disabled', false);

            $('#editPostModal').modal('toggle');
        }
    );
}

function button_edit_race(race_name)
{
    $('#wait_race').removeClass('d-none').addClass('d-block');

    $('#editRace').prop('disabled', true);
    $('#cancelEditRace').prop('disabled', true);

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: {
                'editRace': race_name
            },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('#editRaceModal').html($(data).find('#editRaceModal').html());
            }

            $('#wait_race').removeClass('d-block').addClass('d-none');

            $('#editRace').prop('disabled', false);
            $('#cancelEditRace').prop('disabled', false);

            $('#editRaceModal').modal('toggle');
        }
    );
}

function button_save_race(race_name, lanes)
{
    $('#wait_race').removeClass('d-none').addClass('d-block');

    $('#editRace').prop('disabled', true);
    $('#cancelEditRace').prop('disabled', true);

    let assignments = new Array()
    for (let i = 1; i <= lanes; i++)
    {
        let team = $('#team_' + i.toString()).val();
        if (team)
        {
            assignments.push(
                {
                    lane: i,
                    team: +team
                }
            );
        }
    }

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: {
                saveRace: race_name,
                assignments: JSON.stringify(assignments)
            },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('.menu').html($(data).find('.menu').html());
                $('#timetable_content').html($(data).find('#timetable_content').html());
            }

            $('#wait_race').removeClass('d-block').addClass('d-none');

            $('#editRace').prop('disabled', false);
            $('#cancelEditRace').prop('disabled', false);

            $('#editRaceModal').modal('toggle');
        }
    );
}

function team_changed(obj, options, id)
{
    if (obj)
    {
        console.log(obj);
        index = obj.selectedIndex
        if (options instanceof Array && index >= 0 && index < options.length)
        {
            $('#' + id).html(options[index].company);
        }
    }
}

function trigger(action)
{
    const csrftoken = getCookie('csrftoken');
    var data = {};
    if (action)
    {
        data[action] = true;
    }

    if ($('#wait_' + action).length > 0)
    {
        $('#wait_' + action).removeClass('d-none').addClass('d-block');
    }
    if ($('#' + action + 'Submit').length > 0)
    {
        $('#' + action + 'Submit').prop('disabled', true);
    }
    if ($('#' + action + 'Cancel').length > 0)
    {
        $('#' + action + 'Cancel').prop('disabled', true);
    }

    $.post(
        {
            url: window.location.href,
            data: data,
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status)
        {
            if ($('#wait_' + action).length > 0)
            {
                $('#wait_' + action).removeClass('d-block').addClass('d-none');
            }

            if ($('#' + action + 'Modal').length > 0)
            {
                $('#' + action + 'Modal').modal('hide');
            }
            if (status === 'success')
            {
                const main = data.match(/<main.*?>.*?<\/main.*?>/s);
                if (main.length > 0)
                {
                    $('main').html(main);
                }
            }
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

    $('#timetable_pdf').click(function()
    {
        window.open(window.location.href + '/pdf');
    });
});
