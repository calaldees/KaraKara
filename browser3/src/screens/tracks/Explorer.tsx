import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext, useEffect, useRef } from "react";

import { useMemoArr } from "@/hooks/memo";
import { ClientContext } from "@/providers/client";
import { ExploreContext } from "@/providers/explore";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import { find_tracks } from "@/utils/track_finder";
import { group_tracks } from "@/utils/track_grouper";

import { Bookmarks } from "./Bookmarks";
import { FilterList } from "./FilterList";
import { GroupedFilterList } from "./GroupedFilterList";
import { TrackItem } from "./TrackItem";

import { List } from "@/components";
import styles from "./Explorer.module.scss";

export function Explorer(): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { trackList } = useContext(RoomContext);
    const { bookmarks } = useContext(ClientContext);
    const { search, setSearch, filters, setFilters, setExpanded } =
        useContext(ExploreContext);

    const sections = useMemoArr(
        () => group_tracks(filters, find_tracks(trackList, filters, search)),
        [trackList, search, filters],
    );

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const article = containerRef.current?.closest("article");
        if (article) {
            article.scrollTo(0, 0);
        }
    }, [filters]);

    return (
        <div ref={containerRef}>
            {/* Full-text search */}
            <input
                className={styles.search}
                type={"search"}
                placeholder={"Add search keywords"}
                defaultValue={search}
                enterKeyHint="done"
                data-cy="search"
                onChange={(e) => setSearch(e.currentTarget.value)}
            />

            {/* List active filters */}
            <div className={styles.activeFilterList}>
                {filters.map((filter) => (
                    <div
                        key={filter}
                        className={styles.activeFilter}
                        onClick={(_) => {
                            setExpanded(null);
                            setFilters(filters.filter((v) => v !== filter));
                        }}
                    >
                        <FAIcon
                            icon={faCircleXmark}
                            className={styles.remove}
                        />
                        <span title={filter}>{filter.split(":")[1]}</span>
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
                        <List key={heading}>
                            {section.tracks.map((track) => (
                                <TrackItem
                                    key={track.id}
                                    track={track}
                                    filters={filters}
                                />
                            ))}
                        </List>
                    );
                }
                if (body === null) {
                    body = (
                        <List>
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
                        </List>
                    );
                }
                return (
                    <div key={heading}>
                        {heading && !heading.startsWith("_") && (
                            <h2>{heading}</h2>
                        )}
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
        </div>
    );
}
