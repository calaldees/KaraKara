import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { Http } from "hyperapp-fx";
import { DisplayResponseMessage } from "../effects";

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
                value={state.queue_id}
                onchange={(state: State, event: FormInputEvent) =>
                    ({
                        ...state,
                        queue_id: event.target.value.toLowerCase(),
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
                            state.queue_id +
                            "/track_list.json",
                        action: (state, response) => ({
                            ...state,
                            queue_id: state.queue_id,
                            loading: false,
                            track_list: track_list_to_map(response.data.list),
                        }),
                        error: (state, response) => [
                            {
                                ...state,
                                queue_id: "",
                                loading: false,
                            },
                            [DisplayResponseMessage, response],
                        ],
                    }),
                    Http({
                        url:
                            state.root +
                            "/queue/" +
                            state.queue_id +
                            "/queue_items.json",
                        action: (state, response) => ({
                            ...state,
                            queue: response.data.queue,
                        }),
                        error: (state, response) => [
                            {...state, queue_id: ""},
                            [DisplayResponseMessage, response],
                        ],
                    }),
                ]}
                disabled={(!state.queue_id) || state.loading}
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
