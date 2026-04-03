import type { Attachment, QueueItem, Track } from "@/types";
import { attachment_path } from "@/utils";

interface PrecacheProps {
    queue: QueueItem[];
    tracks: Record<string, Track>;
    count?: number;
}

export function Precache({ queue, tracks, count = 3 }: PrecacheProps) {
    const precache = queue
        .slice(1, count + 1)
        .map((item) => {
            const track = tracks[item.track_id];
            if (!track) return null;
            const videos = track.attachments.video
                .filter((a) => a.variant === item.video_variant)
                .filter((a) => a.mime.startsWith("video/webm"))
                .map((a: Attachment) => attachment_path(a));
            return videos.map((video) => (
                <link key={video} rel="prefetch" as="video" href={video} />
            ));
        })
        .filter((x) => x !== null)
        .flat();

    return <>{precache}</>;
}
