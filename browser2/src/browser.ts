/// <reference path='./browser.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import {
    LocalStorageLoader,
    LocalStorageSaver,
} from "@shish2k/hyperapp-localstorage";

import { Root } from "./screens/root";
import { BeLoggedIn, getMQTTListener, ResizeListener, RoundedInterval } from "./subs";
import { ApiRequest } from "./effects";

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
    priority_token: null,
    show_settings: false,
    download_size: null,
    download_done: 0,
    booth: false,
    widescreen: isWidescreen(),
    scroll_stack: [],
    now: Date.now()/1000,

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
        "track_space": 30.0,
        "forced_tags": [],
        "hidden_tags": ["red:duplicate"],
    },

    // priority_tokens
    priority_tokens: [],
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
            credentials: 'omit',
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

const subscriptions = (state: State): Array<Subscription> => [
    HashStateManager(
        {
            push: ["root", "filters", "track_id", "room_name"],
            replace: ["search", "booth", "widescreen", "room_name_edit"],
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
    RoundedInterval({
        every: 1000,
        action(state: State, timestamp: number): Dispatchable {
            if(state.screen == "room_settings") {
                // don't update time while on the settings screen, see #117
                return state;
            }
            (window as any).state = state;
            return { ...state, now: Date.now()/1000 };
        },
    }),
];

app({
    init: init,
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
