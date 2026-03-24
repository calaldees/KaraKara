import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useContext } from "react";

import { ListItem, Thumb } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import type { QueueItem, Track } from "@/types";
import { dict2css, is_my_song, time_until, track_title } from "@/utils";

import styles from "./QueueItemRender.module.scss";

export function QueueItemRender({
    item,
    show_time,
    track,
}: {
    item: QueueItem;
    show_time: boolean;
    track: Track;
}): React.ReactElement {
    const { now } = useContext(ServerTimeContext);
    const { performerName } = useContext(ClientContext);
    const { request, sessionId } = useApi();

    function removeTrack(queue_item_id: number) {
        request({
            notify: "Removing track...",
            notify_ok: "Track removed!",
            function: "queue/" + queue_item_id.toString(),
            options: {
                method: "DELETE",
            },
        });
    }

    return (
        <ListItem
            className={dict2css({
                [styles.me]: is_my_song(item, sessionId, performerName),
            })}
            thumb={<Thumb track={track} />}
            title={track_title(track)}
            info={item.performer_name}
            count={
                show_time && item.start_time
                    ? time_until(now, item.start_time)
                    : undefined
            }
            action={
                is_my_song(item, sessionId) ? (
                    <FAIcon
                        icon={faCircleXmark}
                        data-cy="remove"
                        onClick={(_) =>
                            confirm(
                                `Remove ${track_title(track)} from the queue?`,
                            ) && removeTrack(item.id)
                        }
                    />
                ) : undefined
            }
        />
    );
}
