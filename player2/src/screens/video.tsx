import h from "hyperapp-jsx-pragma";
import { current_and_future, percent } from "../utils";
import { EventInfo, JoinInfo, Video } from "./_common";

///////////////////////////////////////////////////////////////////////
// Views

export const VideoScreen = ({
    state,
    track,
    queue_item,
}: {
    state: State;
    track: Track;
    queue_item: QueueItem;
}): VNode => (
    <section key="video" class={"screen_video"}>
        <Video state={state} track={track} />
        <JoinInfo state={state} />
        <EventInfo state={state} />
        <div
            id="seekbar"
            style={{
                left: percent(
                    state.now - (queue_item.start_time ?? state.now),
                    track.duration,
                ),
            }}
        />
        <div id="pimpkk" class="pimp">
            KaraKara
        </div>
        <div id="pimpsong" class="pimp">
            {track.tags.title[0]}
            <br />
            Performed by {queue_item.performer_name}
        </div>
        <div id="pimpcontributor" class="pimp">
            Contributed by {track.tags['contributor']?.[0]}
        </div>
    </section>
);
