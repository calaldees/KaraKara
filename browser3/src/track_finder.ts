/**
 * If track has a 'hidden' tag, then skip it, UNLESS it also has
 * other non-hidden tags with the same parent. Consider top-level
 * tags to have different parents.
 */
export function apply_hidden(
    tracks: Array<Track>,
    hidden_tags: Array<string>,
): Array<Track> {
    // Translate
    //   hidden=category:anime,category:retro,broken
    // into
    //   {"category": ["anime", "retro"], "broken": []}
    let hidden: Record<string, string[]> = {};
    hidden_tags.forEach((x) => {
        let [k, v] = x.split(":");
        if (!hidden[k]) hidden[k] = [];
        if (v) hidden[k].push(v);
    });

    return tracks.filter((track) => {
        return Object.entries(hidden).every(([hidden_key, hidden_values]) => {
            // If
            //   hidden = {"category": ["anime", "cartoon"]}
            // then keep any track where:
            //   tags["category"].length == 0 ||
            //   tags["category"] - {"anime", "cartoon"} != set()
            if (hidden_values.length > 0) {
                let values = track.tags[hidden_key];
                // track["category"] needs to be both defined *and*
                // empty-after-removing-hidden-subtags. If it's not
                // defined, we don't care.
                return (
                    !values ||
                    values.filter((x) => !hidden_values.includes(x)).length
                );
            }

            // If
            //   hidden = {"broken": []}
            // then keep any track where:
            //   !tags[""].includes("broken")
            else {
                return !track.tags[""]?.includes(hidden_key);
            }
        });
    });
}

/**
 * If user filters for from:macross, then check
 *   track.tags["from"].includes("macross")
 */
export function apply_tags(
    tracks: Array<Track>,
    tags: Array<string>,
): Array<Track> {
    // convert "retro" to ["", "retro"] and "from:Macross" to ["from", "Macross"]
    let tag_pairs = tags.map((x) => (x.includes(":") ? x : ":" + x).split(":"));

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
export function apply_search(
    tracks: Array<Track>,
    search: string,
): Array<Track> {
    search = search.trim();
    if (search === "") return tracks;
    search = search.toLowerCase();

    // Keep tracks where ...
    return tracks.filter((track) => {
        // ... any tag ...
        return Object.values(track.tags).some(
            // ... has any value ...
            (tag_values) =>
                (tag_values as Array<string>).some(
                    // ... which contains the text we're looking for
                    (value) => value.toLowerCase().indexOf(search) >= 0,
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
    let ret_filters = filters.map((x) => x);
    let ret_search: string[] = [];
    search.split(" ").forEach((word) => {
        let m = word.match("([a-z]+):(.*)");
        if (m) ret_filters.push(word);
        else ret_search.push(word);
    });
    return [ret_filters, ret_search.join(" ")];
}

/**
 * All the searching in one place, for benchmarking
 */
export function find_tracks(
    tracks: Array<Track>,
    filters_: string[],
    search_: string,
): Array<Track> {
    let [filters, search] = text_to_filters(filters_, search_);
    tracks = apply_tags(tracks, filters);
    tracks = apply_search(tracks, search);
    return tracks;
}
