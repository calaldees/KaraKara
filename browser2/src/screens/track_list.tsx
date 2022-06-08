import h from "hyperapp-jsx-pragma";
import { Screen, Thumb } from "./_common";
import {
    ClearScrollPos,
    ApiRequest,
    PushScrollPos,
    PopScrollPos,
} from "../effects";
import { GoToScreen } from "../actions";
import { track_info, find_tracks, choose_section_names, find_all_tags } from "../utils";


///////////////////////////////////////////////////////////////////////
// Actions

function Back(state: State): Dispatchable {
    state.filters.pop();
    return [{ ...state }, PopScrollPos()];
}

const GoToPriorityTokens = (state: State): Dispatchable => [
    state,
    ApiRequest({
        function: "priority_tokens",
        state: state,
        action: (state, response): Dispatchable =>
            response.status == "ok"
                ? [
                    {
                        ...state,
                        screen: "priority_tokens",
                        priority_tokens: response.data.priority_tokens,
                    },
                    PushScrollPos(),
                ]
                : {
                    ...state,
                    priority_tokens: [],
                },
    }),
];

const SelectTrack = (state: State, track_id: string): Dispatchable => [
    { ...state, track_id },
    PushScrollPos(),
];


///////////////////////////////////////////////////////////////////////
// Views

/*
 * List individual tracks
 */
const TrackItem = ({ state, track }: { state: State; track: Track }): VNode => (
    <li class={"track_item"} onclick={[SelectTrack, track.id]}>
        <Thumb state={state} track={track} />
        <span class={"text track_info"}>
            <span class={"title"}>
                {track.tags.title[0]}
                {track.tags.vocaltrack?.[0] == "off" && " (Instrumental)"}
            </span>
            <br />
            <span class={"info"}>
                {track_info(state, track)}
            </span>
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
): VNode => (
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

const GroupedFilterList = ({ heading, filters, expanded }): Array<VNode> =>
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
                        {group}
                    </FilterListGroupHeader>
                    <FilterList heading={heading} filters={filters[group]} />
                </div>
            ) : (
                <FilterListGroupHeader
                    filter={group}
                    count={Object.keys(filters[group]).length}
                    expanded={false}
                >
                    {group}
                </FilterListGroupHeader>
            ),
        );

const FilterList = ({ heading, filters }): Array<VNode> =>
    Object.keys(filters)
        .sort()
        .map((child) => (
            <AddFilter filter={heading + ":" + child} count={filters[child]}>
                {child}
            </AddFilter>
        ));

const AddFilter = (
    { filter, count }: { filter: string; count: number },
    children,
): VNode => (
    <li
        class={"add_filter"}
        onclick={(state) => [
            {
                ...state,
                expanded: null,
                filters: state.filters.concat([filter]),
            },
            PushScrollPos(),
        ]}
    >
        <span class={"text"}>{children}</span>
        <span class={"count"}>{count}</span>
        <span class={"go_arrow"}>
            <i class={"fas fa-chevron-circle-right"} />
        </span>
    </li>
);

/**
 * Search for tracks given the user's conditions
 * - If we have a few tracks, list the tracks
 * - If we have a lot of tracks, prompt for more filters
 */
function show_list(state: State) {
    let tracks = find_tracks(
        state.track_list,
        state.settings['karakara.search.tag.silent_hidden'],
        state.settings['karakara.search.tag.silent_forced'],
        state.filters,
        state.search,
    );
    // console.log("Found", tracks.length, "tracks matching", state.filters, state.search);

    // If we have a few tracks, just list them
    if (tracks.length < 20) {
        return (
            <ul>
                {tracks.map((track) => (
                    <TrackItem state={state} track={track} />
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
    let leftover_tracks: Track[] = tracks;
    let sections: any[] = [];
    for (let i = 0; i < section_names.length; i++) {
        let tag_key = section_names[i]; // eg "vocaltrack"
        let tag_values = all_tags[tag_key]; // eg {"on": 2003, "off": 255}
        let filter_list = null;
        // remove all tracks which would be discovered by this sub-query
        leftover_tracks = leftover_tracks.filter((t) => !(tag_key in t.tags));
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
                <h2>{tag_key}</h2>
                <ul>{filter_list}</ul>
            </div>,
        );
    }

    // if there are tracks which wouldn't be found if we used any
    // of the above filters, show them now
    if (leftover_tracks.length > 0) {
        sections.push(
            <div>
                <h2>Tracks</h2>
                <ul>
                    {leftover_tracks.map((track) => (
                        <TrackItem state={state} track={track} />
                    ))}
                </ul>
            </div>,
        );
    }
    return sections;
}

const Bookmarks = ({ state }: { state: State }) => (
    state.bookmarks.length > 0 &&
    state.filters.length == 0 &&
    state.search == "" && (
        <div>
            <h2>Bookmarks</h2>
            <ul>
                {state.bookmarks.map((bm) => (
                    <TrackItem state={state} track={state.track_list[bm]} />
                ))}
            </ul>
        </div>
    )
);

const AdminButtons = ({ state }: { state: State }): VNode => (
    <footer>
        <div class={"buttons"}>
            <button onclick={GoToPriorityTokens} disabled={state.loading}>
                Priority Tokens
            </button>
            <button onclick={GoToScreen("room_settings", [PushScrollPos()])}>
                Room Settings
            </button>
            <button onclick={GoToScreen("printable_list", [PushScrollPos()])}>
                Printable Tracklist
            </button>
        </div>
    </footer>
);

export const TrackList = ({ state }: { state: State }): VNode => (
    <Screen
        state={state}
        className={"track_list"}
        navLeft={
            (state.filters.length > 0) && (
                <a onclick={Back}>
                    <i class={"fas fa-2x fa-chevron-circle-left"} />
                </a>
            )
        }
        title={"Explore Tracks"}
        navRight={
            !state.widescreen && (
                <a onclick={GoToScreen("queue", [PushScrollPos()])}>
                    <i class={"fas fa-2x fa-list-ol"} />
                </a>
            )
        }
        footer={
            state.is_admin &&
            !state.booth && <AdminButtons state={state} />
        }
    >
        {/* Full-text search */}
        <input
            class={"search"}
            type={"text"}
            placeholder={"Add search keywords"}
            value={state.search}
            oninput={(state: State, event: FormInputEvent): Dispatchable => ({
                ...state,
                search: event.target.value,
            })}
        />

        {/* List active filters */}
        <div class={"active_filter_list"}>
            {state.filters.map((filter) => (
                <a
                    class={"active_filter"}
                    onclick={(state: State): Dispatchable => [
                        {
                            ...state,
                            expanded: null,
                            filters: state.filters.filter((v) => v !== filter),
                        },
                        ClearScrollPos(),
                    ]}
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

        {/* If no filters, show bookmarks */}
        <Bookmarks state={state} />
    </Screen>
);
