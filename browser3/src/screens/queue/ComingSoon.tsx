import { useContext } from "react";

import { List } from "@/components";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";

import { QueueItemRender } from "./QueueItemRender";

export function ComingSoon(): React.ReactElement | null {
    const { tracks } = useContext(ServerContext);
    const { queue, settings } = useContext(RoomContext);

    if (queue.length <= 1 || !settings.coming_soon_track_count) {
        return null;
    }

    return (
        <section>
            <h2>Coming Soon</h2>
            <List>
                {queue
                    .slice(1, 1 + settings.coming_soon_track_count)
                    .map((item) => (
                        <QueueItemRender
                            key={item.id}
                            item={item}
                            show_time={true}
                            track={tracks[item.track_id]}
                        />
                    ))}
            </List>
        </section>
    );
}
