import { useContext } from "react";

import { ClientContext } from "../providers/client";
import type { Track, Attachment } from "../types";
import { attachment_path } from "../utils";

interface VideoProps {
    track: Track;
    [Key: string]: any;
}
export function Video({ track, ...kwargs }: VideoProps) {
    const { root } = useContext(ClientContext);
    return (
        <div className="videoScaler">
            <video
                autoPlay={true}
                poster={attachment_path(root, track.attachments.image[0])}
                // ensure the video element gets re-created when <source> changes
                key={track.id}
                crossOrigin="anonymous"
                {...kwargs}
            >
                {track.attachments.video.map((a: Attachment) => (
                    <source
                        key={a.path}
                        src={attachment_path(root, a)}
                        type={a.mime}
                    />
                ))}
                {track.attachments.subtitle
                    ?.filter((a) => a.mime === "text/vtt")
                    .map((a: Attachment) => (
                        <track
                            key={a.path}
                            kind="subtitles"
                            src={attachment_path(root, a)}
                            default={true}
                            label="English"
                            srcLang="en"
                        />
                    ))}
            </video>
        </div>
    );
}
