import { useContext, useMemo } from "react";
import { attachment_path } from "../utils";
import { EventInfo, JoinInfo } from "./_common";
import { RoomContext } from "../providers/room";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";

export function Splash() {
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
        <div id={"splash"}>
            {items.map(({ src, style }, n) => <img key={n} src={src} style={style} />)}
        </div>
    );
}

export function TitleScreen() {
    const { settings } = useContext(RoomContext);
    return (
        <section key="title" className={"screen_title"}>
            <Splash />
            <JoinInfo />
            <h1>{settings["title"]}</h1>
            <EventInfo />
        </section>
    );
}
