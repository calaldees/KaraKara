/*
 * Subscriptions: functions which take data from the outside world
 */
import { MQTTSubscribe } from "hyperapp-mqtt";
import { http2ws } from "./utils";
import { CheckSettings, CheckQueue } from "./effects";

export function getMQTTListener(state: State): [CallableFunction, any] {
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
        error(state: State, err) {
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
            const topic = msg.topic.split("/").pop();
            const data = msg.payload.toString();

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
