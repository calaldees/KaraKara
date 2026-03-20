import { useContext } from "react";

import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { is_queue_hog } from "@/utils";

import styles from "./QueueHogWarning.module.scss";

export function QueueHogWarning({ trackId }: { trackId: string }) {
    const { queue } = useContext(RoomContext);
    const { performerName, booth } = useContext(ClientContext);
    const { sessionId } = useApi();

    // The admin control panel is shared by many people
    if (booth) return null;

    // If this track is already in the queue, no need to
    // warn about adding it to the queue
    const isQueued = queue.find((i) => i.track_id === trackId) !== undefined;
    if (isQueued) return null;

    const warningMessage = is_queue_hog(queue, performerName, sessionId);
    if (warningMessage) {
        return <div className={styles.warning}>{warningMessage}</div>;
    }
    return null;
}
