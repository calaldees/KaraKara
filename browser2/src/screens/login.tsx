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
                    { ...state, loading: true } as State,
                    Http({
                        url:
                            state.root +
                            "/queue/" +
                            state.room_name_edit +
                            "/track_list.json",
                        action: (state, response) => ({
                            ...state,
                            room_name: state.room_name_edit,
                            loading: false,
                            track_list: track_list_to_map(response.data.list),
                        }),
                        error: (state, response) => [
                            {
                                ...state,
                                room_name_edit: "",
                                loading: false,
                            },
                            [DisplayResponseMessage, response],
                        ],
                    }),
                ]}
                disabled={(!state.room_name_edit) || state.loading}
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
