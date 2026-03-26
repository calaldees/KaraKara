import type { Track } from "@/types";

/**
 * If user filters for from:macross, then check
 *   track.tags["from"].includes("macross")
 */
export function apply_tags(tracks: Track[], tags: string[]): Track[] {
    if (tags.length === 0) return tracks;

    // convert "retro" to ["", "retro"] and "from:Macross" to ["from", "Macross"]
    const tag_pairs = tags.map((x) =>
        (x.includes(":") ? x : ":" + x).split(":"),
    );

    // keep tracks where ...
    return tracks.filter(
        // ... every ...
        (track) =>
            tag_pairs.every(
                // ... tag-pair that we're looking for is found in the track
                ([tag_key, tag_value]) =>
                    track.tags[tag_key]?.includes(tag_value),
            ),
    );
}

/**
 * If the user uses free-text search, then check all tag values
 * for matching text, and skip if we have no matches
 */
export function apply_search(tracks: Track[], search: string): Track[] {
    search = search.trim();
    if (search === "") return tracks;
    search = search.toLowerCase();

    // Keep tracks where ...
    return tracks.filter((track) => {
        // ... any tag ...
        return Object.values(track.tags).some(
            // ... has any value ...
            (tag_values) =>
                tag_values &&
                tag_values.some(
                    // ... which contains the text we're looking for
                    (value) => value.toLowerCase().includes(search),
                ),
        );
    });
}

/**
 * If somebody searches for "foo:bar", remove that from the text
 * search and add it to the tag filters
 */
export function text_to_filters(
    filters: string[],
    search: string,
): [string[], string] {
    const ret_filters = filters.map((x) => x);
    const ret_search: string[] = [];
    search.split(" ").forEach((word) => {
        const m = word.match("([a-z]+):(.*)");
        if (m) ret_filters.push(word);
        else ret_search.push(word);
    });
    return [ret_filters, ret_search.join(" ")];
}

/**
 * All the searching in one place, for benchmarking
 */
export function find_tracks(
    tracks: Track[],
    filters_: string[],
    search_: string,
): Track[] {
    const [filters, search] = text_to_filters(filters_, search_);
    tracks = apply_tags(tracks, filters);
    tracks = apply_search(tracks, search);
    return tracks;
}
