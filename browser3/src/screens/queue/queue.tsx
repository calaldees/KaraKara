import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useContext, useEffect, useState } from "react";

import { BackToExplore, FontAwesomeIcon, Screen, Thumb } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import type { QueueItem, Subtitle, Track } from "@/types";
import {
    attachment_path,
    dict2css,
    is_my_song,
    shuffle,
    time_until,
} from "@/utils";

import "./queue.scss";

function QueueItemRender({
    item,
    show_time,
    track,
}: {
    item: QueueItem;
    show_time: boolean;
    track: Track;
}): React.ReactElement {
    const { performerName } = useContext(ClientContext);
    const { now } = useContext(ServerTimeContext);
    const { request, sessionId } = useApi();

    function removeTrack(queue_item_id: number) {
        request({
            notify: "Removing track...",
            notify_ok: "Track removed!",
            function: "queue/" + queue_item_id.toString(),
            options: {
                method: "DELETE",
            },
        });
    }

    return (
        <li
            className={dict2css({
                queue_item: true,
                me: is_my_song(sessionId, performerName, item),
            })}
        >
            <Thumb track={track} />
            <span className={"text queue_info"}>
                <span className={"title"}>{track.tags.title[0]}</span>
                <br />
                <span className={"performer"}>{item.performer_name}</span>
            </span>
            {show_time && item.start_time && (
                <span className={"count"}>
                    {time_until(now, item.start_time)}
                </span>
            )}

            {/*
             * Specifically check ID matches, not name-or-ID matches
             * (as in is_my_song()) because ID needs to match otherwise
             * the server will reject it
             */}
            {sessionId === item.session_id && (
                <span
                    data-cy="remove"
                    className={"go_arrow"}
                    onClick={(_) => removeTrack(item.id)}
                >
                    <FontAwesomeIcon icon={faCircleXmark} />
                </span>
            )}
        </li>
    );
}

function Lyrics({ track }: { track: Track }) {
    const { request } = useApi();

    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    useEffect(() => {
        const subtitleAttachment = track?.attachments.subtitle?.find(
            (a) => a.mime === "application/json",
        );
        if (subtitleAttachment) {
            request({
                url: attachment_path(subtitleAttachment),
                options: { credentials: "omit" },
                onAction: (result) => setLyrics(result),
            });
        }
    }, [request, track]);
    if (lyrics.length > 0) {
        return (
            <li>
                <span className={"lyrics"}>
                    {lyrics.map((line, n) => (
                        <div key={n}>{line.text}</div>
                    ))}
                </span>
            </li>
        );
    } else {
        return null;
    }
}

export function Queue(): React.ReactElement {
    const { performerName, widescreen } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const { queue, settings } = useContext(RoomContext);
    const { sessionId } = useApi();

    return (
        <Screen
            className={"queue"}
            navLeft={!widescreen && <BackToExplore />}
            title={"Now Playing"}
        >
            {/* No items */}
            {queue.length === 0 && <h2>Queue Empty</h2>}

            {/* At least one item */}
            {queue.length > 0 && (
                <section>
                    <ul>
                        <QueueItemRender
                            item={queue[0]}
                            show_time={true}
                            track={tracks[queue[0].track_id]}
                        />
                        <Lyrics
                            key={queue[0].track_id}
                            track={tracks[queue[0].track_id]}
                        />
                    </ul>
                </section>
            )}

            {/* Some items */}
            {queue.length > 1 && settings["coming_soon_track_count"] && (
                <section>
                    <h2>Coming Soon</h2>
                    <ul>
                        {queue
                            .slice(1, 1 + settings["coming_soon_track_count"])
                            .map((item) => (
                                <QueueItemRender
                                    key={item.id}
                                    item={item}
                                    show_time={true}
                                    track={tracks[item.track_id]}
                                />
                            ))}
                    </ul>
                </section>
            )}

            {/* Many items */}
            {queue.length > 1 + settings["coming_soon_track_count"] && (
                <section>
                    <h2>Coming Later</h2>
                    <div className={"coming_later"}>
                        {shuffle(
                            queue.slice(
                                1 + settings["coming_soon_track_count"],
                            ),
                        ).map((item) => (
                            <span key={item.id}>{item.performer_name}</span>
                        ))}
                    </div>
                </section>
            )}

            {/* My Stuff */}
            {queue.filter((item) => is_my_song(sessionId, performerName, item))
                .length > 0 && (
                <section>
                    <h2>My Entries</h2>
                    <ul>
                        {queue
                            .filter((item) =>
                                is_my_song(sessionId, performerName, item),
                            )
                            .map((item) => (
                                <QueueItemRender
                                    key={item.id}
                                    item={item}
                                    show_time={false}
                                    track={tracks[item.track_id]}
                                />
                            ))}
                    </ul>
                </section>
            )}
        </Screen>
    );
}
