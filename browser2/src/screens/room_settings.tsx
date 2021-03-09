import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./base";
import { ApiRequest } from "../effects";

export function UpdateSettings(state: State, event) {
    state.settings[event.target.name] = event.target.value;
    return state;
}

export function SaveSettings(state: State) {
    return [
        { ...state },
        ApiRequest({
            title: "Saving setting...",
            function: "settings",
            state: state,
            options: {
                method: "PUT",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams(state.settings),
            },
            // action: (state, response) => [{ ...state }],
        }),
    ];
}

const SettingsButtons = (state) => (
    <footer>
        <div class={"buttons"}>
            <button
                onclick={SaveSettings}
                // disabled={state.loading}
            >
                Save
            </button>
        </div>
    </footer>
);

export const RoomSettings = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"room_settings"}
        navLeft={<BackToExplore />}
        title={"Room Settings"}
        //navRight={}
        footer={<SettingsButtons settings={state.settings} />}
    >
        {Object.entries(state.settings).map(([key, value]) => (
            <p>
                {key}:
                <br />
                <input name={key} value={value} onchange={UpdateSettings} />
            </p>
        ))}
    </Screen>
);
