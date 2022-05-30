import h from "hyperapp-jsx-pragma";
import {
    attachment_path,
    get_tag,
    timedelta_str,
    short_date,
} from "../utils";
import { AutoplayCountdown } from "./common";
import { SetPreviewVolume } from "../actions";

const show_tracks = 5;

export const PreviewScreen = ({ state }: { state: State }): VNode => (
    <PreviewInternal
        state={state}
        track={state.track_list[state.queue[0].track_id]}
    />
);

const PreviewInternal = ({ state, track }: { state: State, track: Track }): VNode => (
    <section key="preview" class={"screen_preview"}>
        <div class="preview_holder">
            <video
                poster={attachment_path(state.root, track.attachments.image?.[0])}
                autoPlay={true}
                onloadstart={SetPreviewVolume}
                loop={true}
            >
                {track.attachments.video?.map(a =>
                    <source src={attachment_path(state.root, a)} type={a.mime} />
                )}
                {track.attachments.subtitle?.map(a =>
                    <track
                        kind="subtitles"
                        src={attachment_path(state.root, a)}
                        default={true}
                        label="English"
                        srclang="en"
                    />
                )}
            </video>
            <AutoplayCountdown state={state} show_if_disabled={false} />
        </div>
        <div id="playlist" key={"playlist"}>
            <ol>
                {state.queue.slice(0, show_tracks).map((item) => (
                    <li key={item.id}>
                        <img src={attachment_path(state.root, state.track_list[item.track_id].attachments.image?.[0])} />
                        <p class="title">
                            {get_tag(state.track_list[item.track_id].tags.title)}
                        </p>
                        <p class="from">
                            {get_tag(state.track_list[item.track_id].tags.from)}
                        </p>
                        <p class="performer">{item.performer_name}</p>
                        <p class="time">
                            <span>
                                {timedelta_str(item.total_duration * 1000)}
                            </span>
                        </p>
                    </li>
                ))}
            </ol>
        </div>
        {state.queue.length > show_tracks && (
            <div id="playlist_obscured" key={"playlist_obscured"}>
                <ul>
                    {state.queue.slice(show_tracks).map((item) => (
                        <li key={item.id}>{item.performer_name}</li>
                    ))}
                </ul>
            </div>
        )}

        {/* key= to make sure this element stays put while the above may disappear */}
        <div id="join_info" key={"join_info"}>
            Join at <strong>{state.root.replace("https://", "")}</strong> -
            Room Name is <strong>{state.room_name}</strong>
            {state.settings["karakara.event.end"] && (
                <span>
                    <br />
                    Event ends at{" "}
                    <strong>
                        {short_date(state.settings["karakara.event.end"])}
                    </strong>
                </span>
            )}
        </div>
    </section>
);
