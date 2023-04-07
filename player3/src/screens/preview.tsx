import { useContext } from "react";
import { attachment_path, time_until } from "../utils";
import { JoinInfo, Video, EventInfo } from "./_common";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";
import { RoomContext } from "../providers/room";

const show_tracks = 5;

///////////////////////////////////////////////////////////////////////
// Views

export function PreviewScreen({
    queue, track,
}: {
    queue: Array<QueueItem>;
    track: Track;
}) {
    const { root } = useContext(ClientContext);
    const { now, tracks } = useContext(ServerContext);
    const { settings } = useContext(RoomContext);

    return (
        <section key="preview" className={"screen_preview"}>
            <JoinInfo />
            <Video
                track={track}
                onLoadStart={(e: any) => {e.target.volume = settings["preview_volume"]}}
                lowres={false}
                loop={true} />
            {queue
                .slice(0, show_tracks)
                .map((item) => ({
                    item: item,
                    track: tracks[item.track_id],
                }))
                .map(({ item, track }, idx) => (
                    <div className={"item n" + (idx + 1)} key={item.id}>
                        <img
                            src={attachment_path(
                                root,
                                track.attachments.image[0]
                            )} />
                        <p className="title">{track.tags.title[0]}</p>
                        <p className="from">
                            {track.tags.from?.[0] ||
                                track.tags.artist?.join(", ") ||
                                ""}
                        </p>
                        <p className="performer">
                            <span className="n">{idx + 1}</span> {item.performer_name}
                        </p>
                        <p className="time">
                            <span>
                                {time_until(now, item.start_time) ||
                                    (idx == 0 && "You're up!") ||
                                    (idx == 1 && "Nearly there!")}
                            </span>
                        </p>
                    </div>
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
