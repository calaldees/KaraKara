/**
 * turn milliseconds into {X}min / {X}sec
 */
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

/**
 * turn seconds into {MM}:{SS}
 */
export function s_to_mns(t: number): string {
    return (
        Math.floor(t / 60) + ":" + (Math.floor(t % 60) + "").padStart(2, "0")
    );
}

/**
 * find the path from the player to the media file
 */
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

/**
 * get a tag if it is defined, else blank
 */
export function get_tag(tag: Array<string>): string {
    if (tag) return tag[0];
    else return "";
}

/**
 * Make track titles look nicer, as the database has them all lowercase
 */
export function title_case(str: string) {
    return str
        .toLowerCase()
        .split(" ")
        .map(function (word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
        })
        .join(" ");
}

/**
 * Looking at the data URL, figure out the websocket URL
 */
export function http2ws(str: string) {
    return str.replace("https://", "wss://").replace("http://", "ws://");
}

/**
 * Turn an ISO8601 date into a nicer time
 *
 * eg "2021-01-03T14:00:00" -> "14:00"
 */
export function short_date(long_date: string): string {
    return long_date.split("T")[1].substring(0, 5);
}
