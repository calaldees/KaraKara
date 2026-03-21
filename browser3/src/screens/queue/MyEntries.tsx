import { useContext } from "react";

import { List } from "@/components";
import { useApi } from "@/hooks/api";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import { is_my_song } from "@/utils";

import { QueueItemRender } from "./QueueItemRender";

export function MyEntries(): React.ReactElement | null {
    const { tracks } = useContext(ServerContext);
    const { queue } = useContext(RoomContext);
    const { sessionId } = useApi();

    const myEntries = queue.filter((item) => is_my_song(item, sessionId));

    if (myEntries.length === 0) {
        return null;
    }

    return (
        <section>
            <h2>My Entries</h2>
            <List>
                {myEntries.map((item) => (
                    <QueueItemRender
                        key={item.id}
                        item={item}
                        show_time={false}
                        track={tracks[item.track_id]}
                    />
                ))}
            </List>
        </section>
    );
}
