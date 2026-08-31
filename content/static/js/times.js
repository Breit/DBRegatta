function request_delete_race_times(race_name)
{
    $('#button_delete_race_times').prop('value', race_name);
    $('#del_race_times_warning').text(race_name);
    $('#deleteRaceTimesModal').modal('toggle');
}

function formatTime(value)
{
    var minutes = Math.floor(value / 60.0);
    var seconds = Math.floor(value - minutes * 60.0);
    var hundredth = Math.round(100.0 * (value - Math.floor(value)));
    function pad(n)
    {
        return (n < 10 ? '0' : '') + n;
    }
    return pad(minutes) + ':' + pad(seconds) + '.' + pad(hundredth);
}

// show not-yet-saved lane times in the display row (in italics/orange) and flag the race red if any are pending
function applyPendingTimes(race_id)
{
    var race = $('#' + race_id);
    var editLanes = $(race).find('.race_edit .timetable_lane');
    var displayLanes = $(race).find('.race_display .timetable_lane');
    var hasPending = false;

    editLanes.each(function(idx)
    {
        var min = parseFloat($(this).find('input[name^="lane_time_min_"]').val()) || 0.0;
        var sec = parseFloat($(this).find('input[name^="lane_time_sec_"]').val()) || 0.0;
        var hnd = parseFloat($(this).find('input[name^="lane_time_hnd_"]').val()) || 0.0;
        var time = min * 60.0 + sec + hnd / 100.0;
        var originalTime = parseFloat($(this).data('time')) || 0.0;

        var displayCell = $(displayLanes.get(idx)).find('.col_time .my-auto');
        if (Math.abs(time - originalTime) > 0.001)
        {
            displayCell.text(formatTime(time));
            displayCell.addClass('fst-italic pending_time');
            hasPending = true;
        }
        else
        {
            displayCell.removeClass('fst-italic pending_time');
        }
    });

    $(race).toggleClass('has_pending_times', hasPending);
    persistPendingTimes(race_id, hasPending);
}

// a full content_panel reload re-renders every race from saved server data, wiping out
// any typed-but-unsubmitted inputs elsewhere; capture/restore them around such reloads
function captureRaceTimeValues(race)
{
    var values = {};
    $(race).find('.race_edit input[name^="lane_time_"]').each(function()
    {
        values[$(this).prop('name')] = $(this).val();
    });
    return values;
}

function capturePendingTimes(exclude_race_id)
{
    var pending = {};
    $('.timetable_race').each(function()
    {
        var race_id = $(this).prop('id');
        if (race_id === exclude_race_id)
        {
            return;
        }
        var values = captureRaceTimeValues(this);
        if (Object.keys(values).length > 0)
        {
            pending[race_id] = values;
        }
    });
    return pending;
}

function restorePendingTimes(pending)
{
    $.each(pending, function(race_id, values)
    {
        var race = $('#' + race_id);
        if (race.length > 0)
        {
            $.each(values, function(name, value)
            {
                $(race).find('input[name="' + name + '"]').val(value);
            });
            applyPendingTimes(race_id);
        }
    });
}

// keep not-yet-submitted times around across a plain browser reload, since they only
// live in the input fields otherwise and a fresh page load would wipe them out
var PENDING_TIMES_STORAGE_KEY = 'dbregatta_pending_times';

function loadStoredPendingTimes()
{
    try
    {
        return JSON.parse(window.sessionStorage.getItem(PENDING_TIMES_STORAGE_KEY)) || {};
    }
    catch (e)
    {
        return {};
    }
}

function persistPendingTimes(race_id, hasPending)
{
    var stored = loadStoredPendingTimes();
    if (hasPending)
    {
        stored[race_id] = captureRaceTimeValues($('#' + race_id));
    }
    else
    {
        delete stored[race_id];
    }
    window.sessionStorage.setItem(PENDING_TIMES_STORAGE_KEY, JSON.stringify(stored));
}

function restoreStoredPendingTimes()
{
    var stored = loadStoredPendingTimes();
    var stale = false;
    $.each(stored, function(race_id, values)
    {
        var race = $('#' + race_id);
        if (race.length > 0)
        {
            $.each(values, function(name, value)
            {
                $(race).find('input[name="' + name + '"]').val(value);
            });
            applyPendingTimes(race_id);
        }
        else
        {
            delete stored[race_id];
            stale = true;
        }
    });
    if (stale)
    {
        window.sessionStorage.setItem(PENDING_TIMES_STORAGE_KEY, JSON.stringify(stored));
    }
}

function close_edit(race_id)
{
    var race = $('#' + race_id);
    if (race.length > 0)
    {
        applyPendingTimes(race_id);
        $(race).find('.race_display').removeClass('d-none');
        $(race).find('.race_edit').addClass('d-none');
        $(race).removeClass('editing_race');
        if (!$(race).is(':last-child'))
        {
            $(race).addClass('border-bottom');
        }
    }
}

function edit_race(race_id)
{
    var old_race = $('.editing_race');
    if (old_race.length > 0)
    {
        applyPendingTimes(old_race.prop('id'));
        $(old_race).find('.race_display').removeClass('d-none');
        $(old_race).find('.race_edit').addClass('d-none');
        $(old_race).removeClass('editing_race');
        if (!$(old_race).is(':last-child'))
        {
            $(old_race).addClass('border-bottom');
        }
    }

    var new_race = $('#' + race_id);
    if (new_race.length > 0)
    {
        $(new_race).addClass('editing_race');
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
        var pendingTimes = capturePendingTimes(race_id);
        $.get(
            window.location.href,
            function(data, status)
            {
                if (status === 'success')
                {
                    $('.content_panel').html($(data).find('.content_panel').html());
                    // discard any remembered pending times for the cancelled race before prep()
                    // re-applies sessionStorage, otherwise the stale values would come right back
                    persistPendingTimes(race_id, false);
                    prep();
                    restorePendingTimes(pendingTimes);
                    applyPendingTimes(race_id);
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

        var pendingTimes = capturePendingTimes(race_id);

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
                    restorePendingTimes(pendingTimes);
                    applyPendingTimes(race_id);
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
    $('.timetable_race > .race_display').click(function()
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

    $('.button_close_edit').click(function()
    {
        close_edit($(this).parents('.timetable_race').prop('id'));
    });

    $('#button_delete_race_times').click(function()
    {
        const csrftoken = getCookie('csrftoken');
        $('#wait_delete_race_times').removeClass('d-none').addClass('d-block');
        $('#button_delete_race_times').prop('disabled', true);
        $('#cancel_delete_race_times').prop('disabled', true);
        var race_name = $('#button_delete_race_times').prop('value');
        var pendingTimes = capturePendingTimes(race_name);
        $.post(
            {
                url: window.location.href,
                data: { delete_race_times: race_name },
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    $('.content_panel').html($(data).find('.content_panel').html());
                    prep();
                    restorePendingTimes(pendingTimes);
                    applyPendingTimes(race_name);
                }
                else
                {
                    $('#wait_delete_race_times').removeClass('d-block').addClass('d-none');
                    $('#button_delete_race_times').prop('disabled', false);
                    $('#cancel_delete_race_times').prop('disabled', false);
                }
            }
        );
    });

    var cs = $('.live_race');
    if (cs.length > 0)
    {
        $(cs).addClass('editing_race');
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

    restoreStoredPendingTimes();
}

$(document).ready(function()
{
    prep();
});
