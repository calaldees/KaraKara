import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useCallback, useContext, useEffect, useRef, useState } from "react";

import { useApi } from "@/hooks/api";
import { RoomContext } from "@/providers/room";
import type { QueueItem, Subtitle, Track } from "@/types";
import { attachment_path, parse_duration, percent, s_to_mns } from "@/utils";

import "./podium.scss";

export function PodiumScreen({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    // Use key= to force reset of all state when track changes
    return <PodiumInner
        track={track}
        queue_item={queue_item}
        key={queue_item.id}
    />;
}

function PodiumInner({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { now } = useContext(ServerTimeContext);
    const { settings } = useContext(RoomContext);
    const { request } = useApi();
    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    const [starting, setStarting] = useState(false);
    const lyricsEl = useRef<HTMLUListElement>(null);
    const currentEl = useRef<HTMLLIElement>(null);

    const start = useCallback(() => {
        setStarting(true);
        request({ function: "command/play" });
        setTimeout(() => setStarting(false), 2000);
    }, [request]);

    useEffect(() => {
        const subtitleAttachment = track.attachments.subtitle?.find(
            (a) => a.mime === "application/json" && a.variant === queue_item.subtitle_variant,
        );
        if (subtitleAttachment) {
            request({
                url: attachment_path(subtitleAttachment),
                options: { credentials: "omit" },
                onAction: (result) => setLyrics(result),
            });
        }
    }, [request, track]);

    useEffect(() => {
        if (lyricsEl.current) {
            lyricsEl.current.scrollTop = 0;
        }
    }, [lyrics]);
    useEffect(() => {
        if (currentEl.current) {
            currentEl.current.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        }
    }, [now]);

    const time_within_track = now - (queue_item.start_time ?? 0);
    return (
        <section key="podium" className={"screen_podium"}>
            <h1>
                {track.tags.title[0]}
                <br />
                Performed by <strong>{queue_item.performer_name}</strong>
            </h1>

            {lyrics.length > 0 ? (
                <ul className="lyrics" ref={lyricsEl}>
                    {lyrics.map((line) => {
                        // bias towards hilighting text early, and have it fade out slowly
                        const is_current =
                            time_within_track >= line.start - 1 &&
                            time_within_track <= line.end - 1;
                        return (
                            <li
                                key={line.start}
                                className={is_current ? "current" : ""}
                                ref={is_current ? currentEl : undefined}
                            >
                                {line.text}
                            </li>
                        );
                    })}
                </ul>
            ) : (
                <div className="lyrics">(Hard-subbed song, please check the projector for lyrics ;( )</div>
            )}

            {starting ? (
                <div className={"startButton"}>
                    <span>Starting Now!</span>
                </div>
            ) : queue_item.start_time ? (
                queue_item.start_time < now ? (
                    <div
                        className={"progressBar"}
                        style={{
                            backgroundPosition: percent(
                                track.duration - (now - queue_item.start_time),
                                track.duration,
                            ),
                        }}
                    >
                        Track Playing
                        <small>
                            ({s_to_mns(now - queue_item.start_time)} /{" "}
                            {s_to_mns(track.duration)})
                        </small>
                    </div>
                ) : (
                    <div
                        className={"startButton"}
                        onClick={(_) => start()}
                        style={{
                            backgroundPosition: percent(
                                queue_item.start_time - now,
                                parse_duration(settings["track_space"]),
                            ),
                        }}
                    >
                        <span>
                            Tap Here to Start
                            <small>
                                Track autoplays in{" "}
                                {s_to_mns(queue_item.start_time - now)}
                            </small>
                        </span>
                    </div>
                )
            ) : (
                <div className={"startButton"} onClick={(_) => start()}>
                    <span>
                        Tap Here to Start
                        <small>Autoplay Disabled</small>
                    </span>
                </div>
            )}
        </section>
    );
}
