/**
 * Effects = things we send into the world (websocket packet,
 * http request, etc) and we'll update the app state some time
 * later, after we get a response.
 */
import { MQTTPublish } from "@shish2k/hyperapp-mqtt";
import { mqtt_login_info } from "./utils";

function apiRequestEffect(dispatch, props) {
    dispatch((state) => ({
        ...state,
        loading: true,
        notification: props.title
            ? { text: props.title, style: "warning" }
            : null,
    }));

    fetch(props.url, props.options)
        .then((response) => {
            if (!response.body) return;
            const reader = response.body.getReader();
            let download_done = 0;
            // Content-Length shows us the compressed size, we can only
            // guess the real size :(
            let download_size = 10*1024*1024;

            return new ReadableStream({
                start(controller) {
                    function push() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                controller.close();
                                return;
                            }
                            if (value) {
                                download_done += value.byteLength;
                                if (props.progress) {
                                    dispatch(props.progress, {
                                        done: download_done,
                                        size: download_size,
                                    });
                                }
                            }
                            controller.enqueue(value);
                            push();
                        });
                    }
                    push();
                },
            });
        })
        .then((stream) => {
            return new Response(stream, {
                headers: { "Content-Type": "text/json" },
            }).json();
        })
        .then(function (result) {
            console.groupCollapsed("api_request(", props.url, ")");
            console.log(result);
            console.groupEnd();

            dispatch(
                (state, result) => [
                    {
                        ...state,
                        session_id: result?.identity?.id || state.session_id,
                        loading: false,
                    },
                ],
                result,
            );

            if ((result.status ?? "ok") != "ok") {
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
            console.groupCollapsed("api_request(", props.url, ") [error]");
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
            if (props.exception) {
                dispatch(props.exception);
            }
        });
}

export function ApiRequest(props): Effect {
    return [
        apiRequestEffect,
        {
            options: {},
            response: "json",
            url: `${props.state.root}/queue/${props.state.room_name}/${props.function}.json`,
            ...props,
        },
    ];
}

export function SendCommand(state: State, command: string): Effect {
    console.log("mqtt_send(", "commands", command, ")");
    return MQTTPublish({
        ...mqtt_login_info(state),
        topic: "karakara/room/" + state.room_name + "/commands",
        payload: command,
    });
}

export function SetTrackState(state: State, value: string): Effect {
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
