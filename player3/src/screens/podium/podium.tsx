import { faFaceFrown } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useCallback, useContext, useEffect, useRef, useState } from "react";

import { useApi } from "@/hooks/api";
import { RoomContext } from "@/providers/room";
import type { QueueItem, Subtitle, Track } from "@/types";
import {
    add_dot_dot_dots,
    attachment_path,
    percent,
    s_to_mns,
    track_title,
} from "@/utils";

import "./podium.scss";

export function PodiumScreen({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    // Use key= to force reset of all state when track changes
    return (
        <PodiumInner
            track={track}
            queue_item={queue_item}
            key={queue_item.id}
        />
    );
}

function PodiumInner({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    return (
        <section key="podium" className={"screen_podium"}>
            <PodiumTitle track={track} queue_item={queue_item} />
            <PodiumLyrics track={track} queue_item={queue_item} />
            <PodiumButton track={track} queue_item={queue_item} />
        </section>
    );
}

function PodiumTitle({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    return (
        <h1>
            {track_title(track)}
            <br />
            Performed by <strong>{queue_item.performer_name}</strong>
        </h1>
    );
}

function PodiumLyrics({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { now } = useContext(ServerTimeContext);
    const { request } = useApi();
    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    const lyricsEl = useRef<HTMLUListElement>(null);
    const currentEl = useRef<HTMLLIElement>(null);

    // Load lyrics when the track or subtitle variant changes
    useEffect(() => {
        const subtitleAttachment = track.attachments.subtitle?.find(
            (a) =>
                a.mime === "application/json" &&
                a.variant === queue_item.subtitle_variant,
        );
        if (subtitleAttachment) {
            request({
                url: attachment_path(subtitleAttachment),
                options: { credentials: "omit" },
                onAction: (result) => setLyrics(add_dot_dot_dots(result)),
            });
        }
    }, [request, track, queue_item.subtitle_variant]);

    // Scroll to top when lyrics change (e.g. new track or new subtitle variant)
    useEffect(() => {
        if (lyricsEl.current) {
            lyricsEl.current.scrollTop = 0;
        }
    }, [lyrics]);

    // Scroll current lyric into view when time changes
    useEffect(() => {
        if (currentEl.current) {
            currentEl.current.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        }
    }, [now]);

    if (lyrics.length === 0) {
        return (
            <div className="lyrics">
                Hard-subbed song, check the projector for lyrics{" "}
                <FAIcon icon={faFaceFrown} />
            </div>
        );
    }

    const time_within_track = now - (queue_item.start_time ?? 0);
    return (
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
    );
}

function PodiumButton({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { now } = useContext(ServerTimeContext);
    const { settings } = useContext(RoomContext);
    const { request } = useApi();
    const [starting, setStarting] = useState(false);

    const start = useCallback(() => {
        setStarting(true);
        request({ function: "command/play" });
        setTimeout(() => setStarting(false), 2000);
    }, [request]);

    // User has tapped the start button recently
    if (starting) {
        return (
            <div className={"startButton"}>
                <span>Starting Now!</span>
            </div>
        );
    }

    // Autoplay disabled, waiting for user to tap start button
    if (!queue_item.start_time) {
        return (
            <div className={"startButton"} onClick={(_) => start()}>
                <span>
                    Tap Here to Start
                    <small>Autoplay Disabled</small>
                </span>
            </div>
        );
    }

    // Track is in-progress
    if (queue_item.start_time < now) {
        return (
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
        );
    }

    // Countdown to track start
    return (
        <div
            className={"startButton"}
            onClick={(_) => start()}
            style={{
                backgroundPosition: percent(
                    queue_item.start_time - now,
                    settings.track_space,
                ),
            }}
        >
            <span>
                Tap Here to Start
                <small>
                    Track autoplays in {s_to_mns(queue_item.start_time - now)}
                </small>
            </span>
        </div>
    );
}
