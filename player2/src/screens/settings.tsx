import { h } from "hyperapp";

export const SettingsMenu = ({ state }: { state: State }) => (
    <div className={"settings"}>
        <div>
            <h2
                onclick={function(state) {
                    console.log(state);
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
                            onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    root: event.target.value,
                                } as State)
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
                            onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    queue_id: event.target.value,
                                } as State)
                            }
                        />
                    </td>
                </tr>
                <tr>
                    <td>Podium</td>
                    <td>
                        <input
                            checked={state.is_podium}
                            type={"checkbox"}
                            onchange={(state: State, event: FormInputEvent) =>
                                ({
                                    ...state,
                                    is_podium: !state.is_podium,
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
                                onchange={function(
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
