import { MQTTSubscribe } from "hyperapp-mqtt";
import { http2ws } from "./utils";
import { refresh } from "./screens/base";

export function getCommandListener(state: State): [CallableFunction, any] {
    return MQTTSubscribe({
        url: http2ws(state.root) + "/mqtt",
        // don't specify un/pw at all, unless pw is non-empty
        ...(state.room_password
            ? {
                  username: state.room_name,
                  password: state.room_password,
              }
            : {}),
        topic: "karakara/room/" + state.room_name + "/commands",
        connect(state: State) {
            // TODO: no need to refresh on connect if we
            // have retained messages
            console.log("Connected, refreshing");
            return refresh(state);
        },
        close(state: State) {
            console.log("MQTT socket closed, assuming it'll reopen");
            return { ...state };
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
        message(state: State, msg) {
            // TODO: state.queue = JSON.parse(msg.payload.toString());
            console.log("Got command, refreshing:", msg.payload.toString());
            return refresh(state);
        },
    });
}

export function getNotificationListener(state: State): [CallableFunction, any] {
    return MQTTSubscribe({
        url: http2ws(state.root) + "/mqtt",
        // don't specify un/pw at all, unless pw is non-empty
        ...(state.room_password
            ? {
                  username: state.room_name,
                  password: state.room_password,
              }
            : {}),
        topic: "karakara/room/" + state.room_name + "/notifications",
        message: (state: State, msg) => ({
            ...state,
            notification: { text: msg.payload.toString(), style: "warning" },
        }),
    });
}
