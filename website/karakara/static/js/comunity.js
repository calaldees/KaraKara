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


// Persona Login ---------------------------------------------------------------

var currentUser = 'bob@example.com';  // $.cookie('karakara_session').comunity.email; ??

navigator.id.watch({
  loggedInUser: currentUser,
  onlogin: function(assertion) {
    // A user has logged in! Here you need to:
    // 1. Send the assertion to your backend for verification and to create a session.
    // 2. Update your UI.
    $.ajax({ /* <-- This example uses jQuery, but you can use whatever you'd like */
      type: 'POST',
      url: '/auth/login', // This is a URL on your website.
      data: {assertion: assertion},
      success: function(res, status, xhr) { window.location.reload(); },
      error: function(xhr, status, err) {
        navigator.id.logout();
        alert("Login failure: " + err);
      }
    });
  },
  onlogout: function() {
    // A user has logged out! Here you need to:
    // Tear down the user's session by redirecting the user or making a call to your backend.
    // Also, make sure loggedInUser will get set to null on the next page load.
    // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
    $.ajax({
      type: 'POST',
      url: '/auth/logout', // This is a URL on your website.
      success: function(res, status, xhr) { window.location.reload(); },
      error: function(xhr, status, err) { alert("Logout failure: " + err); }
    });
  }
});


// Page Load Event -------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function() {
    
});
