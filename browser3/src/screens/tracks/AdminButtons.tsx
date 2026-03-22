import { useContext } from "react";
import { Link } from "react-router-dom";

import { ButtonRow } from "@/components";
import { PageContext } from "@/providers/page";

export function AdminButtons(): React.ReactElement {
    const { roomName } = useContext(PageContext);
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
