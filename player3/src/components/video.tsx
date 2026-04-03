import { useState, useEffect } from "react";
import type { Attachment, Track } from "@/types";
import { attachment_path } from "@/utils";
import { faWifi } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";

import "./video.scss";

type VideoProps = {
    track: Track;
    subs?: boolean;
    loop?: boolean;
    mute?: boolean;
    onLoadStart?: (e: any) => void;
    videoVariant: string;
    subtitleVariant: string;
};

export function Video(props: VideoProps) {
    return <VideoInternal key={props.track.id} {...props} />;
}

function VideoInternal({
    track,
    subs = true,
    loop = false,
    mute = false,
    onLoadStart = undefined,
    videoVariant,
    subtitleVariant,
}: VideoProps) {
    const [isBuffering, setIsBuffering] = useState<boolean | null>(null);

    // Set buffering to true after 1 second if it hasn't been set yet
    useEffect(() => {
        if (isBuffering === null) {
            console.log("Setting timeout");
            const timeout = setTimeout(() => {
                console.log("Setting buffering to true");
                setIsBuffering(true);
            }, 1000);

            return () => clearTimeout(timeout);
        }
    }, [isBuffering]);

    return (
        <div className="videoScaler">
            {isBuffering === true && (
                <FAIcon
                    icon={faWifi}
                    className="buffering-indicator"
                />
            )}
            <video
                autoPlay={true}
                poster={attachment_path(track.attachments.image[0])}
                crossOrigin="anonymous"
                loop={loop}
                muted={mute}
                onLoadStart={onLoadStart}
                onCanPlayThrough={() => setIsBuffering(false)}
                onWaiting={() => setIsBuffering(true) }
                //onStalled={() => console.log("stalled")}
                //onSuspend={() => console.log("suspend")}
            >
                {track.attachments.video
                    .filter((a) => a.variant === videoVariant)
                    .filter((a) => a.mime.startsWith("video/webm"))
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
