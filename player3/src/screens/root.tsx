import { useContext } from "react";
import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
    RouterProvider,
    useParams,
} from "react-router-dom";
import { ServerTimeContext } from "@shish2k/react-use-servertime";

import { RoomContext, RoomProvider } from "@/providers/room";
import { ClientContext } from "@/providers/client";
import { ServerContext } from "@/providers/server";

import { ConfigMenu } from "./config";
import { TitleScreen } from "./title";
import { VideoScreen } from "./video";
import { PodiumScreen } from "./podium";
import { PreviewScreen } from "./preview";
import { percent } from "@/utils";

const router = createBrowserRouter(
    createRoutesFromElements(
        <Route path="/">
            <Route index element={<RoomWrapper />} />
            <Route path=":roomName" element={<RoomWrapper />} />
        </Route>,
    ),
    { basename: process.env.NODE_ENV === "development" ? "/" : "/player3" },
);

function RoomWrapper() {
    const { roomName } = useParams();
    return (
        <RoomProvider key={roomName}>
            <Room />
        </RoomProvider>
    );
}
function Room() {
    const { roomName } = useParams();
    const {
        podium,
        audioAllowed,
        setAudioAllowed,
        showSettings,
        setShowSettings,
        underscan,
    } = useContext(ClientContext);
    const { tracks, downloadSize, downloadDone, connected } =
        useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const { queue, isAdmin, settings } = useContext(RoomContext);

    let screen = <section>Unknown state :(</section>;

    if (Object.keys(tracks).length === 0)
        screen = (
            <section key="title" className={"screen_title"}>
                <h1>Loading {percent(downloadDone, downloadSize ?? 1)}</h1>
            </section>
        );
    else if (!audioAllowed && !podium)
        // podium doesn't play sound
        screen = (
            <section key="title" className={"screen_title"}>
                <h1>Click to Activate</h1>
            </section>
        );
    else if (!roomName)
        screen = (
            <section key="title" className={"screen_title"}>
                <h1>KaraKara</h1>
            </section>
        );
    else if (queue.length === 0) screen = <TitleScreen />;
    else if (podium)
        screen = (
            <PodiumScreen
                track={tracks[queue[0].track_id]}
                queue_item={queue[0]}
            />
        );
    else if (queue[0].start_time == null || queue[0].start_time > now)
        screen = (
            <PreviewScreen track={tracks[queue[0].track_id]} queue={queue} />
        );
    else
        screen = (
            <VideoScreen
                track={tracks[queue[0].track_id]}
                queue_item={queue[0]}
            />
        );

    const errors: string[] = [];
    if (!roomName) errors.push("No Room Set");
    if (!connected) errors.push("Not Connected");
    if (!isAdmin) errors.push("Not Admin");
    if (Object.keys(tracks).length === 0) errors.push("No Tracks");

    const css = ":root {--underscan: " + underscan + ";}";
    return (
        <div
            onClick={(_) => setAudioAllowed(true)}
            onDoubleClick={(_) => setShowSettings(true)}
        >
            <style>{css}</style>
            <main className={"theme-" + (settings["theme"] ?? "metalghosts")}>
                {errors.length > 0 && <h1 id={"error"}>{errors.join(", ")}</h1>}
                {screen}
            </main>
            {showSettings && <ConfigMenu />}
        </div>
    );
}

export function Root(): React.ReactElement {
    return <RouterProvider router={router} />;
}
