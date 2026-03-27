import { useContext } from "react";

import { RoomContext } from "@/providers/room";
import { sorted, unique } from "@/utils";

import styles from "./ComingLater.module.scss";

export function ComingLater(): React.ReactElement | null {
    const { queue, settings } = useContext(RoomContext);

    if (queue.length <= 1 + settings.coming_soon_track_count) {
        return null;
    }

    return (
        <section>
            <h2>Coming Later</h2>
            <div className={styles.comingLater}>
                {sorted(
                    unique(
                        queue
                            .slice(1 + settings.coming_soon_track_count)
                            .map((item) => item.performer_name),
                    ),
                ).map((name) => (
                    <span key={name}>{name}</span>
                ))}
            </div>
        </section>
    );
}
