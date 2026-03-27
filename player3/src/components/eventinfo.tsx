import { faPlay } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { RoomContext } from "@/providers/room";
import { short_date } from "@/utils";

export function EventInfo() {
    const { settings, queue } = useContext(RoomContext);
    return (
        <div id="event_info" key={"event_info"}>
            {settings.validation_event_end_datetime ? (
                <span>
                    Event ends at{" "}
                    <strong>
                        {short_date(settings.validation_event_end_datetime)}
                    </strong>
                </span>
            ) : queue[0] && queue[0].start_time === null ? (
                <span>
                    Click{" "}
                    <strong>
                        <FAIcon icon={faPlay} />
                    </strong>{" "}
                    on the control panel to start
                </span>
            ) : null}
        </div>
    );
}
