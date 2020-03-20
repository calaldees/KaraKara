import {h} from "hyperapp";
import {Screen} from "./base";
import { Http } from "hyperapp-fx";

function track_list_to_map(raw_list: Array<Track>) {
    let map = {};
    for(let i=0; i<raw_list.length; i++) {
        raw_list[i].attachments = [
            {
                "id": 18977,
                "location": "5/510549ce7604d0c03ad2d2b8a229efaf2f0d023276ff665ae517b64d59ac2916.jpg",
                "type": "image",
                "extra_fields": {}
            },
            {
                "id": 18981,
                "location": "8/8d8eb74c302749071f33de4fcf271de1598113f61fc5e612648f1a9278cc33e2.mp4",
                "type": "video",
                "extra_fields": {}
            },
            {
                "id": 18982,
                "location": "3/39377ba11786fc97e3cbfb2e78b6f0a8da57176463863f186d9fffa2226189f4.mp4",
                "type": "preview",
                "extra_fields": {}
            },
            {
                "id": 18983,
                "location": "0/0f147e0508ca3c35d0c4956dd4a2ed2f49e17670796ab54a4f00a5f0ed36c889.srt",
                "type": "srt",
                "extra_fields": {}
            },
            {
                "id": 18984,
                "location": "e/ef11bf2dc5de1e6983242697ea35d76b9e2d080fd05ab4956dadf13cf198335a.txt",
                "type": "tags",
                "extra_fields": {}
            }
        ];
        raw_list[i].lyrics = "blah blah";
        map[raw_list[i].id] = raw_list[i];
    }
    return map;
}

// TODO: set up websocket listener, refresh queue on each message
export const Login = ({state}: {state: State}) => (
    <Screen
        state={state}
        className={"login"}
        title={"Welcome to KaraKara"}
    >
        <div class={"flex-center"}>
            <input
                type={"text"}
                placeholder={"Room Name"}
                value={state.tmp_queue_id}
                oninput={(state: State, event: FormInputEvent) => ({
                    ...state, tmp_queue_id: event.target.value,
                } as State)}
                disabled={state.loading}
            />
            <button
                onclick={(state: State) => [
                    {...state, loading: true} as State,
                    Http({
                        url: "/track_list_full.json",
                        action: (state, response) => ({
                            ...state,
                            queue_id: state.tmp_queue_id,
                            loading: false,
                            track_list: track_list_to_map(response.data.list),
                        }),
                        error: (state, response) => ({
                            ...state,
                            queue_id: null,
                            loading: false,
                            notification: ""+response,
                        })
                    }),
                    Http({
                        url: state.root + "/queue/" + state.tmp_queue_id + "/queue_items.json",
                        action: (state, response) => ({...state, queue: response.data.queue}),
                        error: (state, response) => ({...state, notification: ""+response, queue_id: null})
                    })
                ]}
                disabled={state.loading}
            >
                {state.loading ?
                    <span>Loading Tracks <i class={"loading fas fa-sync-alt"}/></span> :
                    <span>Enter Room <i class={"fas fa-sign-in-alt"}/></span>
                }
            </button>
        </div>
    </Screen>
);