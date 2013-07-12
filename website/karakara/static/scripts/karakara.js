$.cookie.json = true;

var priority_token_cookie = $.cookie('priority_token');
var interval_id;

function update_priority_token_feedback() {
    if (priority_token_cookie) {
        // If the server time and the client time differ, calculate an offset
        // TODO - this needs to be persistantly stored in the cookie because we loose our state each page view
        if (!priority_token_cookie.server_datetime_offset) {
            priority_token_cookie.server_datetime_offset = new Date() - new Date(priority_token_cookie.server_datetime);
            console.log("Calculated server_datetime_offset: " + priority_token_cookie.server_datetime_offset);
        }
        var now = new Date() - priority_token_cookie.server_datetime_offset;
        
        var valid_start = new Date(priority_token_cookie.valid_start);
        var valid_end   = new Date(priority_token_cookie.valid_end  );
        var delta_start = valid_start - now;
        var delta_end   = valid_end   - now;
        
        if (delta_end < 0) {
            $.removeCookie('priority_token');
            clearInterval(interval_id);
            priority_token_cookie = null;
            $("#priority_countdown")[0].innerHTML = "";
            console.log("Deleted stale 'priority_token' cookie");
        }
        if (delta_start > 0) {
            $("#priority_countdown")[0].innerHTML = "Priority mode in "+timedelta_str(delta_start);
        }
        if (delta_start < 0 && delta_end > 0) {
            $(".ui-header").removeClass("ui-bar-a").addClass("ui-bar-b");
            $("#priority_countdown")[0].innerHTML = "Priority mode for "+timedelta_str(delta_end);
        }
    }
}

$(document).ready(function() {
    if (priority_token_cookie) {
        interval_id = setInterval(update_priority_token_feedback, 1000);
        update_priority_token_feedback();
    }
});
