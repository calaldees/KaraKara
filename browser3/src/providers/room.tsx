import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useApi } from "../hooks/api";
import { useSubscription } from "@shish2k/react-mqtt";
import { useLocalStorage } from "usehooks-ts";
import { current_and_future, normalise_cmp } from "../utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";
import { apply_hidden, apply_tags } from "../track_finder";
import type { Track, QueueItem } from "../types";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useMemoObj } from "../hooks/memo";

export interface RoomContextType {
    trackList: Track[];
    isAdmin: boolean;
    sessionId: string;
    queue: QueueItem[];
    fullQueue: QueueItem[];
    setOptimisticQueue: (q: QueueItem[] | null) => void;
    settings: Record<string, any>;
}

/* eslint-disable react-refresh/only-export-components */
export const RoomContext = createContext<RoomContextType>(
    {} as RoomContextType,
);

export function RoomProvider(props: any) {
    const { roomName } = useParams();
    const { root, roomPassword } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [sessionId, setSessionId] = useLocalStorage<string>("session_id", "");
    const [fullQueue, setFullQueue] = useState<QueueItem[]>([]);
    const [optimisticQueue, setOptimisticQueue] = useState<QueueItem[] | null>(
        null,
    );
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [settings, setSettings] = useState<Record<string, any>>({});
    const { request } = useApi();
    const navigate = useNavigate();

    useSubscription(`room/${roomName}/queue`, (pkt) => {
        console.groupCollapsed(`mqtt_msg(${pkt.topic})`);
        console.log(pkt.json());
        console.groupEnd();
        setOptimisticQueue(null);
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

    // This component re-renders every time "now" changes, but
    // we don't want that to cause re-renders in the consumers
    const ctxVal: RoomContextType = useMemoObj({
        trackList,
        isAdmin,
        sessionId,
        queue: optimisticQueue ?? queue,
        fullQueue,
        setOptimisticQueue,
        settings,
    });
    return <RoomContext value={ctxVal}>{props.children}</RoomContext>;
}
