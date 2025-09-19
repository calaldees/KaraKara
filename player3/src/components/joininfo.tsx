import { useContext } from "react";
import { useParams } from "react-router-dom";

import { ClientContext } from "../providers/client";


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
