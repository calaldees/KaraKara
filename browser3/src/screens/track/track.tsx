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
import { attachment_path, is_my_song, nth, unique } from "@/utils";

import "./track.scss";

const BLOCKED_KEYS = [
    "",
    "title",
    "from",
    "source_type",
    "subs",
    "aspect_ratio",
    "date",
    "added",
    "new",
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
        booth,
    } = useContext(ClientContext);
    const [action, setAction] = useState<TrackAction>(TrackAction.NONE);
    const { request, sessionId } = useApi();

    const videoVariants = unique(track.attachments.video
        .map((a) => a.variant)
        .filter((v) => v !== null)
    );
    const [videoVariant, setVideoVariant] = useState<string>(videoVariants.length === 1 ? videoVariants[0] : "");

    const subtitleVariants = unique(
        track.attachments.subtitle
            ?.map((a) => a.variant)
            .filter((v) => v !== null) ?? []
    );
    const [subtitleVariant, setSubtitleVariant] = useState<string>(subtitleVariants.length === 1 ? subtitleVariants[0] : "");

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
    if (videoVariants.length > 1) {
        videoSelect = (
            <select
                name="video_variant"
                onChange={(e) => setVideoVariant(e.currentTarget.value)}
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
    if (subtitleVariants.length > 1) {
        subtitleSelect = (
            <select
                name="subtitle_variant"
                onChange={(e) => setSubtitleVariant(e.currentTarget.value)}
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

    const isQueued =
        queue.find((i) => i.track_id === track.id) !== undefined;

    const myTracks = queue.filter((item) =>
        is_my_song(item, sessionId, performerName)
    );
    const otherPeoplesTracks = queue.filter((item) =>
        !is_my_song(item, sessionId, performerName)
    );
    const averageTracksPerPerformer = otherPeoplesTracks.length > 0
        ? otherPeoplesTracks.length /
          unique(otherPeoplesTracks.map((item) => item.performer_name)).length
        : 0;
    const averageTracksPerPerformerStr = averageTracksPerPerformer.toFixed(1);
    const myTrackCount = myTracks.length + 1;
    let warning = null;
    if (!isQueued && !booth && queue.length > 3 && myTrackCount > averageTracksPerPerformer * 2) {
        warning = (
            <div className="warning" style={{ textAlign: "center" }}>
                The average person has {averageTracksPerPerformerStr}{" "}
                {averageTracksPerPerformerStr !== "1.0" ? "tracks" : "track"} in the queue, this will be{" "}
                your {nth(myTrackCount)} — please make sure everybody
                gets a chance to sing ❤️
            </div>
        );
    }

    if (action === TrackAction.NONE) {
        return (
            <footer>
                {warning}
                {isQueued && (
                    <div className={"already_queued"}>
                        Track is already queued
                    </div>
                )}
                <div className={"buttons"}>
                    <button
                        type="button"
                        onClick={(_) => setAction(TrackAction.ENQUEUE)}
                        disabled={isQueued}
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
                {warning}
                <input
                    type="text"
                    name="performer_name"
                    value={performerName}
                    placeholder={"Enter Name"}
                    required={true}
                    autoFocus={performerName.trim().length === 0}
                    enterKeyHint="done"
                    onChange={(e) => setPerformerName(e.currentTarget.value)}
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
                <div
                    onClick={() => void navigate(-1)}
                    data-cy="back"
                    role="button"
                    aria-label="Go Back"
                >
                    <FontAwesomeIcon
                        icon={faCircleChevronLeft}
                        className="x2"
                    />
                </div>
            }
            title={track.tags.title[0]}
            navRight={
                !widescreen && (
                    <Link
                        to={"../queue"}
                        data-cy="queue"
                        aria-label="Show Queue"
                    >
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
