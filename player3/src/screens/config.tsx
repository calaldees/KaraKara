import { useNavigate, useParams } from "react-router-dom";
import { ClientContext } from "../providers/client";
import { FormEvent, useContext, useState } from "react";
import { ServerContext } from "../providers/server";

export function ConfigMenu() {
    const { roomName } = useParams();
    const {
        root,
        setRoot,
        roomPassword,
        setRoomPassword,
        podium,
        setPodium,
        blankPodium,
        setBlankPodium,
        setShowSettings,
        fullscreen,
        setFullscreen,
        wakeLock,
    } = useContext(ClientContext);
    const { now } = useContext(ServerContext);
    const [rootEdit, setRootEdit] = useState(root);
    const [roomNameEdit, setRoomNameEdit] = useState(roomName ?? "");
    const [roomPasswordEdit, setRoomPasswordEdit] = useState(roomPassword);
    const navigate = useNavigate();

    function onSubmit(e: FormEvent) {
        e.preventDefault();
        setRoot(rootEdit);
        if (roomNameEdit != roomName) {
            navigate("/" + roomNameEdit);
        }
        setRoomPassword(roomPasswordEdit);
        setShowSettings(false);
    }

    return (
        <div className={"settings"}>
            <div>
                <h2>App Settings</h2>
                <form onSubmit={onSubmit}>
                    <table>
                        <tbody>
                            <tr>
                                <td>Server</td>
                                <td>
                                    <input
                                        value={rootEdit}
                                        type={"text"}
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
                                        onChange={(e) => setPodium(!podium)}
                                    />
                                </td>
                            </tr>
                            {podium && <tr>
                                <td>Blank Podium</td>
                                <td>
                                    <input
                                        checked={blankPodium}
                                        type={"checkbox"}
                                        onChange={(e) => setBlankPodium(!blankPodium)}
                                    />
                                </td>
                            </tr>}
                            {document.body.requestFullscreen && (
                                <tr>
                                    <td>Fullscreen</td>
                                    <td>
                                        <input
                                            checked={fullscreen}
                                            type={"checkbox"}
                                            onChange={(e) => {
                                                if (fullscreen) {
                                                    document.exitFullscreen();
                                                } else {
                                                    document.body.requestFullscreen();
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
                                        value={Date.now() / 1000 - now}
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td>WakeLock</td>
                                <td>
                                    <input
                                        disabled={true}
                                        value={wakeLock}
                                    />
                                </td>
                            </tr>
                            <tr>
                                <td colSpan={2}>
                                    <button>Close</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </form>
            </div>
        </div>
    );
}
