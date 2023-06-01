function select(element) {
    element.children('.subtable_header_row').removeClass('d-none');
    element.children('.subtable_header_row').addClass('marked');
    element.children('.subtable_content_row').removeClass('d-none');
    element.children('.subtable_content_row').addClass('marked');
    element.children('.main_table_row_data').addClass('border-bottom border-primary marked');
    // element.find('.id_col').addClass('id_col_selected');
    // element.find('.id_col').removeClass('id_col');
    element.removeClass('border-bottom');
    element.addClass('selected');
}

function unselect(element) {
    element.children('.subtable_header_row').addClass('d-none');
    element.children('.subtable_header_row').removeClass('marked');
    element.children('.subtable_content_row').addClass('d-none');
    element.children('.subtable_content_row').removeClass('marked');
    element.children('.main_table_row_data').removeClass('border-bottom border-primary marked');
    // element.find('.id_col_selected').addClass('id_col');
    // element.find('.id_col_selected').removeClass('id_col_selected');
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