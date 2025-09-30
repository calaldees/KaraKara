import { useMemoObj } from "@/hooks/memo";
import { createContext, useCallback, useEffect, useState } from "react";
import { useWakeLock } from "react-screen-wake-lock";
import { useLocalStorage, useSessionStorage } from "usehooks-ts";

export interface ClientContextType {
    roomPassword: string;
    setRoomPassword: (n: string) => void;
    showSettings: boolean;
    setShowSettings: (n: boolean) => void;
    podium: boolean;
    setPodium: (b: boolean) => void;
    audioAllowed: boolean;
    setAudioAllowed: (b: boolean) => void;
    fullscreen: boolean;
    setFullscreen: (b: boolean) => void;
    setNotification: (n: any) => void;
    wakeLock: string;
    underscan: string;
    setUnderscan: (n: string) => void;
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
    const [underscan, setUnderscan] = useSessionStorage<string>(
        "underscan",
        "0px",
    );
    const [showSettings, setShowSettings] = useState<boolean>(false);
    const [podium, setPodium] = useSessionStorage<boolean>("podium", false);
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

    const setNotification = useCallback((n: any) => {
        console.log(n);
    }, []);

    const ctxVal: ClientContextType = useMemoObj({
        roomPassword,
        setRoomPassword,
        showSettings,
        setShowSettings,
        podium,
        setPodium,
        audioAllowed,
        setAudioAllowed,
        fullscreen,
        setFullscreen,
        setNotification,
        wakeLock,
        underscan,
        setUnderscan,
    });
    return <ClientContext value={ctxVal}>{props.children}</ClientContext>;
}
