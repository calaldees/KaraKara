import { useContext, useMemo } from "react";
import { attachment_path } from "../utils";
import { EventInfo, JoinInfo } from "./_common";
import { RoomContext } from "../providers/room";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";

// eslint-disable-next-line
function StatsTable() {
    const { tracks } = useContext(ServerContext);
    const ts = Object.values(tracks);
    const stats = {
        tracks: ts.length,
        lines: ts.map((t) => t.lyrics.length).reduce((sum, n) => sum + n, 0),
        shows: new Set(ts.map((t) => t.tags.from?.[0])).size,
        hours: Math.floor(
            ts.map((t) => t.duration).reduce((sum, n) => sum + n, 0) / 60 / 60,
        ),
    };
    return (
        <h2>
            <table>
                <tbody>
                    {Object.entries(stats).map(([key, value]) => (
                        <tr key={key}>
                            <th>
                                <strong>{value}</strong>
                            </th>
                            <td>{key}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </h2>
    );
}

function getNiceTracks(tracks: Record<string, Track>, n: number) {
    const good_tracks = [
        "07_Ghost_OP1_Aka_no_Kakera",
        "Air_OP_Tori_no_Uta",
        "Ah_My_Goddess_TV_ED1_Negai",
        "Jojo_s_Bizarre_Adventure_Stone_Ocean_OP_Stone_Ocean",
        "Gekiganger_3_OP_Seigi_no_Robot_Gekiganger_3",
        "Naruto_OP4_Go",
    ]
        .map((t) => tracks[t])
        .filter((t) => t);
    const first_tracks = Object.values(tracks)
        // ignore instrumental tracks, because instrumentals
        // tend to have hard-subs, which makes ugly thumbnails
        .filter((track) => track.tags.vocaltrack?.[0] !== "off")
        .slice(0, n);
    return [...good_tracks, ...first_tracks].slice(0, n);
}

function Waterfall() {
    const { settings } = useContext(RoomContext);
    const { root } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const items = useMemo(() => {
        return getNiceTracks(tracks, 25).map((track, n, arr) => ({
            src: attachment_path(root, track.attachments.image[0]),
            style: {
                animationDelay: ((n % 5) + Math.random()) * 2 + "s",
                animationDuration: 5 + Math.random() * 5 + "s",
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
