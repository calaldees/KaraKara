import { FormEvent, useCallback, useContext, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ClientContext } from "@/providers/client";

import "./config.scss";

export function ConfigMenu(): React.ReactElement {
    const { roomName } = useParams();
    const { roomPassword, setRoomPassword, booth, setBooth, setShowSettings } =
        useContext(ClientContext);
    const [roomNameEdit, setRoomNameEdit] = useState(roomName ?? "");
    const [roomPasswordEdit, setRoomPasswordEdit] = useState(roomPassword);
    const navigate = useNavigate();

    const onSubmit = useCallback(
        (e: FormEvent) => {
            e.preventDefault();
            if (roomNameEdit !== roomName) {
                void navigate("/" + roomNameEdit);
            }
            setRoomPassword(roomPasswordEdit);
            setShowSettings(false);
        },
        [
            roomNameEdit,
            roomName,
            navigate,
            setRoomPassword,
            roomPasswordEdit,
            setShowSettings,
        ],
    );

    return (
        <div className={"config"}>
            <div>
                <h2>App Config</h2>
                <form onSubmit={onSubmit}>
                    <table>
                        <tbody>
                            <tr>
                                <td>Room</td>
                                <td>
                                    <input
                                        value={roomNameEdit}
                                        type={"text"}
                                        autoComplete="off"
                                        autoCorrect="off"
                                        autoCapitalize="none"
                                        data-cy="room-input"
                                        onChange={(e) =>
                                            setRoomNameEdit(e.currentTarget.value)
                                        }
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>Password</td>
                                <td>
                                    <input
                                        value={roomPasswordEdit}
                                        type={"text"}
                                        autoComplete="off"
                                        autoCorrect="off"
                                        autoCapitalize="none"
                                        className="fakePassword"
                                        data-cy="password-input"
                                        onChange={(e) =>
                                            setRoomPasswordEdit(e.currentTarget.value)
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
