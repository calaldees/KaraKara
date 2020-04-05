import {Dequeue, MarkTrackSkipped, Pause, Play, SeekBackwards, SeekForwards, Stop} from "./actions";
import {CheckQueue, CheckSettings, SendCommand} from "./effects";
import {WebSocketListen, Keyboard, Interval} from "hyperapp-fx";
import {http2ws} from "./utils";

let mySubs = {};

export function getOpenWebSocketListener(state: State): WebSocketListen {
    let url = http2ws(state.root) + "/" + state.queue_id +".ws?ws_error_count=" + state.ws_error_count;
    if (!mySubs[url]) {
        mySubs[url] = WebSocketListen({
            url: url,
            open(state: State) {
                return [{...state, connected: true}, CheckSettings(state), CheckQueue(state)];
            },
            close(state: State) {
                delete mySubs[url];
                return {...state, connected: false, ws_error_count: state.ws_error_count + 1};
            },
            action(state: State, msg: MessageEvent) {
                const cmd = msg.data.trim();
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
                        return state.is_podium ? Dequeue(state) : MarkTrackSkipped(state);
                    default:
                        console.log("unknown command: " + cmd);
                        return state;
                }
            },
            error(state: State, response) {
                console.log("Error listening to websocket:", response);
                return {...state, ws_error_count: state.ws_error_count + 1}
            },
        });
    }
    return mySubs[url]
}

export const KeyboardListener = Keyboard({
    downs: true,
    action(state: State, event): State {
        let action = null;
        switch (event.key) {
            case "s"          :
                action = Dequeue;
                break; // skip
            case "Enter"      :
                action = Play;
                break;
            case "Escape"     :
                action = Stop;
                break;
            case "ArrowLeft"  :
                action = SeekBackwards;
                break;
            case "ArrowRight" :
                action = SeekForwards;
                break;
            case " "          :
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
            return {...state, progress: state.progress + 1 / 5};
        }
    },
});