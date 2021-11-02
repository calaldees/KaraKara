import h from "hyperapp-jsx-pragma";
import { HideSettings } from "../actions";

export const SettingsMenu = ({ state }: { state: State }): VNode => (
    <div class={"settings"}>
        <div>
            <h2
                onclick={function (state) {
                    console.log(state);
                    (window as any).state = state;
                    return state;
                }}
            >
                Settings
            </h2>
            <table>
                <tr>
                    <td>Server</td>
                    <td>
                        <input
                            value={state.root_edit}
                            type={"text"}
                            oninput={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    root_edit: event.target.value,
                                } as State)
                            }
                            onchange={(state: State, event: FormInputEvent) =>
                                ({ ...state, root: state.root_edit } as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td>Password</td>
                    <td>
                        <input
                            value={state.room_password_edit}
                            type={"password"}
                            oninput={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    room_password_edit: event.target.value,
                                } as State)
                            }
                            onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    room_password: state.room_password_edit,
                                } as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td>Booth Mode</td>
                    <td>
                        <input
                            checked={state.booth}
                            type={"checkbox"}
                            onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    booth: !state.booth,
                                } as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td colspan={2}>
                        <button onclick={HideSettings()}>Close</button>
                    </td>
                </tr>
            </table>
        </div>
    </div>
);
