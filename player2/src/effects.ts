/**
 * Effects = things we send into the world (websocket packet,
 * http request, etc) and we'll update the app state some time
 * later, after we get a response.
 */
import { Delay } from "hyperapp-fx";

function apiRequestEffect(
    dispatch: Dispatch,
    props: {
        url: string;
        options: Dictionary<any>;
        notify?: string;
        notify_ok?: string;
        progress?: Dispatchable<{ done: number; size: number }>;
        action?: Dispatchable;
        exception?: Dispatchable;
    },
) {
    dispatch((state) => ({
        ...state,
        loading: true,
        notification: props.notify
            ? { text: props.notify, style: "warning" }
            : null,
    }));

    props.options["credentials"] ??= "include";

    fetch(props.url, props.options)
        .then((response) => {
            if (!response.body) return;
            const reader = response.body.getReader();
            let download_done = 0;
            // Content-Length shows us the compressed size, we can only
            // guess the real size :(
            let download_size = 5 * 1024 * 1024;

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
                        loading: false,
                        notification: props.notify_ok
                            ? { text: props.notify_ok, style: "ok" }
                            : null,
                    },
                    Delay({
                        wait: 2000,
                        action: (state) => ({
                            ...state,
                            notification: null,
                        }),
                    }),
                ],
                result,
            );

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

export function ApiRequest(props: {
    state: State;
    function?: string;
    url?: string;
    options?: Dictionary<any>;
    notify?: string;
    notify_ok?: string;
    progress?: Dispatchable<{ done: number; size: number }>;
    action?: Dispatchable;
    exception?: Dispatchable;
}): Effect {
    return [
        apiRequestEffect,
        {
            options: {},
            response: "json",
            url: `${props.state.root}/room/${props.state.room_name}/${props.function}.json`,
            ...props,
        },
    ];
}

export function SendCommand(state: State, command: string): Effect {
    return ApiRequest({
        function: `command/${command}`,
        state: state,
    });
}
