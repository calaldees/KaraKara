import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import { ApiRequest } from "../effects";


///////////////////////////////////////////////////////////////////////
// Actions

function UpdateSettings(
    state: State,
    event: FormInputEvent,
): Dispatchable {
    if (Array.isArray(state.settings[event.target.name])) {
        state.settings[event.target.name] = event.target.value.split(",");
    } else if(typeof state.settings[event.target.name] == 'number') {
        state.settings[event.target.name] = parseFloat(event.target.value);
    } else {
        state.settings[event.target.name] = event.target.value;
    }
    return state;
}

const SaveSettings = (state: State, event: SubmitEvent): Dispatchable => {
    event.preventDefault();
    return [
        { ...state },
        ApiRequest({
            title: "Saving settings...",
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
        </form>
    </Screen>
);
