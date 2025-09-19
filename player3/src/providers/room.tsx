import React, { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useApi } from "../hooks/api";
import { useSubscription } from "@shish2k/react-mqtt";
import { useLocalStorage } from "usehooks-ts";
import { current_and_future } from "../utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";
import type { QueueItem } from "../types";

export interface RoomContextType {
    isAdmin: boolean;
    sessionId: string;
    queue: QueueItem[];
    setQueue: (q: QueueItem[]) => void;
    settings: Record<string, any>;
}

/* eslint-disable react-refresh/only-export-components */
export const RoomContext = React.createContext<RoomContextType>(
    {} as RoomContextType,
);

export function RoomProvider(props: any) {
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
        const newQueue = current_and_future(now, fullQueue);
        // Only update if something has actually changed, to avoid
        // unnecessary re-renders every time "now" changes but the
        // contents of the queue are the same.
        // setQueue(newQueue);
        setQueue((prevQueue) => {
            if (
                prevQueue.length === newQueue.length &&
                prevQueue.every((item, idx) => item === newQueue[idx])
            ) {
                return prevQueue;
            }
            return newQueue;
        });
    }, [fullQueue, now]);

    return (
        <RoomContext
            value={{
                isAdmin,
                sessionId,
                queue,
                setQueue,
                settings,
            }}
        >
            {props.children}
        </RoomContext>
    );
}
