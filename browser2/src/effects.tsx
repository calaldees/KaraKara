import { MQTTPublish } from "hyperapp-mqtt";
import { http2ws } from "./utils";

export function DisplayResponseMessage(dispatch, response) {
    if(response.status >= 200 && response.status < 400) {
        dispatch(state => ({ ...state, notification: "" }));
    }

    response
        .json()
        .then(json => {
            dispatch(state => ({ ...state, notification: json.messages[0] }));
        })
        .catch(err => {
            console.log(err);
            dispatch(state => ({ ...state, notification: "Internal Error" }));
        });
}

export function SendCommand(state: State, command: string) {
    console.log("websocket_send(" + command + ")");
    return MQTTPublish({
        url: http2ws(state.root) + "/mqtt",
        topic: "karakara/queue/" + state.queue_id,
        payload: command,
    });
}
