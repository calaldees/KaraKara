import { useContext, useState } from "react";
import { Screen } from "./_common";
import { attachment_path } from "../utils";
import * as icons from "../static/icons";
import { Link, useParams, useNavigate } from "react-router-dom";
import { ClientContext } from "../providers/client";
import { ServerContext } from "../providers/server";
import { RoomContext } from "../providers/room";
import { useApi } from "../hooks/api";

const BLOCKED_KEYS = [
    null,
    "null",
    "",
    "title",
    "from",
    "source_type",
    "subs",
    "aspect_ratio",
    "date",
    "source",  // TODO: figure out a nice way to display source URLs?
];
enum TrackAction {
    NONE = 0,
    ENQUEUE = 1,
}

export function TrackDetails(): React.ReactElement {
    const { trackId } = useParams();
    const {
        root,
        widescreen,
        bookmarks,
        addBookmark,
        removeBookmark,
        performerName,
        setPerformerName,
    } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const { queue } = useContext(RoomContext);
    const [action, setAction] = useState<TrackAction>(TrackAction.NONE);
    const { request } = useApi();
    const navigate = useNavigate();
    if (!trackId) throw Error("Can't get here?");
    const track = tracks[trackId];
    if (!track) return <div>No track with ID {trackId}</div>;

    function enqueue(performer_name: string, track_id: string) {
        request({
            notify: "Adding to queue...",
            notify_ok: "Added to queue!",
            function: "queue",
            options: {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    track_id: track_id || "error",
                    performer_name: performer_name.trim(),
                }),
            },
            onAction: () => setAction(TrackAction.NONE),
        });
    }

    let buttons = null;
    if (action === TrackAction.NONE) {
        const is_queued =
            queue.find((i) => i.track_id === track.id) !== undefined;

        buttons = (
            <footer>
                {is_queued && (
                    <div className={"already_queued"}>
                        Track is already queued
                    </div>
                )}
                <div className={"buttons"}>
                    <button
                        onClick={(_) => setAction(TrackAction.ENQUEUE)}
                        disabled={is_queued}
                    >
                        Enqueue
                    </button>
                    {bookmarks.includes(track.id) ? (
                        <button onClick={(_) => removeBookmark(track.id)}>
                            Un-Bookmark
                        </button>
                    ) : (
                        <button onClick={(_) => addBookmark(track.id)}>
                            Bookmark
                        </button>
                    )}
                </div>
            </footer>
        );
    }
    if (action === TrackAction.ENQUEUE) {
        buttons = (
            <footer>
                <input
                    type="text"
                    name="performer_name"
                    value={performerName}
                    placeholder={"Enter Name"}
                    required={true}
                    onChange={(e) => setPerformerName(e.target.value)}
                />
                <div className={"buttons"}>
                    <button onClick={(_) => setAction(TrackAction.NONE)}>
                        Cancel
                    </button>
                    <button onClick={(_) => enqueue(performerName, track.id)}>
                        Confirm
                    </button>
                </div>
            </footer>
        );
    }

    return (
        <Screen
            className={"track_details"}
            navLeft={
                <div onClick={() => void navigate(-1)} data-cy="back">
                    <icons.CircleChevronLeft className="x2" />
                </div>
            }
            title={track.tags.title[0]}
            navRight={
                !widescreen && (
                    <Link to={"../queue"} data-cy="queue">
                        <icons.ListOl className="x2" />
                    </Link>
                )
            }
            footer={buttons}
        >
            {/* Preview */}
            <video
                className={"video_placeholder"}
                preload={"none"}
                poster={attachment_path(
                    root,
                    track.attachments.image.slice(-1)[0],
                )}
                controls={true}
                crossOrigin="anonymous"
            >
                {track.attachments.video.map((a) => (
                    <source
                        key={a.path}
                        src={attachment_path(root, a)}
                        type={a.mime}
                    />
                ))}
                {track.attachments.subtitle?.map((a) => (
                    <track
                        key={a.path}
                        src={attachment_path(root, a)}
                        default={true}
                    />
                ))}
            </video>

            {/* Tags */}
            <h2>Tags</h2>
            <div className={"tags"}>
                {Object.keys(track.tags)
                    .filter((key) => !BLOCKED_KEYS.includes(key))
                    .map((key) => (
                        <div key={key} className={"tag"}>
                            <div className={"tag_key"}>{key}</div>
                            <div className={"tag_value"}>
                                {track.tags[key]?.join(", ")}
                            </div>
                        </div>
                    ))}
            </div>

            {/* Lyrics */}
            {track.lyrics.length > 0 && (
                <div className={"lyrics"}>
                    <h2>Lyrics</h2>
                    {track.lyrics.map((item, n) => (
                        <div key={n}>{item}</div>
                    ))}
                </div>
            )}
        </Screen>
    );
}
