import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useCallback, useContext, useEffect, useRef, useState } from "react";

import { Video } from "@/components/video";
import { useApi } from "@/hooks/api";
import { RoomContext } from "@/providers/room";
import type { QueueItem, Subtitle, Track } from "@/types";
import { attachment_path, percent, s_to_mns } from "@/utils";

import "./podium.scss";

export function PodiumScreen({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { now } = useContext(ServerTimeContext);
    const { settings } = useContext(RoomContext);
    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    const [starting, setStarting] = useState(false);
    const { request } = useApi();
    const currentEl = useRef<HTMLElement>(null);

    const start = useCallback(() => {
        setStarting(true);
        request({ function: "command/play" });
        setTimeout(() => setStarting(false), 2000);
    }, [request]);

    useEffect(() => {
        const subtitleAttachment = track.attachments.subtitle?.find(
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
                <ul className="lyrics">
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
                <Video
                    track={track}
                    loop={true}
                    mute={true}
                    videoVariant={queue_item.video_variant}
                    subtitleVariant={queue_item.subtitle_variant}
                />
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
                                settings["track_space"],
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
