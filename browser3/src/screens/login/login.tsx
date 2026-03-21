import { faRightToBracket } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { SubmitEvent, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Screen } from "@/components";

import "./login.scss";

export function Login(): React.ReactElement {
    const [roomNameEdit, setRoomNameEdit] = useState("");
    const navigate = useNavigate();
    const onSubmit = useCallback(
        (e: SubmitEvent) => {
            e.preventDefault();
            void navigate("/" + roomNameEdit.toLowerCase());
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
                        onChange={(e) => setRoomNameEdit(e.currentTarget.value)}
                        required={true}
                        autoFocus={true}
                        maxLength={10}
                    />
                    <button type="submit" disabled={!roomNameEdit.trim()}>
                        Enter Room <FAIcon icon={faRightToBracket} />
                    </button>
                </form>
            </div>
        </Screen>
    );
}
