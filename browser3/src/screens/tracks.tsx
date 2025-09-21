import {
    createContext,
    useCallback,
    useContext,
    useMemo,
    useState,
    ReactElement,
} from "react";
import { Screen, Thumb } from "./_common";
import { normalise_cmp, track_info } from "../utils";
import { find_tracks } from "../track_finder";
import { group_tracks } from "../track_grouper";
import * as icons from "../static/icons";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ClientContext } from "../providers/client";
import { ServerContext } from "../providers/server";
import { RoomContext } from "../providers/room";
import type { Track } from "../types";
import { useMemoArr } from "../hooks/memo";

interface ExploreContextType {
    search: string;
    setSearch: (_: string) => void;
    filters: string[];
    setFilters: (_: any) => void;
    expanded: string | null;
    setExpanded: (_: string | null) => void;
}

const ExploreContext = createContext<ExploreContextType>({
    search: "",
    setSearch: (_: string) => null,
    filters: [],
    setFilters: (_: any) => null,
    expanded: null,
    setExpanded: (_: string | null) => null,
});

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
            onClick={(_) => void navigate(`tracks/${track.id}`)}
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
function FilterListGroupHeader({
    filter,
    count,
    expanded,
    children,
}: {
    filter: string;
    count: number;
    expanded: boolean;
    children: React.ReactNode;
}): React.ReactElement {
    const { setExpanded } = useContext(ExploreContext);

    return (
        <li
            className={"filter_list_group_header"}
            onClick={(_) => setExpanded(expanded ? null : filter)}
        >
            <span className={"text"}>{children}</span>
            <span className={"count"}>{count}</span>
            <span className={"go_arrow"}>
                {expanded ? <icons.CircleMinus /> : <icons.CirclePlus />}
            </span>
        </li>
    );
}

function GroupedFilterList({
    heading,
    filters,
}: {
    heading: string;
    filters: Record<string, Record<string, number>>;
}): React.ReactElement {
    const { expanded } = useContext(ExploreContext);

    return (
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
                            key={group}
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
}

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

function FilterList({
    heading,
    filters,
}: {
    heading: string;
    filters: Record<string, number>;
}): React.ReactElement {
    const { setFilters, setExpanded } = useContext(ExploreContext);

    return (
        <ul>
            {Object.keys(filters)
                .sort(normalise_cmp)
                .map((child) => (
                    <li
                        key={child}
                        className={"add_filter"}
                        onClick={(_) => {
                            setExpanded(null);
                            setFilters((fs: string[]) => [
                                ...fs,
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
}

function Bookmarks({
    bookmarks,
    tracks,
    trackList,
}: {
    bookmarks: string[];
    tracks: Record<string, Track>;
    trackList: Track[];
}) {
    const visibleTrackIDs = useMemoArr(
        () => trackList.map((track) => track.id),
        [trackList],
    );
    return (
        <div>
            <h2>Bookmarks</h2>
            <ul>
                {bookmarks
                    .filter((bm) => bm in tracks)
                    .filter((bm) => visibleTrackIDs.includes(bm))
                    .map((bm) => (
                        <TrackItem key={bm} track={tracks[bm]} filters={[]} />
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
                    Printable QR Code
                </Link>
            </div>
        </footer>
    );
}

function Explorer(): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { trackList } = useContext(RoomContext);
    const { bookmarks } = useContext(ClientContext);
    const { search, setSearch, filters, setFilters, setExpanded } =
        useContext(ExploreContext);

    const sections = useMemoArr(
        () => group_tracks(filters, find_tracks(trackList, filters, search)),
        [trackList, search, filters],
    );

    return (
        <>
            {/* Full-text search */}
            <input
                className={"search"}
                type={"text"}
                placeholder={"Add search keywords"}
                defaultValue={search}
                data-cy="search"
                onChange={(e) => setSearch(e.target.value)}
            />

            {/* List active filters */}
            <div className={"active_filter_list"}>
                {filters.map((filter) => (
                    <div
                        key={filter}
                        className={"active_filter"}
                        onClick={(_) => {
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
                        />
                    );
                }
                if (section.filters) {
                    body = (
                        <FilterList
                            key={heading}
                            heading={heading}
                            filters={section.filters}
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
                <Bookmarks
                    bookmarks={bookmarks}
                    tracks={tracks}
                    trackList={trackList}
                />
            )}
        </>
    );
}

export function TrackList(): ReactElement {
    const { isAdmin } = useContext(RoomContext);
    const { booth, widescreen } = useContext(ClientContext);

    const [expanded, setExpanded] = useState<string | null>(null);
    const [inSearch, setInSearch] = useState(false);

    const [searchParams, setSearchParams] = useSearchParams();
    const search = useMemo(
        () => searchParams.get("search") ?? "",
        [searchParams],
    );
    const filters = useMemo(
        () => searchParams.getAll("filters"),
        [searchParams],
    );

    const setSearch = useCallback(
        (new_search: string | ((search: string) => string)) => {
            const updatedSearch =
                typeof new_search === "function"
                    ? new_search(search)
                    : new_search;
            setSearchParams(
                { search: updatedSearch, filters },
                { replace: inSearch },
            );
            setInSearch(true);
        },
        [search, filters, setSearchParams, inSearch],
    );

    const setFilters = useCallback(
        (new_filters: string[] | ((filters: string[]) => string[])) => {
            const updatedFilters =
                typeof new_filters === "function"
                    ? new_filters(filters)
                    : new_filters;
            setSearchParams({ search, filters: updatedFilters });
            setInSearch(false);
        },
        [search, filters, setSearchParams],
    );

    const exploreContextValue = useMemo(
        (): ExploreContextType => ({
            search,
            setSearch,
            filters,
            setFilters,
            expanded,
            setExpanded,
        }),
        [search, setSearch, filters, setFilters, expanded, setExpanded],
    );
    return (
        <Screen
            className={"track_list"}
            navLeft={
                filters.length > 0 && (
                    <div
                        onClick={(_) => setFilters(filters.slice(0, -1))}
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
            <ExploreContext value={exploreContextValue}>
                <Explorer />
            </ExploreContext>
        </Screen>
    );
}
