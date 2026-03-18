import { useContext, useState } from "react";

import { ButtonRow } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { Track } from "@/types";

import { BookmarkButton } from "./BookmarkButton";
import { QueueHogWarning } from "./QueueHogWarning";
import styles from "./TrackButtons.module.scss";

enum TrackAction {
    NONE = 0,
    ENQUEUE = 1,
}

export function TrackButtons({
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
    const { performerName, setPerformerName } = useContext(ClientContext);
    const [action, setAction] = useState<TrackAction>(TrackAction.NONE);
    const { request } = useApi();

    const isQueued = queue.find((i) => i.track_id === track.id) !== undefined;

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
            <ButtonRow>
                {videoSelect}
                {subtitleSelect}
            </ButtonRow>
        );
    }

    const validInputs =
        performerName.trim().length >= 0 &&
        (videoVariants.length === 0 || videoVariant !== "") &&
        (subtitleVariants.length === 0 || subtitleVariant !== "");

    if (action === TrackAction.NONE) {
        return (
            <>
                <QueueHogWarning trackId={track.id} />
                {isQueued && (
                    <div className={styles.alreadyQueued}>
                        Track is already queued
                    </div>
                )}
                {variantSelect}
                <ButtonRow>
                    <button
                        type="button"
                        onClick={(_) => setAction(TrackAction.ENQUEUE)}
                        disabled={isQueued}
                    >
                        Enqueue
                    </button>
                    <BookmarkButton trackId={track.id} />
                </ButtonRow>
            </>
        );
    }
    if (action === TrackAction.ENQUEUE) {
        return (
            <footer>
                <QueueHogWarning trackId={track.id} />
                {variantSelect}
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
                <ButtonRow>
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
                </ButtonRow>
            </footer>
        );
    }
    return null;
}
