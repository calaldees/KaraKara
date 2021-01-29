import h from "hyperapp-jsx-pragma";

export const SettingsMenu = ({ state }: { state: State }) => (
    <div class={"settings"}>
        <div>
            <h2
                onclick={function(state) {
                    console.log(state);
                    window.state = state;
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
                            value={state.root}
                            type={"text"}
                            oninput={(state: State, event: FormInputEvent) =>
                                ({...state, root_edit: event.target.value} as State)
                            }
                            onchange={(state: State, event: FormInputEvent) =>
                                ({...state, root: state.root_edit} as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td>Room</td>
                    <td>
                        <input
                            value={state.queue_id}
                            type={"text"}
                            oninput={(state: State, event: FormInputEvent) =>
                                ({...state, queue_id_edit: event.target.value} as State)
                            }
                            onchange={(state: State, event: FormInputEvent) =>
                                ({...state, queue_id: state.queue_id_edit} as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td>Password</td>
                    <td>
                        <input
                            value={state.queue_password}
                            type={"password"}
                            oninput={(state: State, event: FormInputEvent) =>
                                ({...state, queue_password_edit: event.target.value} as State)
                            }
                            onchange={(state: State, event: FormInputEvent) =>
                                ({...state, queue_password: state.queue_password_edit} as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td colspan={2}>
                        <button
                            onclick={state => ({
                                ...state,
                                show_settings: false,
                            })}
                        >
                            Close
                        </button>
                    </td>
                </tr>
            </table>
        </div>
    </div>
);
