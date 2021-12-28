import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { TryLogin, UpdateRoomName } from "../actions";

function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

import ico_sync_alt from 'data-url:../static/sync-alt.svg';
import ico_sign_in_alt from 'data-url:../static/sign-in-alt.svg';

export const Login = ({ state }: { state: State }): VNode => (
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
                            <img class={"ico loading"} src={ico_sync_alt} />
                        )}
                    </span>
                ) : (
                    <span>
                        Enter Room <img class={"ico"} src={ico_sign_in_alt} />
                    </span>
                )}
            </button>
        </div>
    </Screen>
);
