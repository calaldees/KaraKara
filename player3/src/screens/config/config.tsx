import { FormEvent, useCallback, useContext, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ServerTimeContext } from "@shish2k/react-use-servertime";

import { ClientContext } from "@/providers/client";

import "./config.scss";

export function ConfigMenu() {
    const { roomName } = useParams();
    const {
        roomPassword,
        setRoomPassword,
        podium,
        setPodium,
        setShowSettings,
        fullscreen,
        setFullscreen,
        wakeLock,
        underscan,
        setUnderscan,
    } = useContext(ClientContext);
    const { now, offset } = useContext(ServerTimeContext);
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
            navigate,
            roomName,
            roomNameEdit,
            roomPasswordEdit,
            setRoomPassword,
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
                                        onChange={(e) =>
                                            setRoomPasswordEdit(e.target.value)
                                        }
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>Podium Mode</td>
                                <td>
                                    <input
                                        checked={podium}
                                        type={"checkbox"}
                                        onChange={(_) => setPodium(!podium)}
                                    />
                                </td>
                            </tr>
                            {document.body.requestFullscreen && (
                                <tr>
                                    <td>Fullscreen</td>
                                    <td>
                                        <input
                                            checked={fullscreen}
                                            type={"checkbox"}
                                            onChange={(_) => {
                                                if (fullscreen) {
                                                    void document.exitFullscreen();
                                                } else {
                                                    void document.body.requestFullscreen();
                                                }
                                                setFullscreen(!fullscreen);
                                            }}
                                        />
                                    </td>
                                </tr>
                            )}
                            <tr>
                                <td
                                    style={{
                                        background: [
                                            "red",
                                            "green",
                                            "yellow",
                                            "purple",
                                            "orange",
                                            "blue",
                                        ][Math.round(now) % 6],
                                    }}
                                >
                                    Sync
                                </td>
                                <td>
                                    <input
                                        disabled={true}
                                        value={`${now.toFixed(
                                            3,
                                        )} (${offset.toFixed(3)})`}
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>WakeLock</td>
                                <td>
                                    <input disabled={true} value={wakeLock} />
                                </td>
                            </tr>
                            <tr>
                                <td>Underscan</td>
                                <td>
                                    <input
                                        value={underscan}
                                        onChange={(e) =>
                                            setUnderscan(e.target.value)
                                        }
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td colSpan={2}>
                                    <button type="submit">Close</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </form>
            </div>
        </div>
    );
}
