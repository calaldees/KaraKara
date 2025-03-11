import { attachment_path, percent, s_to_mns } from "../utils";
import { Video } from "./_common";
import { useContext, useState } from "react";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";
import { RoomContext } from "../providers/room";
import { useApi } from "../hooks/api";

///////////////////////////////////////////////////////////////////////
// Views

const blank = new URL("../static/blank.mp4", import.meta.url);

export function PodiumScreen({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { root, blankPodium } = useContext(ClientContext);
    const { now } = useContext(ServerContext);
    const { settings } = useContext(RoomContext);
    const [starting, setStarting] = useState(false);
    const { request } = useApi();

    function start() {
        setStarting(true);
        request({ function: "command/play" });
        setTimeout(() => setStarting(false), 2000);
    }

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
                    {track.attachments.subtitle?.map((a) => (
                        <track
                            kind="subtitles"
                            src={attachment_path(root, a)}
                            default={true}
                            label="English"
                            srcLang="en"
                        />
                    ))}
                </video>
            ) : (
                <Video track={track} lowres={true} loop={true} />
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
