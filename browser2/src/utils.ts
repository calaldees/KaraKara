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
    return ""+val;
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
    item?: QueueItem
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
export function last_tag(tags: Dictionary<Array<string> | undefined>, start: string): string {
    let tag = start;
    while(tags[tag]) {
        tag = tags[tag]?.[0] || "";
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
export function track_info(state: Pick<State, "filters">, track: Pick<Track, "tags">): string {
    let info_tags = title_tags_for_category[track.tags.category?.[0] || "DEFAULT"] || title_tags_for_category["DEFAULT"];
    // look at series that are in the search box
    let search_from = state.filters.filter(x => x.startsWith("from:")).map(x => x.replace("from:", ""));
    let info_data = (
        info_tags
            // Ignore undefined tags
            .filter(x => track.tags.hasOwnProperty(x))
            // We always display track title, so ignore any tags which duplicate that
            .filter(x => track.tags[x]?.[0] != track.tags.title[0])
            // If we've searched for "from:naruto", don't prefix every track title with "this is from naruto"
            .filter(x => x != "from" || !search_from.includes(track.tags[x]?.[0] || ""))
            // Format a list of tags
            .map(x => track.tags[x]?.join(", "))
    );
    let info = info_data.join(" - ");
    return info;
}

/**
 * Search the full list of all known tracks based on tags + full-text search,
 * return a list of Track objects
 */
export function find_tracks(
    track_list: Dictionary<Track>,
    silent_hidden: Array<string>,
    silent_forced: Array<string>,
    user_filters: Array<string>,
    search: string,
): Array<Track> {
    let tracks: any[] = [];

    // translate hidden=category:anime,category:retro,broken into
    // {"category": ["anime", "retro"], "broken": []}
    let hidden: Dictionary<Array<string>> = {};
    silent_hidden.map(x => {
        let [k, v] = x.split(":");
        if(!hidden[k]) hidden[k] = [];
        if(v) hidden[k].push(v);
    });

    // translate eg "retro" to ":retro" so that all filters
    // consistently use the "key:value" syntax
    let forced = silent_forced.map(x => x.includes(":") ? x : ":"+x);
    let filters = user_filters.concat(forced);

    tracks: for (let track_id in track_list) {
        let track = track_list[track_id];

        // If track has a 'hidden' tag, then skip it, UNLESS it also has
        // other non-hidden tags with the same parent. Consider top-level
        // tags to have different parents.
        let hidden_keys = Object.keys(hidden);
        for(let i=0; i<hidden_keys.length; i++) {
            let hidden_key = hidden_keys[i];
            let hidden_values = hidden[hidden_key];

            // If
            //   hidden = {"category": ["anime", "cartoon"]}
            // then remove any track where:
            //   tags["category"].length > 0 &&
            //   tags["category"] - {"anime", "cartoon"} == set()
            if(hidden_values.length > 0) {
                if(
                    track.tags[hidden_key]?.length &&
                    !track.tags[hidden_key]?.filter(x => !hidden_values.includes(x)).length
                ) {
                    continue tracks;
                }    
            }

            // If
            //   hidden = {"broken": []}
            // then remove any track where:
            //   tags[""].includes("broken")
            else {
                if(track.tags[""]?.includes(hidden_key)) {
                    continue tracks;
                }
            }
        }

        // If user filters for from:macross, then check
        //   track.tags["from"].includes("macross")
        for (let i = 0; i < filters.length; i++) {
            let [filter_key, filter_value] = filters[i].split(":");
            if (!track.tags[filter_key]?.includes(filter_value)) {
                continue tracks;
            }
        }

        // If the user uses free-text search, then check all tag values
        // for matching text, and skip if we have no matches
        if (search != "") {
            search = search.toLowerCase();
            let any_match = Object.values(track.tags).some(
                tag_values => (tag_values || []).some(
                    value => value.toLowerCase().indexOf(search) >= 0
                )
            )
            if (!any_match) continue;
        }

        tracks.push(track);
    }
    tracks.sort((a, b) => (a.tags.title[0] > b.tags.title[0] ? 1 : -1));
    return tracks;
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
            tracks[n].tags[tag]?.map(value => {
                if (tags[tag] == undefined) tags[tag] = {};
                if (tags[tag][value] == undefined) tags[tag][value] = 0;
                tags[tag][value]++;
            });
        }
    }
    return tags;
}
