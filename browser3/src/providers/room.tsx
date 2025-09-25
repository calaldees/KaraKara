import { useSubscription } from "@shish2k/react-mqtt";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { UAParser } from "ua-parser-js";
import { useLocalStorage } from "usehooks-ts";

import { useApi } from "../hooks/api";
import { useMemoObj } from "../hooks/memo";
import { apply_hidden, apply_tags } from "../track_finder";
import type { QueueItem, Track } from "../types";
import { current_and_future, normalise_cmp } from "../utils";
import { ClientContext } from "./client";
import { ServerContext } from "./server";

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
    const { roomPassword } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [sessionId, setSessionId] = useLocalStorage<string>("session_id", "");
    const [fullQueue, setFullQueue] = useState<QueueItem[]>([]);
    const [optimisticQueue, setOptimisticQueue] = useState<QueueItem[] | null>(
        null,
    );
    const [settings, setSettings] = useState<Record<string, any>>({});
    const { request } = useApi();
    const navigate = useNavigate();
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
    }, [roomName, roomPassword, request, setSessionId, navigate]);

    useEffect(() => {
        const ua = UAParser();
        const an = {
            event: "open_room",
            ua: ua,
            dev: process.env.NODE_ENV === "development" ? true : false,
            session: sessionId,
            admin: isAdmin,
            room: roomName,
        };
        request({
            url: `/api/analytics.json`,
            options: {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(an),
            },
        });
    }, [request, roomName, sessionId, isAdmin]);

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
