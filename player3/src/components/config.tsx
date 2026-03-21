import { useFullscreen } from "@mantine/hooks";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { SubmitEvent, useCallback, useContext, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

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
        wakeLock,
        underscan,
        setUnderscan,
    } = useContext(ClientContext);
    const { toggle: toggleFullscreen, fullscreen } = useFullscreen();
    const { now, offset } = useContext(ServerTimeContext);
    const [roomNameEdit, setRoomNameEdit] = useState(roomName ?? "");
    const [roomPasswordEdit, setRoomPasswordEdit] = useState(roomPassword);
    const navigate = useNavigate();

    const onSubmit = useCallback(
        (e: SubmitEvent) => {
            e.preventDefault();
            if (roomNameEdit !== roomName) {
                void navigate("/" + roomNameEdit.toLowerCase());
            }
            setRoomPassword(roomPasswordEdit.toLowerCase());
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
                                        maxLength={16}
                                        pattern={"[a-z0-9]+"}
                                        autoComplete="off"
                                        autoCorrect="off"
                                        autoCapitalize="none"
                                        onInvalid={(e) => {
                                            e.currentTarget.setCustomValidity("Room name must be a-z, 0-9");
                                        }}
                                        onChange={(e) => {
                                            e.currentTarget.setCustomValidity("");
                                            setRoomNameEdit(e.currentTarget.value)
                                        }}
                                        required={true}
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
                                        onChange={(e) =>
                                            setRoomPasswordEdit(
                                                e.currentTarget.value,
                                            )
                                        }
                                        required={true}
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
                            {"requestFullscreen" in document.body && (
                                <tr>
                                    <td>Fullscreen</td>
                                    <td>
                                        <input
                                            checked={fullscreen}
                                            type={"checkbox"}
                                            onChange={() => void toggleFullscreen()}
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
                                            setUnderscan(e.currentTarget.value)
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
