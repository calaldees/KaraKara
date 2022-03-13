import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { TryLogin } from "../actions";

function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

export const Login = ({ state }: { state: State }): VNode => (
    <Screen state={state} className={"login"} title={"Welcome to KaraKara"}>
        <div class={"flex-center"}>
            <form onsubmit={TryLogin()}>
                <input
                    type={"text"}
                    placeholder={"Room Name"}
                    value={state.room_name}
                    oninput={(state, event) => ({
                        ...state,
                        room_name: event.target.value.toLowerCase().trim(),
                    })}
                    disabled={state.loading}
                    required={true}
                />
                <button disabled={!state.room_name || state.loading}>
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
