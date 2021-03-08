import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { get_attachment, title_case } from "../utils";
import {
    GoToScreen,
    ActivateEnqueue,
    CancelEnqueue,
    EnqueueCurrentTrack,
    SelectTrack,
    AddBookmark,
    RemoveBookmark,
    SetPerformerName,
} from "../actions";

const TrackButtons = ({ state, track }: { state: State; track: Track }) => (
    <footer>
        {state.queue.find((i) => i.track.id == track.id) && (
            <div class={"already_queued"}>Track is already queued</div>
        )}
        <div class={"buttons"}>
            <button
                onclick={ActivateEnqueue()}
                disabled={state.queue.find((i) => i.track.id == track.id)}
            >
                Enqueue
            </button>
            {state.bookmarks.includes(track.id) ? (
                <button onclick={RemoveBookmark(track.id)}>Un-Bookmark</button>
            ) : (
                <button onclick={AddBookmark(track.id)}>Bookmark</button>
            )}
        </div>
    </footer>
);

const EnqueueButtons = ({ state, track }: { state: State; track: Track }) => (
    <footer>
        <input
            type="text"
            name="performer_name"
            value={state.performer_name}
            placeholder={"Performer Name"}
            required={true}
            oninput={SetPerformerName()}
        />
        <div class={"buttons"}>
            <button onclick={CancelEnqueue()}>Cancel</button>
            <button onclick={EnqueueCurrentTrack()}>Confirm</button>
        </div>
    </footer>
);

function get_buttons(state: State, track: Track) {
    if (state.action == null)
        return <TrackButtons state={state} track={track} />;
    if (state.action == "enqueue")
        return <EnqueueButtons state={state} track={track} />;
}

const BLOCKED_KEYS = [null, "null", "title", "from"];

export const TrackDetails = ({
    state,
    track,
}: {
    state: State;
    track: Track;
}) => (
    <Screen
        state={state}
        className={"track_details"}
        navLeft={
            <a onclick={SelectTrack(null)}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={title_case(track.tags["title"][0])}
        navRight={
            <a onclick={GoToScreen(state.room_password ? "control" : "queue")}>
                <i class={"fas fa-2x fa-list-ol"} />
            </a>
        }
        footer={get_buttons(state, track)}
    >
        {/* Preview */}
        <video
            class={"video_placeholder"}
            preload={"none"}
            poster={get_attachment(track, "image")}
            durationHint={track.duration}
            controls={true}
        >
            <source src={get_attachment(track, "preview")} type={"video/mp4"} />
        </video>

        {/* Lyrics */}
        {track.lyrics && (
            <div class={"lyrics"}>
                <h2>Lyrics</h2>
                {track.lyrics.map((item) => (
                    <div>{item.text}</div>
                ))}
            </div>
        )}

        {/* Tags */}
        <h2>Tags</h2>
        <div class={"tags"}>
            {Object.keys(track.tags)
                .filter((key) => BLOCKED_KEYS.indexOf(key) == -1)
                .map((key) => (
                    <div class={"tag"}>
                        <div class={"tag_key"}>{title_case(key)}</div>
                        <div class={"tag_value"}>
                            {title_case(track.tags[key].join(", "))}
                        </div>
                    </div>
                ))}
        </div>
    </Screen>
);
