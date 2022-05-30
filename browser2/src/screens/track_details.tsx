import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { attachment_path } from "../utils";
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
import { PushScrollPos } from "../effects";

const TrackButtons = ({ state, track }: { state: State; track: Track }): VNode => (
    <footer>
        {state.queue.find((i) => i.track_id == track.source_hash) && (
            <div class={"already_queued"}>Track is already queued</div>
        )}
        <div class={"buttons"}>
            <button
                onclick={ActivateEnqueue()}
                disabled={state.queue.find((i) => i.track_id == track.source_hash)}
            >
                Enqueue
            </button>
            {state.bookmarks.includes(track.source_hash) ? (
                <button onclick={RemoveBookmark(track.source_hash)}>Un-Bookmark</button>
            ) : (
                <button onclick={AddBookmark(track.source_hash)}>Bookmark</button>
            )}
        </div>
    </footer>
);

const EnqueueButtons = ({ state }: { state: State }): VNode => (
    <footer>
        <input
            type="text"
            name="performer_name"
            value={state.performer_name}
            placeholder={
                state.settings["karakara.template.input.performer_name"]
            }
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
        return <EnqueueButtons state={state} />;
}

const BLOCKED_KEYS = [null, "null", "", "title", "from"];

export const TrackDetails = ({
    state,
    track,
}: {
    state: State;
    track: Track;
}): VNode => (
    <Screen
        state={state}
        className={"track_details"}
        navLeft={
            <a onclick={SelectTrack(null)}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={track.tags.title[0]}
        navRight={
            !state.widescreen && (
                <a onclick={GoToScreen("queue", [PushScrollPos()])}>
                    <i class={"fas fa-2x fa-list-ol"} />
                </a>
            )
        }
        footer={get_buttons(state, track)}
    >
        {/* Preview */}
        <video
            class={"video_placeholder"}
            preload={"none"}
            poster={attachment_path(state.root, track.attachments.image[0])}
            durationHint={track.duration}
            controls={true}
        >
            {track.attachments.preview.map(a => 
                <source
                    src={attachment_path(state.root, a)}
                    type={a.mime}
                />)}
        </video>

        {/* Tags */}
        <h2>Tags</h2>
        <div class={"tags"}>
            {Object.keys(track.tags)
                .filter((key) => BLOCKED_KEYS.indexOf(key) == -1)
                .map((key) => (
                    <div class={"tag"}>
                        <div class={"tag_key"}>{key}</div>
                        <div class={"tag_value"}>
                            {track.tags[key].join(", ")}
                        </div>
                    </div>
                ))}
        </div>

        {/* Lyrics */}
        {track.lyrics && (
            <div class={"lyrics"}>
                <h2>Lyrics</h2>
                {track.lyrics.split("\n").map((item) => (
                    <div>{item.replace(/^\{.*?\}/, "")}</div>
                ))}
            </div>
        )}
    </Screen>
);
