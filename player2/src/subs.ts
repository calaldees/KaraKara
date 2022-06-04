import {
    Dequeue,
    MarkTrackSkipped,
    Pause,
    Play,
    SeekBackwards,
    SeekForwards,
    Stop,
} from "./actions";
import { ApiRequest, SendCommand } from "./effects";
import { Keyboard, Interval } from "hyperapp-fx";
import { MQTTSubscribe } from "@shish2k/hyperapp-mqtt";
import { attachment_path, mqtt_login_info } from "./utils";

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
        ...mqtt_login_info(state),
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
                    const new_queue = JSON.parse(data).filter(track => state.track_list.hasOwnProperty(track.id));
                    // if the first song in the queue has changed, stop playing
                    if (
                        state.queue.length === 0 ||
                        new_queue.length === 0 ||
                        state.queue[0].id !== new_queue[0].id
                    ) {
                        return {
                            ...state,
                            queue: new_queue,
                            playing: false,
                            paused: false,
                            progress: 0,
                        };
                    } else {
                        return { ...state, queue: new_queue };
                    }
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

function track_list_to_images(state: State, raw_list: Dictionary<Track>): Array<WaterfallImage> {
    // TODO: pick a random 25 tracks (will people even notice if it's
    // the same 25 every time?)
    let num = 25;
    return Object
        .values(raw_list)
        .slice(0, num)
        .map(track => track.attachments.image[0])
        .map((image, n) => ({
            filename: attachment_path(state.root, image),
            x: n / num,
            delay: ((n % 5) + Math.random()) * 2,
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
                    action: (state, response) => [
                        {
                            ...state,
                            track_list: response,
                            images: track_list_to_images(state, response),
                            download_done: 0,
                            download_size: null,
                        },
                    ],
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
