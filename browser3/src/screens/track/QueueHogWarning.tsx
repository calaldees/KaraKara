import { useContext } from "react";

import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { is_my_song, nth, unique } from "@/utils";

import styles from "./QueueHogWarning.module.scss";

export function QueueHogWarning({ trackId }: { trackId: string }) {
    const { queue } = useContext(RoomContext);
    const { performerName, booth } = useContext(ClientContext);
    const { sessionId } = useApi();

    const isQueued = queue.find((i) => i.track_id === trackId) !== undefined;

    const myTracks = queue.filter((item) =>
        is_my_song(item, sessionId, performerName),
    );
    const otherPeoplesTracks = queue.filter(
        (item) => !is_my_song(item, sessionId, performerName),
    );
    const averageTracksPerPerformer =
        otherPeoplesTracks.length > 0
            ? otherPeoplesTracks.length /
              unique(otherPeoplesTracks.map((item) => item.performer_name))
                  .length
            : 0;
    const averageTracksPerPerformerStr = averageTracksPerPerformer.toFixed(1);
    const myTrackCount = myTracks.length + 1;
    if (
        !isQueued &&
        !booth &&
        queue.length > 3 &&
        myTrackCount > averageTracksPerPerformer * 2
    ) {
        return (
            <div className={styles.warning}>
                The average person has {averageTracksPerPerformerStr}{" "}
                {averageTracksPerPerformerStr !== "1.0" ? "tracks" : "track"} in
                the queue, this will be your {nth(myTrackCount)} — please make
                sure everybody gets a chance to sing ❤️
            </div>
        );
    }
    return null;
}
