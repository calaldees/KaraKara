import { h } from "hyperapp";
import { get_attachment, get_tag, timedelta_str, title_case } from "../utils";
import { AutoplayCountdown } from "./common";
import { SetPreviewVolume } from "../actions";

const show_tracks = 5;

export const PreviewScreen = ({ state }: { state: State }) => (
    <section key="preview" className={"screen_preview"}>
        <div className="preview_holder">
            <video
                src={get_attachment(state, state.queue[0].track, "video")}
                preload={"auto"}
                muted={true}
                style={{ display: "none" }}
            />
            <video
                src={get_attachment(state, state.queue[0].track, "preview")}
                poster={get_attachment(
                    state,
                    state.queue[0].track,
                    "thumbnail",
                )}
                autoPlay={true}
                onloadstart={SetPreviewVolume}
                loop={true}
            />
            <AutoplayCountdown state={state} show_if_disabled={false} />
        </div>
        <div id="playlist" key={"playlist"}>
            <ol>
                {state.queue.slice(0, show_tracks).map(item => (
                    <li key={item.id}>
                        <img src={get_attachment(state, item.track, "image")} />
                        <p className="title">
                            {title_case(get_tag(item.track.tags.title))}
                        </p>
                        <p className="from">
                            {title_case(get_tag(item.track.tags.from))}
                        </p>
                        <p className="performer">{item.performer_name}</p>
                        <p className="time">
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
                    {state.queue.slice(show_tracks).map(item => (
                        <li key={item.id}>{item.performer_name}</li>
                    ))}
                </ul>
            </div>
        )}

        {/* key= to make sure this element stays put while the above may disappear */}
        <div id="join_info" key={"join_info"}>
            Join at <strong>{state.root.replace("https://", "")}</strong> - Room
            Name is <strong>{state.queue_id}</strong>
            {state.settings["karakara.event.end"] && (
                <span>
                    <br />
                    Event ends at{" "}
                    <strong>{state.settings["karakara.event.end"]}</strong>
                </span>
            )}
        </div>
    </section>
);
