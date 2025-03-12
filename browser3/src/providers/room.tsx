import React, { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useApi } from "../hooks/api";
import { MqttProvider, useSubscription } from "@shish2k/react-mqtt";
import { useLocalStorage } from "usehooks-ts";
import { current_and_future, mqtt_url, normalise_cmp } from "../utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";
import { apply_hidden, apply_tags } from "../track_finder";
import type { Track, QueueItem } from "../types";

export interface RoomContextType {
    trackList: Track[];
    isAdmin: boolean;
    sessionId: string;
    queue: QueueItem[];
    fullQueue: QueueItem[];
    setQueue: (q: QueueItem[]) => void;
    settings: Record<string, any>;
    connected: boolean;
};

export const RoomContext = React.createContext<RoomContextType>({
    trackList: [],
    isAdmin: false,
    sessionId: "",
    queue: [],
    fullQueue: [],
    setQueue: () => {},
    settings: {},
    connected: false,
});

function InternalRoomProvider(props: any) {
    const { roomName } = useParams();
    const { root, roomPassword } = useContext(ClientContext);
    const { now, tracks } = useContext(ServerContext);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [sessionId, setSessionId] = useLocalStorage<string>("session_id", "");
    const [fullQueue, setFullQueue] = useState<QueueItem[]>([]);
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [settings, setSettings] = useState<Record<string, any>>({});
    const { request } = useApi();
    const navigate = useNavigate();

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

    const hiddenTags = settings["hidden_tags"];
    const forcedTags = settings["forced_tags"];
    const trackList = useMemo(() => {
        // going from a dict of "all tracks known to the system" to a list of
        // "all tracks active for this room, sorted alphabetically" takes 15ms,
        // so let's do that and cache the results, and then the user can search
        // within this pre-filtered / pre-sorted list (which takes 1ms)
        let trackList = Object.values(tracks);
        if (hiddenTags) trackList = apply_hidden(trackList, hiddenTags);
        if (forcedTags) trackList = apply_tags(trackList, forcedTags);
        trackList = trackList.sort((a, b) =>
            normalise_cmp(a.tags.title[0], b.tags.title[0]),
        );
        return trackList;
    }, [tracks, hiddenTags, forcedTags]);

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
                    create: roomPassword !== "",
                }),
            },
            onAction: (response) => {
                setIsAdmin(response.is_admin);
                setSessionId(response.session_id);
            },
            onException: () => {
                // request() function will already have shown an error,
                // so we just need to redirect to root
                void navigate("/");
            },
        });
    }, [root, roomName, roomPassword, request, setSessionId, navigate]);
    useEffect(() => {
        setQueue(current_and_future(now, fullQueue));
    }, [fullQueue, now]);

    return (
        <RoomContext.Provider
            value={{
                trackList,
                isAdmin,
                sessionId,
                queue,
                fullQueue,
                setQueue,
                settings,
                connected,
            }}
        >
            {props.children}
        </RoomContext.Provider>
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
