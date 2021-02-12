import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { ApiRequest } from "../effects";

function track_list_to_map(raw_list: Array<Track>) {
    let map = {};
    for (let i = 0; i < raw_list.length; i++) {
        map[raw_list[i].id] = raw_list[i];
    }
    return map;
}

const FetchTrackList = (state) =>
    ApiRequest({
        function: "track_list",
        state: state,
        progress: (state, done, size) => [
            {
                ...state,
                download_done: done,
                download_size: size,
            },
        ],
        action: (state, response) =>
            response.status == "ok"
                ? {
                      ...state,
                      room_name: state.room_name_edit,
                      session_id: response.identity.id,
                      track_list: track_list_to_map(response.data.list),
                  }
                : {
                      ...state,
                      room_name_edit: "",
                  },
    });

const LoginThenFetchTrackList = (state) =>
    ApiRequest({
        function: "admin",
        state: state,
        options: {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                password: state.room_password,
            }),
        },
        action: (state, response) =>
            response.status == "ok" ? [state, FetchTrackList(state)] : state,
    });

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
                oninput={(state: State, event: FormInputEvent) =>
                    ({
                        ...state,
                        room_name_edit: event.target.value.toLowerCase(),
                    } as State)
                }
                disabled={state.loading}
            />
            <button
                onclick={(state: State) => [
                    state,
                    state.room_password
                        ? LoginThenFetchTrackList(state)
                        : FetchTrackList(state),
                ]}
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
