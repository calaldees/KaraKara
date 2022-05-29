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
 * Looking at a Track, find the first matching attachment, or throw an exception
 *
 * eg get_attachment(track, "video") -> {use: "video", mime: "video/mp4", path: "asdfasdfa.mp4"}
 */
export function get_attachment(
    track: Track,
    type: string,
): Attachment {
    for (let i = 0; i < track.attachments.length; i++) {
        let a = track.attachments[i];
        if (a.use == type) {
            return a;
        }
    }
    throw `Unable to find an attachment of type ${type} for track ${track.source_hash}`;
}

/**
 * Looking at a Track, find all matching attachments
 *
 * eg get_attachments(track, "video") -> [
 *    {use: "video", mime: "video/mp4", path: "asdfasdfa.mp4"},
 *    {use: "video", mime: "video/webm", path: "dhfghdfgh.webm"},
 * ]
 */
export function get_attachments(
    track: Track,
    type: string,
): Array<Attachment> {
    let as: Array<Attachment> = [];
    for (let i = 0; i < track.attachments.length; i++) {
        let a = track.attachments[i];
        if (a.use == type) {
            as.push(a);
        }
    }
    return as;
}

/**
 * Looking at an Attachment, get the full URL
 *
 * eg attachment_path(state.root, attachment) -> https://karakara.uk/files/asdfasdfa.mp4
 */
export function attachment_path(root: string, attachment: Attachment): string {
    return root + "/files/" + attachment.path;
}

/**
 * Generic function to shuffle an array, modifying it in-place
 * and also returning it
 */
export function shuffle<T>(array: Array<T>): Array<T> {
    let currentIndex = array.length;
    let temporaryValue, randomIndex;

    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        // And swap it with the current element.
        temporaryValue = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temporaryValue;
    }

    return array;
}

/**
 * Looking at the data URL, figure out the websocket URL
 */
export function http2ws(str: string): string {
    return str.replace("https://", "wss://").replace("http://", "ws://");
}

/**
 * Take a setting (string, int, list) and turn it into a string in
 * a format that the karakara server will understand
 */
export function flatten_setting(val: any): string {
    if (Array.isArray(val)) {
        return "[" + val.join(",") + "]";
    }
    return val;
}

/**
 * Takes a settings dictionary and returns string:string pairs suitable
 * for submitting as an HTTP form
 */
export function flatten_settings(settings: Dictionary<any>): string[][] {
    return Object.entries(settings).map(([key, value]) => [
        key,
        flatten_setting(value),
    ]);
}

/**
 * Turn an ISO8601 date into a nicer time
 *
 * eg "2021-01-03T14:00:00" -> "14:00"
 */
export function short_date(long_date: string): string {
    return long_date.split("T")[1].substring(0, 5);
}

export function is_logged_in(state: State): boolean {
    return (state.room_name !== "" && Object.keys(state.track_list).length > 0);
}