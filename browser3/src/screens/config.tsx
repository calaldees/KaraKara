import { FormEvent, useContext, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ClientContext } from "../providers/client";

import "../static/config.scss";

export function ConfigMenu(): React.ReactElement {
    const { roomName } = useParams();
    const {
        root,
        setRoot,
        roomPassword,
        setRoomPassword,
        booth,
        setBooth,
        setShowSettings,
    } = useContext(ClientContext);
    const [rootEdit, setRootEdit] = useState(root);
    const [roomNameEdit, setRoomNameEdit] = useState(roomName ?? "");
    const [roomPasswordEdit, setRoomPasswordEdit] = useState(roomPassword);
    const navigate = useNavigate();

    function onSubmit(e: FormEvent) {
        e.preventDefault();
        setRoot(rootEdit);
        if (roomNameEdit !== roomName) {
            void navigate("/" + roomNameEdit);
        }
        setRoomPassword(roomPasswordEdit);
        setShowSettings(false);
    }

    return (
        <div className={"config"}>
            <div>
                <h2>App Config</h2>
                <form onSubmit={onSubmit}>
                    <table>
                        <tbody>
                            <tr>
                                <td>Server</td>
                                <td>
                                    <input
                                        value={rootEdit}
                                        type={"text"}
                                        data-cy="server-input"
                                        onChange={(e) =>
                                            setRootEdit(e.target.value)
                                        }
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>Room</td>
                                <td>
                                    <input
                                        value={roomNameEdit}
                                        type={"text"}
                                        data-cy="room-input"
                                        onChange={(e) =>
                                            setRoomNameEdit(e.target.value)
                                        }
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>Password</td>
                                <td>
                                    <input
                                        value={roomPasswordEdit}
                                        type={"password"}
                                        data-cy="password-input"
                                        onChange={(e) =>
                                            setRoomPasswordEdit(e.target.value)
                                        }
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>Booth Mode</td>
                                <td>
                                    <input
                                        checked={booth}
                                        type={"checkbox"}
                                        data-cy="booth-input"
                                        onChange={(_) => setBooth(!booth)}
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td colSpan={2}>
                                    <button type="submit" data-cy="save-button">
                                        Close
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </form>
            </div>
        </div>
    );
}
