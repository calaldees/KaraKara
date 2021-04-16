import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { TryLogin, UpdateRoomName } from "../actions";

function percent(a, b) {
    return (a / b) * 100 + "%";
}

export const Login = ({ state }: { state: State }) => (
    <Screen state={state} className={"login"} title={"Welcome to KaraKara"}>
        <div class={"flex-center"}>
            <input
                type={"text"}
                placeholder={"Room Name"}
                value={state.room_name_edit}
                oninput={UpdateRoomName()}
                disabled={state.loading}
            />
            <button
                onclick={TryLogin()}
                disabled={!state.room_name_edit || state.loading}
            >
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
        </div>
    </Screen>
);
