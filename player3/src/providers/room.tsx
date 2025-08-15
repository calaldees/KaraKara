import React, { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useApi } from "../hooks/api";
import { MqttProvider, useSubscription } from "@shish2k/react-mqtt";
import { useLocalStorage } from "usehooks-ts";
import { current_and_future, mqtt_url } from "../utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";
import type { QueueItem } from "../types";

export interface RoomContextType {
    isAdmin: boolean;
    sessionId: string;
    queue: QueueItem[];
    setQueue: (q: QueueItem[]) => void;
    settings: Record<string, any>;
    connected: boolean;
}

/* eslint-disable react-refresh/only-export-components */
export const RoomContext = React.createContext<RoomContextType>(
    {} as RoomContextType,
);

function InternalRoomProvider(props: any) {
    const { roomName } = useParams();
    const { root, roomPassword } = useContext(ClientContext);
    const { now } = useContext(ServerContext);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [sessionId, setSessionId] = useLocalStorage<string>("session_id", "");
    const [fullQueue, setFullQueue] = useState<QueueItem[]>([]);
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [settings, setSettings] = useState<Record<string, any>>({});
    const { request } = useApi();

    // reset to default when room changes
    useEffect(() => {
        setFullQueue([]);
        setQueue([]);
        setSettings({});
    }, [roomName]);

    const { connected } = useSubscription(`room/${roomName}/queue`, (pkt) => {
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
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    password: roomPassword,
                }),
            },
            onAction: (response) => {
                setIsAdmin(response.is_admin);
                setSessionId(response.session_id);
            },
        });
    }, [root, roomName, roomPassword, request, setSessionId]);
    useEffect(() => {
        setQueue(current_and_future(now, fullQueue));
    }, [fullQueue, now]);

    return (
        <RoomContext
            value={{
                isAdmin,
                sessionId,
                queue,
                setQueue,
                settings,
                connected,
            }}
        >
            {props.children}
        </RoomContext>
    );
}

export function RoomProvider(props: any) {
    const { root } = useContext(ClientContext);
    return (
        <MqttProvider url={mqtt_url(root)}>
            <InternalRoomProvider>{props.children}</InternalRoomProvider>
        </MqttProvider>
    );
}
