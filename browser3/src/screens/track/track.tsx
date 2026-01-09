import {
    faCircleChevronLeft,
    faListOl,
} from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { Screen } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import { Subtitle, Track } from "@/types";
import {
    attachment_path,
    is_my_song,
    nth,
    preferred_variant,
    unique,
} from "@/utils";

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
    "id", // TODO: display id:imdb, id:mal, etc. nicely
];
enum TrackAction {
    NONE = 0,
    ENQUEUE = 1,
}

// Validate parameters and fetch track data,
// then render inner track details component
// with a known-good track.
export function TrackDetails(): React.ReactElement {
    const { trackId } = useParams();
    const { tracks } = useContext(ServerContext);
    if (!trackId) throw Error("Can't get here?");
    const track = tracks[trackId];
    if (!track) return <div>No track with ID {trackId}</div>;

    return <TrackDetailsInner key={trackId} track={track} />;
}

function TrackDetailsInner({ track }: { track: Track }): React.ReactElement {
    const { widescreen } = useContext(ClientContext);
    const navigate = useNavigate();

    const videoVariants = unique(track.attachments.video.map((a) => a.variant));
    const [videoVariant, setVideoVariant] = useState<string>(() =>
        preferred_variant(videoVariants),
    );

    const subtitleVariants = unique(
        track.attachments.subtitle?.map((a) => a.variant) ?? [],
    );
    const [subtitleVariant, setSubtitleVariant] = useState<string>(() =>
        preferred_variant(subtitleVariants),
    );

    return (
        <Screen
            className={"track"}
            navLeft={
                <FAIcon
                    icon={faCircleChevronLeft}
                    className="x2"
                    onClick={() => void navigate(-1)}
                    data-cy="back"
                    role="button"
                    aria-label="Go Back"
                />
            }
            title={track.tags.title[0]}
            navRight={
                !widescreen && (
                    <Link
                        to={"../queue"}
                        data-cy="queue"
                        aria-label="Show Queue"
                    >
                        <FAIcon icon={faListOl} className="x2" />
                    </Link>
                )
            }
            footer={
                <Buttons
                    track={track}
                    videoVariants={videoVariants}
                    videoVariant={videoVariant}
                    setVideoVariant={setVideoVariant}
                    subtitleVariants={subtitleVariants}
                    subtitleVariant={subtitleVariant}
                    setSubtitleVariant={setSubtitleVariant}
                />
            }
        >
            <Preview
                track={track}
                videoVariant={videoVariant}
                subtitleVariant={subtitleVariant}
            />
            <Tags track={track} />
            <Lyrics
                track={track}
                key={subtitleVariant}
                variant={subtitleVariant}
            />
        </Screen>
    );
}

function Preview({
    track,
    videoVariant,
    subtitleVariant,
}: {
    track: Track;
    videoVariant: string | null;
    subtitleVariant: string | null;
}) {
    let videoAttachments = track.attachments.video.filter(
        (a) => a.variant === videoVariant,
    );
    if (videoAttachments.length == 0)
        videoAttachments = track.attachments.video;
    const imageAttachment =
        track.attachments.image.find((a) => a.variant == videoVariant) ||
        track.attachments.image[0];

    const subtitleAttachment = track.attachments.subtitle?.find(
        (a) => a.mime === "text/vtt" && a.variant === subtitleVariant,
    );

    return (
        <video
            className={"video_placeholder"}
            key={videoVariant}
            preload={"none"}
            poster={attachment_path(imageAttachment)}
            playsInline={true}
            controls={true}
            crossOrigin="anonymous"
        >
            {videoAttachments.map((videoAttachment) => (
                <source
                    key={videoAttachment.path}
                    src={attachment_path(videoAttachment)}
                    type={videoAttachment.mime}
                />
            ))}
            {subtitleAttachment && (
                <track
                    key={subtitleAttachment.path}
                    src={attachment_path(subtitleAttachment)}
                    default={true}
                />
            )}
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

function Lyrics({
    track,
    variant,
}: {
    track: Track;
    variant: string | null;
}): React.ReactElement | null {
    const [lyrics, setLyrics] = useState<Subtitle[]>([]);
    const { request } = useApi();

    useEffect(() => {
        const subtitleAttachment = track.attachments.subtitle?.find(
            (a) => a.mime === "application/json" && a.variant === variant,
        );
        if (subtitleAttachment) {
            request({
                url: attachment_path(subtitleAttachment),
                options: { credentials: "omit" },
                onAction: (result) => setLyrics(result),
            });
        }
    }, [request, track, variant]);

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

function Buttons({
    track,
    videoVariants,
    videoVariant,
    setVideoVariant,
    subtitleVariants,
    subtitleVariant,
    setSubtitleVariant,
}: {
    track: Track;
    videoVariants: string[];
    videoVariant: string;
    setVideoVariant: (v: string) => void;
    subtitleVariants: string[];
    subtitleVariant: string;
    setSubtitleVariant: (v: string) => void;
}) {
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
                    video_variant: videoVariant,
                    subtitle_variant: subtitleVariant,
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

    const isQueued = queue.find((i) => i.track_id === track.id) !== undefined;

    const myTracks = queue.filter((item) =>
        is_my_song(item, sessionId, performerName),
    );
    const otherPeoplesTracks = queue.filter(
        (item) => !is_my_song(item, sessionId, performerName),
    );
    const averageTracksPerPerformer =
        otherPeoplesTracks.length > 0
            ? otherPeoplesTracks.length /
              unique(otherPeoplesTracks.map((item) => item.performer_name))
                  .length
            : 0;
    const averageTracksPerPerformerStr = averageTracksPerPerformer.toFixed(1);
    const myTrackCount = myTracks.length + 1;
    let warning = null;
    if (
        !isQueued &&
        !booth &&
        queue.length > 3 &&
        myTrackCount > averageTracksPerPerformer * 2
    ) {
        warning = (
            <div className="warning" style={{ textAlign: "center" }}>
                The average person has {averageTracksPerPerformerStr}{" "}
                {averageTracksPerPerformerStr !== "1.0" ? "tracks" : "track"} in
                the queue, this will be your {nth(myTrackCount)} — please make
                sure everybody gets a chance to sing ❤️
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
                {variantSelect}
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
