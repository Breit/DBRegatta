function button_toggle_team(action, team_id)
{
    const csrftoken = getCookie('csrftoken');
    var data = {};
    data[action] = team_id;

    $.post(
        {
            url: window.location.href,
            data: data,
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('.menu').html($(data).find('.menu').html());
                $('#team_table').html($(data).find('#team_table').html());
            }
        }
    );
}

function request_delete_team(team_name, team_id)
{
    $('#button_delete_team').prop('value', team_id);
    $('#del_team_warning').text(team_name);
    $('#deleteTeamModal').modal('toggle');
}

function request_delete_category(category_name, category_id)
{
    $('#button_delete_category').prop('value', category_id);
    $('#del_category_warning').text(category_name);
    $('#deleteCategoryModal').modal('toggle');
}

function button_mod_team(team_id)
{
    $('#team_' + team_id).addClass('team_edit');
    $('#team_' + team_id)[0].scrollIntoView();

    $('#wait').removeClass('d-none').addClass('d-block');

    $('#button_edit_team').prop('disabled', true);
    $('#button_cancel_team').prop('disabled', true);

    $('#team_form').attr('name', 'mod_team');
    $('#button_edit_team').prop('value', team_id);

    $('#formAddTeamLabel').removeClass('d-block').addClass('d-none');
    $('#formEditTeamLabel').removeClass('d-none').addClass('d-block');

    $('#button_add_team').removeClass('d-block').addClass('d-none');
    $('#button_edit_team').removeClass('d-none').addClass('d-block');

    $('#formTeamModal').modal('toggle');

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: { 'edit_team': team_id },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('#team_form').html($(data).find('#team_form').html());
            }

            $('#wait').removeClass('d-block').addClass('d-none');

            $('#button_edit_team').prop('disabled', false);
            $('#button_cancel_team').prop('disabled', false);
        }
    );
}

function button_mod_category(category_id)
{
    $('#category_' + category_id).addClass('category_edit');
    $('#category_' + category_id)[0].scrollIntoView();

    $('#wait').removeClass('d-none').addClass('d-block');

    $('#button_edit_category').prop('disabled', true);
    $('#button_cancel_category').prop('disabled', true);

    $('#category_form').attr('name', 'mod_category');
    $('#button_edit_category').prop('value', category_id);

    $('#formAddCategoryLabel').removeClass('d-block').addClass('d-none');
    $('#formEditCategoryLabel').removeClass('d-none').addClass('d-block');

    $('#button_add_category').removeClass('d-block').addClass('d-none');
    $('#button_edit_category').removeClass('d-none').addClass('d-block');

    $('#formCategoryModal').modal('toggle');

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: { 'edit_category': category_id },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('#category_form').html($(data).find('#category_form').html());
            }

            $('#wait').removeClass('d-block').addClass('d-none');

            $('#button_edit_category').prop('disabled', false);
            $('#button_cancel_category').prop('disabled', false);
        }
    );
}

$(document).ready(function()
{
    $('#team_form').submit(function(e)
    {
        e.preventDefault();

        $('#wait').removeClass('d-none').addClass('d-block');

        $('#button_add_team').prop('disabled', true);
        $('#button_edit_team').prop('disabled', true);
        $('#button_cancel_team').prop('disabled', true);

        var edit_team = false;
        var edit_id = null;
        if ($("#team_form").attr('name') == 'mod_team')
        {
            edit_team = true;
            edit_id = $("#button_edit_team").prop('value');
        }
        const csrftoken = getCookie('csrftoken');
        var form_data = null;
        if (edit_team)
        {
            form_data = 'mod_team=';
            form_data += edit_id;
            form_data += '&';
            form_data += $(this).serialize();
        }
        else
        {
            form_data = 'add_team=&';
            form_data += $(this).serialize();
        }

        $.post(
            {
                url: window.location.href,
                data: form_data,
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    $('.menu').html($(data).find('.menu').html());
                    $('#team_table').html($(data).find('#team_table').html());

                    const form_content = $(data).find('#team_form');
                    $('#team_form').html(form_content.html());
                    $('#team_form').attr('name', form_content.attr('name'));
                }

                $('#wait').removeClass('d-block').addClass('d-none');

                $('#button_add_team').prop('disabled', false);
                $('#button_edit_team').prop('disabled', false);
                $('#button_cancel_team').prop('disabled', false);

                if (!$('#team_form .input-error').length)
                {
                    $('#formTeamModal').modal('toggle');

                    $('#formAddTeamLabel').removeClass('d-none').addClass('d-block');
                    $('#formEditTeamLabel').removeClass('d-block').addClass('d-none');

                    $('#button_add_team').removeClass('d-none').addClass('d-block');
                    $('#button_edit_team').removeClass('d-block').addClass('d-none');

                    $('.content_panel').scrollTop($('.content_panel')[0].scrollHeight);

                    if (edit_team && edit_id !== null && edit_id !== undefined)
                    {
                        $('#team_' + edit_id).removeClass('team_edit');
                    }
                }
                else
                {
                    if (edit_team)
                    {
                        $("#team_form").attr('name', 'mod_team');
                    }
                }
            }
        );
    });

    $('#category_form').submit(function(e)
    {
        e.preventDefault();

        $('#wait').removeClass('d-none').addClass('d-block');

        $('#button_add_category').prop('disabled', true);
        $('#button_edit_category').prop('disabled', true);
        $('#button_cancel_category').prop('disabled', true);

        var edit_category = false;
        var edit_id = null;
        if ($("#category_form").attr('name') == 'mod_category')
        {
            edit_category = true;
            edit_id = $("#button_edit_category").prop('value');
        }
        const csrftoken = getCookie('csrftoken');
        var form_data = null;
        if (edit_category)
        {
            form_data = 'mod_category=';
            form_data += edit_id;
            form_data += '&';
            form_data += $(this).serialize();
        }
        else
        {
            form_data = 'add_category=&';
            form_data += $(this).serialize();
        }

        $.post(
            {
                url: window.location.href,
                data: form_data,
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    $('.menu').html($(data).find('.menu').html());
                    $('#team_table').html($(data).find('#team_table').html());

                    const form_content = $(data).find('#category_form');
                    $('#category_form').html(form_content.html());
                    $('#category_form').attr('name', form_content.attr('name'));
                }

                $('#wait').removeClass('d-block').addClass('d-none');

                $('#button_add_category').prop('disabled', false);
                $('#button_edit_category').prop('disabled', false);
                $('#button_cancel_category').prop('disabled', false);

                if (!$('#category_form .input-error').length)
                {
                    $('#formCategoryModal').modal('toggle');

                    $('#formAddCategoryLabel').removeClass('d-none').addClass('d-block');
                    $('#formEditCategoryLabel').removeClass('d-block').addClass('d-none');

                    $('#button_add_category').removeClass('d-none').addClass('d-block');
                    $('#button_edit_category').removeClass('d-block').addClass('d-none');

                    $('.content_panel').scrollTop($('.content_panel')[0].scrollHeight);

                    if (edit_category && edit_id !== null && edit_id !== undefined)
                    {
                        $('#category_' + edit_id).removeClass('category_edit');
                    }
                }
                else
                {
                    if (edit_category)
                    {
                        $("#category_form").attr('name', 'mod_category');
                    }
                }
            }
        );
    });

    $('#button_cancel_team, #button_cancel_team_x').click(function()
    {
        var edit_team = false;
        var edit_id = null;
        if ($("#team_form").attr('name') === 'mod_team')
        {
            edit_team = true;
            edit_id = $("#button_edit_team").prop('value');
        }

        $.get(
            {
                url: window.location.href
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    const form_content = $(data).find('#team_form');
                    $('#team_form').html(form_content.html());
                    $('#team_form').attr('name', form_content.attr('name'));
                }

                if (edit_team && edit_id !== null && edit_id !== undefined)
                {
                    $('#team_' + edit_id).removeClass('team_edit');
                }

                $('#team_form').trigger('reset');

                $('#formAddTeamLabel').removeClass('d-none').addClass('d-block');
                $('#formEditTeamLabel').removeClass('d-block').addClass('d-none');

                $('#button_add_team').removeClass('d-none').addClass('d-block');
                $('#button_edit_team').removeClass('d-block').addClass('d-none');
            }
        );
    });

    $('#button_cancel_category, #button_cancel_category_x').click(function()
    {
        var edit_category = false;
        var edit_id = null;
        if ($("#category_form").attr('name') === 'mod_category')
        {
            edit_category = true;
            edit_id = $("#button_edit_category").prop('value');
        }

        $.get(
            {
                url: window.location.href
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    const form_content = $(data).find('#category_form');
                    $('#category_form').html(form_content.html());
                    $('#category_form').attr('name', form_content.attr('name'));
                }

                if (edit_category && edit_id !== null && edit_id !== undefined)
                {
                    $('#category_' + edit_id).removeClass('category_edit');
                }

                $('#category_form').trigger('reset');

                $('#formAddCategoryLabel').removeClass('d-none').addClass('d-block');
                $('#formEditCategoryLabel').removeClass('d-block').addClass('d-none');

                $('#button_add_category').removeClass('d-none').addClass('d-block');
                $('#button_edit_category').removeClass('d-block').addClass('d-none');
            }
        );
    });

    $('#button_delete_team').click(function()
    {
        const csrftoken = getCookie('csrftoken');
        $('#wait_delete_team').removeClass('d-none').addClass('d-block');
        $('#button_delete_team').prop('disabled', true);
        $('#cancel_delete_team').prop('disabled', true);
        $.post(
            {
                url: window.location.href,
                data: { delete_team: $('#button_delete_team').prop('value') },
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status){
                $('#wait_delete_team').removeClass('d-block').addClass('d-none');
                $('#button_delete_team').prop('disabled', false);
                $('#cancel_delete_team').prop('disabled', false);
                if (status === 'success')
                {
                    $('.menu').html($(data).find('.menu').html());
                    $('#team_table').html($(data).find('#team_table').html());
                }
            }
        );
    });

    $('#button_delete_category').click(function()
    {
        const csrftoken = getCookie('csrftoken');
        $('#wait_delete_category').removeClass('d-none').addClass('d-block');
        $('#button_delete_category').prop('disabled', true);
        $('#cancel_delete_category').prop('disabled', true);
        $.post(
            {
                url: window.location.href,
                data: { delete_category: $('#button_delete_category').prop('value') },
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status){
                $('#wait_delete_category').removeClass('d-block').addClass('d-none');
                $('#button_delete_category').prop('disabled', false);
                $('#cancel_delete_category').prop('disabled', false);
                if (status === 'success')
                {
                    $('.menu').html($(data).find('.menu').html());
                    $('#team_table').html($(data).find('#team_table').html());
                }
            }
        );
    });

    $('#teams_pdf').click(function()
    {
        window.open(window.location.href + '/pdf');
    });
});
