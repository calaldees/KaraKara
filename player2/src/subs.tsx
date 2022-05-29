import {
    Dequeue,
    MarkTrackSkipped,
    Pause,
    Play,
    SeekBackwards,
    SeekForwards,
    Stop,
    UpdateQueue,
} from "./actions";
import { ApiRequest, SendCommand } from "./effects";
import { Keyboard, Interval } from "hyperapp-fx";
import { MQTTSubscribe } from "@shish2k/hyperapp-mqtt";
import { get_attachment, http2ws } from "./utils";

/**
 * Connect to the MQTT server, listen for queue / settings state updates,
 * and react to commands on the command channel
 */
export function getOpenMQTTListener(
    state: State,
): Subscription | null {
    if (!state.room_name) {
        return null;
    }

    return MQTTSubscribe({
        url: http2ws(state.root) + "/mqtt",
        username: state.room_name,
        password: state.room_password,
        topic: "karakara/room/" + state.room_name + "/#",
        connect(state: State): Dispatchable {
            return { ...state, connected: true };
        },
        close(state: State): Dispatchable {
            return { ...state, connected: false };
        },
        message(state: State, msg): Dispatchable {
            // msg = mqtt-packet
            const topic: string = msg.topic.split("/").pop();
            const data: string = msg.payload.toString();

            console.groupCollapsed("mqtt_onmessage(", topic, ")");
            try {
                console.log(JSON.parse(data));
            } catch (error) {
                console.log(data);
            }
            console.groupEnd();

            switch (topic) {
                case "commands":
                    const cmd = data.trim();
                    switch (cmd) {
                        case "play":
                            return Play(state);
                        case "stop":
                            return Stop(state);
                        case "pause":
                            return Pause(state);
                        case "seek_forwards":
                            return SeekForwards(state, null);
                        case "seek_backwards":
                            return SeekBackwards(state, null);
                        case "played":
                            return Dequeue(state);
                        // Only one instance should mark the current track as skipped, to avoid
                        // skipping two tracks
                        case "skip":
                            return state.podium
                                ? Dequeue(state)
                                : MarkTrackSkipped(state);
                        default:
                            return state;
                    }
                case "settings":
                    return {
                        ...state,
                        settings: {
                            ...state.settings,
                            ...JSON.parse(data),
                        },
                    };
                case "queue":
                    return UpdateQueue(state, JSON.parse(data));
                default:
                    return state;
            }
        },
    });
}

export const KeyboardListener = Keyboard({
    downs: true,
    action(state: State, event: KeyboardEvent): Dispatchable {
        // Disable keyboard shortcuts when the settings
        // screen is active
        if (state.show_settings) {
            return state;
        }
        let action: CallableFunction | null = null;
        switch (event.key) {
            case "s":
                action = Dequeue;
                break; // skip
            case "Enter":
                action = Play;
                break;
            case "Escape":
                action = Stop;
                break;
            case "ArrowLeft":
                action = SeekBackwards;
                break;
            case "ArrowRight":
                action = SeekForwards;
                break;
            case " ":
                action = Pause;
                break;
        }
        if (action) {
            event.preventDefault();
            return action(state);
        }
        return state;
    },
});

export const IntervalListener = Interval({
    every: 200,
    action(state: State, timestamp): Dispatchable {
        if (
            state.progress >= state.settings["karakara.player.autoplay.seconds"]
        ) {
            return [state, SendCommand(state, "play")];
        } else {
            return { ...state, progress: state.progress + 1 / 5 };
        }
    },
});

function track_list_to_map(raw_list: Array<Track>): Dictionary<Track> {
    let map = {};
    for (let i = 0; i < raw_list.length; i++) {
        map[raw_list[i].id] = raw_list[i];
    }
    return map;
}

function track_list_to_images(state: State, raw_list: Array<Track>): Array<WaterfallImage> {
    // TODO: pick a random 25 tracks (will people even notice if it's
    // the same 25 every time?)
    let num = 25;
    return raw_list.slice(0, num).map((track, n) => ({
        filename: get_attachment(state, track, "image"),
        x: n / num,
        delay: Math.random() * 10,
    }));
}

function _ftlSubscriber(dispatch, props) {
    // subscription is restarted whenever props changes,
    // and props is just {room: state.room_name}
    if (props.room) {
        setTimeout(function () {
            dispatch((state) => [
                state,
                ApiRequest({
                    function: "track_list",
                    state: state,
                    progress: (state, { done, size }) => [
                        {
                            ...state,
                            download_done: done,
                            download_size: size,
                        },
                    ],
                    action: (state, response): State =>
                        response.status == "ok"
                            ? {
                                  ...state,
                                  track_list: track_list_to_map(response.data.list),
                                  images: track_list_to_images(state, response.data.list),
                                  download_done: 0,
                                  download_size: null,
                              }
                            : {
                                  ...state,
                                  download_done: 0,
                                  download_size: null,
                              },
                })
            ]);
        }, 0);
    }

    return function () {
        // no unsubscribe
    };
}

export function FetchTrackList(room_name: string): Subscription {
    return [_ftlSubscriber, { room: room_name }];
}
