import h from "hyperapp-jsx-pragma";
import { current_and_future, percent } from "../utils";
import { JoinInfo, Video } from "./_common";

///////////////////////////////////////////////////////////////////////
// Views

export const VideoScreen = ({ state }: { state: State }): VNode => (
    <VideoInternal
        state={state}
        track={
            state.track_list[
                current_and_future(state.now, state.queue)[0].track_id
            ]
        }
        queue_item={current_and_future(state.now, state.queue)[0]}
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
        {/* too much on screen at once?
        <div id="pimpcontributor" class="pimp">
            Contributed by {get_tag(track.tags.contributor)}
        </div>
        */}
    </section>
);
