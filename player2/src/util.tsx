import parseSRT from 'parse-srt';
import xhr from 'xhr';
import { stringify as queryEncode, parse as queryDecode } from "query-string";

// GET /queue/${queue_id}/${url}.json
export function api(state, method, url, params, callback) {
    const uri = (
        get_protocol() + "//" + get_hostname() +
        "/queue/" + get_queue_id() + "/" +
        url + ".json" +
        (params ? "?" + queryEncode(params) : "")
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
export function timedelta_str(timedelta) {
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
export function s_to_mns(t) {
    return Math.floor(t/60) + ":" + (Math.floor(t%60)+"").padStart(2, "0");
}

export function get_file_root() {
    return get_protocol() + "//" + get_hostname() + "/files/";
}

// find the path from the player to the media file
export function get_attachment(state, track, type) {
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
export function get_lyrics(state, track) {
    let xhr = new XMLHttpRequest();
    let data = null;
    xhr.open('GET', get_attachment(state, track, "srt"), false);
    xhr.onload = function(e: ProgressEvent<XMLHttpRequest>) {
        data = e.target.responseText;
    };
    xhr.send();
    return data ? parseSRT(data) : null;
}

// get a tag if it is defined, else blank
export function get_tag(tag) {
    if(tag) return tag[0];
    else return "";
}

// figure out where our server is, accounting for three use-cases:
// - stand-alone file:// mode
// - development http:// mode
// - production https:// mode
// and allow manual overrides where appropriate
export function get_protocol() {
    const specified = queryDecode(location.hash).protocol;
    if(specified) return specified;
    else if(document.location.protocol === "file:") return "https:";
    else return document.location.protocol;
}
export function get_hostname() {
    const specified = queryDecode(location.hash).hostname;
    if(specified) return specified;
    else if(document.location.protocol === "file:") return "karakara.org.uk";
    else return document.location.hostname;
}
export function get_ws_port() {
    const specified = queryDecode(location.hash).ws_port;
    if(specified) return ":" + specified;
    else if(document.location.protocol === "http:") return ":9873";
    else return "";
}
export function get_queue_id() {
    const specified = queryDecode(location.hash).queue_id;
    return specified ? specified : "demo";
}
export function is_podium() {
    return Boolean(queryDecode(location.hash).podium);
}
export function get_theme_var() {
    const v = queryDecode(location.hash).theme_var;
    return v ? " var-"+v : "";
}
