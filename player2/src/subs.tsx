import {
    Dequeue,
    MarkTrackSkipped,
    Pause,
    Play,
    SeekBackwards,
    SeekForwards,
    Stop,
} from "./actions";
import { CheckQueue, CheckSettings, SendCommand } from "./effects";
import { Keyboard, Interval } from "hyperapp-fx";
import { MQTTSubscribe } from "hyperapp-mqtt";
import { http2ws } from "./utils";

let mySubs = {};

export function getOpenMQTTListener(state: State): MQTTSubscribe {
    let url = http2ws(state.root) + "/mqtt";
    if (!mySubs[url]) {
        mySubs[url] = MQTTSubscribe({
            url: url,
            topic: "karakara/queue/" + state.queue_id,
            connect(state: State) {
                return [
                    { ...state, connected: true },
                    CheckSettings(state),
                    CheckQueue(state),
                ];
            },
            close(state: State) {
                // delete mySubs[url];
                return {
                    ...state,
                    connected: false,
                };
            },
            message(state: State, msg) {
                // msg = mqtt-packet
                const cmd = msg.payload.toString().trim();
                console.log("websocket_onmessage(" + cmd + ")");
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
                    case "queue_updated":
                        return [state, CheckQueue(state)];
                    case "settings":
                        return [state, CheckSettings(state)];
                    // Only one instance should mark the current track as skipped, to avoid
                    // skipping two tracks
                    case "skip":
                        return state.podium
                            ? Dequeue(state)
                            : MarkTrackSkipped(state);
                    default:
                        console.log("unknown command: " + cmd);
                        return state;
                }
            },
        });
    }
    return mySubs[url];
}

export const KeyboardListener = Keyboard({
    downs: true,
    action(state: State, event): State {
        // Disable keyboard shortcuts when the settings
        // screen is active
        if (state.show_settings) {
            return state;
        }
        let action = null;
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
    action(state: State, timestamp) {
        if (state.progress >= state.settings["karakara.player.autoplay"]) {
            return [state, SendCommand(state, "play")];
        } else {
            return { ...state, progress: state.progress + 1 / 5 };
        }
    },
});
