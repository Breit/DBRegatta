function button_toggle_skipper(action, skipper_id)
{
    const csrftoken = getCookie('csrftoken');
    var data = {};
    data[action] = skipper_id;

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
                $('#skipper_table').html($(data).find('#skipper_table').html());
            }
        }
    );
}

function request_delete_skipper(skipper_name, skipper_id)
{
    $('#button_delete_skipper').prop('value', skipper_id);
    $('#del_skipper_warning').text(skipper_name);
    $('#deleteSkipperModal').modal('toggle');
}

function button_mod_skipper(skipper_id)
{
    $('#skipper_' + skipper_id).addClass('skipper_edit');
    $('#skipper_' + skipper_id)[0].scrollIntoView();

    $('#wait').removeClass('d-none').addClass('d-block');

    $('#button_edit_skipper').prop('disabled', true);
    $('#button_cancel_skipper').prop('disabled', true);

    $('#skipper_form').attr('name', 'mod_skipper');
    $('#button_edit_skipper').prop('value', skipper_id);

    $('#formAddSkipperLabel').removeClass('d-block').addClass('d-none');
    $('#formEditSkipperLabel').removeClass('d-none').addClass('d-block');

    $('#button_add_skipper').removeClass('d-block').addClass('d-none');
    $('#button_edit_skipper').removeClass('d-none').addClass('d-block');

    $('#formSkipperModal').modal('toggle');

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: { 'edit_skipper': skipper_id },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('#skipper_form').html($(data).find('#skipper_form').html());
            }

            $('#wait').removeClass('d-block').addClass('d-none');

            $('#button_edit_skipper').prop('disabled', false);
            $('#button_cancel_skipper').prop('disabled', false);
        }
    );
}

$(document).ready(function()
{
    $('#skipper_form').submit(function(e)
    {
        e.preventDefault();

        $('#wait').removeClass('d-none').addClass('d-block');

        $('#button_add_skipper').prop('disabled', true);
        $('#button_edit_skipper').prop('disabled', true);
        $('#button_cancel_skipper').prop('disabled', true);

        var edit_skipper = false;
        var edit_id = null;
        if ($("#skipper_form").attr('name') === 'mod_skipper')
        {
            edit_skipper = true;
            edit_id = $("#button_edit_skipper").prop('value');
        }
        const csrftoken = getCookie('csrftoken');
        var form_data = null;
        if (edit_skipper)
        {
            form_data = 'mod_skipper=';
            form_data += edit_id;
            form_data += '&';
            form_data += $(this).serialize();
        }
        else
        {
            form_data = 'add_skipper=&';
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
                    $('#skipper_table').html($(data).find('#skipper_table').html());

                    const form_content = $(data).find('#skipper_form');
                    $('#skipper_form').html(form_content.html());
                    $('#skipper_form').attr('name', form_content.attr('name'));
                }

                $('#wait').removeClass('d-block').addClass('d-none');

                $('#button_add_skipper').prop('disabled', false);
                $('#button_edit_skipper').prop('disabled', false);
                $('#button_cancel_skipper').prop('disabled', false);

                if (!$('#skipper_form .input-error').length)
                {
                    $('#formSkipperModal').modal('toggle');

                    $('#formAddSkipperLabel').removeClass('d-none').addClass('d-block');
                    $('#formEditSkipperLabel').removeClass('d-block').addClass('d-none');

                    $('#button_add_skipper').removeClass('d-none').addClass('d-block');
                    $('#button_edit_skipper').removeClass('d-block').addClass('d-none');

                    $('.content_panel').scrollTop($('.content_panel')[0].scrollHeight);

                    if (edit_skipper && edit_id !== null && edit_id !== undefined)
                    {
                        $('#skipper_' + edit_id).removeClass('skipper_edit');
                    }
                }
            }
        );
    });

    $('#button_cancel_skipper').click(function()
    {
        var edit_skipper = false;
        var edit_id = null;
        if ($("#skipper_form").attr('name') == 'mod_skipper')
        {
            edit_skipper = true;
            edit_id = $("#button_edit_skipper").prop('value');
        }

        $.get(
            {
                url: window.location.href
            },
            function(data, status)
            {
                if (status == 'success')
                {
                    const form_content = $(data).find('#skipper_form');
                    $('#skipper_form').html(form_content.html());
                    $('#skipper_form').attr('name', form_content.attr('name'));
                }

                if (edit_skipper && edit_id !== null && edit_id !== undefined)
                {
                    $('#skipper_' + edit_id).removeClass('skipper_edit');
                }

                $('#skipper_form').trigger('reset');

                $('#formAddSkipperLabel').removeClass('d-none').addClass('d-block');
                $('#formEditSkipperLabel').removeClass('d-block').addClass('d-none');

                $('#button_add_skipper').removeClass('d-none').addClass('d-block');
                $('#button_edit_skipper').removeClass('d-block').addClass('d-none');
            }
        );
    });

    $('#button_delete_skipper').click(function()
    {
        const csrftoken = getCookie('csrftoken');
        $.post(
            {
                url: window.location.href,
                data: { delete_skipper: $('#button_delete_skipper').prop('value') },
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status){
                if (status === 'success')
                {
                    $('.menu').html($(data).find('.menu').html());
                    $('#skipper_table').html($(data).find('#skipper_table').html());
                }
            }
        );
    });
});
