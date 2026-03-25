import { useContext, useEffect } from "react";
import {
    BrowserRouter,
    Outlet,
    Route,
    Routes,
    useParams,
} from "react-router-dom";

import { ConfigMenu } from "../components";
import { useWidescreen } from "../hooks/widescreen";
import { ClientContext } from "../providers/client";
import { PageProvider } from "../providers/page";
import { RoomContext, RoomProvider } from "../providers/room";
import { ServerContext } from "../providers/server";
import Control from "./control/control";
import Loading from "./loading/loading";
import Login from "./login/login";
import Printable from "./printable/printable";
import Queue from "./queue/queue";
import TrackDetails from "./track/track";
import TrackList from "./tracks/tracks";

function PageWrapper() {
    const { showSettings } = useContext(ClientContext);

    return (
        <PageProvider>
            <Outlet />
            {showSettings && <ConfigMenu />}
        </PageProvider>
    );
}

function RoomWrapper() {
    const { roomName } = useParams();
    const widescreen = useWidescreen();
    const { tracks } = useContext(ServerContext);

    return (
        <RoomProvider key={roomName}>
            {Object.keys(tracks).length > 0 ? (
                widescreen ? (
                    <div className={"widescreen"}>
                        <QueueOrControl />
                        <Outlet />
                    </div>
                ) : (
                    <Outlet />
                )
            ) : (
                <Loading />
            )}
        </RoomProvider>
    );
}

function TracksOrQueueOrControl(): React.ReactElement {
    const widescreen = useWidescreen();
    return widescreen ? <TrackList /> : <QueueOrControl />;
}

function QueueOrControl(): React.ReactElement {
    const { isAdmin } = useContext(RoomContext);
    return isAdmin ? <Control /> : <Queue />;
}

export function Root(): React.ReactElement {
    // Refresh the app if it has been open for more than
    // 12 hours to avoid stale API clients
    useEffect(() => {
        const interval = setInterval(() => {
            if (performance.now() > 12 * 60 * 60 * 1000) {
                window.location.reload();
            }
        }, 60 * 1000); // check every minute
        return () => clearInterval(interval);
    }, []);

    const basename = process.env.NODE_ENV === "development" ? "/" : "/browser3";
    return (
        <BrowserRouter basename={basename}>
            <Routes>
                <Route path="/" element={<PageWrapper />}>
                    <Route index element={<Login />} />
                    <Route path=":roomName" element={<RoomWrapper />}>
                        <Route index element={<TrackList />} />
                        <Route
                            path="tracks/:trackId"
                            element={<TrackDetails />}
                        />
                        <Route
                            path="queue"
                            element={<TracksOrQueueOrControl />}
                        />
                        <Route path="settings" element={<RoomSettings />} />
                        <Route path="printable" element={<Printable />} />
                    </Route>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}
