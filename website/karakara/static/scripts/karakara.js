$.cookie.json = true;

var priority_token_cookie = $.cookie('priority_token');


function timedelta_str(timedelta) {
    var seconds_total = Math.floor(timedelta/1000);
    var seconds       = seconds_total % 60;
    var minutes       = Math.floor(seconds_total/60);
    if (minutes>=1) {
        return minutes+"min";
    }
    return seconds+"sec";
}

function update_priority_token_feedback() {
    if (priority_token_cookie) {
        var now = new Date();
        var valid_start = new Date(priority_token_cookie.valid_start);
        var valid_end   = new Date(priority_token_cookie.valid_end  );
        var delta_start = valid_start - now;
        var delta_end   = valid_end   - now;
        
        if (delta_end < 0) {
            $.removeCookie('priority_token');
            priority_token_cookie = null;
            console.log("Deleted stale 'priority_token' cookie");
        }
        if (delta_start > 0) {
            console.log("Priority Mode in "+timedelta_str(delta_start));
            $("#priority_countdown")[0].innerHTML = "pmode in "+timedelta_str(delta_start);
        }
        if (delta_start < 0 && delta_end > 0) {
            $("#priority_countdown")[0].innerHTML = "pmode for "+timedelta_str(delta_end);
        }
    }
}

$(document).ready(function() {
    if (priority_token_cookie) {
        var interval_id = setInterval(update_priority_token_feedback, 1000);
        update_priority_token_feedback();
    }
});
