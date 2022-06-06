import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import { ApiRequest } from "../effects";
import { flatten_settings } from "../utils";


///////////////////////////////////////////////////////////////////////
// Actions

function UpdateSettings(
    state: State,
    event: FormInputEvent,
): Dispatchable {
    if (Array.isArray(state.settings[event.target.name])) {
        state.settings[event.target.name] = event.target.value.split(",");
    } else {
        state.settings[event.target.name] = event.target.value;
    }
    return state;
}

const SaveSettings = (state: State): Dispatchable => [
    { ...state },
    ApiRequest({
        title: "Saving settings...",
        function: "settings",
        state: state,
        options: {
            method: "PUT",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(flatten_settings(state.settings)),
        },
        // action: (state, response) => [{ ...state }],
    }),
];


///////////////////////////////////////////////////////////////////////
// Views

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
