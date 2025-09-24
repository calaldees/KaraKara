import { useParams } from "react-router-dom";

export function JoinInfo() {
    const { roomName } = useParams();
    const root = window.location.protocol + "//" + window.location.host;
    return (
        <div id="join_info">
            <span>
                Join at <strong>{root.replace("https://", "")}</strong> - Room
                Name is <strong>{roomName}</strong>
            </span>
        </div>
    );
}
