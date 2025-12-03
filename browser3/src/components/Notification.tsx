import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { ClientContext } from "@/providers/client";

export function Notification() {
    const { notification, setNotification } = useContext(ClientContext);

    return (
        notification && (
            <div
                className={"main-only notification " + notification.style}
                onClick={(_) => setNotification(null)}
            >
                <span>{notification.text}</span>
                <FAIcon icon={faCircleXmark} />
            </div>
        )
    );
}
