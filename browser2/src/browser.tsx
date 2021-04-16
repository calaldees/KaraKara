/// <reference path='./browser.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import { LocalStorageLoader, LocalStorageSaver } from "@shish2k/hyperapp-localstorage";

import { Root } from "./screens/root";
import { getMQTTListener } from "./subs";

// If we're running stand-alone, then use the main karakara.org.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.org.uk"
        : window.location.protocol + "//" + window.location.host;

let state: State = {
    // bump this each time the schema changes to
    // invalidate anybody's saved state
    version: 1,

    // global
    root: auto_root,
    root_edit: auto_root,
    screen: "explore",
    notification: null,
    show_settings: false,
    download_size: null,
    download_done: 0,

    // login
    session_id: null,
    room_name: "",
    room_name_edit: "",
    room_password: "",
    room_password_edit: "",
    loading: false,

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
    settings: {},

    // priority_tokens
    priority_tokens: [],
};

app({
    init: [
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
    ],
    view: Root,
    subscriptions: (state) => [
        HashStateManager(
            {
                push: ["root", "filters", "track_id"],
                replace: ["room_name_edit", "search"],
            },
            state,
        ),
        state.room_name && state.track_list && getMQTTListener(state),
        LocalStorageSaver("performer_name", state.performer_name),
        LocalStorageSaver("room_password", state.room_password),
        LocalStorageSaver("bookmarks", state.bookmarks),
    ],
    node: document.body,
});
