import React, { useContext, useEffect, useState } from "react";
import { useApi } from "../hooks/api";
import { useServerTime } from "@shish2k/react-use-servertime";
import { MqttProvider, useSubscription } from "@shish2k/react-mqtt";
import { ClientContext } from "./client";
import { mqtt_url } from "../utils";
import type { Track } from "../types";
import { useLocalStorage } from "usehooks-ts";

export interface ServerContextType {
    tracks: Record<string, Track>;
    downloadSize: number | null;
    downloadDone: number;
    now: number;
    offset: number;
    connected: boolean;
}

/* eslint-disable react-refresh/only-export-components */
export const ServerContext = React.createContext<ServerContextType>(
    {} as ServerContextType,
);

function InternalServerProvider(props: any) {
    const { root } = useContext(ClientContext);
    const [tracks, setTracks] = useState<Record<string, Track>>({});
    const [downloadSize, setDownloadSize] = useState<number | null>(null);
    const [downloadDone, setDownloadDone] = useState<number>(0);
    const [tracksUpdated, setTracksUpdated] = useLocalStorage<number>(
        "tracksUpdated",
        0,
    );
    const { request } = useApi();
    const { now, offset } = useServerTime({ url: `${root}/time.json` });

    const { connected } = useSubscription(`global/tracks-updated`, (pkt) => {
        console.groupCollapsed(`mqtt_msg(${pkt.topic})`);
        console.log(pkt.json());
        console.groupEnd();
        setTracksUpdated(pkt.json()["tracks_json_mtime"]);
    });
    useEffect(() => {
        request({
            url: `${root}/files/tracks.json?ver=${tracksUpdated}`,
            options: {
                credentials: "omit",
            },
            onAction: (result) => setTracks(result),
            onProgress: ({ done, size }) => {
                setDownloadDone(done);
                setDownloadSize(size);
            },
        });
    }, [root, request, tracksUpdated]);

    return (
        <ServerContext
            value={{
                tracks,
                downloadSize,
                downloadDone,
                now,
                offset,
                connected,
            }}
        >
            {props.children}
        </ServerContext>
    );
}

export function ServerProvider(props: any) {
    const { root } = useContext(ClientContext);
    return (
        <MqttProvider url={mqtt_url(root)}>
            <InternalServerProvider>{props.children}</InternalServerProvider>
        </MqttProvider>
    );
}
