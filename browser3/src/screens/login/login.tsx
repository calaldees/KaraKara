import { faRightToBracket } from "@fortawesome/free-solid-svg-icons";
import { FormEvent, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";

import { FontAwesomeIcon, Screen } from "@/components";

import "./login.scss";

export function Login(): React.ReactElement {
    const [roomNameEdit, setRoomNameEdit] = useState("");
    const navigate = useNavigate();
    const onSubmit = useCallback(
        (e: FormEvent) => {
            e.preventDefault();
            void navigate(roomNameEdit.toLowerCase());
        },
        [navigate, roomNameEdit],
    );

    return (
        <Screen className={"login"} title={"Welcome to KaraKara"}>
            <div className={"flex-center"}>
                <form onSubmit={onSubmit}>
                    <input
                        type={"text"}
                        placeholder={"Room Name"}
                        value={roomNameEdit}
                        enterKeyHint="go"
                        onChange={(e) => setRoomNameEdit(e.target.value)}
                        required={true}
                        autoFocus={true}
                    />
                    <button type="submit" disabled={!roomNameEdit.trim()}>
                        Enter Room <FontAwesomeIcon icon={faRightToBracket} />
                    </button>
                </form>
            </div>
        </Screen>
    );
}
