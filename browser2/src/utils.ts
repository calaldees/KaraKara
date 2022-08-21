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
 * Get the URL, username, and password to be passed to MQTTSubscribe or MQTTPublish
 */
export function mqtt_login_info(
    state: Pick<State, "root" | "room_name" | "room_password">
): Dictionary<string> {
    return {
        url: state.root.replace("https://", "wss://").replace("http://", "ws://") + "/mqtt",
        username: state.room_name,
        password: state.room_password,
    };
}

/**
 * Take a setting (string, int, list) and turn it into a string in
 * a format that the karakara server will understand
 */
export function flatten_setting(val: any): string {
    if (Array.isArray(val)) {
        return "[" + val.join(",") + "]";
    }
    return "" + val;
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

export function is_my_song(
    state: Pick<State, "session_id" | "performer_name">,
    item?: Pick<QueueItem, "session_owner" | "performer_name">
): boolean {
    return (
        item?.session_owner === state.session_id ||
        item?.performer_name === state.performer_name
    );
}

export function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

export function shortest_tag(n: Array<string> | undefined): string {
    if (n === undefined) {
        return "";
    }
    return n.sort((a, b) => a.length > b.length ? 1 : -1)[0];
}

/*
Given a tag set like

  from:macross
  macross:macross frontier

we want last_tag("from") to get "macross frontier"
*/
export function last_tag(tags: Dictionary<Array<string>>, start: string): string {
    let tag = start;
    while (tags[tag]) {
        tag = tags[tag][0];
    }
    return tag;
}

/**
 * Figure out what extra info is relevant for a given track, given what the
 * user is currently searching for
 */
let title_tags_for_category: Dictionary<Array<string>> = {
    'DEFAULT': ['from', 'use', 'length'],
    'vocaloid': ['artist'],
    'jpop': ['artist'],
    'meme': ['from'],
};
export function track_info(filters: Array<string>, track: Pick<Track, "tags">): string {
    let info_tags = title_tags_for_category[track.tags.category?.[0] || "DEFAULT"] || title_tags_for_category["DEFAULT"];
    // look at series that are in the search box
    let search_from = filters.filter(x => x.startsWith("from:")).map(x => x.replace("from:", ""));
    // we manually check that all our keys exist
    let track_tags = track.tags as Dictionary<Array<string>>; 
    let info_data = (
        info_tags
            // Ignore undefined tags
            .filter(x => track_tags.hasOwnProperty(x))
            // We always display track title, so ignore any tags which duplicate that
            .filter(x => track_tags[x][0] != track.tags.title[0])
            // If we've searched for "from:naruto", don't prefix every track title with "this is from naruto"
            .filter(x => x != "from" || !search_from.includes(track_tags[x][0]))
            // Format a list of tags
            .map(x => track_tags[x].join(", "))
    );
    let info = info_data.join(" - ");
    return info;
}
