import h from "hyperapp-jsx-pragma";
import { Video } from "./common"
import { MarkTrackPlayed, UpdateProgress } from "../actions";

export const VideoScreen = ({ state }: { state: State }): VNode => (
    <VideoInternal
        state={state}
        track={state.track_list[state.queue[0].track_id]}
        queue_item={state.queue[0]}
    />
);

const VideoInternal = ({ state, track, queue_item }: { state: State, track: Track, queue_item: QueueItem }): VNode => (
    <section key="video" class={"screen_video"}>
        <Video
            state={state}
            track={track}
            ontimeupdate={UpdateProgress}
            onended={MarkTrackPlayed}
        />
        <div
            id="seekbar"
            style={{
                left:
                    (state.progress / track.duration) * 100 +
                    "%",
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
