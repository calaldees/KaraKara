import h from "hyperapp-jsx-pragma";
import { attachment_path, short_date } from "../utils";

type VideoProps = {
    state: State,
    track: Track,
    lowres: boolean,
    [Key: string]: any,
};
export const Video = ({ state, track, lowres, ...kwargs }: VideoProps) => (
    <video
        autoPlay={true}
        poster={attachment_path(state.root, track.attachments.image[0])}
        // ensure the video element gets re-created when <source> changes
        key={track.id}
        crossorigin="anonymous"
        {...kwargs}
    >
        {(lowres ? track.attachments.preview : track.attachments.video).map(
            (a: Attachment) => (
                <source src={attachment_path(state.root, a)} type={a.mime} />
            ),
        )}
        {track.attachments.subtitle?.map((a: Attachment) => (
            <track
                kind="subtitles"
                src={attachment_path(state.root, a)}
                default={true}
                label="English"
                srclang="en"
            />
        ))}
    </video>
);

export const JoinInfo = ({ state }: { state: State }) => (
    <div id="join_info">
        Join at <strong>{state.root.replace("https://", "")}</strong> - Room
        Name is <strong>{state.room_name}</strong>
    </div>
);

export const EventInfo = ({ state }: { state: State }) => (
    // key= to make sure this element stays put others before it come and go
    <div id="event_info" key={"event_info"}>
        {state.settings["validation_event_end_datetime"] && (
            <span>
                Event ends at{" "}
                <strong>
                    {short_date(
                        state.settings["validation_event_end_datetime"],
                    )}
                </strong>
            </span>
        )}
        {state.settings["validation_event_end_datetime"] &&
            state.settings["admin_list"]?.length > 0 &&
            " - "}
        {state.settings["admin_list"]?.length > 0 && (
            <span>
                Admins are{" "}
                {state.settings["admin_list"].map((a: string, n: number, as: string[]) => (
                    <span>
                        <strong>{a}</strong>
                        {n == as.length - 1
                            ? ""
                            : n == as.length - 2
                            ? " and "
                            : ", "}
                    </span>
                ))}
            </span>
        )}
    </div>
);
