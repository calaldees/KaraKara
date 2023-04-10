import { useContext, useEffect, useState } from "react";
import { BackToExplore, Screen } from "./_common";
import { copy_type } from "../utils";
import { RoomContext } from "../providers/room";
import { useApi } from "../hooks/api";

export function RoomSettings(): React.ReactElement {
    const { settings: roomSettings } = useContext(RoomContext);
    const [roomSettingsEdit, setRoomSettingsEdit] = useState(roomSettings);
    const [saving, setSaving] = useState(false);
    const { request } = useApi();

    useEffect(() => {
        setRoomSettingsEdit(roomSettings);
    }, [roomSettings]);

    function update(key: string, value: string) {
        let newSettings = { ...roomSettingsEdit };
        newSettings[key] = copy_type(roomSettings[key], value);
        setRoomSettingsEdit(newSettings);
    }

    function saveSettings(event: any) {
        event.preventDefault();
        setSaving(true);
        request({
            notify: "Saving settings...",
            notify_ok: "Settings saved!",
            function: "settings",
            options: {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(roomSettingsEdit),
            },
            onAction: () => setSaving(false),
        });
    }

    const buttons = (
        <footer>
            <div className={"buttons"}>
                <button onClick={saveSettings} disabled={saving}>
                    Save
                </button>
            </div>
        </footer>
    );

    return (
        <Screen
            className={"room_settings"}
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
                            value={value ?? ""}
                            onChange={(e) => update(key, e.target.value)}
                        />
                    </p>
                ))}
            </form>
        </Screen>
    );
}
