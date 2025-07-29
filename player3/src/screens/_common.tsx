import { attachment_path, short_date } from "../utils";
import { useParams } from "react-router-dom";
import { useContext } from "react";
import { ClientContext } from "../providers/client";
import { RoomContext } from "../providers/room";
import type { Track, Attachment } from "../types";

interface VideoProps {
    track: Track;
    [Key: string]: any;
};
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
                {track.attachments.subtitle?.map((a: Attachment) => (
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

export function JoinInfo() {
    const { roomName } = useParams();
    const { root } = useContext(ClientContext);
    return (
        <div id="join_info">
            <span>
                Join at <strong>{root.replace("https://", "")}</strong> - Room
                Name is <strong>{roomName}</strong>
            </span>
        </div>
    );
}

export function EventInfo() {
    const { settings } = useContext(RoomContext);
    return (
        <div id="event_info" key={"event_info"}>
            {settings["validation_event_end_datetime"] && (
                <span>
                    Event ends at{" "}
                    <strong>
                        {short_date(settings["validation_event_end_datetime"])}
                    </strong>
                </span>
            )}
            {settings["validation_event_end_datetime"] &&
                settings["admin_list"]?.length > 0 &&
                " - "}
            {settings["admin_list"]?.length > 0 && (
                <span>
                    Admins are{" "}
                    {settings["admin_list"].map(
                        (a: string, n: number, as: string[]) => (
                            <span>
                                <strong>{a}</strong>
                                {n === as.length - 1
                                    ? ""
                                    : n === as.length - 2
                                      ? " and "
                                      : ", "}
                            </span>
                        ),
                    )}
                </span>
            )}
        </div>
    );
}
