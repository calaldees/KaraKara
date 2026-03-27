import { Track } from "@/types";
import { attachment_path } from "@/utils";

import styles from "./VideoPreview.module.scss";

export function VideoPreview({
    track,
    videoVariant,
    subtitleVariant,
}: {
    track: Track;
    videoVariant: string;
    subtitleVariant: string;
}) {
    let videoAttachments = track.attachments.video.filter(
        (a) => a.variant === videoVariant,
    );
    if (videoAttachments.length === 0)
        videoAttachments = track.attachments.video;
    const imageAttachment =
        track.attachments.image.find((a) => a.variant === videoVariant) ||
        track.attachments.image[0];

    const subtitleAttachment = track.attachments.subtitle?.find(
        (a) => a.mime === "text/vtt" && a.variant === subtitleVariant,
    );

    return (
        <video
            className={styles.video}
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
