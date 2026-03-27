import { useFullscreen } from "@mantine/hooks";
import { type SubmitEvent, useCallback, useContext, useState } from "react";

import { ClientContext } from "@/providers/client";
import { PageContext } from "@/providers/page";

import styles from "./ConfigMenu.module.scss";

export function ConfigMenu(): React.ReactElement {
    const { roomName, navigate } = useContext(PageContext);
    const { roomPassword, setRoomPassword, booth, setBooth, setShowSettings } =
        useContext(ClientContext);
    const { toggle: toggleFullscreen, fullscreen } = useFullscreen();
    const [roomNameEdit, setRoomNameEdit] = useState(roomName ?? "");
    const [roomPasswordEdit, setRoomPasswordEdit] = useState(roomPassword);

    const onSubmit = useCallback(
        (e: SubmitEvent) => {
            e.preventDefault();
            if (roomNameEdit !== roomName) {
                void navigate(`/${roomNameEdit}`);
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
        <div className={styles.config}>
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
                                        data-cy="room-input"
                                        onChange={(e) => {
                                            setRoomNameEdit(
                                                e.currentTarget.value
                                                    .toLowerCase()
                                                    .replace(/[^a-z0-9]/g, ""),
                                            );
                                        }}
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
                                        className={styles.fakePassword}
                                        data-cy="password-input"
                                        onChange={(e) =>
                                            setRoomPasswordEdit(
                                                e.currentTarget.value.toLowerCase(),
                                            )
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
                            {"requestFullscreen" in document.body && (
                                <tr>
                                    <td>Fullscreen</td>
                                    <td>
                                        <input
                                            checked={fullscreen}
                                            type={"checkbox"}
                                            onChange={() =>
                                                void toggleFullscreen()
                                            }
                                        />
                                    </td>
                                </tr>
                            )}
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
