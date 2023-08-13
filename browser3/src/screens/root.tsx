import { useContext } from "react";
import {
    createBrowserRouter,
    createRoutesFromElements,
    Outlet,
    Route,
    RouterProvider,
} from "react-router-dom";

import { Login } from "./login";
import { TrackList } from "./tracks";
import { TrackDetails } from "./track";
import { Queue } from "./queue";
import { Control } from "./control";
import { ConfigMenu } from "./config";
import { Printable } from "./printable";
import { RoomSettings } from "./settings";
import { RoomContext, RoomProvider } from "../providers/room";
import { ClientContext } from "../providers/client";
import { ServerContext } from "../providers/server";
import { Loading } from "./loading";

export const router = createBrowserRouter(
    createRoutesFromElements(
        <Route path="/" element={<Page />}>
            <Route index element={<Login />} />
            <Route path=":roomName" element={<Room />} loader={() => null}>
                <Route index element={<TrackList />} />
                <Route path="tracks/:trackId" element={<TrackDetails />} />
                <Route path="queue" element={<TracksOrQueueOrControl />} />
                <Route path="settings" element={<RoomSettings />} />
                <Route path="printable" element={<Printable />} />
            </Route>
        </Route>,
    ),
    { basename: process.env.NODE_ENV === "development" ? "/" : "/browser3" },
);

function Page() {
    const { showSettings } = useContext(ClientContext);

    return (
        <>
            <Outlet />
            {showSettings && <ConfigMenu />}
        </>
    );
}
function Room() {
    const { widescreen } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);

    return (
        <RoomProvider>
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
    const { widescreen } = useContext(ClientContext);
    return widescreen ? <TrackList /> : <QueueOrControl />;
}

function QueueOrControl(): React.ReactElement {
    const { isAdmin } = useContext(RoomContext);
    return isAdmin ? <Control /> : <Queue />;
}

export function Root(): React.ReactElement {
    //const { root } = useContext(ClientContext);
    return <RouterProvider router={router} />;
}
