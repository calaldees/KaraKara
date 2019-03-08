import parseSRT from 'parse-srt';
import xhr from 'xhr';
import queryString from 'query-string';

// GET /queue/${queue_id}/${url}.json
function api(state, method, url, params, callback) {
    const uri = (
        get_protocol() + "//" + get_hostname() +
        "/queue/" + get_queue_id() + "/" +
        url + ".json" +
        (params ? "?" + queryString.stringify(params) : "")
    );
    xhr({
        method: method,
        uri: uri,
        useXDR: true,  // cross-domain, so file:// can reach karakara.org.uk
        json: true,
    }, function (err, resp, body) {
        console.groupCollapsed("api(" + uri + ")");
        if(resp.statusCode === 200) {
            console.log(body.data);
            callback(body.data);
        }
        else {
            console.log(err, resp, body);
        }
        console.groupEnd();
    })

}

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

function get_file_root() {
    return get_protocol() + "//" + get_hostname() + "/files/";
}

// find the path from the player to the media file
function get_attachment(state, track, type) {
    for(let i=0; i<track.attachments.length; i++) {
        if(track.attachments[i].type === type) {
            return (
                get_file_root() +
                track.attachments[i].location
            );
        }
    }
    return "";
}

// get_attachment(srt) + parse SRT file
function get_lyrics(state, track) {
    let xhr = new XMLHttpRequest();
    let data = null;
    xhr.open('GET', get_attachment(state, track, "srt"), false);
    xhr.onload = function(e) {
        data = e.target.responseText;
    };
    xhr.send();
    return data ? parseSRT(data) : null;
}

// get a tag if it is defined, else blank
function get_tag(tag) {
    if(tag) return tag[0];
    else return "";
}

// figure out where our server is, accounting for three use-cases:
// - stand-alone file:// mode
// - development http:// mode
// - production https:// mode
// and allow manual overrides where appropriate
function get_protocol() {
    if(document.location.protocol === "file:") return "https:";
    else return document.location.protocol;
}
function get_hostname() {
    const specified = queryString.parse(location.hash).hostname;
    if(specified) return specified;
    else if(document.location.protocol === "file:") return "karakara.org.uk";
    else return document.location.hostname;
}
function get_ws_port() {
    const specified = queryString.parse(location.hash).ws_port;
    if(specified) return ":" + specified;
    else if(document.location.protocol === "http:") return ":9873";
    else return "";
}
function get_queue_id() {
    const specified = queryString.parse(location.hash).queue_id;
    return specified ? specified : "demo";
}
function is_podium() {
    return Boolean(queryString.parse(location.hash).podium);
}
function get_theme_var() {
    const v = queryString.parse(location.hash).theme_var;
    return v ? " var-"+v : "";
}

export {
    timedelta_str,
    get_attachment,
    get_tag,
    s_to_mns,
    get_ws_port,
    get_hostname,
    get_queue_id,
    is_podium,
    get_lyrics,
    api,
    get_protocol,
    get_file_root,
    get_theme_var,
};
