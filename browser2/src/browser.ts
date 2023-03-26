/// <reference path='./browser.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import { SyncedInterval } from "@shish2k/hyperapp-synced-interval";
import {
    LocalStorageLoader,
    LocalStorageSaver,
} from "@shish2k/hyperapp-localstorage";

import { Root } from "./screens/root";
import { BeLoggedIn, getMQTTListener, ResizeListener } from "./subs";
import { ApiRequest } from "./effects";
import { CastSender } from "./cc_sender";

declare global {
    namespace JSX {
        interface IntrinsicElements {
            [elemName: string]: any;
        }
    }
}

// If we're running stand-alone, then use the main karakara.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.uk"
        : window.location.protocol + "//" + window.location.host;

function isWidescreen() {
    return window.innerWidth > 780 && window.innerWidth > window.innerHeight;
}

let state: State = {
    // global
    root: auto_root,
    root_edit: auto_root,
    screen: "explore",
    notification: null,
    show_settings: false,
    download_size: null,
    download_done: 0,
    booth: false,
    widescreen: isWidescreen(),
    scroll_stack: [],
    now: Date.now() / 1000,
    casting: false,

    // login
    session_id: null,
    room_name: "",
    room_name_edit: "",
    room_password: "",
    room_password_edit: "",
    loading: false,
    is_admin: false,

    // track list
    track_list: {},
    search: "",
    filters: [],
    expanded: null,

    // track
    track_id: null,
    performer_name: "",
    action: null,

    // queue
    queue: [],
    drop_source: null,
    drop_target: null,

    // bookmarks
    bookmarks: [],

    // settings
    settings: {
        track_space: 15.0,
        forced_tags: [],
        hidden_tags: ["red:duplicate"],
        title: "KaraKara",
        preview_volume: 0.2,
        validation_event_start_datetime: undefined,
        validation_event_end_datetime: undefined,
        validation_performer_names: [],
        coming_soon_track_count: 10,
    },
    settings_edit: {},
};

const init: Dispatchable = [
    state,
    LocalStorageLoader("performer_name", (state, x) => ({
        ...state,
        performer_name: x,
    })),
    LocalStorageLoader("room_password", (state, x) => ({
        ...state,
        room_password_edit: x,
        room_password: x,
    })),
    LocalStorageLoader("bookmarks", (state, x) => ({
        ...state,
        bookmarks: x,
    })),
    ApiRequest({
        url: `${state.root}/files/tracks.json`,
        options: {
            credentials: "omit",
        },
        state: state,
        progress: (state, { done, size }) => [
            {
                ...state,
                download_done: done,
                download_size: size,
            },
        ],
        action: (state, response) => [
            {
                ...state,
                track_list: response,
                download_done: 0,
                download_size: null,
            },
        ],
    }),
];

const subscriptions = (state: State): Array<Subscription | boolean> => [
    HashStateManager(
        {
            push: ["root", "filters", "track_id", "room_name"],
            replace: ["search", "booth", "room_name_edit"],
        },
        state,
    ),
    getMQTTListener(state),
    LocalStorageSaver("performer_name", state.performer_name),
    LocalStorageSaver("room_password", state.room_password),
    LocalStorageSaver("bookmarks", state.bookmarks),
    ResizeListener((state, event) => ({
        ...state,
        widescreen: isWidescreen(),
    })),
    BeLoggedIn(state.room_name, state.room_password),
    SyncedInterval({
        server: state.root + "/time.json",
        interval: 1000,
        sync: 5 * 60 * 1000,
        onInterval(state: State, timestamp_ms: number): Dispatchable {
            (window as any).state = state;
            return { ...state, now: timestamp_ms / 1000 };
        },
    }),
    state.casting && CastSender(state.room_name, state.room_password),
];

app({
    init: init,
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
