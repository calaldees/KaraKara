import h from "hyperapp-jsx-pragma";
import { Screen, Thumb } from "./_common";
import {
    ClearScrollPos,
    ApiRequest,
    PushScrollPos,
    PopScrollPos,
} from "../effects";
import { GoToScreen } from "../actions";
import { track_info } from "../utils";
import { find_tracks } from "../track_finder";
import { group_tracks } from "../track_grouper";

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
            <span class={"info"}>{track_info(state.filters, track)}</span>
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

const GroupedFilterList = ({ heading, filters, expanded }): VNode => (
    <ul>
        {Object.keys(filters)
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
                        <FilterList
                            heading={heading}
                            filters={filters[group]}
                        />
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
            )}
    </ul>
);

function titleCmp(a: string, b: string): number {
    const nameA = a.toLowerCase().replace(/^(the )/, "");
    const nameB = b.toLowerCase().replace(/^(the )/, "");
    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }
    return 0;
}

const FilterList = ({ heading, filters }): VNode => (
    <ul>
        {Object.keys(filters)
            .sort(titleCmp)
            .map((child) => (
                <AddFilter
                    filter={heading + ":" + child}
                    count={filters[child]}
                >
                    {child}
                </AddFilter>
            ))}
    </ul>
);

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
    let tracks = find_tracks(state);
    // console.log("Found", tracks.length, "tracks matching", state.filters, state.search);
    let sections = group_tracks(state.filters, tracks);
    return sections.map(([heading, section]) => {
        let body = null;
        if (section.groups) {
            body = (
                <GroupedFilterList
                    heading={heading}
                    filters={section.groups}
                    expanded={state.expanded}
                />
            );
        }
        if (section.filters) {
            body = <FilterList heading={heading} filters={section.filters} />;
        }
        if (section.tracks) {
            body = (
                <ul>
                    {section.tracks.map((track) => (
                        <TrackItem state={state} track={track} />
                    ))}
                </ul>
            );
        }
        return (
            <div>
                {heading && <h2>{heading}</h2>}
                {body}
            </div>
        );
    });
}

const Bookmarks = ({ state }: { state: State }) =>
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
    );

const AdminButtons = ({ state }: { state: State }): VNode => (
    <footer>
        <div class={"buttons"}>
            {/*
            <button onclick={GoToPriorityTokens} disabled={state.loading}>
                Priority Tokens
            </button>
            */}
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
            state.filters.length > 0 && (
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
            state.is_admin && !state.booth && <AdminButtons state={state} />
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
