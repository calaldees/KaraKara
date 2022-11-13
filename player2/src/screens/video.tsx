import h from "hyperapp-jsx-pragma";
import { current_and_future, percent } from "../utils";
import { EndTime, JoinInfo, Video } from "./_common";

///////////////////////////////////////////////////////////////////////
// Views

export const VideoScreen = ({ state, visible_queue }: { state: State, visible_queue: Array<QueueItem> }): VNode => (
    <VideoInternal
        state={state}
        track={state.track_list[visible_queue[0].track_id]}
        queue_item={visible_queue[0]}
    />
);

const VideoInternal = ({
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
        <EndTime state={state} />
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
