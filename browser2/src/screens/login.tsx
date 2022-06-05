import h from "hyperapp-jsx-pragma";
import { Screen } from "./_common";

function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

function TryLogin(state: State, event: SubmitEvent): State {
    event.preventDefault();
    return {
        ...state,
        room_name: state.room_name_edit.toLowerCase().trim(),
    };
}

export const Login = ({ state }: { state: State }): VNode => (
    <Screen state={state} className={"login"} title={"Welcome to KaraKara"}>
        <div class={"flex-center"}>
            <form onsubmit={TryLogin}>
                <input
                    type={"text"}
                    placeholder={"Room Name"}
                    value={state.room_name_edit}
                    oninput={(state: State, event: FormInputEvent): State => ({
                        ...state,
                        room_name_edit: event.target.value,
                    })}
                    required={true}
                />
                <button disabled={!state.room_name_edit.trim() || state.loading}>
                    {state.loading ? (
                        <span>
                            Loading Tracks{" "}
                            {state.download_size ? (
                                percent(state.download_done, state.download_size)
                            ) : (
                                <i class={"loading fas fa-sync-alt"} />
                            )}
                        </span>
                    ) : (
                        <span>
                            Enter Room <i class={"fas fa-sign-in-alt"} />
                        </span>
                    )}
                </button>
            </form>
        </div>
    </Screen>
);
