import h from "hyperapp-jsx-pragma";
import { attachment_path, time_until } from "../utils";
import { JoinInfo, Video, EventInfo } from "./_common";

const show_tracks = 5;

///////////////////////////////////////////////////////////////////////
// Actions

function SetPreviewVolume(state: State, event): Dispatchable {
    event.target.volume = state.settings["preview_volume"];
    return state;
}

///////////////////////////////////////////////////////////////////////
// Views

export const PreviewScreen = ({
    state,
    queue,
    track,
}: {
    state: State;
    queue: Array<QueueItem>;
    track: Track;
}): VNode => (
    <section key="preview" class={"screen_preview"}>
        <JoinInfo state={state} />
        <Video
            state={state}
            track={track}
            onloadstart={SetPreviewVolume}
            loop={true}
        />
        {queue
            .slice(0, show_tracks)
            .map((item) => ({
                item: item,
                track: state.track_list[item.track_id],
            }))
            .map(({ item, track }, idx) => (
                <div class={"item n" + (idx + 1)} key={item.id}>
                    <img
                        src={attachment_path(
                            state.root,
                            track.attachments.image[0],
                        )}
                    />
                    <p class="title">{track.tags.title[0]}</p>
                    <p class="from">
                        {track.tags.from?.[0] ||
                            track.tags.artist?.join(", ") ||
                            ""}
                    </p>
                    <p class="performer">
                        <span class="n">{idx + 1}</span> {item.performer_name}
                    </p>
                    <p class="time">
                        <span>
                            {time_until(state.now, item.start_time) ||
                                (idx == 0 && "You're up!") ||
                                (idx == 1 && "Nearly there!")}
                        </span>
                    </p>
                </div>
            ))}
        {queue.length > show_tracks && (
            <div id="playlist_obscured" key={"playlist_obscured"}>
                <ul>
                    {queue.slice(show_tracks).map((item) => (
                        <li key={item.id}>{item.performer_name}</li>
                    ))}
                </ul>
            </div>
        )}
        {queue.length > show_tracks && (
            <div id="n_more" key={"n_more"}>
                <div>
                    and <span>{queue.length - show_tracks}</span> more...
                </div>
            </div>
        )}
        <EventInfo state={state} />
    </section>
);
