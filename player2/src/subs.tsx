import {
    Dequeue,
    MarkTrackSkipped,
    Pause,
    Play,
    SeekBackwards,
    SeekForwards,
    Stop,
    AddLyricsToNewQueue,
} from "./actions";
import { CheckQueue, CheckSettings, SendCommand } from "./effects";
import { Keyboard, Interval } from "hyperapp-fx";
import { MQTTSubscribe } from "hyperapp-mqtt";
import { http2ws } from "./utils";

export function getOpenMQTTListener(state: State): [CallableFunction, any] {
    return MQTTSubscribe({
        url: http2ws(state.root) + "/mqtt",
        username: state.room_name,
        password: state.room_password,
        topic: "karakara/room/" + state.room_name + "/#",
        connect(state: State) {
            // TODO: no need to refresh on connect if we
            // have retained messages
            return [
                { ...state, connected: true },
                CheckSettings(state),
                CheckQueue(state),
            ];
        },
        close(state: State) {
            return {
                ...state,
                connected: false,
            };
        },
        message(state: State, msg): State | [State, any] {
            // msg = mqtt-packet
            const topic = msg.topic.split("/").pop();
            const data = msg.payload.toString();

            console.groupCollapsed("mqtt_onmessage(", topic, ")");
            try {
                console.log(JSON.parse(data));
            } catch (error) {
                console.log(data);
            }
            console.groupEnd();

            switch(topic) {
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
                        settings: JSON.parse(data),
                    };
                case "queue":
                    return AddLyricsToNewQueue(state, JSON.parse(data));
                default:
                    return state;
            }
        },
    });
}

export const KeyboardListener = Keyboard({
    downs: true,
    action(state: State, event: KeyboardEvent): State {
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
    action(state: State, timestamp) {
        if (state.progress >= state.settings["karakara.player.autoplay"]) {
            return [state, SendCommand(state, "play")];
        } else {
            return { ...state, progress: state.progress + 1 / 5 };
        }
    },
});
