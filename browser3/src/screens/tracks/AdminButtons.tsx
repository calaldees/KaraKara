import { Link, useParams } from "react-router-dom";

import { ButtonRow } from "@/components";

export function AdminButtons(): React.ReactElement {
    const { roomName } = useParams();
    return (
        <ButtonRow>
            <Link to={`/${roomName}/settings`} className="button">
                Room Settings
            </Link>
            <Link to={`/${roomName}/printable`} className="button">
                Printable QR Code
            </Link>
        </ButtonRow>
    );
}
