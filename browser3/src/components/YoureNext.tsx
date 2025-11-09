import { useContext } from "react";

import { useApi } from "@/hooks/api";
import { ServerContext } from "@/providers/server";
import { ClientContext } from "@/providers/client";
import type { QueueItem } from "@/types";
import { is_my_song } from "@/utils";

export function YoureNext({
    queue,
}: {
    queue: QueueItem[];
}): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { performerName } = useContext(ClientContext);
    const { sessionId } = useApi();

    return (
        <>
            {(is_my_song(queue[0], sessionId, performerName) && (
                <h2 className="main-only upnext">
                    Your song "{tracks[queue[0].track_id]?.tags.title[0]}" is up
                    now!
                </h2>
            )) ||
                (is_my_song(queue[1], sessionId, performerName) && (
                    <h2 className="main-only upnext">
                        Your song "{tracks[queue[1].track_id]?.tags.title[0]}"
                        is up next!
                    </h2>
                ))}
        </>
    );
}
