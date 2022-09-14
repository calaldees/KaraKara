import h from "hyperapp-jsx-pragma";
import {
    attachment_path,
    time_until,
    short_date,
    current_and_future,
} from "../utils";
import { Video } from "./_common";


const show_tracks = 5;


///////////////////////////////////////////////////////////////////////
// Actions

function SetPreviewVolume(state: State, event): Dispatchable {
    event.target.volume = state.settings["preview_volume"];
    return state;
}


///////////////////////////////////////////////////////////////////////
// Views

export const PreviewScreen = ({ state }: { state: State }): VNode => (
    <PreviewInternal
        state={state}
        queue={current_and_future(state.now, state.queue)}
        track={state.track_list[current_and_future(state.now, state.queue)[0].track_id]}
    />
);

const PreviewInternal = ({ state, queue, track }: { state: State, queue: Array<QueueItem>, track: Track }): VNode => (
    <section key="preview" class={"screen_preview"}>
        <div class="preview_holder">
            <Video
                state={state}
                track={track}
                onloadstart={SetPreviewVolume}
                loop={true}
            />
        </div>
        <div id="playlist" key={"playlist"}>
            <ol>
                {queue
                .slice(0, show_tracks)
                .map(item => ({item: item, track: state.track_list[item.track_id]}))
                .map(({item, track}) => (
                    <li key={item.id}>
                        <img src={attachment_path(state.root, track.attachments.image[0])} />
                        <p class="title">
                            {track.tags.title[0]}
                        </p>
                        <p class="from">
                            {
                                track.tags.from?.[0] ||
                                track.tags.artist?.join(", ") ||
                                ""
                            }
                        </p>
                        <p class="performer">{item.performer_name}</p>
                        <p class="time">
                            <span>
                                {time_until(state.now, item.start_time)}
                            </span>
                        </p>
                    </li>
                ))}
            </ol>
        </div>
        {queue.length > show_tracks && (
            <div id="playlist_obscured" key={"playlist_obscured"}>
                <ul>
                    {queue.slice(show_tracks).map((item) => (
                        <li key={item.id}>{item.performer_name}</li>
                    ))}
                </ul>
            </div>
        )}

        {/* key= to make sure this element stays put while the above may disappear */}
        <div id="join_info" key={"join_info"}>
            Join at <strong>{state.root.replace("https://", "")}</strong> -
            Room Name is <strong>{state.room_name}</strong>
            {state.settings["event_end"] && (
                <span>
                    <br />
                    Event ends at{" "}
                    <strong>
                        {short_date(state.settings["event_end"])}
                    </strong>
                </span>
            )}
        </div>
    </section>
);
