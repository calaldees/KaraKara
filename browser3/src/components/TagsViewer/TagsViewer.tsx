import { Track } from "@/types";

import styles from "./TagsViewer.module.scss";

const BLOCKED_KEYS = [
    "",
    "title",
    "from",
    "source_type",
    "subs",
    "aspect_ratio",
    "date",
    "added",
    "new",
    "source", // TODO: figure out a nice way to display source URLs?
    "id", // TODO: display id:imdb, id:mal, etc. nicely
];

export function TagsViewer({ track }: { track: Track }) {
    return (
        <>
            <h2>Tags</h2>
            <div className={styles.tags}>
                {Object.keys(track.tags)
                    .filter((key) => !key.startsWith("_"))
                    .filter((key) => !BLOCKED_KEYS.includes(key))
                    .map((key) => (
                        <div key={key} className={styles.tag}>
                            <div className={styles.tagKey}>{key}</div>
                            <div className={styles.tagValue}>
                                {track.tags[key]?.join(", ")}
                            </div>
                        </div>
                    ))}
            </div>
        </>
    );
}
