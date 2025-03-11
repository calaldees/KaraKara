import { useCallback, useContext, useState } from "react";
import { useParams } from "react-router-dom";
import { ClientContext } from "../providers/client";

export function useApi() {
    const { roomName } = useParams();
    const { root, setNotification } = useContext(ClientContext);
    const [loading, setLoading] = useState(false);

    const request = useCallback(
        function (props_: {
            function: string;
            url?: string;
            options?: Record<string, any>;
            notify?: string;
            notify_ok?: string;
            onProgress?: ({
                done,
                size,
            }: {
                done: number;
                size: number;
            }) => void;
            onAction?: (result: any) => void;
            onException?: () => void;
        }) {
            const props = {
                response: "json",
                url: `${root}/room/${roomName}/${props_.function}.json`,
                options: {},
                ...props_,
            };

            setLoading(true);
            if (props.notify)
                setNotification({ text: props.notify, style: "warning" });

            if (!props.options.credentials)
                props.options.credentials = "include";

            fetch(props.url, props.options)
                .then((response) => {
                    if (response.status >= 500) {
                        throw new Error(response.statusText);
                    }
                    if (!response.body) throw new Error("No response body");
                    const reader = response.body.getReader();
                    let download_done = 0;
                    // Content-Length shows us the compressed size, we can only
                    // guess the real size :(
                    const download_size = 5 * 1024 * 1024;

                    return new ReadableStream({
                        start(controller) {
                            function push() {
                                reader
                                    .read()
                                    .then(({ done, value }) => {
                                        if (done) {
                                            controller.close();
                                            return;
                                        }
                                        if (value) {
                                            download_done += value.byteLength;
                                            if (props.onProgress) {
                                                props.onProgress({
                                                    done: download_done,
                                                    size: download_size,
                                                });
                                            }
                                        }
                                        controller.enqueue(value);
                                        push();
                                    })
                                    .catch(() => {
                                        controller.error(
                                            new Error("Failed to read"),
                                        );
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
                    if (result.status >= 400) {
                        throw result;
                    }

                    console.groupCollapsed("api_request(", props.url, ")");
                    console.log(result);
                    console.groupEnd();

                    setLoading(false);
                    if (props.notify_ok) {
                        setNotification({ text: props.notify_ok, style: "ok" });
                        setTimeout(() => {
                            setNotification(null);
                        }, 2000);
                    }

                    if (props.onAction) {
                        props.onAction(result);
                    }
                })
                .catch(function (error) {
                    console.groupCollapsed(
                        "api_request(",
                        props.url,
                        ") [error]",
                    );
                    console.log(error);
                    console.groupEnd();

                    setLoading(false);
                    setNotification({
                        text:
                            error.message === "queue validation failed"
                                ? error.context
                                : "Internal Error: " +
                                  (error.message ?? "unknown") +
                                  (error.context ? ": " + error.context : ""),
                        style: "error",
                    });

                    if (props.onException) {
                        props.onException();
                    }
                });
        },
        [roomName, root, setNotification],
    );

    const sendCommand = useCallback(
        function (command: string) {
            return request({
                function: `command/${command}`,
                options: {},
            });
        },
        [request],
    );

    return { request, sendCommand, loading };
}
