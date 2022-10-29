import { normalise_cmp } from "./utils";

/**
 * If track has a 'hidden' tag, then skip it, UNLESS it also has
 * other non-hidden tags with the same parent. Consider top-level
 * tags to have different parents.
 */
 export function apply_hidden(tracks: Array<Track>, hidden_tags: Array<string>): Array<Track> {
    // Translate
    //   hidden=category:anime,category:retro,broken
    // into
    //   {"category": ["anime", "retro"], "broken": []}
    let hidden: Dictionary<Array<string>> = {};
    hidden_tags.map(x => {
        let [k, v] = x.split(":");
        if (!hidden[k]) hidden[k] = [];
        if (v) hidden[k].push(v);
    });

    return tracks.filter(track => {
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
                    values.filter(x => !hidden_values.includes(x)).length
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
export function apply_tags(tracks: Array<Track>, tags: Array<string>): Array<Track> {
    // convert "retro" to ["", "retro"] and "from:Macross" to ["from", "Macross"]
    let tag_pairs = tags.map(x => (x.includes(":") ? x : ":" + x).split(":"));

    // keep tracks where ...
    return tracks.filter(
        // ... every ...
        track => tag_pairs.every(
            // ... tag-pair that we're looking for is found in the track
            ([tag_key, tag_value]) => track.tags[tag_key]?.includes(tag_value)
        )
    );
}

/**
 * If the user uses free-text search, then check all tag values
 * for matching text, and skip if we have no matches
 */
export function apply_search(tracks: Array<Track>, search: string): Array<Track> {
    search = search.trim();
    if (search == "") return tracks;
    search = search.toLowerCase();

    // Keep tracks where ...
    return tracks.filter(track => {
        // ... any tag ...
        return Object.values(track.tags).some(
            // ... has any value ...
            tag_values => (tag_values as Array<string>).some(
                // ... which contains the text we're looking for
                value => value.toLowerCase().indexOf(search) >= 0
            )
        )
    });
}

/**
 * All the searching in one place, for benchmarking
 */
 export function find_tracks(state: State): Array<Track> {
    let tracks = Object.values(state.track_list);
    tracks = apply_hidden(tracks, state.settings['hidden_tags']);
    tracks = apply_tags(tracks, state.settings['forced_tags']);
    tracks = apply_tags(tracks, state.filters);
    tracks = apply_search(tracks, state.search);
    tracks.sort((a, b) => normalise_cmp(a.tags.title[0], b.tags.title[0]));
    return tracks;
}
