import { useContext, useMemo, useState, useCallback } from "react";
import { Screen, Thumb } from "./_common";
import { normalise_cmp, track_info } from "../utils";
import { find_tracks } from "../track_finder";
import { group_tracks } from "../track_grouper";
import * as icons from "../static/icons";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ClientContext } from "../providers/client";
import { ServerContext } from "../providers/server";
import { RoomContext } from "../providers/room";

///////////////////////////////////////////////////////////////////////
// Views

/*
 * List individual tracks
 */
function TrackItem({
    track,
    filters,
}: {
    track: Track;
    filters: string[];
}): React.ReactElement {
    const navigate = useNavigate();

    return (
        <li
            className={"track_item"}
            onClick={(e) => navigate(`tracks/${track.id}`)}
        >
            <Thumb track={track} />
            <span className={"text track_info"}>
                <span className={"title"}>
                    {track.tags.title[0]}
                    {track.tags.vocaltrack?.[0] === "off" && " (Instrumental)"}
                </span>
                <br />
                <span className={"info"}>{track_info(filters, track)}</span>
            </span>
            <span className={"go_arrow"}>
                <icons.CircleChevronRight />
            </span>
        </li>
    );
}

/*
 * List groups of tracks
 */
const FilterListGroupHeader = ({
    filter,
    count,
    expanded,
    setExpanded,
    children,
}: {
    filter: string;
    count: number;
    expanded: boolean;
    setExpanded: any;
    children: React.ReactNode;
}): React.ReactElement => (
    <li
        className={"filter_list_group_header"}
        onClick={(e) => setExpanded(expanded ? null : filter)}
    >
        <span className={"text"}>{children}</span>
        <span className={"count"}>{count}</span>
        <span className={"go_arrow"}>
            {expanded ? <icons.CircleMinus /> : <icons.CirclePlus />}
        </span>
    </li>
);

const GroupedFilterList = ({
    heading,
    filters,
    expanded,
    setExpanded,
    setFilters,
}: {
    heading: string;
    filters: Record<string, Record<string, number>>;
    expanded: string | null;
    setExpanded: any;
    setFilters: any;
}): React.ReactElement => (
    <ul>
        {Object.keys(filters)
            .sort(normalise_cmp)
            .map((group) =>
                group === expanded ? (
                    <div key={group} className={"filter_list_group"}>
                        <FilterListGroupHeader
                            filter={group}
                            count={Object.keys(filters[group]).length}
                            expanded={true}
                            setExpanded={setExpanded}
                        >
                            {group}
                        </FilterListGroupHeader>
                        <FilterList
                            heading={heading}
                            filters={filters[group]}
                            setExpanded={setExpanded}
                            setFilters={setFilters}
                        />
                    </div>
                ) : (
                    <FilterListGroupHeader
                        key={group}
                        filter={group}
                        count={Object.keys(filters[group]).length}
                        expanded={false}
                        setExpanded={setExpanded}
                    >
                        {group}
                    </FilterListGroupHeader>
                ),
            )}
    </ul>
);

function unThe(filter: string): string {
    if (filter.toLowerCase().endsWith(", the")) {
        return (
            filter.substring(filter.length - 3) +
            " " +
            filter.substring(0, filter.length - 5)
        );
    }
    return filter;
}

const FilterList = ({
    heading,
    filters,
    setExpanded,
    setFilters,
}: {
    heading: string;
    filters: Record<string, number>;
    setExpanded: any;
    setFilters: any;
}): React.ReactElement => (
    <ul>
        {Object.keys(filters)
            .sort(normalise_cmp)
            .map((child) => (
                <li
                    key={child}
                    className={"add_filter"}
                    onClick={(e) => {
                        setExpanded(null);
                        setFilters((filters: string[]) => [
                            ...filters,
                            heading + ":" + unThe(child),
                        ]);
                    }}
                >
                    <span className={"text"}>{child}</span>
                    <span className={"count"}>{filters[child]}</span>
                    <span className={"go_arrow"}>
                        <icons.CircleChevronRight />
                    </span>
                </li>
            ))}
    </ul>
);

function Bookmarks({
    bookmarks,
    track_list,
}: {
    bookmarks: string[];
    track_list: Record<string, Track>;
}) {
    return (
        <div>
            <h2>Bookmarks</h2>
            <ul>
                {bookmarks
                    .filter((bm) => bm in track_list)
                    .map((bm) => (
                        <TrackItem key={bm} track={track_list[bm]} filters={[]} />
                    ))}
            </ul>
        </div>
    );
}

function AdminButtons(): React.ReactElement {
    return (
        <footer>
            <div className={"buttons"}>
                <Link to="settings" className="button">
                    Room Settings
                </Link>
                <Link to="printable" className="button">
                    Printable Tracklist
                </Link>
            </div>
        </footer>
    );
}

export function TrackList(): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { isAdmin, settings } = useContext(RoomContext);
    const { booth, bookmarks, widescreen } = useContext(ClientContext);
    const [expanded, setExpanded] = useState<string | null>(null);
    const [inSearch, setInSearch] = useState(false);

    const [searchParams, setSearchParams] = useSearchParams();
    const search: string = searchParams.get("search") ?? "";
    const filters: string[] = searchParams.getAll("filters");
    const setSearch = useCallback(function(s: string) {
        setSearchParams({ search: s, filters: filters }, { replace: inSearch });
        setInSearch(true);
    }, []);
    const setFilters = useCallback(function(fs: string[] | CallableFunction) {
        const f2 = Array.isArray(fs) ? fs : fs(filters);
        setSearchParams({ search: search, filters: f2 });
        setInSearch(false);
    }, []);

    // find_tracks took 16ms, of which 15ms was spent sorting the
    // results of the search -- if we sort once in advance, then
    // every future search is 1ms
    let allTrackList = useMemo(
        () => Object.values(tracks).sort((a, b) => normalise_cmp(a.tags.title[0], b.tags.title[0])),
        [tracks],
    )
    // memoise based on searchParams, not searchParams.getAll("filters"),
    // because the latter returns a fresh new Array object every time
    let sections = useMemo(
        () => group_tracks(
            searchParams.getAll("filters"),
            find_tracks(
                allTrackList,
                searchParams.getAll("filters"),
                searchParams.get("search") ?? "",
                settings["hidden_tags"] ?? [],
                settings["forced_tags"] ?? [],
            )
        ),
        [allTrackList, searchParams, settings],
    );

    return (
        <Screen
            className={"track_list"}
            navLeft={
                filters.length > 0 && (
                    <div
                        onClick={(e) => setFilters(filters.slice(0, -1))}
                        data-cy="back"
                    >
                        <icons.CircleChevronLeft className="x2" />
                    </div>
                )
            }
            title={"Explore Tracks"}
            navRight={
                !widescreen && (
                    <Link to="queue" data-cy="queue">
                        <icons.ListOl className="x2" />
                    </Link>
                )
            }
            footer={isAdmin && !booth && <AdminButtons />}
        >
            {/* Full-text search */}
            <input
                className={"search"}
                type={"text"}
                placeholder={"Add search keywords"}
                value={search}
                data-cy="search"
                onChange={(e) => setSearch(e.target.value)}
            />

            {/* List active filters */}
            <div className={"active_filter_list"}>
                {filters.map((filter) => (
                    <div
                        key={filter}
                        className={"active_filter"}
                        onClick={(e) => {
                            setExpanded(null);
                            setFilters(filters.filter((v) => v !== filter));
                        }}
                    >
                        <span className={"remove"}>
                            <icons.CircleXmark />
                        </span>
                        <span className={"name"} title={filter}>
                            {filter.split(":")[1]}
                        </span>
                    </div>
                ))}
            </div>

            {/* Show list of tags, or tracks */}
            {sections.map(([heading, section]) => {
                let body = null;
                if (section.groups) {
                    body = (
                        <GroupedFilterList
                            key={heading}
                            heading={heading}
                            filters={section.groups}
                            expanded={expanded}
                            setExpanded={setExpanded}
                            setFilters={setFilters}
                        />
                    );
                }
                if (section.filters) {
                    body = (
                        <FilterList
                            key={heading}
                            heading={heading}
                            filters={section.filters}
                            setExpanded={setExpanded}
                            setFilters={setFilters}
                        />
                    );
                }
                if (section.tracks) {
                    body = (
                        <ul key={heading}>
                            {section.tracks.map((track) => (
                                <TrackItem
                                    key={track.id}
                                    track={track}
                                    filters={filters}
                                />
                            ))}
                        </ul>
                    );
                }
                return (
                    <div key={heading}>
                        {heading && <h2>{heading}</h2>}
                        {body}
                    </div>
                );
            })}

            {/* If no filters, show bookmarks */}
            {bookmarks.length > 0 && filters.length === 0 && search === "" && (
                <Bookmarks bookmarks={bookmarks} track_list={tracks} />
            )}
        </Screen>
    );
}
