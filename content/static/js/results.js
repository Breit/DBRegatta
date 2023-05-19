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
    $('.rankings_table').each(
        function()
        {
            $(this).removeClass('d-none');
        }
    );

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

            $('.rankings_table').each(
                function()
                {
                    if ($(this).find('.col_team').text() !== team)
                    {
                        $(this).addClass('d-none');
                    }
                }
            );
        }
    }

    $('.timetable_race, .rankings_table')
        .removeClass('rounded-bottom')
        .addClass('border-bottom');
    $('.card-body').each(function()
        {
            $(this)
                .find('.timetable_race, .rankings_table')
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
    $('.timetable_lane, .rankings_table').click(function()
    {
        focus_team(this);
    });

    $('#results_pdf').click(function()
    {
        window.open(window.location.href + '/pdf');
    });
});