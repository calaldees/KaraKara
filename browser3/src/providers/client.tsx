import { createContext, useCallback, useState } from "react";
import { useLocalStorage } from "usehooks-ts";
import { useMemoObj } from "../hooks/memo";

type Notification = {
    text: string;
    style: "ok" | "warning" | "error";
} | null;

export interface ClientContextType {
    roomPassword: string;
    setRoomPassword: (_: string) => void;
    showSettings: boolean;
    setShowSettings: (_: boolean) => void;
    booth: boolean;
    setBooth: (_: boolean) => void;
    performerName: string;
    setPerformerName: (_: string) => void;
    bookmarks: string[];
    addBookmark: (_: string) => void;
    removeBookmark: (_: string) => void;
    notification: Notification;
    setNotification: (_: Notification) => void;
}

/* eslint-disable react-refresh/only-export-components */
export const ClientContext = createContext<ClientContextType>(
    {} as ClientContextType,
);

export function ClientProvider(props: any) {
    const [roomPassword, setRoomPassword] = useLocalStorage<string>(
        "room_password",
        "",
    );
    const [showSettings, setShowSettings] = useState<boolean>(false);
    const [booth, setBooth] = useLocalStorage<boolean>("booth", false);
    const [bookmarks, setBookmarks] = useLocalStorage<string[]>(
        "bookmarks",
        [],
    );
    const [performerName, setPerformerName] = useLocalStorage<string>(
        "performer_name",
        "",
    );
    const [notification, setNotification] = useState<Notification>(null);

    const addBookmark = useCallback(
        (track_id: string): void => {
            setBookmarks((prev: string[]) => [...prev, track_id]);
        },
        [setBookmarks],
    );

    const removeBookmark = useCallback(
        (track_id: string): void => {
            setBookmarks((prev: string[]) =>
                prev.filter((x) => x !== track_id),
            );
        },
        [setBookmarks],
    );

    const ctxVal: ClientContextType = useMemoObj({
        roomPassword,
        setRoomPassword,
        showSettings,
        setShowSettings,
        booth,
        setBooth,
        performerName,
        setPerformerName,
        bookmarks,
        addBookmark,
        removeBookmark,
        notification,
        setNotification,
    });
    return <ClientContext value={ctxVal}>{props.children}</ClientContext>;
}
