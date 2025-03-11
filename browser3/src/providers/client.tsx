import React, { useState } from "react";
import { useLocalStorage, useMediaQuery } from "usehooks-ts";

type Notification = {
    text: string;
    style: string;
} | null;

export type ClientContextType = {
    root: string;
    setRoot: (_: string) => void;
    roomPassword: string;
    setRoomPassword: (_: string) => void;
    showSettings: boolean;
    setShowSettings: (_: boolean) => void;
    booth: boolean;
    setBooth: (_: boolean) => void;
    widescreen: boolean;
    performerName: string;
    setPerformerName: (_: string) => void;
    bookmarks: string[];
    addBookmark: (_: string) => void;
    removeBookmark: (_: string) => void;
    notification: Notification;
    setNotification: (_: Notification) => void;
};

export const ClientContext = React.createContext<ClientContextType>({
    root: "",
    setRoot: (_) => null,
    roomPassword: "",
    setRoomPassword: (_) => null,
    showSettings: false,
    setShowSettings: (_) => null,
    booth: false,
    setBooth: (_) => null,
    widescreen: false,
    performerName: "",
    setPerformerName: (_) => null,
    bookmarks: [],
    addBookmark: (_) => null,
    removeBookmark: (_) => null,
    notification: null,
    setNotification: (_) => null,
});

export function ClientProvider(props: any) {
    // If we're running stand-alone, then use the main karakara.uk
    // server; else we're probably running as part of the full-stack,
    // in which case we should use server we were loaded from.
    const auto_root =
        process.env.NODE_ENV === "development"
            ? "https://karakara.uk"
            : window.location.protocol + "//" + window.location.host;
    const [root, setRoot] = useLocalStorage<string>("root", auto_root);
    const [roomPassword, setRoomPassword] = useLocalStorage<string>(
        "room_password",
        "",
    );
    const [showSettings, setShowSettings] = useState<boolean>(false);
    const [booth, setBooth] = useLocalStorage<boolean>("booth", false);
    const widescreen = useMediaQuery(
        "(min-width: 780px) and (min-aspect-ratio: 1/1)",
    );
    const [bookmarks, setBookmarks] = useLocalStorage<string[]>(
        "bookmarks",
        [],
    );
    const [performerName, setPerformerName] = useLocalStorage<string>(
        "performer_name",
        "",
    );
    const [notification, setNotification] = useState<Notification>(null);

    function addBookmark(track_id: string): void {
        setBookmarks([...bookmarks, track_id]);
    }
    function removeBookmark(track_id: string): void {
        setBookmarks(bookmarks.filter((x) => x !== track_id));
    }

    return (
        <ClientContext.Provider
            value={{
                root,
                setRoot,
                roomPassword,
                setRoomPassword,
                showSettings,
                setShowSettings,
                booth,
                setBooth,
                widescreen,
                performerName,
                setPerformerName,
                bookmarks,
                addBookmark,
                removeBookmark,
                notification,
                setNotification,
            }}
        >
            {props.children}
        </ClientContext.Provider>
    );
}
