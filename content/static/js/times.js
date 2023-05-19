function edit_race(race_id)
{
    var old_race = $('.current_race');
    if (old_race.length > 0)
    {
        $(old_race).find('.race_display').removeClass('d-none');
        $(old_race).find('.race_edit').addClass('d-none');
        $(old_race).removeClass('current_race');
        if (!$(old_race).is(':last-child'))
        {
            $(old_race).addClass('border-bottom');
        }
    }

    var new_race = $('#' + race_id);
    if (new_race.length > 0)
    {
        $(new_race).addClass('current_race');
        $(new_race).removeClass('border-bottom');
        $(new_race).find('.race_display').addClass('d-none');
        $(new_race).find('.race_edit').removeClass('d-none');
        $(new_race).find('.race_edit')[0].scrollIntoView(
            {
                behavior: 'smooth',
                block: 'center'
            }
        );
    }
}

function reset(race_id)
{
    var race = $('#' + race_id);
    if (race.prop('id') !== undefined)
    {
        $(race).find('input, select, .btn').attr('disabled', 'disabled');
        $(race).find('.wait').removeClass('d-none');
        $.get(
            window.location.href,
            function(data, status)
            {
                if (status === 'success')
                {
                    $('.content_panel').html($(data).find('.content_panel').html());
                    prep();
                }
                else
                {
                    edit_race(race_id);
                    $(race).find('input, select, .btn').removeAttr('disabled');
                    $(race).find('.wait').addClass('d-none');
                }
            }
        );
    }
}

function submit(race_id)
{
    var race = $('#' + race_id);
    if (race.prop('id') !== undefined)
    {
        $(race).find('input, select, .btn').attr('disabled', 'disabled');
        $(race).find('.wait').removeClass('d-none');

        var data = {};
        data['race_name'] = race.prop('id');
        for (let item of $(race).find('select, input'))
        {
            data[$(item).prop('name')] = $(item).val();
        }

        const csrftoken = getCookie('csrftoken');
        $.post(
            {
                url: window.location.href,
                data: data,
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    $('.content_panel').html($(data).find('.content_panel').html());
                    $('.menu').html($(data).find('.menu').html());
                    prep();
                }
                else
                {
                    $(race).find('input, select, .btn').removeAttr('disabled');
                    $(race).find('.wait').addClass('d-none');
                }
            }
        );
    }
}

function prep()
{
    $('.timetable_race > .race_display').find('.timetable_lane > .col_time').click(function()
    {
        edit_race($(this).parents('.timetable_race').prop('id'));
    });

    $('.button_enter_times').click(function()
    {
        submit($(this).parents('.timetable_race').prop('id'));
    });

    $('.button_cancel_edit').click(function()
    {
        reset($(this).parents('.timetable_race').prop('id'));
    });

    var cs = $('.current_race');
    if (cs.length > 0)
    {
        $(cs).removeClass('border-bottom');
        $(cs).find('.race_display').addClass('d-none');
        $(cs).find('.race_edit').removeClass('d-none');
        $(cs).find('.race_edit')[0].scrollIntoView(
            {
                behavior: 'smooth',
                block: 'center'
            }
        );
    }
}

$(document).ready(function()
{
    prep();
});
