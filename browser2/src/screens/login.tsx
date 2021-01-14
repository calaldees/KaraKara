import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { Http } from "hyperapp-fx";
import { DisplayErrorResponse } from "../effects";

function track_list_to_map(raw_list: Array<Track>) {
    let map = {};
    for (let i = 0; i < raw_list.length; i++) {
        map[raw_list[i].id] = raw_list[i];
    }
    return map;
}

export const Login = ({ state }: { state: State }) => (
    <Screen state={state} className={"login"} title={"Welcome to KaraKara"}>
        <div class={"flex-center"}>
            <input
                type={"text"}
                placeholder={"Room Name"}
                value={state.tmp_queue_id}
                oninput={(state: State, event: FormInputEvent) =>
                    ({
                        ...state,
                        tmp_queue_id: event.target.value,
                    } as State)
                }
                disabled={state.loading}
            />
            <button
                onclick={(state: State) => [
                    { ...state, loading: true } as State,
                    Http({
                        url:
                            state.root +
                            "/queue/" +
                            state.tmp_queue_id +
                            "/track_list.json",
                        action: (state, response) => ({
                            ...state,
                            queue_id: state.tmp_queue_id,
                            loading: false,
                            track_list: track_list_to_map(response.data.list),
                        }),
                        error: (state, response) => [
                            {
                                ...state,
                                queue_id: null,
                                loading: false,
                            },
                            DisplayErrorResponse(response),
                        ],
                    }),
                    Http({
                        url:
                            state.root +
                            "/queue/" +
                            state.tmp_queue_id +
                            "/queue_items.json",
                        action: (state, response) => ({
                            ...state,
                            queue: response.data.queue,
                        }),
                        error: (state, response) => ({
                            ...state,
                            notification: "" + response,
                            queue_id: null,
                        }),
                    }),
                ]}
                disabled={state.loading}
            >
                {state.loading ? (
                    <span>
                        Loading Tracks <i class={"loading fas fa-sync-alt"} />
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
