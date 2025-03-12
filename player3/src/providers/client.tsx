import React, { useEffect, useState } from "react";
import { useWakeLock } from "react-screen-wake-lock";
import { useLocalStorage } from "usehooks-ts";

export interface ClientContextType {
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
    underscan: string;
    setUnderscan: (n: string) => void;
};

export const ClientContext = React.createContext<ClientContextType>({
    root: "",
    setRoot: (_) => null,
    roomPassword: "",
    setRoomPassword: (_) => null,
    showSettings: false,
    setShowSettings: (_) => null,
    podium: false,
    setPodium: (_) => null,
    blankPodium: false,
    setBlankPodium: (_) => null,
    audioAllowed: false,
    setAudioAllowed: (_) => null,
    fullscreen: false,
    setFullscreen: (_) => null,
    setNotification: (_) => null,
    wakeLock: "",
    underscan: "0em",
    setUnderscan: (_) => null,
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
    const [underscan, setUnderscan] = useLocalStorage<string>(
        "underscan",
        "0em 0em",
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
        if (isSupported) {
            void request().then(() => {
                setWakeLock("Acquired");
            });
        }
    }, [isSupported, request]);

    function setNotification(n: any) {
        console.log(n);
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
                underscan,
                setUnderscan,
            }}
        >
            {props.children}
        </ClientContext.Provider>
    );
}
