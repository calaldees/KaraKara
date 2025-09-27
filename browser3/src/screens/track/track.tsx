import {
    faCircleChevronLeft,
    faListOl,
} from "@fortawesome/free-solid-svg-icons";
import { useContext, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { FontAwesomeIcon, Screen } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import { Subtitle, Track } from "@/types";
import { attachment_path } from "@/utils";

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
    "added",
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
            playsInline={true}
            controls={true}
            crossOrigin="anonymous"
        >
            {track.attachments.video.map((a) => (
                <source key={a.path} src={attachment_path(a)} type={a.mime} />
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

function Tag({ name, values }: { name: string; values: string[] }) {
    let view: React.ReactNode[] = [];
    if (["artist", "contributor"].indexOf(name) !== -1) {
        view = values.map((v) => (
            <Link key={v} to={`../?filters=${name}:${v}`}>
                {v}
            </Link>
        ));
    } else {
        view = values;
    }
    return (
        <div className={"tag"}>
            <div className={"tag_key"}>{name}</div>
            <div className={"tag_value"}>
                {view.reduce((prev, curr) => [prev, ", ", curr])}
            </div>
        </div>
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
                        <Tag key={key} name={key} values={track.tags[key]!} />
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
    const [videoVariant, setVideoVariant] = useState<string>("");
    const [subtitleVariant, setSubtitleVariant] = useState<string>("");
    const { request } = useApi();

    function enqueue(performer_name: string, track_id: string) {
        request({
            notify: "Adding to queue...",
            notify_ok: "Added to queue!",
            function: "queue",
            options: {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    track_id: track_id,
                    performer_name: performer_name.trim(),
                    video_variant: videoVariant || null,
                    subtitle_variant: subtitleVariant || null,
                }),
            },
            onAction: () => setAction(TrackAction.NONE),
        });
    }

    let videoSelect = null;
    const videoVariants = [
        ...new Set(
            track.attachments.video
                .map((a) => a.variant)
                .filter((v) => v !== null),
        ),
    ];
    if (videoVariants.length > 1) {
        videoSelect = (
            <select
                name="video_variant"
                onChange={(e) => setVideoVariant(e.target.value)}
                value={videoVariant}
            >
                {/** while the variants are different videos, the effect for the user is different audio */}
                <option value="">Select Audio</option>
                {videoVariants.map((v) => (
                    <option key={v} value={v}>
                        {v}
                    </option>
                ))}
            </select>
        );
    }

    let subtitleSelect = null;
    const subtitleVariants = [
        ...new Set(
            track.attachments.subtitle
                ?.map((a) => a.variant)
                .filter((v) => v !== null),
        ),
    ];
    if (subtitleVariants.length > 1) {
        subtitleSelect = (
            <select
                name="subtitle_variant"
                onChange={(e) => setSubtitleVariant(e.target.value)}
                value={subtitleVariant}
            >
                <option value={""}>Select Subtitles</option>
                {subtitleVariants.map((v) => (
                    <option key={v} value={v}>
                        {v}
                    </option>
                ))}
            </select>
        );
    }

    let variantSelect = null;
    if (videoSelect || subtitleSelect) {
        variantSelect = (
            <div className="buttons">
                {videoSelect}
                {subtitleSelect}
            </div>
        );
    }

    const validInputs =
        performerName.trim().length >= 0 &&
        (videoVariants.length === 0 || videoVariant !== "") &&
        (subtitleVariants.length === 0 || subtitleVariant !== "");

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
                {variantSelect}
                <input
                    type="text"
                    name="performer_name"
                    value={performerName}
                    placeholder={"Enter Name"}
                    required={true}
                    autoFocus={performerName.trim().length === 0}
                    enterKeyHint="done"
                    onChange={(e) => setPerformerName(e.target.value)}
                />
                <div className={"buttons"}>
                    <button
                        type="button"
                        onClick={(_) => setAction(TrackAction.NONE)}
                        autoFocus={performerName.trim().length > 0}
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        onClick={(_) => enqueue(performerName, track.id)}
                        disabled={!validInputs}
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
                    <FontAwesomeIcon
                        icon={faCircleChevronLeft}
                        className="x2"
                    />
                </div>
            }
            title={track.tags.title[0]}
            navRight={
                !widescreen && (
                    <Link to={"../queue"} data-cy="queue">
                        <FontAwesomeIcon icon={faListOl} className="x2" />
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
