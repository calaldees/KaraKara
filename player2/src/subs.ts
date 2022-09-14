import { Keyboard } from "hyperapp-fx";
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
    if(props.room_name) {
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
            dispatch((state) => ({...state, is_admin: false}));
        }, 0);
    }

    return function () {
        // no unsubscribe
    };
}

export function BeLoggedIn(room_name: string, room_password: string): Subscription {
    return [_bleSubscriber, { room_name, room_password }];
}
