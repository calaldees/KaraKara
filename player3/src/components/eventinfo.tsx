import { useContext } from "react";

import { RoomContext } from "@/providers/room";
import { short_date } from "@/utils";

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
                            <span key={a}>
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
