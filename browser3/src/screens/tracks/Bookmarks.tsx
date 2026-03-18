import { List } from "@/components";
import { useMemoArr } from "@/hooks/memo";
import type { Track } from "@/types";

import { TrackItem } from "./TrackItem";

export function Bookmarks({
    bookmarks,
    tracks,
    trackList,
}: {
    bookmarks: string[];
    tracks: Record<string, Track>;
    trackList: Track[];
}) {
    const visibleTrackIDs = useMemoArr(
        () => trackList.map((track) => track.id),
        [trackList],
    );
    return (
        <div>
            <h2>Bookmarks</h2>
            <List>
                {bookmarks
                    .filter((bm) => bm in tracks)
                    .filter((bm) => visibleTrackIDs.includes(bm))
                    .map((bm) => (
                        <TrackItem key={bm} track={tracks[bm]} filters={[]} />
                    ))}
            </List>
        </div>
    );
}
