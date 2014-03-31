$('a.track_popup').on('click', function() {
    $popup_link = $(this);
    $.ajax($popup_link.attr('href'), {
        type: "GET",
        success: function(data, text, jqXHR) {
            //console.log(data, text, jqXHR);
            $("#popup .content").html(data);
            $("#popup").removeClass('hidden');
        },
        error: function(jqXHR) {
            console.error(jqXHR);
        }
    });
    return false;
});

document.addEventListener("DOMContentLoaded", function() {
    
});
