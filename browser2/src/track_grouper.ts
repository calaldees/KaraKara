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
    groups: Dictionary<Dictionary<number>>
): Array<string> {
    let last_filter = filters[filters.length - 1];

    // if no search, show a sensible selection
    if (last_filter == undefined) {
        return ["category", "vocalstyle", "vocaltrack", "lang"];
    }

    // if we have an explicit map for "you searched for 'anime',
    // now search by series name", then show that
    const search_configs = {
        "category:anime": ["from"],
        "category:cartoon": ["from"],
        "category:game": ["from"],
        "category:jdrama": ["from"],
        "category:jpop": ["artist", "from"],
        "category:vocaloid": ["artist"],
        "category:tokusatsu": ["from"],
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

    // give up, just show all the tags
    return Object.keys(groups);
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
    tracks: Array<Pick<Track, "tags">>
): Dictionary<Dictionary<number>> {
    let tags: Dictionary<Dictionary<number>> = {};
    for (let n in tracks) {
        for (let tag in tracks[n].tags) {
            if (tag == "title") {
                continue;
            }
            (tracks[n].tags[tag] as Array<string>).map(value => {
                if (tags[tag] == undefined) tags[tag] = {};
                if (tags[tag][value] == undefined) tags[tag][value] = 0;
                tags[tag][value]++;
            });
        }
    }
    return tags;
}

/**
 * Given a number of tracks from 0 to LOTS, decide how best
 * to render the list.
 */
export function group_tracks(
    filters: Array<string>,
    tracks: Array<Track>
): Array<[string, TrackListSection]> {
    // If there are no tracks, show a friendly error
    if (tracks.length == 0) {
        return [["No Results", {}]];
    }

    // If we have a few tracks, just list them all
    if (tracks.length < 20) {
        return [["", { tracks: tracks }]];
    }

    // If we have many tracks, prompt for more filters
    let all_tags = summarise_tags(tracks);
    let section_names = suggest_next_filters(filters, all_tags);
    let leftover_tracks: Array<Track> = tracks;
    let sections: Array<[string, TrackListSection]> = [];
    for (let i = 0; i < section_names.length; i++) {
        let tag_key = section_names[i]; // eg "vocaltrack"
        let tag_values = all_tags[tag_key]; // eg {"on": 2003, "off": 255}
        if (!tag_values) continue;
        // If a filter has a lot of options (eg artist=...) then show options
        // grouped alphabetically
        if (Object.keys(tag_values).length > 50) {
            let grouped_groups = {};
            Object.keys(tag_values).forEach(function (x) {
                if (grouped_groups[x[0]] == undefined)
                    grouped_groups[x[0]] = {};
                grouped_groups[x[0]][x] = tag_values[x];
            });
            sections.push([tag_key, { groups: grouped_groups }]);
        }
        // If a filter has a few options (eg vocaltrack=on/off), then show
        // all the options
        else {
            sections.push([tag_key, { filters: tag_values }]);
        }
        // Remove all tracks which would be discovered by this sub-query
        leftover_tracks = leftover_tracks.filter((t) => !(tag_key in t.tags));
    }

    // If there are tracks which wouldn't be found if we used any
    // of the above filters, show them in a general "Tracks" section
    if (leftover_tracks.length > 0) {
        sections.push(["Tracks", { tracks: leftover_tracks }])
    }

    return sections;
}