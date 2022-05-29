import h from "hyperapp-jsx-pragma";
import { attachment_path, get_attachments, get_tag } from "../utils";
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
        <video
            autoPlay={true}
            ontimeupdate={UpdateProgress}
            // TODO: Action + Effect at once?
            onended={MarkTrackPlayed}
        >
            {get_attachments(track, "video").map(a =>
                <source src={attachment_path(state.root, a)} type={a.mime} />
            )}
            {get_attachments(track, "subtitle").map(a =>
                <track
                    kind="subtitles"
                    src={attachment_path(state.root, a)}
                    default={true}
                    label="English"
                    srclang="en"
                />
            )}
        </video>
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
            {get_tag(track.tags.title)}
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
