/**
 * Effects = things we send into the world (websocket packet,
 * http request, etc) and we'll update the app state some time
 * later, after we get a response.
 */
import {Http, WebSocketSend} from "hyperapp-fx";
import {get_lyrics, http2ws} from "./utils";
import {SetImages, SetQueue} from "./actions";

export function SendCommand(state: State, command: string) {
    console.log("websocket_send(" + command + ")");
    return WebSocketSend({
        url: http2ws(state.root) + "/ws/",
        data: command,
    })
}

export function FetchRandomImages(state: State) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/random_images.json?count=25",
        action: SetImages,
        error: (state, response) => ({...state})
    });
}

export function CheckSettings(state: State) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/settings.json",
        action: (state, response) => ({
            ...state, settings: {...state.settings, ...response.data.settings}
        }),
        error: (state, response) => ({...state})
    });
}

export function CheckQueue(state: State) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
        action: function(state, response) {
            function merge_lyrics(item) {
                item.track.srt_lyrics = get_lyrics(state, item.track);
                return item;
            }
            let queue_with_lyrics = response.data.queue.map((item) => merge_lyrics(item));
            return SetQueue(state, queue_with_lyrics);
        },
        error: (state, response) => ({...state})
    });
}

export function SetTrackState(state: State, value: string) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
        method: "PUT",
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({
            "queue_item.id": state.queue[0].id.toString(),
            "status": value,
            "uncache": new Date().getTime().toString(),
        }),
        action: (state, response) => [state, CheckQueue],
        error: (state, response) => ({...state})
    });
}
