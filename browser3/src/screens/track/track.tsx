import { faListOl } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { PageContext } from "@/providers/page";

import {
    BackOr,
    LyricsViewer,
    Screen,
    TagsViewer,
    VideoPreview,
} from "@/components";
import { useWidescreen } from "@/hooks/widescreen";
import { ServerContext } from "@/providers/server";
import { Track } from "@/types";
import { preferred_variant, unique, track_title } from "@/utils";

import { TrackButtons } from "./TrackButtons";

import styles from "./track.module.scss";

// Validate parameters and fetch track data,
// then render inner track details component
// with a known-good track.
export function TrackDetails(): React.ReactElement {
    const { trackId } = useParams();
    const { tracks } = useContext(ServerContext);
    if (!trackId) throw Error("Can't get here?");
    const track = tracks[trackId];
    if (!track) return <div>No track with ID {trackId}</div>;

    return <TrackDetailsInternal key={trackId} track={track} />;
}

function TrackDetailsInternal({ track }: { track: Track }): React.ReactElement {
    const { roomName } = useContext(PageContext);
    const widescreen = useWidescreen();

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
            className={styles.track}
            navLeft={<BackOr to={`/${roomName}`} />}
            title={track_title(track)}
            navRight={
                !widescreen && (
                    <Link
                        to={`/${roomName}/queue`}
                        data-cy="queue"
                        aria-label="Show Queue"
                    >
                        <FAIcon icon={faListOl} />
                    </Link>
                )
            }
            footer={
                <TrackButtons
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
            <VideoPreview
                track={track}
                videoVariant={videoVariant}
                subtitleVariant={subtitleVariant}
            />
            <TagsViewer track={track} />
            <LyricsViewer
                track={track}
                key={subtitleVariant}
                variant={subtitleVariant}
            />
        </Screen>
    );
}
