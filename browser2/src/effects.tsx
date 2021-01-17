import { MQTTPublish } from "hyperapp-mqtt";
import { Delay } from "hyperapp-fx";
import { http2ws } from "./utils";

export function DisplayResponseMessage(dispatch, response) {
    function parseResponse(data) {
        if(data.code >= 200 && data.code < 400) {
            dispatch(state => [
                { ...state, notification: {text: data.messages[0], style: "ok"} },
                Delay({
                    wait: 2000,
                    action: (state) => ({...state, notification: null})
                })
            ]);
        }
        else {
            dispatch(state => ({ ...state, notification: {text: data.messages[0], style: "error"} }));
        }
    }

    // When Http() is successful, response = the json from the server
    if(response.code) {
        parseResponse(response);
    }

    // When Http() fails, response = the raw blob, which we need
    // to decode for ourselves. First attempt to decode JSON, like
    // if karakara sent us a 403; fall back to "internal error" if
    // we can't decode it, like if the server crashed)
    else {
        response
        .json()
        .then(parseResponse)
        .catch(err => {
            console.log(err);
            dispatch(state => ({ ...state, notification: {text: "Internal Error", style: "error"} }));
        });
    }
}

export function SendCommand(state: State, command: string) {
    console.log("websocket_send(" + command + ")");
    return MQTTPublish({
        url: http2ws(state.root) + "/mqtt",
        topic: "karakara/queue/" + state.queue_id,
        payload: command,
    });
}
