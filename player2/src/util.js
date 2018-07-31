function timedelta_str(timedelta) {
    const seconds_total = Math.floor(timedelta/1000);
    const seconds       = seconds_total % 60;
    const minutes       = Math.floor(seconds_total/60);
    if (minutes >= 1) {
        return minutes + "min";
    }
    if (seconds === 0) {
        return "Now";
    }
    return seconds + "sec";
}

function get_attachment(track, type) {
    for(let i=0; i<track.attachments.length; i++) {
        if(track.attachments[i].type === type) {
            return "./files/" + track.attachments[i].location;
        }
    }
    return "";
}

function s_to_mns(t) {
    return Math.floor(t/60) + ":" + (Math.floor(t%60)+"").padStart(2, "0");
}
export {timedelta_str, get_attachment, s_to_mns};