import { h } from "hyperapp";
import { Screen } from "./base";
import { get_attachment, title_case } from "../utils";
import { DisplayErrorResponse } from "../effects";
import { Http } from "hyperapp-fx";
import parseSRT from "parse-srt";

const TrackButtons = ({ state, track }: { state: State; track: Track }) => (
    <footer>
        {track.id in state.queue.map(i => i.track.id) && (
            <div class={"notification"}>Track is already queued</div>
        )}
        <div class={"buttons"}>
            <button
                onclick={(state: State, event: FormInputEvent) =>
                    ({
                        ...state,
                        action: "enqueue",
                    } as State)
                }
                disabled={track.id in state.queue.map(i => i.track.id)}
            >
                Enqueue
            </button>
            {state.bookmarks.filter(x => x == track.id).length == 0 ? (
                <button
                    onclick={(state: State, event: FormInputEvent) =>
                        ({
                            ...state,
                            bookmarks: state.bookmarks.concat([track.id]),
                        } as State)
                    }
                >
                    Bookmark
                </button>
            ) : (
                <button
                    onclick={(state: State, event: FormInputEvent) =>
                        ({
                            ...state,
                            bookmarks: state.bookmarks.filter(
                                x => x != track.id,
                            ),
                        } as State)
                    }
                >
                    Un-Bookmark
                </button>
            )}
        </div>
    </footer>
);

// TODO: remove self from queue?
function enqueue(state: State) {
    let adding_title = title_case(
        state.track_list[state.track_id].tags["title"][0],
    );
    let adding_performer = state.performer_name;
    return [
        { ...state, notification: "Adding to queue..." },
        Http({
            url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
            options: {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    track_id: state.track_id,
                    performer_name: state.performer_name,
                }),
            },
            action: (state, response) => ({
                ...state,
                notification:
                    "Added " +
                    adding_title +
                    " (" +
                    adding_performer +
                    ") to queue",
                action: null,
            }),
            error: (state, response) => ([
                {...state,},
                DisplayErrorResponse({response})
            ]),
        }),
    ];
}

const EnqueueButtons = ({ state, track }: { state: State; track: Track }) => (
    <footer>
        <input
            type="text"
            name="performer_name"
            value={state.performer_name}
            placeholder={"Performer Name"}
            required={true}
            oninput={(state: State, event: FormInputEvent) =>
                ({
                    ...state,
                    performer_name: event.target.value,
                } as State)
            }
        />
        <div class={"buttons"}>
            <button
                onclick={(state: State, event: FormInputEvent) =>
                    ({
                        ...state,
                        action: null,
                    } as State)
                }
            >
                Cancel
            </button>
            <button onClick={enqueue}>Confirm</button>
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
            <a onclick={state => ({ ...state, track_id: null })}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={title_case(track.tags["title"][0])}
        navRight={
            <a onclick={state => ({ ...state, screen: "queue" })}>
                <i class={"fas fa-2x fa-list-ol"} />
            </a>
        }
        footer={get_buttons(state, track)}
    >
        {/* Preview */}
        <video
            className={"video_placeholder"}
            preload={"none"}
            poster={get_attachment(track, "image")}
            durationHint={track.duration}
            controls={true}
        >
            <source src={get_attachment(track, "preview")} type={"video/mp4"} />
        </video>

        {/* Lyrics */}
        {track.srt && (
            <div className={"lyrics"}>
                <h2>Lyrics</h2>
                {parseSRT(track.srt).map(item => (
                    <div>{item.text}</div>
                ))}
            </div>
        )}

        {/* Tags */}
        <h2>Tags</h2>
        <div className={"tags"}>
            {Object.keys(track.tags)
                .filter(key => BLOCKED_KEYS.indexOf(key) == -1)
                .map(key => (
                    <div className={"tag"}>
                        <div className={"tag_key"}>{title_case(key)}</div>
                        <div className={"tag_value"}>
                            {title_case(track.tags[key].join(", "))}
                        </div>
                    </div>
                ))}
        </div>
    </Screen>
);
