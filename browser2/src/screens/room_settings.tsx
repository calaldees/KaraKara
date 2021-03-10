import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./base";
import { SaveSettings } from "../effects";
import { UpdateSettings } from "../actions";

const SettingsButtons = ({ state }: { state: State }) => (
    <footer>
        <div class={"buttons"}>
            <button onclick={SaveSettings} disabled={state.loading}>
                Save
            </button>
        </div>
    </footer>
);

function val2str(val: any): string {
    if (Array.isArray(val)) {
        return "[" + val.join(",") + "]";
    }
    return val;
}

export const RoomSettings = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"room_settings"}
        navLeft={<BackToExplore />}
        title={"Room Settings"}
        //navRight={}
        footer={<SettingsButtons state={state} />}
    >
        {Object.entries(state.settings).map(([key, value]) => (
            <p>
                {key}:
                <br />
                <input
                    name={key}
                    value={val2str(value)}
                    onchange={UpdateSettings}
                />
            </p>
        ))}
    </Screen>
);
