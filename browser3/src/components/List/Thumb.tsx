import { faGripVertical } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import type { Track } from "@/types";
import { attachment_path } from "@/utils";

import styles from "./Thumb.module.scss";

export function Thumb({
    track,
    dragHandle = false,
    ...kwargs
}: {
    track: Track | undefined;
    dragHandle?: boolean;
    [Key: string]: any;
}): React.ReactElement {
    return (
        <div className={styles.thumb} {...kwargs}>
            <img
                alt=""
                draggable="false"
                src={
                    track?.attachments.image[0] &&
                    attachment_path(track.attachments.image[0])
                }
            />
            {dragHandle && (
                <FAIcon icon={faGripVertical} className={styles.dragHandle} />
            )}
        </div>
    );
}
