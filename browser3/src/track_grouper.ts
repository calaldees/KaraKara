import { normalise_cmp, normalise_name } from "./utils";

/**
 * Given a selection of tracks and some search terms, figure out
 * what the user might want to search for next, eg
 *
 *   [no search]    -> category (anime, game, jpop)
 *                     language (jp, en, fr)
 *                     vocal (on, off)
 *   category:anime -> from (gundam, macross, one piece)
 *   category:jpop  -> artist (akb48, mell, x japan)
 *                     from (gundam, macross, one piece)
 *   from:gundam    -> gundam (wing, waltz, unicorn)
 */
export function suggest_next_filters(
    filters: Array<string>,
    groups: Record<string, Record<string, number>>,
): Array<string> {
    let last_filter = filters[filters.length - 1];

    // if no search, show a sensible selection
    if (last_filter === undefined) {
        return ["category", "vocalstyle", "vocaltrack", "lang"];
    }

    // if we have an explicit map for "you searched for 'anime',
    // now search by series name", then show that
    const search_configs: Record<string, string[]> = {
        "category:anime": ["from"],
        "category:cartoon": ["from"],
        "category:game": ["from"],
        "category:jdrama": ["from"],
        "category:jpop": ["artist", "from"],
        "category:kpop": ["artist", "from"],
        "category:tokusatsu": ["from"],
        "category:vocaloid": ["artist"],
        "vocalstyle:male": ["artist"],
        "vocalstyle:female": ["artist"],
        "vocalstyle:duet": ["artist", "from"],
        "vocalstyle:group": ["artist", "from"],
        "lang:jp": ["category", "vocalstyle", "vocaltrack"],
        "lang:en": ["category", "vocalstyle", "vocaltrack"],
        "vocaltrack:on": ["category", "vocalstyle", "lang"],
        "vocaltrack:off": ["category", "vocalstyle", "lang"],
    };
    if (search_configs[last_filter]) {
        return search_configs[last_filter];
    }

    // if we searched for "from:gundam" and we have a set of tags
    // "gundam:wing", "gundam:unicorn", "gundam:seed", then show
    // those
    if (groups[last_filter.split(":")[1]]) {
        return [last_filter.split(":")[1]];
    }

    // give up, let the caller decide how to fall back
    return [];
}

/**
 * Find all the tags in the current search results, what possible
 * values each tag has, and how many tracks have that tag:value.
 * Returns data that looks like:
 *
 * tags = {
 *     "category": {
 *         "anime": 1619,  // there are 1619 tracks tagged "category:anime"
 *         "cartoon": 195,
 *         "game": 149,
 *         ...
 *     },
 *     "vocaltrack": {
 *         "on": 2003,
 *         "off": 255,
 *     },
 *     ...
 *  }
 */
export function summarise_tags(
    tracks: Array<Pick<Track, "tags">>,
): Record<string, Record<string, number>> {
    let tags: Record<string, Record<string, number>> = {};
    tracks.forEach((track) => {
        Object.entries(track.tags)
            .filter(([tag, values]) => tag !== "title")
            .forEach(([tag, values]) => {
                values?.forEach((value) => {
                    if (tags[tag] === undefined) tags[tag] = {};
                    if (tags[tag][value] === undefined) tags[tag][value] = 0;
                    tags[tag][value]++;
                });
            });
    });
    return tags;
}

/**
 * Given a number of tracks from 0 to LOTS, decide how best
 * to render the list.
 *
 * Returns a list of [heading, section] pairs.
 *
 * A "section" be one of:
 * - A list of tracks
 * - A list of filters
 * - A list of filter groups
 *
 * Terminology for this function:
 * - tag_key, eg "vocaltrack", "from"
 * - tag_values, eg {"on": 32, "off": 64}, {"Gundam": 41, "Macross": 52}
 * - tag_children, eg ["on", "off"], ["Gundam", "Macross"]
 * - tag_child, eg "on", "Gundam"
 */
export function group_tracks(
    filters: Array<string>,
    tracks: Array<Track>,
): Array<[string, TrackListSection]> {
    let sections: Array<[string, TrackListSection]> = [];
    let leftover_tracks: Array<Track> = tracks;
    let all_tags = summarise_tags(tracks);

    // If there are no tracks, show a friendly error
    if (tracks.length === 0) {
        sections.push(["No Results", {}]);
    }

    // If we have a few tracks, just list them all
    else if (tracks.length < 25) {
        // If we are searching for some tags, see if our most recently
        // searched tag has any children, eg if we are currently searching
        // for "from:Macross" then the resulting list of tracks will be
        // grouped by "Macross:*".
        let most_recent_tag = filters[filters.length - 1]?.split(":")[1];
        if(most_recent_tag && all_tags[most_recent_tag]) {
            let found_track_ids: Array<string> = [];

            let tag_key = most_recent_tag;
            // Look at our all_tags table to see what children we have
            let tag_children = Object.keys(all_tags[tag_key]).sort(
                normalise_cmp,
            );
            // tag_children then lists the children of this tag
            // like ["Delta", "Frontier", "Plus"], and we want to
            // add one [section title, track list] pair into the
            // sections list for each of those.
            tag_children.forEach(function (tag_child) {
                let tracks_in_this_section = tracks.filter((t) =>
                    t.tags[tag_key]?.includes(tag_child),
                );
                sections.push([tag_child, { tracks: tracks_in_this_section }]);
                found_track_ids = found_track_ids.concat(
                    tracks_in_this_section.map((t) => t.id),
                );
            });

            leftover_tracks = leftover_tracks.filter(
                (t) => !found_track_ids.includes(t.id),
            );
        }

        // if we're unable to figure out any groups, then all the
        // tracks will end up in leftover_tracks, which will be
        // handled below
    }

    // If we have many tracks, prompt for more filters
    else {
        // Try to pick some smart filters, like if we've searched
        // "category:anime", then next filter by "from:*"
        let next_filters = suggest_next_filters(filters, all_tags);
        // If we have a ton of tracks, but we can't figure out any
        // sensible filters, then desperately try using any and every
        // available tag as a filter, because we really don't want to
        // be listing 50+ tracks with no filters at all.
        if (next_filters.length === 0) {
            next_filters = Object.keys(all_tags);
            // Avoid repeating filter categories
            let filter_categories = filters.map(f => f.split(":")[0])
            next_filters = next_filters.filter((tag_key) => !(filter_categories.includes(tag_key)));
            // Remove tags with null parent (system tags like
            // "source-video" or "hard-subs")
            next_filters = next_filters.filter((tag_key) => tag_key);
        }
        // Remove any suggestions which would give 0 results
        next_filters = next_filters.filter((tag_key) => tag_key in all_tags);
        // For each section, either add a filter list, or a grouped filter list
        next_filters.forEach(function (tag_key) {
            // Look at our all_tags table to see what children we have
            let tag_children = Object.keys(all_tags[tag_key]).sort(
                normalise_cmp,
            );
            // If a tag has a lot of children (eg artist=...) then show
            // children grouped alphabetically
            if (tag_children.length > 50) {
                let grouped_groups: Record<string, Record<string, number>> = {};
                tag_children.forEach(function (tag_child) {
                    // Group by first alphabetic character
                    var initial = normalise_name(tag_child)[0];
                    if (grouped_groups[initial] === undefined)
                        grouped_groups[initial] = {};
                    grouped_groups[initial][tag_child] =
                        all_tags[tag_key][tag_child];
                    // If our title is "The X", then put the track into both
                    // "T" and "X" sections in case people are looking for
                    // "The X" or "X, The"
                    if (
                        tag_child.toLowerCase().startsWith("the ") &&
                        tag_child.length > 4
                    ) {
                        var x2 =
                            tag_child.substring(4) +
                            ", " +
                            tag_child.substring(0, 3);
                        initial = x2[0].toUpperCase();
                        if (grouped_groups[initial] === undefined)
                            grouped_groups[initial] = {};
                        grouped_groups[initial][x2] =
                            all_tags[tag_key][tag_child];
                    }
                });
                sections.push([tag_key, { groups: grouped_groups }]);
            }
            // If a tag has a few children (eg vocaltrack=on/off),
            // then show all the children
            else {
                sections.push([
                    tag_key,
                    { filters: all_tags[tag_key] },
                ]);
            }
            // Remove all tracks which would be discovered by this sub-query
            leftover_tracks = leftover_tracks.filter(
                (t) => !(tag_key in t.tags),
            );
        });
    }

    // If we came up with a bunch of sections, but not every track
    // is included in a section, then include the leftovers in a
    // "Tracks" section.
    // If we didn't come up with any sections, then include the
    // leftovers in an untitled section.
    if (leftover_tracks.length > 0) {
        let leftover_title = sections.length > 0 ? "Tracks" : "";
        sections.push([leftover_title, { tracks: leftover_tracks }]);
    }

    return sections;
}
