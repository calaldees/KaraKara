import React, { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useApi } from "../hooks/api";
import { useMqtt, useMqttSubscription } from "../hooks/mqtt";
import { current_and_future, mqtt_url } from "../utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";

export type RoomContextType = {
    isAdmin: boolean;
    sessionId: string;
    queue: QueueItem[];
    setQueue: (q: QueueItem[]) => void,
    settings: Record<string, any>;
};

export const RoomContext = React.createContext<RoomContextType>({
    isAdmin: false,
    sessionId: "",
    queue: [],
    setQueue: () => {},
    settings: {},
});

export function RoomProvider(props: any) {
    const { roomName } = useParams();
    const { root, roomPassword } = useContext(ClientContext);
    const { now } = useContext(ServerContext);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [sessionId, setSessionId] = useState<string>("");
    const [fullQueue, setFullQueue] = useState<QueueItem[]>([]);
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [settings, setSettings] = useState<Record<string, any>>({});
    const { request } = useApi();

    const { client } = useMqtt(mqtt_url(root));
    useMqttSubscription(client, `room/${roomName}/queue`, (msg) => {
        setFullQueue(msg);
    });
    useMqttSubscription(client, `room/${roomName}/settings`, (msg) => {
        setSettings(msg);
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
            },
        });
    }, [root, roomName, roomPassword]);
    useEffect(() => {
        setQueue(current_and_future(now, fullQueue))
    }, [fullQueue, now])

    return (
        <RoomContext.Provider
            value={{
                isAdmin,
                sessionId,
                queue,
                setQueue,
                settings,
            }}
        >
            {props.children}
        </RoomContext.Provider>
    );
}
