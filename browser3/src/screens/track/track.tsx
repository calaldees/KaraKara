import { useContext, useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";

import { Screen } from "../_common";
import { attachment_path } from "@/utils";
import { ClientContext } from "@/providers/client";
import { ServerContext } from "@/providers/server";
import { RoomContext } from "@/providers/room";
import { useApi } from "@/hooks/api";
import { Track, Subtitle } from "@/types";

import * as icons from "@/static/icons";
import "./track.scss";

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
    "source", // TODO: figure out a nice way to display source URLs?
];
enum TrackAction {
    NONE = 0,
    ENQUEUE = 1,
}

function Preview({ track }: { track: Track }) {
    return (
        <video
            className={"video_placeholder"}
            preload={"none"}
            poster={attachment_path(track.attachments.image.slice(-1)[0])}
            controls={true}
            crossOrigin="anonymous"
        >
            {track.attachments.video.map((a) => (
                <source
                    key={a.path}
                    src={attachment_path(a)}
                    type={a.mime}
                />
            ))}
            {track.attachments.subtitle
                ?.filter((a) => a.mime === "text/vtt")
                .map((a) => (
                    <track
                        key={a.path}
                        src={attachment_path(a)}
                        default={true}
                    />
                ))}
        </video>
    );
}

function Tags({ track }: { track: Track }) {
    return (
        <>
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
        </>
    );
}

function Lyrics({ track }: { track: Track }): React.ReactElement | null {
    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    const { request } = useApi();

    useEffect(() => {
        const subtitleAttachment = track.attachments.subtitle?.find(
            (a) => a.mime === "application/json",
        );
        if (subtitleAttachment) {
            request({
                url: attachment_path(subtitleAttachment),
                options: { credentials: "omit" },
                onAction: (result) => setLyrics(result),
            });
        }
    }, [request, track]);

    if (lyrics.length === 0) {
        return null;
    } else {
        return (
            <>
                <h2>Lyrics</h2>
                <div className={"lyrics"}>
                    {lyrics.map((item, n) => (
                        <div key={n}>{item.text}</div>
                    ))}
                </div>
            </>
        );
    }
}

function Buttons({ track }: { track: Track }) {
    const { queue } = useContext(RoomContext);
    const {
        bookmarks,
        addBookmark,
        removeBookmark,
        performerName,
        setPerformerName,
    } = useContext(ClientContext);
    const [action, setAction] = useState<TrackAction>(TrackAction.NONE);
    const { request } = useApi();

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

    if (action === TrackAction.NONE) {
        const is_queued =
            queue.find((i) => i.track_id === track.id) !== undefined;

        return (
            <footer>
                {is_queued && (
                    <div className={"already_queued"}>
                        Track is already queued
                    </div>
                )}
                <div className={"buttons"}>
                    <button
                        type="button"
                        onClick={(_) => setAction(TrackAction.ENQUEUE)}
                        disabled={is_queued}
                    >
                        Enqueue
                    </button>
                    {bookmarks.includes(track.id) ? (
                        <button
                            type="button"
                            onClick={(_) => removeBookmark(track.id)}
                        >
                            Un-Bookmark
                        </button>
                    ) : (
                        <button
                            type="button"
                            onClick={(_) => addBookmark(track.id)}
                        >
                            Bookmark
                        </button>
                    )}
                </div>
            </footer>
        );
    }
    if (action === TrackAction.ENQUEUE) {
        return (
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
                    <button
                        type="button"
                        onClick={(_) => setAction(TrackAction.NONE)}
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        onClick={(_) => enqueue(performerName, track.id)}
                        disabled={performerName.trim().length === 0}
                    >
                        Confirm
                    </button>
                </div>
            </footer>
        );
    }
    return null;
}
export function TrackDetails(): React.ReactElement {
    const { trackId } = useParams();
    const { widescreen } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const navigate = useNavigate();
    if (!trackId) throw Error("Can't get here?");
    const track = tracks[trackId];
    if (!track) return <div>No track with ID {trackId}</div>;

    return (
        <Screen
            className={"track"}
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
            footer={<Buttons track={track} />}
        >
            <Preview track={track} />
            <Tags track={track} />
            <Lyrics track={track} />
        </Screen>
    );
}
