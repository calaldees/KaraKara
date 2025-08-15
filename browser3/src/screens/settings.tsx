import { useContext, useEffect, useState } from "react";
import { BackToExplore, Screen } from "./_common";
import { copy_type } from "../utils";
import { RoomContext } from "../providers/room";
import { useApi } from "../hooks/api";

export function RoomSettings(): React.ReactElement {
    const { settings: roomSettings } = useContext(RoomContext);
    const [roomSettingsEdit, setRoomSettingsEdit] = useState<
        Record<string, string>
    >({});
    const { request, loading } = useApi();

    // on first loading this screen, and whenever server-side settings change,
    // convert the string:any settings into string:string
    useEffect(() => {
        const roomSettingsUntyped: Record<string, string> = {};
        for (const key of Object.keys(roomSettings)) {
            roomSettingsUntyped[key] = "" + (roomSettings[key] ?? "");
        }
        setRoomSettingsEdit(roomSettingsUntyped);
    }, [roomSettings]);

    // when user types in a textbox, update the string:string
    function update(key: string, value: string) {
        const newSettings = { ...roomSettingsEdit };
        newSettings[key] = value;
        setRoomSettingsEdit(newSettings);
    }

    // when saving settings, convert the string:string into string:any
    function saveSettings(event: any) {
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
    }

    const buttons = (
        <footer>
            <div className={"buttons"}>
                <button
                    onClick={saveSettings}
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
                            data-setting={key}
                            value={value ?? ""}
                            onChange={(e) => update(key, e.target.value)}
                        />
                    </p>
                ))}
            </form>
        </Screen>
    );
}
