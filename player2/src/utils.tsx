import parseSRT from "parse-srt";

// turn milliseconds into {X}min / {X}sec
export function timedelta_str(timedelta: number): String {
    const seconds_total = Math.floor(timedelta / 1000);
    const seconds = seconds_total % 60;
    const minutes = Math.floor(seconds_total / 60);
    if (minutes >= 1) {
        return minutes + "min";
    }
    if (seconds === 0) {
        return "Now";
    }
    return seconds + "sec";
}

// turn seconds into {MM}:{SS}
export function s_to_mns(t: number): string {
    return (
        Math.floor(t / 60) + ":" + (Math.floor(t % 60) + "").padStart(2, "0")
    );
}

// find the path from the player to the media file
export function get_attachment(
    state: State,
    track: Track,
    type: string,
): string {
    for (let i = 0; i < track.attachments.length; i++) {
        if (track.attachments[i].type === type) {
            return state.root + "/files/" + track.attachments[i].location;
        }
    }
    return "";
}

// get_attachment(srt) + parse SRT file
export function get_lyrics(state: State, track: Track): Array<SrtLine> {
    let xhr = new XMLHttpRequest();
    let data: string | null = null;
    xhr.open("GET", get_attachment(state, track, "srt"), false);
    xhr.onload = function (e: ProgressEvent<XMLHttpRequest>) {
        data = e.target ? e.target.responseText : null;
    };
    xhr.send();
    return data ? parseSRT(data) : null;
}

// get a tag if it is defined, else blank
export function get_tag(tag: Array<string>): string {
    if (tag) return tag[0];
    else return "";
}

export function title_case(str: string) {
    return str
        .toLowerCase()
        .split(" ")
        .map(function (word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
        })
        .join(" ");
}

export function http2ws(str: string) {
    return str.replace("https://", "wss://").replace("http://", "ws://");
}
