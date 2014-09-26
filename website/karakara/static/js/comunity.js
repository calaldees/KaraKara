// Modal Track 
function modal_track_show(data) {
    $("#modalTrack .modal-body").html(data);
    // Set the title of the modal as the first heading in the body data. Ensure the heading is removed from the original doc
    $("#modalTrack .modal-title").text(
        $("#modalTrack .modal-body").find('h1,h2,h3').first().remove().text()
    );
    $('#modalTrack').modal('show');
}

function modal_track_hide() {
    $("#modalTrack .modal-title").text("");
    $("#modalTrack .modal-body").html("");
    // TODO: stop video playing?
    $("#modalTrack").modal('hide');
}

// Modal Track - Links
$('a.modal_track_link').on('click', function() {
    $popup_link = $(this);
    modal_track_show("<p>Loading...</p>");
    $.ajax($popup_link.attr('href')+".html_template", {
        type: "GET",
        success: function(data, text, jqXHR) {
            //console.log(data, text, jqXHR);
            modal_track_show(data);
            init_track_popup('#form_track');
        },
        error: function(jqXHR) {
            console.error(jqXHR);
            modal_track_show("<p>Error</p>");
        }
    });
    return false;
});

// Modal Track - Setup Submit Handlers
function init_track_popup(form_selector) {
    init_video();
    //$('#modalTrack .collapse').collapse();  // TODO: Manually init the collapse behaviour somehow.
    
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
                modal_track_hide();
            },
            error: function(jqXHR) {
                console.error(jqXHR);
                $form.find("input[type='submit']").removeAttr('disabled');
            }
        });
        return false;
    });
}


// Login ---------------------------------------------------------------

var currentUserEmail = 'bob@example.com';  // $.cookie('karakara_session').comunity.email; ??



// Page Load Event -------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function() {
    
});
