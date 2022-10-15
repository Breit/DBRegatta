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