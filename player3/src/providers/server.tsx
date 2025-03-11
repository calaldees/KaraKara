import React, { useContext, useEffect, useState } from "react";
import { useApi } from "../hooks/api";
import { useServerTime } from "@shish2k/react-use-servertime";
import { ClientContext } from "./client";
import type { Track } from "../types";

export type ServerContextType = {
    tracks: Record<string, Track>;
    downloadSize: number | null;
    downloadDone: number;
    now: number;
    offset: number;
};

export const ServerContext = React.createContext<ServerContextType>({
    tracks: {},
    downloadSize: null,
    downloadDone: 0,
    now: 0,
    offset: 0,
});

export function ServerProvider(props: any) {
    const { root } = useContext(ClientContext);
    const [tracks, setTracks] = useState<Record<string, Track>>({});
    const [downloadSize, setDownloadSize] = useState<number | null>(null);
    const [downloadDone, setDownloadDone] = useState<number>(0);
    const { request } = useApi();
    const { now, offset } = useServerTime({ url: `${root}/time.json` });

    useEffect(() => {
        request({
            function: "overridden by url",
            url: `${root}/files/tracks.json`,
            options: {
                credentials: "omit",
            },
            onAction: (result) => setTracks(result),
            onProgress: ({ done, size }) => {
                setDownloadDone(done);
                setDownloadSize(size);
            },
        });
    }, [root, request]);

    return (
        <ServerContext.Provider
            value={{ tracks, downloadSize, downloadDone, now, offset }}
        >
            {props.children}
        </ServerContext.Provider>
    );
}
