function request_delete_training(training_id, team, skipper)
{
    $('#button_delete_training').prop('value', training_id);
    $('#del_training_team').text(team);
    $('#del_training_skipper').text(skipper);
    $('#deleteTrainingModal').modal('toggle');
}

function button_mod_training(training_id)
{
    $('#training_' + training_id).addClass('training_edit');
    $('#training_' + training_id)[0].scrollIntoView();

    $('#wait').removeClass('d-none').addClass('d-block');

    $('#button_edit_training').prop('disabled', true);
    $('#button_cancel_training').prop('disabled', true);

    $('#training_form').attr('name', 'mod_training');
    $('#button_edit_training').prop('value', training_id);

    $('#formAddTrainingLabel').removeClass('d-block').addClass('d-none');
    $('#formEditTrainingLabel').removeClass('d-none').addClass('d-block');

    $('#button_add_training').removeClass('d-block').addClass('d-none');
    $('#button_edit_training').removeClass('d-none').addClass('d-block');

    $('#formTrainingModal').modal('toggle');

    const csrftoken = getCookie('csrftoken');
    $.post(
        {
            url: window.location.href,
            data: { 'edit_training': training_id },
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if (status === 'success')
            {
                $('#training_form').html($(data).find('#training_form').html());
            }

            $('#wait').removeClass('d-block').addClass('d-none');

            $('#button_edit_training').prop('disabled', false);
            $('#button_cancel_training').prop('disabled', false);
        }
    );
}

$(document).ready(function()
{
    $('#training_form').submit(function(e)
    {
        e.preventDefault();

        $('#wait').removeClass('d-none').addClass('d-block');

        $('#button_add_training').prop('disabled', true);
        $('#button_edit_training').prop('disabled', true);
        $('#button_cancel_training').prop('disabled', true);

        var edit_training = false;
        var edit_id = null;
        if ($("#training_form").attr('name') == 'mod_training')
        {
            edit_training = true;
            edit_id = $("#button_edit_training").prop('value');
        }
        const csrftoken = getCookie('csrftoken');
        var form_data = null;
        if (edit_training)
        {
            form_data = 'mod_training=';
            form_data += edit_id;
            form_data += '&';
            form_data += $(this).serialize();
        }
        else
        {
            form_data = 'add_training=&';
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
                    $('#training_table').html($(data).find('#training_table').html());
                    $('#training_statistics').html($(data).find('#training_statistics').html());

                    const form_content = $(data).find('#training_form');
                    $('#training_form').html(form_content.html());
                    $('#training_form').attr('name', form_content.attr('name'));
                }

                $('#wait').removeClass('d-block').addClass('d-none');

                $('#button_add_training').prop('disabled', false);
                $('#button_edit_training').prop('disabled', false);
                $('#button_cancel_training').prop('disabled', false);

                if (!$('#training_form .input-error').length)
                {
                    $('#formTrainingModal').modal('toggle');

                    $('#formAddTrainingLabel').removeClass('d-none').addClass('d-block');
                    $('#formEditTrainingLabel').removeClass('d-block').addClass('d-none');

                    $('#button_add_training').removeClass('d-none').addClass('d-block');
                    $('#button_edit_training').removeClass('d-block').addClass('d-none');

                    $('.content_panel').scrollTop($('.content_panel')[0].scrollHeight);

                    if (edit_training && edit_id !== null && edit_id !== undefined)
                    {
                        $('#training_' + edit_id).removeClass('training_edit');
                    }
                }
                else
                {
                    if (edit_training)
                    {
                        $("#training_form").attr('name', 'mod_training');
                    }
                }
            }
        );
    });

    $('#button_cancel_training, #button_cancel_training_x').click(function()
    {
        var edit_training = false;
        var edit_id = null;
        if ($("#training_form").attr('name') === 'mod_training')
        {
            edit_training = true;
            edit_id = $("#button_edit_training").prop('value');
        }

        $.get(
            {
                url: window.location.href
            },
            function(data, status)
            {
                if (status === 'success')
                {
                    const form_content = $(data).find('#training_form');
                    $('#training_form').html(form_content.html());
                    $('#training_form').attr('name', form_content.attr('name'));
                }

                if (edit_training && edit_id !== null && edit_id !== undefined)
                {
                    $('#training_' + edit_id).removeClass('training_edit');
                }

                $('#training_form').trigger('reset');

                $('#formAddTrainingLabel').removeClass('d-none').addClass('d-block');
                $('#formEditTrainingLabel').removeClass('d-block').addClass('d-none');

                $('#button_add_training').removeClass('d-none').addClass('d-block');
                $('#button_edit_training').removeClass('d-block').addClass('d-none');
            }
        );
    });

    $('#button_delete_training').click(function()
    {
        const csrftoken = getCookie('csrftoken');
        $('#wait_delete').removeClass('d-none').addClass('d-block');
        $('#button_delete_team').prop('disabled', true);
        $('#cancel_delete_team').prop('disabled', true);
        $.post(
            {
                url: window.location.href,
                data: { delete_training: $('#button_delete_training').prop('value') },
                headers: { 'X-CSRFToken': csrftoken }
            },
            function(data, status){
                $('#wait_delete').removeClass('d-block').addClass('d-none');
                $('#button_delete_training').prop('disabled', false);
                $('#cancel_delete_training').prop('disabled', false);
                if (status === 'success')
                {
                    $('.menu').html($(data).find('.menu').html());
                    $('#training_table').html($(data).find('#training_table').html());
                    $('#training_statistics').html($(data).find('#training_statistics').html());
                }
            }
        );
    });

    $('#trainings_pdf').click(function()
    {
        window.open(window.location.href + '/pdf');
    });
});