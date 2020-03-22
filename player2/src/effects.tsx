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
        error(state, response) {console.log("Error fetching random images:", response); return {...state}}
    });
}

export function CheckSettings(state: State) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/settings.json",
        action(state, response) {
            return {...state, settings: {...state.settings, ...response.data.settings}}
        },
        error(state, response) {console.log("Error checking settings:", response); return {...state}}
    });
}

export function CheckQueue(state: State) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
        action(state, response) {
            function merge_lyrics(item) {
                item.track.srt_lyrics = get_lyrics(state, item.track);
                return item;
            }
            let queue_with_lyrics = response.data.queue.map((item) => merge_lyrics(item));
            return SetQueue(state, queue_with_lyrics);
        },
        error(state, response) {console.log("Error checking queue:", response); return {...state}}
    });
}

export function SetTrackState(state: State, value: string) {
    return Http({
        url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
        options: {
            method: "PUT",
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({
                "queue_item.id": state.queue[0].id.toString(),
                "status": value,
                "uncache": new Date().getTime().toString(),
            })
        },
        // we could `return [state, CheckQueue(state)]` to check for a new queue
        // as soon as we've updated the status, but right now the call to
        // `PUT queue_items.json` will trigger `queue_updated` over the websocket
        // from the server so we'll check as soon as we see that already.
        action(state, response) {return state},
        error(state, response) {console.log("Error setting track state:", response); return {...state}}
    });
}
