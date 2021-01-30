import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { get_attachment, title_case } from "../utils";
import { ApiRequest } from "../effects";

/*
 * List individual tracks
 */
const TrackItem = ({ track }: { track: Track }) => (
    <li
        class={"track_item"}
        onclick={(state) => ({ ...state, track_id: track.id })}
    >
        <div
            class={"thumb"}
            style={{
                "background-image":
                    "url(" + get_attachment(track, "image") + ")",
            }}
        />
        <span class={"text track_info"}>
            <span class={"from"}>
                {title_case((track.tags["from"] || track.tags["artist"])[0])}
            </span>
            <br />
            <span class={"title"}>{title_case(track.tags["title"][0])}</span>
        </span>
        <span class={"go_arrow"}>
            <i class={"fas fa-chevron-circle-right"} />
        </span>
    </li>
);

/*
 * List groups of tracks
 */
const FilterListGroupHeader = (
    {
        filter,
        count,
        expanded,
    }: { filter: string; count: number; expanded: boolean },
    children,
) => (
    <li
        class={"filter_list_group_header"}
        onclick={(state) => ({ ...state, expanded: expanded ? null : filter })}
    >
        <span class={"text"}>{children}</span>
        <span class={"count"}>{count}</span>
        <span class={"go_arrow"}>
            <i
                class={expanded ? "fas fa-minus-circle" : "fas fa-plus-circle"}
            />
        </span>
    </li>
);

const GroupedFilterList = ({ heading, filters, expanded }) =>
    Object.keys(filters)
        .sort()
        .map((group) =>
            group == expanded ? (
                <div class={"filter_list_group"}>
                    <FilterListGroupHeader
                        filter={group}
                        count={Object.keys(filters[group]).length}
                        expanded={true}
                    >
                        {title_case(group)}
                    </FilterListGroupHeader>
                    <FilterList heading={heading} filters={filters[group]} />
                </div>
            ) : (
                <FilterListGroupHeader
                    filter={group}
                    count={Object.keys(filters[group]).length}
                    expanded={false}
                >
                    {title_case(group)}
                </FilterListGroupHeader>
            ),
        );

const FilterList = ({ heading, filters }) =>
    Object.keys(filters)
        .sort()
        .map((child) => (
            <AddFilter filter={heading + ":" + child} count={filters[child]}>
                {title_case(child)}
            </AddFilter>
        ));

const AddFilter = (
    { filter, count }: { filter: string; count: number },
    children,
) => (
    <li
        class={"add_filter"}
        onclick={(state) => ({
            ...state,
            expanded: null,
            filters: state.filters.concat([filter]),
        })}
    >
        <span class={"text"}>{children}</span>
        <span class={"count"}>{count}</span>
        <span class={"go_arrow"}>
            <i class={"fas fa-chevron-circle-right"} />
        </span>
    </li>
);

/**
 * Search the full list of all known tracks based on tags + full-text search,
 * return a list of Track objects
 */
function find_tracks(
    track_list: Dictionary<Track>,
    filters: Array<string>,
    search: string,
): Array<Track> {
    let tracks = [];
    tracks: for (let track_id in track_list) {
        let track = track_list[track_id];
        if (filters.length > 0) {
            for (let filter_n = 0; filter_n < filters.length; filter_n++) {
                let filter = filters[filter_n].split(":");
                let filter_key = filter[0];
                let filter_value = filter[1];
                if (track.tags[filter_key] == undefined) {
                    continue tracks;
                }
                if (
                    track.tags[filter_key].filter((x) => x == filter_value)
                        .length == 0
                ) {
                    continue tracks;
                }
            }
        }
        if (search != "") {
            search = search.toLowerCase();
            let any_match = false;
            if (track_id.startsWith(search)) any_match = true;
            fts_match: for (let tag in track.tags) {
                if (!track.tags.hasOwnProperty(tag)) continue;
                for (let i = 0; i < track.tags[tag].length; i++) {
                    if (track.tags[tag][i].toLowerCase().indexOf(search) >= 0) {
                        any_match = true;
                        break fts_match;
                    }
                }
            }
            if (!any_match) continue;
        }
        tracks.push(track);
    }
    tracks.sort((a, b) => (a.title > b.title ? 1 : -1));
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
 *   from:gundam    -> gundam (wing, waltz, unicorn)
 */
function choose_section_names(state: State, groups: {}) {
    let last_filter = state.filters[state.filters.length - 1];

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
function find_all_tags(tracks: Array<Track>) {
    let tags = {};
    for (let n in tracks) {
        for (let tag in tracks[n].tags) {
            if (tag == "title") {
                continue;
            }
            for (let value_n in tracks[n].tags[tag]) {
                let value = tracks[n].tags[tag][value_n];
                if (tags[tag] == undefined) tags[tag] = {};
                if (tags[tag][value] == undefined) tags[tag][value] = 0;
                tags[tag][value]++;
            }
        }
    }
    return tags;
}

/**
 * Search for tracks given the user's conditions
 * - If we have a few tracks, list the tracks
 * - If we have a lot of tracks, prompt for more filters
 */
function show_list(state: State) {
    let tracks = find_tracks(state.track_list, state.filters, state.search);
    // console.log("Found", tracks.length, "tracks matching", state.filters, state.search);

    // If we have a few tracks, just list them
    if (tracks.length < 20) {
        return (
            <ul>
                {tracks.map((track) => (
                    <TrackItem track={track} />
                ))}
            </ul>
        );
    }
    let all_tags = find_all_tags(tracks);
    let section_names = choose_section_names(state, all_tags);

    /*
     * If we're looking at a tag with few values (eg vocaltrack=on/off),
     * then show the full list.
     *
     * <FilterList filters={{"on": 2003, "off": 255}} />
     *
     * If we're looking at a tag with a lot of values (eg artist=...),
     * then group those values like:
     *
     * <GroupedFilterList filters={{
     *     "a": {"a little snow fairy sugar": 41, "a.d. police": 22, ...},
     *     "b": {"baka and test": 2, "bakemonogatari": 1, ...},
     *     ...
     * }} />
     */
    let sections = [];
    for (let i = 0; i < section_names.length; i++) {
        let tag_key = section_names[i]; // eg "vocaltrack"
        let tag_values = all_tags[tag_key]; // eg {"on": 2003, "off": 255}
        let filter_list = null;
        if (Object.keys(tag_values).length > 50) {
            let grouped_groups = {};
            Object.keys(tag_values).forEach(function (x) {
                if (grouped_groups[x[0]] == undefined)
                    grouped_groups[x[0]] = {};
                grouped_groups[x[0]][x] = tag_values[x];
            });
            filter_list = (
                <GroupedFilterList
                    heading={tag_key}
                    filters={grouped_groups}
                    expanded={state.expanded}
                />
            );
        } else {
            filter_list = <FilterList heading={tag_key} filters={tag_values} />;
        }
        sections.push(
            <div>
                <h2>{title_case(tag_key)}</h2>
                <ul>{filter_list}</ul>
            </div>,
        );
    }
    return sections;
}

function back(state: State): State {
    if (state.filters.length > 0) {
        // if we're searching the list, take a step back in the search
        state.filters.pop();
    } else {
        // if we're at the start of the exploring process and
        // go back, go to the login screen
        state.room_name = "";
        state.track_list = {};
    }
    return { ...state };
}

const AdminButtons = () => (
    <footer>
        <div class={"buttons"}>
            <button
                onclick={(state) => [
                    state,
                    ApiRequest({
                        function: "priority_tokens",
                        state: state,
                        action: (state, response) =>
                            response.status == "ok"
                                ? {
                                      ...state,
                                      screen: "priority_tokens",
                                      priority_tokens:
                                          response.data.priority_tokens,
                                  }
                                : {
                                      ...state,
                                      priority_tokens: [],
                                  },
                    }),
                ]}
            >
                Priority Tokens
            </button>
            <button
                onclick={(state) => [
                    state,
                    ApiRequest({
                        function: "settings",
                        state: state,
                        action: (state, response) => ({
                            ...state,
                            screen: "room_settings",
                            settings: response.data.settings,
                        }),
                    }),
                ]}
            >
                Room Settings
            </button>
            <button
                onclick={(state) => [{ ...state, screen: "printable_list" }]}
            >
                Printable Tracklist
            </button>
        </div>
    </footer>
);

export const TrackList = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"track_list"}
        navLeft={
            <a onclick={back}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={"Explore Tracks"}
        navRight={
            <a
                onclick={(state) => ({
                    ...state,
                    screen: state.room_password ? "control" : "queue",
                })}
            >
                <i class={"fas fa-2x fa-list-ol"} />
            </a>
        }
        footer={state.room_password && <AdminButtons />}
    >
        {/* Full-text search */}
        <input
            class={"search"}
            type={"text"}
            placeholder={"Add search keywords"}
            value={state.search}
            oninput={(state: State, event: FormInputEvent) =>
                ({
                    ...state,
                    search: event.target.value,
                } as State)
            }
        />

        {/* List active filters */}
        <div class={"active_filter_list"}>
            {state.filters.map((filter) => (
                <a
                    class={"active_filter"}
                    onclick={(state) => ({
                        ...state,
                        expanded: null,
                        filters: state.filters.filter((v) => v !== filter),
                    })}
                >
                    <span class={"remove"}>
                        <i class={"fas fa-times-circle"} />
                    </span>
                    <span class={"name"} title={filter.split(":")[0]}>
                        {filter.split(":")[1]}
                    </span>
                </a>
            ))}
        </div>

        {/* Show list of tags, or tracks */}
        {show_list(state)}
    </Screen>
);
