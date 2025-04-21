import type { Track, QueueItem, Attachment } from "./types";

export function dict2css(d: Record<string, any>) {
    return Object.entries(d)
        .filter(([_, v]) => v)
        .map(([k, _]) => k)
        .join(" ");
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
 * Looking at an Attachment, get the full URL
 *
 * eg attachment_path(state.root, attachment) -> https://karakara.uk/files/asdfasdfa.mp4
 */
export function attachment_path(root: string, attachment: Attachment): string {
    return root + "/files/" + attachment.path;
}

/**
 * turn timestamp into into "{X}min / {X}sec [in the future]"
 */
export function time_until(now: number, time: number | null): string {
    if (time === null) return "";

    const seconds_total = Math.floor(time - now);
    const seconds = seconds_total % 60;
    const minutes = Math.floor(seconds_total / 60);
    if (minutes > 1) {
        return `In ${minutes} mins`;
    }
    if (minutes === 1) {
        return `In ${minutes} min`;
    }
    if (seconds <= 0) {
        return "Now";
    }
    return `In ${seconds} secs`;
}

/**
 * Generic function to shuffle an array, modifying it in-place
 * and also returning it
 */
export function shuffle<T>(array: T[]): T[] {
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
export function mqtt_url(root: string): string {
    return (
        root.replace("https://", "wss://").replace("http://", "ws://") + "/mqtt"
    );
}

/**
 * Turn an ISO8601 UTC datetime into the user's local time
 *
 * eg "2021-01-03T14:00:00" -> "14:00"
 */
export function short_date(long_date: string): string {
    const date = new Date(long_date);
    return date.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

export function is_my_song(
    session_id: string,
    performer_name: string,
    item?: Pick<QueueItem, "session_id" | "performer_name">,
): boolean {
    return (
        item?.session_id === session_id ||
        item?.performer_name === performer_name
    );
}

export function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

export function shortest_tag(n: string[] | undefined): string {
    if (n === undefined) {
        return "";
    }
    return n.sort((a, b) => (a.length > b.length ? 1 : -1))[0];
}

/*
Given a tag set like

  from:macross
  macross:macross frontier

we want last_tag("from") to get "macross frontier"
*/
export function last_tag(
    tags: Record<string, string[]>,
    start: string,
): string {
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
const title_tags_for_category: Record<string, string[]> = {
    DEFAULT: ["from", "use", "length"],
    vocaloid: ["artist"],
    jpop: ["artist"],
    meme: ["from"],
};
export function track_info(
    filters: string[],
    track: Pick<Track, "tags">,
): string {
    const info_tags =
        title_tags_for_category[track.tags.category?.[0] ?? "DEFAULT"] ||
        title_tags_for_category["DEFAULT"];
    // look at series that are in the search box
    const search_from = filters
        .filter((x) => x.startsWith("from:"))
        .map((x) => x.replace("from:", ""));
    // we manually check that all our keys exist
    const track_tags = track.tags as Record<string, string[]>;
    const info_data = info_tags
        // Ignore undefined tags
        .filter((x) => Object.prototype.hasOwnProperty.call(track_tags, x))
        // We always display track title, so ignore any tags which duplicate that
        .filter((x) => track_tags[x][0] !== track.tags.title[0])
        // If we've searched for "from:naruto", don't prefix every track title with "this is from naruto"
        .filter((x) => x !== "from" || !search_from.includes(track_tags[x][0]))
        // Format a list of tags
        .map((x) => track_tags[x].join(", "));
    const info = info_data.join(" - ");
    return info;
}

/*
 * Given a string value from the settings form, check what data
 * type the setting is now, and try to keep that type
 */
export function copy_type(original: any, value: any) {
    if (Array.isArray(original)) {
        return value.split(",").filter((x: any) => x);
    } else if (typeof original == "number") {
        return parseFloat(value);
    } else {
        return value;
    }
}

/*
 * Given a list of all tracks in the queue, find which ones are in-progress
 * now or queued for the future
 */
export function current_and_future(
    now: number,
    tracks: QueueItem[],
): QueueItem[] {
    return tracks.filter(
        (t) => t.start_time == null || t.start_time + t.track_duration > now,
    );
}

/*
 * Normalise weird band names so that they show up in the right place when
 * sorted in alphabetic order:
 * - case insensitive
 * - ignore punctuation (unless punctuation is all we have)
 */
export function normalise_name(name: string): string {
    return (name.replace(/[^a-zA-Z0-9]/g, "") || name).toUpperCase();
}

/*
 * Compare two strings for sorting into alphabetic order, but after
 * normalising with normalise_name
 */
export function normalise_cmp(a: string, b: string): number {
    return normalise_name(a) > normalise_name(b) ? 1 : -1;
}
