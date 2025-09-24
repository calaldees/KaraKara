import { useContext } from "react";
import { ServerTimeContext } from "@shish2k/react-use-servertime";

import { EventInfo } from "@/components/eventinfo";
import { JoinInfo } from "@/components/joininfo";
import { Video } from "@/components/video";
import type { Track, QueueItem } from "@/types";
import { percent } from "@/utils";

export function VideoScreen({
    track,
    queue_item,
}: {
    track: Track;
    queue_item: QueueItem;
}) {
    const { now } = useContext(ServerTimeContext);

    return (
        <section key="video" className={"screen_video"}>
            <Video track={track} lowres={false} />
            <JoinInfo />
            <EventInfo />
            <div
                id="seekbar"
                style={{
                    left: percent(
                        now - (queue_item.start_time ?? now),
                        track.duration,
                    ),
                }}
            />
            <div id="pimpkk" className="pimp">
                KaraKara
            </div>
            <div id="pimpsong" className="pimp">
                {track.tags.title[0]}
                <br />
                Performed by {queue_item.performer_name}
            </div>
            <div id="pimpcontributor" className="pimp">
                Contributed by {track.tags["contributor"]?.[0]}
            </div>
        </section>
    );
}
