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

/**
 * If track has a 'hidden' tag, then skip it, UNLESS it also has
 * other non-hidden tags with the same parent. Consider top-level
 * tags to have different parents.
 */
export function apply_hidden(tracks: Array<Track>, silent_hidden: Array<string>): Array<Track> {
    // Translate
    //   hidden=category:anime,category:retro,broken
    // into
    //   {"category": ["anime", "retro"], "broken": []}
    let hidden: Dictionary<Array<string>> = {};
    silent_hidden.map(x => {
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
            ([tag_key, tag_value]) => (track.tags[tag_key] as Array<string>).includes(tag_value)
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
export function choose_section_names(
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
export function calculate_list_sections(
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
    let section_names = choose_section_names(filters, all_tags);
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

/**
 * All the searching in one place, for benchmarking
 */
export function find_tracks(state: State): Array<Track> {
    let tracks = Object.values(state.track_list);
    tracks = apply_hidden(tracks, state.settings['karakara.search.tag.silent_hidden']);
    tracks = apply_tags(tracks, state.settings['karakara.search.tag.silent_forced']);
    tracks = apply_tags(tracks, state.filters);
    tracks = apply_search(tracks, state.search);
    tracks.sort((a, b) => (a.tags.title[0] > b.tags.title[0] ? 1 : -1));
    return tracks;
}
