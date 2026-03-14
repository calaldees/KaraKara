import { useContext } from "react";

import { RoomContext } from "@/providers/room";
import { short_date } from "@/utils";

export function EventInfo() {
    const { settings, queue } = useContext(RoomContext);
    const nextTrackStartTime = queue[0]?.start_time;
    return (
        <div id="event_info" key={"event_info"}>
            {settings["validation_event_end_datetime"] ? (
                <span>
                    Event ends at{" "}
                    <strong>
                        {short_date(settings["validation_event_end_datetime"])}
                    </strong>
                </span>
            ) : !nextTrackStartTime ? (
                <span>Click the <strong>play</strong> icon on the control panel when you're ready to start</span>
            ) : null}
        </div>
    );
}
