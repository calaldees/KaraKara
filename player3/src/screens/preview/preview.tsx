import { useContext } from "react";
import { ServerTimeContext } from "@shish2k/react-use-servertime";

import { EventInfo } from "@/components/eventinfo";
import { JoinInfo } from "@/components/joininfo";
import { Video } from "@/components/video";
import { ServerContext } from "@/providers/server";
import { RoomContext } from "@/providers/room";
import type { Track, QueueItem } from "@/types";
import { time_until } from "@/utils";

import "./preview.scss";

const show_tracks = 5;

///////////////////////////////////////////////////////////////////////
// Views

function QueueItem({
    item,
    track,
    idx,
    now,
}: {
    item: QueueItem;
    track: Track;
    idx: number;
    now: number;
}) {
    return (
        <div className={"item n" + (idx + 1)} key={item.id}>
            <p className="title">{track.tags.title[0]}</p>
            <p className="from">
                {track.tags.from?.[0] ?? track.tags.artist?.join(", ") ?? ""}
            </p>
            <p className="performer">
                <span className="n">{idx + 1}</span> {item.performer_name}
            </p>
            <p className="time">
                <span>
                    {time_until(now, item.start_time) ||
                        (idx === 0 && "You're up!") ||
                        (idx === 1 && "Nearly there!")}
                </span>
            </p>
        </div>
    );
}

export function PreviewScreen({
    queue,
    track,
}: {
    queue: QueueItem[];
    track: Track;
}) {
    const { tracks } = useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const { settings } = useContext(RoomContext);

    return (
        <section key="preview" className={"screen_preview"}>
            <JoinInfo />
            <Video
                track={track}
                onLoadStart={(e: any) => {
                    e.target.volume = settings["preview_volume"];
                }}
                subs={false}
                loop={true}
            />
            {queue
                .slice(0, show_tracks)
                .map((item) => ({
                    item: item,
                    track: tracks[item.track_id],
                }))
                .map(({ item, track }, idx) => (
                    <QueueItem
                        item={item}
                        track={track}
                        idx={idx}
                        now={now}
                        key={item.id}
                    />
                ))}
            {queue.length > show_tracks && (
                <div id="playlist_obscured" key={"playlist_obscured"}>
                    <ul>
                        {queue.slice(show_tracks).map((item) => (
                            <li key={item.id}>{item.performer_name}</li>
                        ))}
                    </ul>
                </div>
            )}
            {queue.length > show_tracks && (
                <div id="n_more" key={"n_more"}>
                    <div>
                        and <span>{queue.length - show_tracks}</span> more...
                    </div>
                </div>
            )}
            <EventInfo />
        </section>
    );
}
