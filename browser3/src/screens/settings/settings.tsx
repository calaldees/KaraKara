import { useCallback, useContext, useState } from "react";

import { BackToExplore, Screen } from "@/components";
import { useApi } from "@/hooks/api";
import { RoomContext } from "@/providers/room";
import { copy_type } from "@/utils";

function removeTypes(
    roomSettings: Record<string, any>,
): Record<string, string> {
    const roomSettingsUntyped: Record<string, string> = {};
    for (const key of Object.keys(roomSettings)) {
        roomSettingsUntyped[key] = "" + (roomSettings[key] ?? "");
    }
    return roomSettingsUntyped;
}

export function RoomSettings(): React.ReactElement {
    const { settings: roomSettings } = useContext(RoomContext);
    // Whenever server-side settings change, change the key,
    // which will totally reset the edit state.
    return (
        <RoomSettingsInternal
            key={JSON.stringify(roomSettings)}
            roomSettings={roomSettings}
        />
    );
}

function RoomSettingsInternal({
    roomSettings,
}: {
    roomSettings: Record<string, any>;
}) {
    const [roomSettingsEdit, setRoomSettingsEdit] = useState<
        Record<string, string>
    >(removeTypes(roomSettings));
    const { request, loading } = useApi();

    // when user types in a textbox, update the string:string
    const update = useCallback(
        (key: string, value: string) => {
            const newSettings = { ...roomSettingsEdit };
            newSettings[key] = value;
            setRoomSettingsEdit(newSettings);
        },
        [roomSettingsEdit],
    );

    // when saving settings, convert the string:string into string:any
    const saveSettings = useCallback(
        (event: any) => {
            event.preventDefault();
            const roomSettingsTyped: Record<string, any> = {};
            for (const key of Object.keys(roomSettings)) {
                roomSettingsTyped[key] = copy_type(
                    roomSettings[key],
                    roomSettingsEdit[key],
                );
            }
            request({
                notify: "Saving settings...",
                notify_ok: "Settings saved!",
                function: "settings",
                options: {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(roomSettingsTyped),
                },
            });
        },
        [roomSettings, roomSettingsEdit, request],
    );

    const buttons = (
        <footer>
            <div className={"buttons"}>
                <button
                    onClick={saveSettings}
                    type="button"
                    data-cy="save-settings-button"
                    disabled={loading}
                >
                    Save
                </button>
            </div>
        </footer>
    );

    return (
        <Screen
            className={"settings"}
            navLeft={<BackToExplore />}
            title={"Room Settings"}
            //navRight={}
            footer={buttons}
        >
            <form onSubmit={saveSettings}>
                {Object.entries(roomSettingsEdit).map(([key, value]) => (
                    <p key={key}>
                        {key.replace(/_/g, " ")}:
                        <br />
                        <input
                            type={"text"}
                            name={key}
                            data-setting={key}
                            value={value ?? ""}
                            onChange={(e) => update(key, e.currentTarget.value)}
                        />
                    </p>
                ))}
            </form>
        </Screen>
    );
}
