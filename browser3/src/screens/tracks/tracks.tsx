import {
    faCircleChevronLeft,
    faCircleChevronRight,
    faCircleMinus,
    faCirclePlus,
    faCircleXmark,
    faListOl,
} from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { ReactElement, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Screen, Thumb } from "@/components";
import { useMemoArr } from "@/hooks/memo";
import { ClientContext } from "@/providers/client";
import { ExploreContext, ExploreProvider } from "@/providers/explore";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import type { Track } from "@/types";
import { normalise_cmp, track_info } from "@/utils";
import { find_tracks } from "@/utils/track_finder";
import { group_tracks } from "@/utils/track_grouper";

import "./tracks.scss";

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
    let extra = "";
    if (
        track.tags.vocaltrack?.includes("on") &&
        track.tags.vocaltrack?.includes("off")
    ) {
        extra = " (Vocal + Instr.)";
    } else if (track.tags.vocaltrack?.includes("off")) {
        extra = " (Instrumental)";
    }

    return (
        <li
            className={"track_item"}
            onClick={(_) => void navigate(`tracks/${track.id}`)}
        >
            <Thumb track={track} />
            <span className={"text track_info"}>
                <span className={"title"}>
                    {track.tags.title[0]}
                    {extra}
                </span>
                <br />
                <span className={"info"}>{track_info(filters, track)}</span>
            </span>
            <FAIcon icon={faCircleChevronRight} className={"go_arrow"} />
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
            <FAIcon
                icon={expanded ? faCircleMinus : faCirclePlus}
                className={"go_arrow"}
            />
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
                        <FAIcon
                            icon={faCircleChevronRight}
                            className={"go_arrow"}
                        />
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
                type={"search"}
                placeholder={"Add search keywords"}
                defaultValue={search}
                enterKeyHint="done"
                data-cy="search"
                onChange={(e) => setSearch(e.currentTarget.value)}
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
                        <FAIcon icon={faCircleXmark} className={"remove"} />
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
                if (body === null) {
                    body = (
                        <ul>
                            <li>
                                <a
                                    style={{
                                        textAlign: "center",
                                        display: "block",
                                        width: "100%",
                                        padding: ".5em",
                                    }}
                                    href="https://karakara.uk/upload/"
                                >
                                    Submit or request additional tracks
                                </a>
                            </li>
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
    return (
        <ExploreProvider>
            <TrackListInternal />
        </ExploreProvider>
    );
}

function TrackListInternal(): ReactElement {
    const { isAdmin } = useContext(RoomContext);
    const { booth, widescreen } = useContext(ClientContext);
    const { filters, setFilters } = useContext(ExploreContext);

    return (
        <Screen
            className={"tracks"}
            navLeft={
                filters.length > 0 && (
                    <FAIcon
                        icon={faCircleChevronLeft}
                        onClick={(_) => setFilters(filters.slice(0, -1))}
                        data-cy="back"
                        className="x2"
                    />
                )
            }
            title={"Explore Tracks"}
            navRight={
                !widescreen && (
                    <Link to="queue" data-cy="queue">
                        <FAIcon icon={faListOl} className="x2" />
                    </Link>
                )
            }
            footer={isAdmin && !booth && <AdminButtons />}
        >
            <Explorer />
        </Screen>
    );
}
