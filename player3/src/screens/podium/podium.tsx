import { useCallback, useContext, useState } from "react";
import { ServerTimeContext } from "@shish2k/react-use-servertime";

import { Video } from "@/components/video";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { useApi } from "@/hooks/api";
import type { Track, QueueItem } from "@/types";
import { attachment_path, percent, s_to_mns } from "@/utils";

import "./podium.scss";

///////////////////////////////////////////////////////////////////////
// Views

const blank = new URL("@/static/blank.mp4", import.meta.url);

export function PodiumScreen({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { blankPodium } = useContext(ClientContext);
    const { now } = useContext(ServerTimeContext);
    const { settings } = useContext(RoomContext);
    const [starting, setStarting] = useState(false);
    const { request } = useApi();

    const start = useCallback(() => {
        setStarting(true);
        request({ function: "command/play" });
        setTimeout(() => setStarting(false), 2000);
    }, [request]);

    return (
        <section key="podium" className={"screen_podium"}>
            <h1>
                {track.tags.title[0]}
                <br />
                Performed by <strong>{queue_item.performer_name}</strong>
            </h1>

            {blankPodium ? (
                <video
                    muted={true}
                    key={
                        queue_item.id +
                        "-" +
                        (queue_item.start_time && queue_item.start_time < now)
                    }
                    autoPlay={true}
                    crossOrigin="anonymous"
                >
                    <source src={blank.href} />
                    {track.attachments.subtitle
                        ?.filter((a) => a.mime === "text/vtt")
                        .filter((a) => a.variant === queue_item.subtitle_variant)
                        .map((a) => (
                            <track
                                key={a.path}
                                kind="subtitles"
                                src={attachment_path(a)}
                                default={true}
                                label="English"
                                srcLang="en"
                            />
                        ))}
                </video>
            ) : (
                <Video
                    track={track}
                    loop={true}
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
