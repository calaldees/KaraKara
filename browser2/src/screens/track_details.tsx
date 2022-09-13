import h from "hyperapp-jsx-pragma";
import { Screen } from "./_common";
import { attachment_path } from "../utils";
import { GoToScreen } from "../actions";
import { PushScrollPos, PopScrollPos, ApiRequest } from "../effects";


///////////////////////////////////////////////////////////////////////
// Actions

const AddBookmark = (state: State, track_id: string, event): State => ({
    ...state,
    notification: { text: "" + event, style: "warning" },
    bookmarks: state.bookmarks.concat([track_id]),
});

const RemoveBookmark = (state: State, track_id: string): State => ({
    ...state,
    bookmarks: state.bookmarks.filter((x) => x != track_id),
});

const SetPerformerName = (state: State, event: FormInputEvent): State => ({
    ...state,
    performer_name: event.target.value,
});

const EnqueueCurrentTrack = (state: State): Dispatchable => [
    state,
    ApiRequest({
        notify: "Adding to queue...",
        notify_ok: "Added to queue!",
        function: "queue",
        state: state,
        options: {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                track_id: state.track_id || "error",
                performer_name: state.performer_name,
            }),
        },
        action: (state, response) => [{ ...state, action: null }],
    }),
];

const UnselectTrack = (state: State): Dispatchable => [
    { ...state, track_id: null },
    PopScrollPos(),
];


///////////////////////////////////////////////////////////////////////
// Views

const TrackButtons = ({ state, track }: { state: State; track: Track }): VNode => (
    <footer>
        {state.queue.find((i) => i.track_id == track.id) && (
            <div class={"already_queued"}>Track is already queued</div>
        )}
        <div class={"buttons"}>
            <button
                onclick={(state: State): State => ({ ...state, action: "enqueue" })}
                disabled={state.queue.find((i) => i.track_id == track.id)}
            >
                Enqueue
            </button>
            {state.bookmarks.includes(track.id) ? (
                <button onclick={[RemoveBookmark, track.id]}>Un-Bookmark</button>
            ) : (
                <button onclick={[AddBookmark, track.id]}>Bookmark</button>
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
            placeholder={"Enter Name"}
            required={true}
            oninput={SetPerformerName}
        />
        <div class={"buttons"}>
            <button onclick={(state: State): State => ({ ...state, action: null })}>Cancel</button>
            <button onclick={EnqueueCurrentTrack}>Confirm</button>
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
            <a onclick={UnselectTrack}>
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
                            {track.tags[key]?.join(", ")}
                        </div>
                    </div>
                ))}
        </div>

        {/* Lyrics */}
        {track.lyrics.length > 0 && (
            <div class={"lyrics"}>
                <h2>Lyrics</h2>
                {track.lyrics.map(item => <div>{item}</div>)}
            </div>
        )}
    </Screen>
);
