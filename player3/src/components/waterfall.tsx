import { useContext } from "react";

import { RoomContext } from "../providers/room";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";
import type { Track } from "../types";
import { attachment_path } from "../utils";
import { useMemoArr } from "../hooks/memo";

function getNiceTracks(tracks: Record<string, Track>, n: number) {
    return Object.values(tracks)
        .filter((track) => track.tags["subs"]?.includes("soft"))
        .filter((track) => track.tags["aspect_ratio"]?.includes("16:9"))
        .filter((track) => track.tags["source_type"]?.includes("image"))
        .filter((track) => track.tags["vocaltrack"]?.includes("on"))
        .slice(0, n);
}

const MAX_WATERFALL = 25;
const RAND_ARR = Array.from({ length: MAX_WATERFALL * 2 }, () => Math.random());
export default function Waterfall() {
    const { settings } = useContext(RoomContext);
    const { root } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const items = useMemoArr(() => {
        return getNiceTracks(tracks, MAX_WATERFALL).map((track, n, arr) => ({
            src: attachment_path(root, track.attachments.image[0]),
            style: {
                animationDelay: ((n % 5) + RAND_ARR[n * 2]) * 2 + "s",
                animationDuration: 5 + RAND_ARR[n * 2 + 1] * 5 + "s",
                left: (n / arr.length) * 90 + "vw",
            },
        }));
    }, [tracks, root]);
    return (
        <>
            <div id={"splash"}>
                {items.map(({ src, style }, n) => (
                    <img key={n} alt="" src={src} style={style} />
                ))}
            </div>
            <h1>{settings["title"]}</h1>
        </>
    );
}
