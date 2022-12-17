import h from "hyperapp-jsx-pragma";
import { attachment_path, short_date } from "../utils";

export const Video = ({ state, track, ...kwargs }) => (
    <video
        autoPlay={true}
        poster={attachment_path(state.root, track.attachments.image[0])}
        // ensure the video element gets re-created when <source> changes
        key={track.id}
        crossorigin="anonymous"
        {...kwargs}
    >
        {track.attachments.video.map((a) => (
            <source src={attachment_path(state.root, a)} type={a.mime} />
        ))}
        {track.attachments.subtitle?.map((a) => (
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
                {state.settings["admin_list"].map((a, n, as) => (
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
