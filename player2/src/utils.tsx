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
 * Looking at a Track, find the first matching attachment, or throw an exception
 *
 * eg get_attachment(track, "preview") -> {type: "video", location: "asdfasdfa.mp4"}
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
 * get a tag if it is defined, else blank
 */
export function get_tag(tag: Array<string>): string {
    if (tag) return tag[0];
    else return "";
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
