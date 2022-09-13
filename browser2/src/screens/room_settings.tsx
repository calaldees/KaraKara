import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import { ApiRequest } from "../effects";
import { copy_type } from "../utils";


///////////////////////////////////////////////////////////////////////
// Actions

function UpdateSettings(
    state: State,
    event: FormInputEvent,
): Dispatchable {
    var name = event.target.name;
    var value = event.target.value;
    state.settings[name] = copy_type(state.settings[name], value);
    return state;
}

const SaveSettings = (state: State, event: SubmitEvent): Dispatchable => {
    event.preventDefault();
    return [
        { ...state },
        ApiRequest({
            notify: "Saving settings...",
            notify_ok: "Settings saved!",
            function: "settings",
            state: state,
            options: {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(state.settings),
            },
            // action: (state, response) => [{ ...state }],
        }),
    ]
};


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
        <form onsubmit={SaveSettings}>
            {Object.entries(state.settings).map(([key, value]) => (
                <p>
                    {key.replace("_", " ")}:
                    <br />
                    <input
                        type={"text"}
                        name={key}
                        value={value}
                        onchange={UpdateSettings}
                    />
                </p>
            ))}
        </form>
    </Screen>
);
