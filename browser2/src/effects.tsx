/*
 * Effects: functions which send data to the outside world
 */
import { MQTTPublish } from "@shish2k/hyperapp-mqtt";
import { Delay } from "hyperapp-fx";
import { http2ws, flatten_settings } from "./utils";
import * as qrcode from "qrcode-generator";

// get article
function _get_article() {
    return document.getElementsByTagName("article")[0];
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
        .then((response) => response.body)
        .then((rb) => {
            if (!rb) return;
            const reader = rb.getReader();
            let download_done = 0;
            let download_size = 7500000; // TODO: add content-length to track_list.json

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
            }).text();
        })
        .then(function (response) {
            return JSON.parse(response);
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

            if (result.status == "ok") {
                if (result.messages.length > 0) {
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

export function SendCommand(state: State, command: string): Effect {
    console.log("mqtt_send(", "commands", command, ")");
    return MQTTPublish({
        url: http2ws(state.root) + "/mqtt",
        username: state.room_name,
        password: state.room_password,
        topic: "karakara/room/" + state.room_name + "/commands",
        payload: command,
    });
}

function track_list_to_map(raw_list: Array<Track>): Dictionary<Track> {
    let map = {};
    for (let i = 0; i < raw_list.length; i++) {
        map[raw_list[i].id] = raw_list[i];
    }
    return map;
}

function make_qr(state: State) {
    let qr = qrcode(8, 'L');
    qr.addData(state.root + "/browser2/?r=" + state.room_name_edit);
    qr.make();
    return qr.createDataURL(4);
}

export const FetchTrackList = (state: State): Effect =>
    ApiRequest({
        function: "track_list",
        state: state,
        progress: (state, { done, size }) => [
            {
                ...state,
                download_done: done,
                download_size: size,
            },
        ],
        action: (state, response) =>
            response.status == "ok"
                ? {
                      ...state,
                      room_name: state.room_name_edit,
                      session_id: response.identity.id,
                      track_list: track_list_to_map(response.data.list),
                      download_done: 0,
                      download_size: null,
                      qr_data: make_qr(state),
                  }
                : {
                      ...state,
                      room_name_edit: "",
                      download_done: 0,
                      download_size: null,
                  },
    });

export const LoginThenFetchTrackList = (state: State): Effect =>
    ApiRequest({
        function: "admin",
        state: state,
        options: {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                password: state.room_password,
                fixme: "true",
            }),
        },
        action: (state, response) =>
            response.status == "ok" ? [state, FetchTrackList(state)] : state,
    });

function _autoLoginEffect(dispatch, props) {
    const params = new URLSearchParams(window.location.search);
    const room_name = params.get('r');
    if(!room_name) return;

    dispatch(function(state: State) {
        if(state.room_name !== "") return state;  // HMR already loaded our data for us
        console.log("Autologin", room_name);
        state = {...state, room_name_edit: room_name};
        return [
            state,
            state.room_password
                ? LoginThenFetchTrackList(state)
                : FetchTrackList(state),
        ];
    });
}
export function AutoLogin() {
    return [_autoLoginEffect, {}]
}

export const SaveSettings = (state: State): Dispatchable => [
    { ...state },
    ApiRequest({
        title: "Saving setting...",
        function: "settings",
        state: state,
        options: {
            method: "PUT",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(flatten_settings(state.settings)),
        },
        // action: (state, response) => [{ ...state }],
    }),
];
