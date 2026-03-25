import { useCallback, useContext, useState } from "react";

import { BackOr, ButtonRow, Screen } from "@/components";
import { useApi } from "@/hooks/api";
import { PageContext } from "@/providers/page";
import { RoomContext } from "@/providers/room";
import type { Settings } from "@/types";
import { copy_type } from "@/utils";

function removeTypes(roomSettings: Settings): Record<string, string> {
    const roomSettingsUntyped: Record<string, string> = {};
    for (const key of Object.keys(roomSettings)) {
        roomSettingsUntyped[key] = "" + ((roomSettings as any)[key] ?? "");
    }
    return roomSettingsUntyped;
}

function RoomSettings(): React.ReactElement {
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

export default RoomSettings;

function RoomSettingsInternal({ roomSettings }: { roomSettings: Settings }) {
    const { roomName } = useContext(PageContext);
    const [roomSettingsEdit, setRoomSettingsEdit] = useState<
        Record<string, string>
    >(() => removeTypes(roomSettings));
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
            const roomSettingsTyped: any = {};
            for (const key of Object.keys(roomSettings)) {
                roomSettingsTyped[key] = copy_type(
                    (roomSettings as any)[key],
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
        <ButtonRow>
            <button
                onClick={saveSettings}
                type="button"
                data-cy="save-settings-button"
                disabled={loading}
            >
                Save
            </button>
        </ButtonRow>
    );

    return (
        <Screen
            className={"settings"}
            navLeft={<BackOr to={`/${roomName}`} />}
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
