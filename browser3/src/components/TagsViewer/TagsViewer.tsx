import { Track } from "@/types";
import { sort_tag_keys } from "@/utils/browser";

import styles from "./TagsViewer.module.scss";

const BLOCKED_KEYS = [
    "",
    "title",
    "from",
    "source_type",
    "subs",
    "aspect_ratio",
    "released",
    "added",
    "updated",
    "new",
    "source",
    "id", // TODO: display id:imdb, id:mal, etc. nicely
];

type TagRenderFunc = (values: string[]) => React.ReactNode;

const TAG_RENDERERS: Record<string, TagRenderFunc> = {
    duration: (values: string[]) => {
        const seconds = parseFloat(values[0]);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}m${remainingSeconds.toString().padStart(2, "0")}s`;
    },
    source: (values: string[]) => {
        return values.map((url, index) => {
            if (url.includes("youtu.be") || url.includes("youtube.com")) {
                return (
                    <a
                        key={index}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        YouTube
                    </a>
                );
            }
            return url;
        });
    },
};

const defaultRenderer: TagRenderFunc = (values: string[]) => values.join(", ");

export function TagsViewer({ track }: { track: Track }) {
    return (
        <>
            <h2>Tags</h2>
            <div className={styles.tags}>
                {sort_tag_keys(Object.keys(track.tags))
                    .filter((key) => !key.startsWith("_"))
                    .filter((key) => !BLOCKED_KEYS.includes(key))
                    .map((key) => {
                        const renderer = TAG_RENDERERS[key] || defaultRenderer;
                        const values = track.tags[key] || [];
                        return (
                            <div key={key} className={styles.tag}>
                                <div className={styles.tagKey}>{key}</div>
                                <div className={styles.tagValue}>
                                    {renderer(values)}
                                </div>
                            </div>
                        );
                    })}
            </div>
        </>
    );
}
