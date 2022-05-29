import h from "hyperapp-jsx-pragma";
import { get_attachment, get_tag, title_case } from "../utils";
import { MarkTrackPlayed, UpdateProgress } from "../actions";

export const VideoScreen = ({ state }: { state: State }): VNode => (
    <section key="video" class={"screen_video"}>
        <video
            src={get_attachment(state, state.queue[0].track, "video")}
            autoPlay={true}
            ontimeupdate={UpdateProgress}
            // TODO: Action + Effect at once?
            onended={MarkTrackPlayed}
        >
            <track
                kind="subtitles"
                src={get_attachment(state, state.queue[0].track, "subtitle")}
                default={state.settings["karakara.player.subs_on_screen"]}
            />
        </video>
        <div
            id="seekbar"
            style={{
                left:
                    (state.progress / state.queue[0].track.duration) * 100 +
                    "%",
            }}
        />
        <div id="pimpkk" class="pimp">
            KaraKara
        </div>
        <div id="pimpsong" class="pimp">
            {title_case(get_tag(state.queue[0].track.tags.title))}
            <br />
            Performed by {state.queue[0].performer_name}
        </div>
        {/* too much on screen at once?
        <div id="pimpcontributor" class="pimp">
            Contributed by {get_tag(state.queue[0].track.tags.contributor)}
        </div>
        */}
    </section>
);
