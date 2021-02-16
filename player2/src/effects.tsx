/**
 * Effects = things we send into the world (websocket packet,
 * http request, etc) and we'll update the app state some time
 * later, after we get a response.
 */
import { Http } from "hyperapp-fx";
import { MQTTPublish } from "hyperapp-mqtt";
import { http2ws } from "./utils";
import { AddLyricsToNewQueue } from "./actions";

export function SendCommand(state: State, command: string) {
    console.log("mqtt_send(", "commands", command, ")");
    return MQTTPublish({
        url: http2ws(state.root) + "/mqtt",
        username: state.room_name,
        password: state.room_password,
        topic: "karakara/room/" + state.room_name + "/commands",
        payload: command,
    });
}

export function FetchRandomImages(state: State) {
    return Http({
        url:
            state.root +
            "/queue/" +
            state.room_name +
            "/random_images.json?count=25",
        action(state: State, response): State {
            return {
                ...state,
                images: response.data.images.map((fn, n) => ({
                    filename: fn,
                    x: n / response.data.images.length,
                    delay: Math.random() * 10,
                })),
            };
        },
        error(state: State, response) {
            console.log("Error fetching random images:", response);
            return { ...state };
        },
    });
}

export function CheckSettings(state: State) {
    return Http({
        url: state.root + "/queue/" + state.room_name + "/settings.json",
        action(state: State, response) {
            return {
                ...state,
                settings: { ...state.settings, ...response.data.settings },
            };
        },
        error(state: State, response) {
            console.log("Error checking settings:", response);
            return { ...state };
        },
    });
}

export function CheckQueue(state: State) {
    return Http({
        url: state.root + "/queue/" + state.room_name + "/queue_items.json",
        action(state: State, response) {
            return AddLyricsToNewQueue(state, response.data.queue);
        },
        error(state: State, response) {
            console.log("Error checking queue:", response);
            return { ...state };
        },
    });
}

export function SetTrackState(state: State, value: string) {
    return Http({
        url: state.root + "/queue/" + state.room_name + "/queue_items.json",
        options: {
            method: "PUT",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                "queue_item.id": state.queue[0].id.toString(),
                status: value,
                uncache: new Date().getTime().toString(),
            }),
        },
        // we could `return [state, CheckQueue(state)]` to check for a new queue
        // as soon as we've updated the status, but right now the call to
        // `PUT queue_items.json` will trigger a `queue` update over the websocket
        // from the server so we'll check as soon as we see that already.
        action(state: State, response) {
            return state;
        },
        error(state: State, response) {
            console.log("Error setting track state:", response);
            return { ...state };
        },
    });
}
