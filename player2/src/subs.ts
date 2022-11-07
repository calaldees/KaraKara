import { Keyboard, Delay } from "hyperapp-fx";
import { MQTTSubscribe } from "@shish2k/hyperapp-mqtt";
import { mqtt_login_info } from "./utils";
import { ApiRequest, SendCommand } from "./effects";

/**
 * Connect to the MQTT server, listen for queue / settings state updates,
 * and react to commands on the command channel
 */
export function getMQTTListener(state: State): Subscription | null {
    if (!state.room_name || !Object.keys(state.track_list).length) {
        return null;
    }

    return MQTTSubscribe({
        ...mqtt_login_info(state),
        topic: "room/" + state.room_name + "/#",
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
                case "notifications":
                    return [
                        {
                            ...state,
                            notification: { text: data, style: "warning" },
                        },
                        Delay({
                            wait: 10000,
                            action: (state) => ({
                                ...state,
                                notification: null,
                            }),
                        }),
                    ];
                case "settings":
                    return {
                        ...state,
                        settings: {
                            ...state.settings,
                            ...JSON.parse(data),
                        },
                    };
                case "queue":
                    const new_queue = JSON.parse(data).filter(queue_item => state.track_list.hasOwnProperty(queue_item.track_id));
                    return { ...state, queue: new_queue };
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
        let action: Dispatchable | null = null;
        switch (event.key) {
            case "s":
                action = [state, SendCommand(state, "skip")];
                break;
            case "Enter":
                action = [state, SendCommand(state, "play")];
                break;
            case "Escape":
                action = [state, SendCommand(state, "stop")];
                break;
            case "ArrowLeft":
                action = [state, SendCommand(state, "seek_forwards")];
                break;
            case "ArrowRight":
                action = [state, SendCommand(state, "seek_backwards")];
                break;
            case " ":
                action = [state, SendCommand(state, "pause")];
                break;
        }
        if (action) {
            event.preventDefault();
            return action;
        }
        return state;
    },
});


function _bleSubscriber(dispatch, props) {
    // subscription is restarted whenever props changes,
    if (props.room_name) {
        setTimeout(function () {
            dispatch((state) => [
                state,
                ApiRequest({
                    function: "login",
                    state: state,
                    options: {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            password: state.room_password,
                        }),
                    },
                    action: (state, response) => ({ ...state, is_admin: response.is_admin }),
                })
            ]);
        }, 0);
    }
    else {
        setTimeout(function () {
            dispatch((state) => ({ ...state, is_admin: false }));
        }, 0);
    }

    return function () {
        // no unsubscribe
    };
}

export function BeLoggedIn(room_name: string, room_password: string): Subscription {
    return [_bleSubscriber, { room_name, room_password }];
}


function _roundedIntervalSubscriber(dispatch, props) {
    var id: number | null = null;
    let offsets: Array<number> = [];

    function offset() {
        return offsets.length ? offsets.reduce((a, b) => a + b, 0) / offsets.length : 0;
    }
    function range() {
        return Math.max(...offsets.map(o => Math.abs(o-offset())));
    }
    function sync() {
        var sent = Date.now() / 1000;
        fetch("https://karakara.uk/time.json")
            .then(response => response.json())
            .then(response => {
                var recvd = Date.now() / 1000;
                var pingpong = recvd - sent;
                // if there's more than 200ms of network lag, don't
                // trust the timestamp to be accurate
                if(pingpong < 0.2) {
                    offsets.push(response - (pingpong / 2) - sent);
                }
                if(offsets.length < 5) {
                    setTimeout(sync, 1000);
                }
                else {
                    console.log("Clock offset set to", offset(), "+/-", range());
                }
            });
    }
    function waitForNextInterval() {
        var now = Date.now() + (offset() * 1000);
        dispatch(props.action, now);
        id = setTimeout(waitForNextInterval, props.every - (now % props.every));
    }

    id = setTimeout(waitForNextInterval, props.every - (Date.now() % props.every));
    //var sync_id = setInterval(sync, props.sync);
    sync();

    return function () {
        id && clearTimeout(id);
        //sync_id && clearInterval(sync_id);
    }
}

export function RoundedInterval(props) {
    return [_roundedIntervalSubscriber, props]
}
