import { MqttProvider, useSubscription } from "@shish2k/react-mqtt";
import { createContext, useEffect, useState } from "react";
import { useLocalStorage } from "usehooks-ts";

import { useApi } from "@/hooks/api";
import { useMemoObj } from "@/hooks/memo";
import type { Track } from "@/types";
import { mqtt_url } from "@/utils";

export interface ServerContextType {
    tracks: Record<string, Track>;
    downloadSize: number | null;
    downloadDone: number;
    connected: boolean;
}

/* eslint-disable react-refresh/only-export-components */
export const ServerContext = createContext<ServerContextType>(
    {} as ServerContextType,
);

function InternalServerProvider(props: any) {
    const [tracks, setTracks] = useState<Record<string, Track>>({});
    const [downloadSize, setDownloadSize] = useState<number | null>(null);
    const [downloadDone, setDownloadDone] = useState<number>(0);
    const [tracksUpdated, setTracksUpdated] = useLocalStorage<number>(
        "tracksUpdated",
        0,
    );
    const { request } = useApi();

    const { connected } = useSubscription(`global/tracks-updated`, (pkt) => {
        console.groupCollapsed(`mqtt_msg(${pkt.topic})`);
        console.log(pkt.json());
        console.groupEnd();
        setTracksUpdated(pkt.json()["tracks_json_mtime"]);
    });
    useEffect(() => {
        request({
            url: `/files/tracks.json?ver=${tracksUpdated}`,
            options: { credentials: "omit" },
            onAction: (result) => setTracks(result),
            onProgress: ({ done, size }) => {
                setDownloadDone(done);
                setDownloadSize(size);
            },
        });
    }, [request, tracksUpdated]);

    const ctxVal: ServerContextType = useMemoObj({
        tracks,
        downloadSize,
        downloadDone,
        connected,
    });
    return <ServerContext value={ctxVal}>{props.children}</ServerContext>;
}

export function ServerProvider(props: any) {
    return (
        <MqttProvider url={mqtt_url()}>
            <InternalServerProvider>{props.children}</InternalServerProvider>
        </MqttProvider>
    );
}
