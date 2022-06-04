import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import { SaveSettings } from "../effects";
import { UpdateSettings } from "../actions";

const SettingsButtons = ({ state }: { state: State }): VNode => (
    <footer>
        <div class={"buttons"}>
            <button onclick={SaveSettings} disabled={state.loading}>
                Save
            </button>
        </div>
    </footer>
);

export const RoomSettings = ({ state }: { state: State }): VNode => (
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
                {key.replace("karakara.", "")}:
                <br />
                <input
                    type={"text"}
                    name={key}
                    value={value}
                    onchange={UpdateSettings}
                />
            </p>
        ))}
    </Screen>
);
