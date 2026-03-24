import { useContext } from "react";

import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { ServerContext } from "@/providers/server";
import type { QueueItem } from "@/types";
import { is_my_song, track_title } from "@/utils";

import styles from "./YoureNext.module.scss";

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
                <h2 className={`main-only ${styles.upnext}`}>
                    Your song "{track_title(tracks[queue[0].track_id])}" is up
                    now!
                </h2>
            )) ||
                (is_my_song(queue[1], sessionId, performerName) && (
                    <h2 className={`main-only ${styles.upnext}`}>
                        Your song "{track_title(tracks[queue[1].track_id])}"
                        is up next!
                    </h2>
                ))}
        </>
    );
}
