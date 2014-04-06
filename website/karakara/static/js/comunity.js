// Popup contols
function popup_show(data) {
    $("#modalTrack .modal-body").html(data);
    $('#modalTrack').modal('show');
}

function popup_hide() {
    $("#modalTrack .modal-body").html("");
    $("#modalTrack").modal('hide');
}

// Attach click event to track_popup links
$('a.track_popup').on('click', function() {
    $popup_link = $(this);
    popup_show("<p>Loading...</p>");
    $.ajax($popup_link.attr('href')+".html_template", {
        type: "GET",
        success: function(data, text, jqXHR) {
            //console.log(data, text, jqXHR);
            popup_show(data);
            attach_form_track('#form_track');
        },
        error: function(jqXHR) {
            console.error(jqXHR);
            popup_show("<p>Error</p>");
        }
    });
    return false;
});

// Popup submit
function attach_form_track(form_selector) {
    $(form_selector).on("submit", function() {
        var $form = $(this);
        var track_id = $form.data().track_id;
        
        // Disable the submit button to prevent unwanted multiple submits
        $form.find("input[type='submit']").attr('disabled', true);
        
        // Only post the changed fields by disbaling the unchanged fields
        $.each($form.find('textarea'), function(index, textarea) {
            $textarea = $(textarea);
            //console.log($textarea.val(), $textarea.data('inital'));
            if ($textarea.val() == $textarea.data('inital')) {
                $textarea.attr('disabled', true);
            }
        });
        
        var form_data = $form.serialize();
        $.ajax("/comunity/track/"+track_id+".json", {
            type: "POST",
            dataType: "json",
            data: form_data,
            success: function(data, text, jqXHR) {
                var response = jqXHR.responseJSON
                console.log(response);
                $form.find("input[type='submit']").removeAttr('disabled');
                popup_hide();
            },
            error: function(jqXHR) {
                console.error(jqXHR);
                $form.find("input[type='submit']").removeAttr('disabled');
            }
        });
        return false;
    });
}



document.addEventListener("DOMContentLoaded", function() {
    
});
