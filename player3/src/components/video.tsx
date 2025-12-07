import type { Attachment, Track } from "@/types";
import { attachment_path } from "@/utils";

export function Video({
    track,
    subs = true,
    loop = false,
    mute = false,
    onLoadStart = undefined,
    videoVariant,
    subtitleVariant,
}: {
    track: Track;
    subs?: boolean;
    loop?: boolean;
    mute?: boolean;
    onLoadStart?: (e: any) => void;
    videoVariant: string;
    subtitleVariant: string;
}) {
    return (
        <div className="videoScaler">
            <video
                autoPlay={true}
                poster={attachment_path(track.attachments.image[0])}
                // ensure the video element gets re-created when <source> changes
                key={track.id}
                crossOrigin="anonymous"
                loop={loop}
                muted={mute}
                onLoadStart={onLoadStart}
            >
                {track.attachments.video
                    .filter((a) => a.variant === videoVariant)
                    .map((a: Attachment) => (
                        <source
                            key={a.path}
                            src={attachment_path(a)}
                            type={a.mime}
                        />
                    ))}
                {subs &&
                    track.attachments.subtitle
                        ?.filter((a) => a.mime === "text/vtt")
                        .filter((a) => a.variant === subtitleVariant)
                        .map((a: Attachment) => (
                            <track
                                key={a.path}
                                kind="subtitles"
                                src={attachment_path(a)}
                                default={true}
                                label={a.variant}
                                srcLang="en"
                            />
                        ))}
            </video>
        </div>
    );
}
