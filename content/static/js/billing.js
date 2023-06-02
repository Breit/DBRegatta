function select(element) {
    element.children('.subtable_header_row').removeClass('d-none');
    element.children('.subtable_header_row').addClass('marked');
    element.children('.subtable_content_row').removeClass('d-none');
    element.children('.subtable_content_row').addClass('marked');
    element.children('.main_table_row_data').addClass('border-bottom border-primary marked');
    element.removeClass('border-bottom');
    element.addClass('selected');
}

function unselect(element) {
    element.children('.subtable_header_row').addClass('d-none');
    element.children('.subtable_header_row').removeClass('marked');
    element.children('.subtable_content_row').addClass('d-none');
    element.children('.subtable_content_row').removeClass('marked');
    element.children('.main_table_row_data').removeClass('border-bottom border-primary marked');
    element.addClass('border-bottom');
    element.removeClass('selected');
}

$(document).ready(function()
{
    $('#billing_pdf').click(function()
    {
        window.open(window.location.href + '/pdf');
    });

    $('.main_table_row').click(function()
    {
        if ($(this).hasClass('selected'))
        {
            unselect($(this));
        }
        else
        {
            unselect($('.selected'));
            select($(this));
        }
    });
});