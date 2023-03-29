import { useEffect, useState } from "react";

export function useServerTime(url: string, interval: number) {
    const [offset, setOffset] = useState<number>(0);
    const [now, setNow] = useState<number>(Date.now() / 1000);

    useEffect(() => {
        fetch(url, { credentials: "omit" })
            .then((r) => r.json())
            .then((t) => setOffset(Date.now() / 1000 - t));
    }, [url]);

    useEffect(() => {
        const x = setInterval(() => {
            setNow(Date.now() / 1000 - offset);
        }, interval);
        return () => {
            clearInterval(x);
        };
    }, [interval]);

    return { now };
}
