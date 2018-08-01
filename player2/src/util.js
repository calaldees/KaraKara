
// turn milliseconds into {X}min / {X}sec
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

// turn seconds into {MM}:{SS}
function s_to_mns(t) {
    return Math.floor(t/60) + ":" + (Math.floor(t%60)+"").padStart(2, "0");
}

// find the path from the player to the media file
function get_attachment(state, track, type) {
    for(let i=0; i<track.attachments.length; i++) {
        if(track.attachments[i].type === type) {
            return (
                state.settings["karakara.player.files"] +
                track.attachments[i].location
            );
        }
    }
    return "";
}

export {timedelta_str, get_attachment, s_to_mns};