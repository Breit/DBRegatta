function update_setting(setting_id)
{
    const csrftoken = getCookie('csrftoken');
    var data = {};

    if ($('#wait_' + setting_id).length > 0)
    {
        $('#wait_' + setting_id).removeClass('d-none').addClass('d-block');
    }
    if ($('#' + setting_id + 'Submit').length > 0)
    {
        $('#' + setting_id + 'Submit').prop('disabled', true);
    }
    if ($('#' + setting_id + 'Cancel').length > 0)
    {
        $('#' + setting_id + 'Cancel').prop('disabled', true);
    }

    switch ($('#' + setting_id).attr('type'))
    {
        case 'date':
            const date = new Date($('#' + setting_id).val());
            data[setting_id] = [
                date.getFullYear().toString().padStart(4, 0),
                (date.getMonth() + 1).toString().padStart(2, 0),
                date.getDate().toString().padStart(2, 0)
            ].join('-');
            break;
        case 'checkbox':
            if ($('#' + setting_id).is(':checked'))
            {
                data[setting_id] = 'on';
            }
            else
            {
                data[setting_id] = 'off';
            }
            break;
        default:
            data[setting_id] = $('#' + setting_id).val();
    }

    $.post(
        {
            url: window.location.href,
            data: data,
            headers: { 'X-CSRFToken': csrftoken }
        },
        function(data, status){
            if ($('#wait_' + setting_id).length > 0)
            {
                $('#wait_' + setting_id).removeClass('d-block').addClass('d-none');
            }
            if ($('#' + setting_id + 'Modal').length > 0)
            {
                $('#' + setting_id + 'Modal').modal('hide');
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
