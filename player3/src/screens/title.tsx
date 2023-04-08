import { useContext, useMemo } from "react";
import { attachment_path } from "../utils";
import { EventInfo, JoinInfo } from "./_common";
import { RoomContext } from "../providers/room";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";

function StatsTable() {
    const { tracks } = useContext(ServerContext);
    const ts = Object.values(tracks);
    const stats = {
        tracks: ts.length,
        lines: ts.map(t => t.lyrics.length).reduce((sum, n) => sum + n, 0),
        shows: new Set(ts.map(t => t.tags.from?.[0])).size,
        hours: Math.floor(ts.map(t => t.duration).reduce((sum, n) => sum + n, 0) / 60 / 60),
    }
    return <h2>
        <table>
            <tbody>
                {Object.entries(stats).map(([key, value]) =>
                    <tr key={key}><th><strong>{value}</strong></th><td>{key}</td></tr>
                )}
            </tbody>
        </table>
    </h2>;
}

function Waterfall() {
    const { settings } = useContext(RoomContext);
    const { root } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const items = useMemo(() => {
        return Object.values(tracks)
            // ignore instrumental tracks, because instrumentals
            // tend to have hard-subs, which makes ugly thumbnails
            .filter((track) => track.tags.vocaltrack?.[0] != "off")
            .slice(0, 25)
            .map((track) => track.attachments.image[0])
            .map((image, n, arr) => (
                {
                    src: attachment_path(root, image),
                    style: {
                        animationDelay: ((n % 5) + Math.random()) * 2 + "s",
                        animationDuration: 5 + Math.random() * 5 + "s",
                        left: (n / arr.length) * 90 + "vw",
                    }
                }
            ))
    }, [tracks])
    return (
        <>
            <div id={"splash"}>
                {items.map(({ src, style }, n) => <img key={n} src={src} style={style} />)}
            </div>
            <h1>{settings["title"]}</h1>
        </>
    );
}

export function TitleScreen() {
    let splash = null;
    if (true) splash = <Waterfall />;
    return (
        <section key="title" className={"screen_title"}>
            {splash}
            <JoinInfo />
            <EventInfo />
        </section>
    );
}
