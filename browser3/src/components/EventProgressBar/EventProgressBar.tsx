import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useContext } from "react";

import { RoomContext } from "@/providers/room";

import styles from "./EventProgressBar.module.scss";

export function EventProgressBar(): React.ReactElement | null {
    const { fullQueue, settings } = useContext(RoomContext);
    const { now } = useContext(ServerTimeContext);

    const queue = fullQueue;
    const startDateTime = settings["validation_event_start_datetime"];
    const endDateTime = settings["validation_event_end_datetime"];

    if (!queue.length) return null;
    const queueLast = queue[queue.length - 1];
    if (!queueLast.start_time) return null;
    if (!startDateTime || !endDateTime) return null;

    return (
        <EventProgressBarInternal
            startTime={Date.parse(startDateTime) / 1000}
            queueEnd={queueLast.start_time + queueLast.track_duration}
            now={now}
            endTime={Date.parse(endDateTime) / 1000}
        />
    );
}

/**
 * All times in seconds since epoch
 */
function EventProgressBarInternal({
    startTime,
    now,
    queueEnd,
    endTime,
}: {
    startTime: number;
    now: number;
    queueEnd: number;
    endTime: number;
}) {
    const eventDuration = endTime - startTime;
    return (
        <div className={styles.eventProgress}>
            <div
                className={styles.played}
                style={{
                    width: `${((now - startTime) / eventDuration) * 100}%`,
                }}
                title={`Played until ${new Date(now * 1000).toLocaleString()}`}
            />
            <div
                className={styles.queued}
                style={{
                    width: `${((queueEnd - now) / eventDuration) * 100}%`,
                }}
                title={`Queued until ${new Date(queueEnd * 1000).toLocaleString()}`}
            />
            <div
                className={styles.space}
                style={{
                    width: `${((endTime - queueEnd) / eventDuration) * 100}%`,
                }}
                title={`Remaining time ${Math.floor((endTime - queueEnd) / 60)} minutes`}
            />
        </div>
    );
}
