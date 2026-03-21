import { useEffect, useState } from "react";

import { useApi } from "@/hooks/api";
import { Subtitle, Track } from "@/types";
import { attachment_path } from "@/utils";

import styles from "./LyricsViewer.module.scss";

export function LyricsViewer({
    track,
    variant,
    listItem = false,
}: {
    track: Track;
    variant: string | null;
    listItem?: boolean;
}): React.ReactElement | null {
    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    const { request } = useApi();

    useEffect(() => {
        const subtitleAttachment = track.attachments.subtitle?.find(
            (a) => a.mime === "application/json" && a.variant === variant,
        );
        if (subtitleAttachment) {
            request({
                url: attachment_path(subtitleAttachment),
                options: { credentials: "omit" },
                onAction: (result) => setLyrics(result),
            });
        }
    }, [request, track, variant]);

    if (lyrics.length === 0) {
        return null;
    } else {
        return listItem ? (
            <li>
                <div className={styles.lyrics}>
                    {lyrics.map((line, n) => (
                        <div key={n}>{line.text}</div>
                    ))}
                </div>
            </li>
        ) : (
            <>
                <h2>Lyrics</h2>
                <div className={styles.lyrics}>
                    {lyrics.map((item, n) => (
                        <div key={n}>{item.text}</div>
                    ))}
                </div>
            </>
        );
    }
}
