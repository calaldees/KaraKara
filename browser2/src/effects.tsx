/*
 * Effects: functions which send data to the outside world
 */
import { MQTTPublish } from "hyperapp-mqtt";
import { Delay } from "hyperapp-fx";
import { http2ws, flatten_settings } from "./utils";

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

function track_list_to_map(raw_list: Array<Track>) {
    let map = {};
    for (let i = 0; i < raw_list.length; i++) {
        map[raw_list[i].id] = raw_list[i];
    }
    return map;
}

export const FetchTrackList = (state) =>
    ApiRequest({
        function: "track_list",
        state: state,
        progress: (state, done, size) => [
            {
                ...state,
                download_done: done,
                download_size: size,
            },
        ],
        action: (state, response) =>
            response.status == "ok"
                ? [
                      {
                          ...state,
                          room_name: state.room_name_edit,
                          session_id: response.identity.id,
                          track_list: track_list_to_map(response.data.list),
                      },
                      // queue & settings should come from mqtt, but if there
                      // was no cache for some reason, fetch from HTTP
                      !state.queue &&
                          ApiRequest({
                              function: "queue_items",
                              state: state,
                              action: (state, response) => ({
                                  ...state,
                                  queue: response.data.queue,
                              }),
                          }),
                      !state.settings &&
                          ApiRequest({
                              function: "settings",
                              state: state,
                              action: (state, response) => ({
                                  ...state,
                                  settings: response.data.settings,
                              }),
                          }),
                  ]
                : {
                      ...state,
                      room_name_edit: "",
                  },
    });

export const LoginThenFetchTrackList = (state) =>
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

export function SaveSettings(state: State) {
    return [
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
            return { ...state, queue: response.data.queue };
        },
    });
}
