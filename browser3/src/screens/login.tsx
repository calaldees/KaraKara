import { FormEvent, useState, useCallback } from "react";
import { Screen } from "./_common";
import * as icons from "../static/icons";
import { useNavigate } from "react-router-dom";

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
                        onChange={(e) => setRoomNameEdit(e.target.value)}
                        required={true}
                    />
                    <button type="submit" disabled={!roomNameEdit.trim()}>
                        Enter Room <icons.RightToBracket />
                    </button>
                </form>
            </div>
        </Screen>
    );
}
