import type { Track, Attachment } from "@/types";
import { attachment_path } from "@/utils";

interface VideoProps {
    track: Track;
    subs?: boolean;
    loop?: boolean;
    onLoadStart?: (e: any) => void;
}
export function Video({
    track,
    subs = true,
    loop = false,
    onLoadStart = undefined,
}: VideoProps) {
    return (
        <div className="videoScaler">
            <video
                autoPlay={true}
                poster={attachment_path(track.attachments.image[0])}
                // ensure the video element gets re-created when <source> changes
                key={track.id}
                crossOrigin="anonymous"
                loop={loop}
                onLoadStart={onLoadStart}
            >
                {track.attachments.video.map((a: Attachment) => (
                    <source
                        key={a.path}
                        src={attachment_path(a)}
                        type={a.mime}
                    />
                ))}
                {subs &&
                    track.attachments.subtitle
                        ?.filter((a) => a.mime === "text/vtt")
                        .map((a: Attachment) => (
                            <track
                                key={a.path}
                                kind="subtitles"
                                src={attachment_path(a)}
                                default={true}
                                label="English"
                                srcLang="en"
                            />
                        ))}
            </video>
        </div>
    );
}
