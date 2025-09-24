import { useParams } from "react-router-dom";

export function JoinInfo() {
    const { roomName } = useParams();
    return (
        <div id="join_info">
            <span>
                Join at <strong>{window.location.hostname}</strong> - Room
                Name is <strong>{roomName}</strong>
            </span>
        </div>
    );
}
