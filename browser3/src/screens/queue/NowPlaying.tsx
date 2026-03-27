import { useContext } from "react";
import { List, LyricsViewer } from "@/components";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import { QueueItemRender } from "./QueueItemRender";

export function NowPlaying(): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { queue } = useContext(RoomContext);

    if (queue.length === 0) {
        return <h2>Queue Empty</h2>;
    }

    return (
        <section>
            <List>
                <QueueItemRender
                    item={queue[0]}
                    show_time={true}
                    track={tracks[queue[0].track_id]}
                />
                <LyricsViewer
                    key={queue[0].track_id}
                    track={tracks[queue[0].track_id]}
                    variant={queue[0].subtitle_variant}
                    listItem={true}
                />
            </List>
        </section>
    );
}
