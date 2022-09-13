/*
 * Subscriptions: functions which take data from the outside world
 */
import { MQTTSubscribe } from "@shish2k/hyperapp-mqtt";
import { mqtt_login_info } from "./utils";
import { ApiRequest } from "./effects";
import Cookies from 'js-cookie'

/**
 * Connect to the MQTT server, listen for updates to queue / settings
 */
export function getMQTTListener(state: State): Subscription | null {
    if (!state.room_name || !Object.keys(state.track_list).length) {
        return null;
    }

    return MQTTSubscribe({
        ...mqtt_login_info(state),
        topic: "room/" + state.room_name + "/#",
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
                        queue: JSON.parse(data).filter(track => state.track_list.hasOwnProperty(track.track_id))
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
                    action: (state, response) => ({ ...state, is_admin: true }),
                    exception: (state) => ({ ...state, is_admin: false })
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


function _cookieListener(dispatch, props) {
    let oldCookieVal: string | null = null;
    let cookieTimer = setInterval(function() {
        let cookieVal = Cookies.get(props.name);
        if(cookieVal != oldCookieVal) {
            oldCookieVal = cookieVal;
            console.log(props.name + " has new cookie val: " + cookieVal);
            dispatch(props.callback, cookieVal);
        }
    }, 1000);
    return function() {
        clearInterval(cookieTimer);
    };
}
export function CookieListener(name, callback) {
    return [_cookieListener, {name: name, callback: callback}];
}
