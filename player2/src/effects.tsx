/**
 * Effects = things we send into the world (websocket packet,
 * http request, etc) and we'll update the app state some time
 * later, after we get a response.
 */
import { MQTTPublish } from "hyperapp-mqtt";
import { http2ws } from "./utils";
import { AddLyricsToNewQueue } from "./actions";


function apiRequestEffect(dispatch, props) {
    dispatch((state) => ({
        ...state,
        loading: true,
        notification: props.title
            ? { text: props.title, style: "warning" }
            : null,
    }));

    fetch(props.url, props.options)
        .then(function (response) {
            return response;
        })
        .then(function (response) {
            return response.json();
        })
        .then(function (result) {
            console.groupCollapsed("api_request(", props.url, ")");
            console.log(result);
            console.groupEnd();

            dispatch(
                (state, result) => [
                    {
                        ...state,
                        loading: false,
                    },
                ],
                result,
            );

            if (result.status != "ok") {
                dispatch((state) => [
                    {
                        ...state,
                        notification: {
                            text: result.messages[0],
                            style: "error",
                        },
                    },
                ]);
            }
            if (props.action) {
                dispatch(props.action, result);
            }
        })
        .catch(function (error) {
            console.groupCollapsed("api_request(", props.url, ")");
            console.log(error);
            console.groupEnd();

            dispatch(
                (state, error) => [
                    {
                        ...state,
                        loading: false,
                        notification: {
                            text: "Internal Error: " + error,
                            style: "error",
                        },
                    },
                ],
                error,
            );
        });
}

export function ApiRequest(props) {
    return [
        apiRequestEffect,
        {
            options: {},
            response: "json",
            url:
                props.state.root +
                "/queue/" +
                (props.state.room_name || props.state.room_name_edit) +
                "/" +
                props.function +
                ".json",
            ...props,
        },
    ];
}

export function SendCommand(state: State, command: string) {
    console.log("mqtt_send(", "commands", command, ")");
    return MQTTPublish({
        url: http2ws(state.root) + "/mqtt",
        username: state.room_name,
        password: state.room_password,
        topic: "karakara/room/" + state.room_name + "/commands",
        payload: command,
    });
}

export function FetchRandomImages(state: State) {
    return ApiRequest({
        function: "random_images",
        state: state,
        action(state: State, response): State {
            let images = response.data.images.slice(0, 25);
            return {
                ...state,
                images: images.map((fn, n) => ({
                    filename: fn,
                    x: n / images.length,
                    delay: Math.random() * 10,
                })),
            };
        },
    });
}

export function CheckSettings(state: State) {
    return ApiRequest({
        function: "settings",
        state: state,
        action(state: State, response) {
            return {
                ...state,
                settings: { ...state.settings, ...response.data.settings },
            };
        },
    });
}

export function CheckQueue(state: State) {
    return ApiRequest({
        function: "queue_items",
        state: state,
        action(state: State, response) {
            return AddLyricsToNewQueue(state, response.data.queue);
        },
    });
}

export function SetTrackState(state: State, value: string) {
    return ApiRequest({
        function: "queue_items",
        state: state,
        options: {
            method: "PUT",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                "queue_item.id": state.queue[0].id.toString(),
                status: value,
                uncache: new Date().getTime().toString(),
            }),
        },
    });
}
