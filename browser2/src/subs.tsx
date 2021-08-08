/*
 * Subscriptions: functions which take data from the outside world
 */
import { MQTTSubscribe } from "@shish2k/hyperapp-mqtt";
import { http2ws } from "./utils";
import { ChromecastSender, LoadMedia } from "./cc_sender";

/**
 * Connect to the MQTT server, listen for updates to queue / settings
 */
export function getMQTTListener(state: State): Subscription {
    return MQTTSubscribe({
        url: http2ws(state.root) + "/mqtt",
        username: state.room_name,
        password: state.room_password,
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
                        queue: JSON.parse(data),
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

export const ChromecastListener = ChromecastSender({
    receiverApplicationId: "05C10F57",
    onCastStateChanged(state: State, event) {
        console.log("Cast state changed:", event);
        return state;
    },
    onSessionStateChanged(state: State, event) {
        console.log("Session state changed:", event);
        switch (event.sessionState) {
            case cast.framework.SessionState.SESSION_STARTED:
                if (state.room_name) {
                    return [
                        { ...state, casting: true },
                        LoadMedia({
                            contentId: state.room_name,
                            contentType: "karakara/room",
                            credentials: state.room_password,
                        }),
                    ];
                }
                return { ...state, casting: true };
            case cast.framework.SessionState.SESSION_RESUMED:
                // TODO: if we log into a room while state.casting=true,
                // then send a LoadMedia
                return { ...state, casting: true };
            case cast.framework.SessionState.SESSION_ENDED:
                return { ...state, casting: false };
                break;
            default:
                return state;
        }
    },
});
