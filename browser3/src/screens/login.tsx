import { FormEvent, useState } from "react";
import { Screen } from "./_common";
import * as icons from "../static/icons";
import { useNavigate } from "react-router-dom";

export function Login(): React.ReactElement {
    const [roomNameEdit, setRoomNameEdit] = useState("");
    const navigate = useNavigate();

    function onSubmit(e: FormEvent) {
        e.preventDefault();
        navigate(roomNameEdit.toLowerCase());
    }

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
                    <button disabled={!roomNameEdit.trim()}>
                        Enter Room <icons.RightToBracket />
                    </button>
                </form>
            </div>
        </Screen>
    );
}
