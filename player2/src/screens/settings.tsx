import h from "hyperapp-jsx-pragma";

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
            <form onsubmit={(state) => ({
                ...state,
                show_settings: false,
            })}>
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
                        <td>Room</td>
                        <td>
                            <input
                                value={state.room_name_edit}
                                type={"text"}
                                oninput={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    room_name_edit: event.target.value,
                                } as State)
                                }
                                onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    room_name: state.room_name_edit,
                                } as State)
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
                        <td>Podium</td>
                        <td>
                            <input
                                checked={state.podium}
                                type={"checkbox"}
                                onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    podium: !state.podium,
                                } as State)
                                }
                            />
                        </td>
                    </tr>
                    {document.body.requestFullscreen && (
                        <tr>
                            <td>Fullscreen</td>
                            <td>
                                <input
                                    checked={state.fullscreen}
                                    type={"checkbox"}
                                    onchange={function (
                                        state: State,
                                        event: FormInputEvent,
                                    ) {
                                        if (state.fullscreen) {
                                            document.exitFullscreen();
                                        } else {
                                            document.body.requestFullscreen();
                                        }
                                        return {
                                            ...state,
                                            fullscreen: !state.fullscreen,
                                        };
                                    }}
                                />
                            </td>
                        </tr>
                    )}
                    <tr>
                        <td colspan={2}>
                            <button>Close</button>
                        </td>
                    </tr>
                </table>
            </form>
        </div>
    </div>
);
