import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { useContext } from "react";

import { ClientContext } from "@/providers/client";
import { FontAwesomeIcon } from "./FontAwesomeIcon";

export function Notification() {
    const { notification, setNotification } = useContext(ClientContext);

    return (
        notification && (
            <div
                className={"main-only notification " + notification.style}
                onClick={(_) => setNotification(null)}
            >
                <span>{notification.text}</span>
                <FontAwesomeIcon icon={faCircleXmark} />
            </div>
        )
    );
}
