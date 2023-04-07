import React, { useEffect, useState } from "react";
import { useWakeLock } from "react-screen-wake-lock";
import { useLocalStorage } from "usehooks-ts";

export type ClientContextType = {
    root: string;
    setRoot: (n: string) => void;
    roomPassword: string;
    setRoomPassword: (n: string) => void;
    showSettings: boolean;
    setShowSettings: (n: boolean) => void;
    podium: boolean;
    setPodium: (b: boolean) => void;
    blankPodium: boolean;
    setBlankPodium: (b: boolean) => void;
    audioAllowed: boolean;
    setAudioAllowed: (b: boolean) => void;
    fullscreen: boolean;
    setFullscreen: (b: boolean) => void;
    setNotification: (n: any) => void;
    wakeLock: string;
};

export const ClientContext = React.createContext<ClientContextType>({
    root: "",
    setRoot: (x) => null,
    roomPassword: "",
    setRoomPassword: (x) => null,
    showSettings: false,
    setShowSettings: (x) => null,
    podium: false,
    setPodium: (x) => null,
    blankPodium: false,
    setBlankPodium: (x) => null,
    audioAllowed: false,
    setAudioAllowed: (x) => null,
    fullscreen: false,
    setFullscreen: (x) => null,
    setNotification: (x) => null,
    wakeLock: "",
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
    const [podium, setPodium] = useState<boolean>(false);
    const [blankPodium, setBlankPodium] = useState<boolean>(false);
    const [audioAllowed, setAudioAllowed] = useState<boolean>(false);
    const [fullscreen, setFullscreen] = useState<boolean>(false);
    const [wakeLock, setWakeLock] = useState<string>("Not supported");

    const { isSupported, request } = useWakeLock({
        onRequest: () => setWakeLock("Requested"),
        onError: () => setWakeLock("Error"),
        onRelease: () => setWakeLock("Released"),
    });
    useEffect(() => {
        if(isSupported) {
            request().then(() => {
                setWakeLock("Acquired")
            });
        }
    }, [isSupported])

    function setNotification(n: any) { console.log(n); }

    return (
        <ClientContext.Provider
            value={{
                root,
                setRoot,
                roomPassword,
                setRoomPassword,
                showSettings,
                setShowSettings,
                podium,
                setPodium,
                blankPodium,
                setBlankPodium,
                audioAllowed,
                setAudioAllowed,
                fullscreen,
                setFullscreen,
                setNotification,
                wakeLock,
            }}
        >
            {props.children}
        </ClientContext.Provider>
    );
}
