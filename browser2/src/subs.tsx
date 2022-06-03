/*
 * Subscriptions: functions which take data from the outside world
 */
import { MQTTSubscribe } from "@shish2k/hyperapp-mqtt";
import { mqtt_login_info } from "./utils";

/**
 * Connect to the MQTT server, listen for updates to queue / settings
 */
export function getMQTTListener(state: State): Subscription {
    return MQTTSubscribe({
        ...mqtt_login_info(state),
        topic: "karakara/room/" + state.room_name + "/#",
        error(state: State, err): State {
            console.log(
                "Got an unrecoverable MQTT error, " +
                "returning to login screen",
                err,
            );
            return {
                ...state,
                room_name: "",
                notification: { text: err.message, style: "error" },
            };
        },
        message(state: State, msg): State {
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
                    return {
                        ...state,
                        notification: { text: data, style: "warning" },
                    };
                case "settings":
                    return {
                        ...state,
                        settings: {
                            ...state.settings,
                            ...JSON.parse(data),
                        },
                    };
                case "queue":
                    return {
                        ...state,
                        queue: JSON.parse(data).filter(track => state.track_list.hasOwnProperty(track.id))
                    };
                default:
                    return state;
            }
        },
    });
}

function _resizeSubscriber(dispatch, props) {
    function handler(event) {
        dispatch(props.onresize, event);
    }
    window.addEventListener("resize", handler);
    return function () {
        window.removeEventListener("resize", handler);
    };
}

export function ResizeListener(callback: Dispatchable): Subscription {
    return [_resizeSubscriber, { onresize: callback }];
}
