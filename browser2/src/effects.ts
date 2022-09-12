/*
 * Effects: functions which send data to the outside world
 */
import { MQTTPublish } from "@shish2k/hyperapp-mqtt";
import { Delay } from "hyperapp-fx";
import { mqtt_login_info } from "./utils";

// get article
function _get_article() {
    let articles = document.getElementsByTagName("article");
    // In portrait mode, only one article; in landscape,
    // there are two and we want the second.
    return articles[articles.length - 1];
}
export function PushScrollPos(): Effect {
    function saveScrollPos(dispatch, props) {
        // note the scroll pos while on the original page
        var pos = _get_article().scrollTop;
        // not immediately (give the new page a chance to generate the DOM),
        // but before the next repaint, scroll the page
        requestAnimationFrame(() =>
            dispatch(function (state: State): State {
                _get_article().scrollTop = 0;
                return {
                    ...state,
                    scroll_stack: state.scroll_stack.concat([pos]),
                };
            }),
        );
    }
    return [saveScrollPos, {}];
}
export function PopScrollPos(): Effect {
    function restoreScrollPos(dispatch, props) {
        // after the new page has loaded, scroll it
        requestAnimationFrame(() =>
            dispatch(function (state: State): State {
                _get_article().scrollTop = state.scroll_stack.pop() || 0;
                return {
                    ...state,
                };
            }),
        );
    }
    return [restoreScrollPos, {}];
}
export function ClearScrollPos(): Effect {
    function clearScrollPos(dispatch, props) {
        dispatch(function (state: State): State {
            return {
                ...state,
                scroll_stack: [],
            };
        });
    }
    return [clearScrollPos, {}];
}

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
            let download_size = 5*1024*1024;

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

            if ((result.status ?? "ok") == "ok") {
                if (result.messages?.length > 0) {
                    dispatch((state) => [
                        {
                            ...state,
                            notification: {
                                text: result.messages[0],
                                style: "ok",
                            },
                        },
                        Delay({
                            wait: 2000,
                            action: (state) => ({
                                ...state,
                                notification: null,
                            }),
                        }),
                    ]);
                }
            } else {
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
            options: {
                credentials: 'include',
            },
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
        topic: "room/" + state.room_name + "/commands",
        payload: command,
    });
}
