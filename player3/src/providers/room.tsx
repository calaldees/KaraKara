import { useSubscription } from "@shish2k/react-mqtt";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { useMemoObj } from "@/hooks/memo";
import type { QueueItem } from "@/types";
import { current_and_future } from "@/utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";

export interface RoomContextType {
    isAdmin: boolean;
    queue: QueueItem[];
    settings: Record<string, any>;
}

/* eslint-disable react-refresh/only-export-components */
export const RoomContext = createContext<RoomContextType>(
    {} as RoomContextType,
);

export function RoomProvider(props: any) {
    const { roomName } = useParams();
    const { roomPassword } = useContext(ClientContext);
    const { now } = useContext(ServerTimeContext);
    const { request } = useContext(ServerContext);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [fullQueue, setFullQueue] = useState<QueueItem[]>([]);
    const [settings, setSettings] = useState<Record<string, any>>({});
    const newQueue = useMemo(
        () => current_and_future(now, fullQueue),
        [now, fullQueue],
    );
    // ignore eslint warning - we don't actually care if newQueue
    // changes, we only care if the _value_ changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const queue = useMemo(() => newQueue, [JSON.stringify(newQueue)]);

    useSubscription(`room/${roomName}/queue`, (pkt) => {
        console.groupCollapsed(`mqtt_msg(${pkt.topic})`);
        console.log(pkt.json());
        console.groupEnd();
        setFullQueue(pkt.json());
    });
    useSubscription(`room/${roomName}/settings`, (pkt) => {
        console.groupCollapsed(`mqtt_msg(${pkt.topic})`);
        console.log(pkt.json());
        console.groupEnd();
        setSettings(pkt.json());
    });

    useEffect(() => {
        request({
            function: "login",
            options: {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    password: roomPassword,
                }),
            },
            onAction: (response) => {
                setIsAdmin(response.is_admin);
            },
        });
    }, [roomName, roomPassword, request]);

    // This component re-renders every time "now" changes, but
    // we don't want that to cause re-renders in the consumers
    const ctxVal: RoomContextType = useMemoObj({
        isAdmin,
        queue,
        settings,
    });
    return <RoomContext value={ctxVal}>{props.children}</RoomContext>;
}
