// ***********************************************************
// This example support/component.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import "./commands";

// Alternatively you can use CommonJS syntax:
// require('./commands')

import { mount } from "cypress/react18";
import { MountOptions, MountReturn } from "cypress/react";

import React, { useState } from "react";
import { ClientContext, ClientContextType } from "../../src/providers/client";
import { RoomContext, RoomContextType } from "../../src/providers/room";
import { ServerContext, ServerContextType } from "../../src/providers/server";
import { createMemoryRouter, RouterProvider } from "react-router-dom";

import "../../src/static/style.scss";
import tracks from "../../cypress/fixtures/small_tracks.json";
import queue from "../../cypress/fixtures/small_queue.json";
import settings from "../../cypress/fixtures/small_settings.json";
import type { QueueItem } from "../../src/types";

// Cypress.Commands.add('mount', mount)

// Augment the Cypress namespace to include type definitions for
// your custom command.
// Alternatively, can be defined in cypress/support/component.d.ts
// with a <reference path="./component" /> at the top of your spec.
declare global {
    namespace Cypress {
        interface Chainable<Subject> {
            mount(
                component: React.ReactNode,
                options?: MountOptions | TestProps,
            ): Cypress.Chainable<MountReturn>;
        }
    }
}

type TestProps = {
    client: Partial<ClientContextType>;
    server: Partial<ServerContextType>;
    room: Partial<RoomContextType>;
    children?: any;
};
function TestHarness(props: TestProps) {
    const cc = {
        root: "https://karakara.uk",
        setRoot: () => {},
        roomPassword: "",
        setRoomPassword: () => {},
        showSettings: false,
        setShowSettings: () => {},
        booth: false,
        setBooth: () => {},
        widescreen: false,
        performerName: "",
        setPerformerName: () => {},
        bookmarks: [],
        addBookmark: () => {},
        removeBookmark: () => {},
        notification: null,
        setNotification: () => {},
        ...props.client,
    };
    const sc = {
        tracks: tracks,
        downloadSize: 100,
        downloadDone: 100,
        now: 1234,
        ...props.server,
    };
    const [queue_, setQueue] = useState(queue as QueueItem[]);
    const rc = {
        isAdmin: true,
        sessionId: "admin",
        queue: queue_,
        fullQueue: queue_,
        setQueue: setQueue,
        settings: settings,
        trackList: Object.values(tracks),
        connected: true,
        ...props.room,
    };

    const router = createMemoryRouter(
        [
            {
                path: "/:roomName",
                element: React.createElement(RoomContext.Provider, {
                    value: rc,
                    children: props.children,
                }),
            },
        ],
        { initialEntries: [`/test`] },
    );
    const router_provider = React.createElement(RouterProvider, {
        router: router,
    });
    const server_provider = React.createElement(ServerContext.Provider, {
        value: sc,
        children: router_provider,
    });
    const client_provider = React.createElement(ClientContext.Provider, {
        value: cc,
        children: server_provider,
    });
    return client_provider;
}

Cypress.Commands.add("mount", (component, options: any = {}) => {
    const provider = React.createElement(TestHarness, {
        client: options.client ?? {},
        server: options.server ?? {},
        room: options.room ?? {},
        children: component,
    });
    return mount(provider, options);
});
