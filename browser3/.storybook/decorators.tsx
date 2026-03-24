import {
    ServerTimeContext,
    ServerTimeContextType,
} from "@shish2k/react-use-servertime";
import { useState } from "react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import type { Decorator } from "storybook-react-rsbuild";

import { queue, settings, tracks } from "../src/utils/test_data";

import { ClientContext, ClientContextType } from "../src/providers/client";
import { PageContext, PageContextType } from "../src/providers/page";
import { RoomContext, RoomContextType } from "../src/providers/room";
import { ServerContext, ServerContextType } from "../src/providers/server";

import type { QueueItem } from "../src/types";

type TestProps = {
    client?: Partial<ClientContextType>;
    server?: Partial<ServerContextType>;
    serverTime?: Partial<ServerTimeContextType>;
    room?: Partial<RoomContextType>;
    page?: Partial<PageContextType>;
    children?: any;
};

function TestHarness(props: TestProps) {
    const [queue_, _setQueue] = useState(queue as QueueItem[]);
    const [optimisticQueue, setOptimisticQueue] = useState<QueueItem[] | null>(
        null,
    );

    const cc: ClientContextType = {
        roomPassword: "",
        setRoomPassword: () => {},
        showSettings: false,
        setShowSettings: () => {},
        booth: false,
        setBooth: () => {},
        performerName: "",
        setPerformerName: () => {},
        bookmarks: [],
        addBookmark: () => {},
        removeBookmark: () => {},
        notification: null,
        setNotification: () => {},
        ...props.client,
    };
    const sc: ServerContextType = {
        tracks: tracks,
        downloadSize: 100,
        downloadDone: 100,
        connected: true,
        ...props.server,
    };
    const rc: RoomContextType = {
        isAdmin: true,
        queue: optimisticQueue ?? queue_,
        fullQueue: queue_,
        setOptimisticQueue,
        settings: settings,
        trackList: Object.values(tracks),
        ...props.room,
    };
    const st: ServerTimeContextType = {
        now: 1000,
        offset: 1.5,
        tweak: 1,
        setTweak: (_n: number) => {},
        ...props.serverTime,
    };
    const pc: PageContextType = {
        roomName: "test",
        hasBack: false,
        navigate: (() => {}) as any,
        ...props.page,
    };

    const router = createMemoryRouter(
        [
            {
                path: "/:roomName",
                element: (
                    <PageContext value={pc}>
                        <RoomContext value={rc}>{props.children}</RoomContext>
                    </PageContext>
                ),
            },
        ],
        { initialEntries: [`/test`] },
    );

    return (
        <ServerTimeContext value={st}>
            <ClientContext value={cc}>
                <ServerContext value={sc}>
                    <RouterProvider router={router} />
                </ServerContext>
            </ClientContext>
        </ServerTimeContext>
    );
}

export const withTestHarness: Decorator = (Story, context) => {
    const { parameters } = context;
    const testProps = parameters.testProps || {};

    return (
        <TestHarness
            client={testProps.client ?? {}}
            server={testProps.server ?? {}}
            serverTime={testProps.serverTime ?? {}}
            room={testProps.room ?? {}}
        >
            <Story />
        </TestHarness>
    );
};
