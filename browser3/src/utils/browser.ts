import { QueueItem, Track } from "@/types";

export function dict2css(d: Record<string, any>) {
    return Object.entries(d)
        .filter(([_, v]) => v)
        .map(([k, _]) => k)
        .join(" ");
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

export function sorted<T>(array: T[], cmp?: (a: T, b: T) => number): T[] {
    const new_array = array.slice();
    new_array.sort(cmp);
    return new_array;
}

export function unique<T>(array: T[]): T[] {
    return Array.from(new Set(array));
}

export function nth(n: number): string {
    const suffixes = ["th", "st", "nd", "rd"];
    const v = n % 100;
    return n + (suffixes[(v - 20) % 10] || suffixes[v] || suffixes[0]);
}

export function is_my_song(
    item?: Pick<QueueItem, "session_id" | "performer_name">,
    sessionId?: string | null,
    performerName?: string | null,
): boolean {
    if (sessionId) {
        if (item?.session_id === sessionId.split("-")[0]) return true;
    }
    if (performerName) {
        if (item?.performer_name === performerName) return true;
    }
    return false;
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

/*
 * If there are multiple variants of a song, pick sensible
 * defaults for novice users
 */
export function preferred_variant(variants: string[]): string {
    const preferences = ["Vocal", "Romaji", "Simple", "Default"];
    for (const pref of preferences) {
        if (variants.includes(pref)) {
            return pref;
        }
    }
    if (variants.length > 0) {
        return variants[0];
    }
    return "Default";
}

/**
 * Check if adding a track would make the user a queue hog.
 * Returns a warning message if the user would have significantly more tracks
 * than the average performer, or null if it's okay to add the track.
 */
export function is_queue_hog(
    queue: Pick<
        QueueItem,
        "session_id" | "performer_name" | "track_duration"
    >[],
    performerName: string | null | undefined,
    sessionId: string | null | undefined,
): string | null {
    // If queue is short, not enough data
    if (queue.length <= 3) return null;

    // Figure out if this track would give the user significantly
    // more air-time than other performers, and if so, return a warning
    const myTracks = queue.filter((item) =>
        is_my_song(item, sessionId, performerName),
    );
    const otherPeoplesTracks = queue.filter(
        (item) => !is_my_song(item, sessionId, performerName),
    );

    // If there are no other people's tracks, can't be hogging the queue
    if (otherPeoplesTracks.length === 0) return null;

    const averageTracksPerPerformer =
        otherPeoplesTracks.length /
        unique(otherPeoplesTracks.map((item) => item.performer_name)).length;
    const averageTracksPerPerformerStr = averageTracksPerPerformer.toFixed(1);
    const myTrackCount = myTracks.length + 1;
    if (myTrackCount > averageTracksPerPerformer * 2) {
        return `The average person has ${averageTracksPerPerformerStr} ${
            averageTracksPerPerformerStr !== "1.0" ? "tracks" : "track"
        } in the queue, this will be your ${nth(myTrackCount)} — please make sure everybody gets a chance to sing ❤️`;
    }
    return null;
}

/**
 * Sort tag keys by importance.
 * Priority order: title, from, artist, category, use, lang, vocaltrack, vocalstyle,
 * then any other tags at the end
 */
export function sort_tag_keys(tagKeys: string[]): string[] {
    const priority = [
        "title",
        "from",
        "released",
        "artist",
        "category",
        "use",
        "opening",
        "ending",
        "lang",
        "vocaltrack",
        "vocalstyle",
    ];

    return tagKeys.slice().sort((a, b) => {
        const aIndex = priority.indexOf(a);
        const bIndex = priority.indexOf(b);

        // If both are in priority list, sort by their position
        if (aIndex !== -1 && bIndex !== -1) {
            return aIndex - bIndex;
        }

        // If only a is in priority list, it comes first
        if (aIndex !== -1) return -1;

        // If only b is in priority list, it comes first
        if (bIndex !== -1) return 1;

        // If neither is in priority list, sort alphabetically
        return a.localeCompare(b);
    });
}
