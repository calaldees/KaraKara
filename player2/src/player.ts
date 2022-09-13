/// <reference path='./player.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import {
    LocalStorageLoader,
    LocalStorageSaver,
} from "@shish2k/hyperapp-localstorage";

import { Root } from "./screens/root";
import {
    getMQTTListener,
    IntervalListener,
    KeyboardListener,
    BeLoggedIn,
} from "./subs";
import { ApiRequest } from "./effects";

// If we're running stand-alone, then use the main karakara.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.uk"
        : window.location.protocol + "//" + window.location.host;

const state: State = {
    // global
    root: auto_root,
    root_edit: auto_root,
    room_name: "",
    room_name_edit: "",
    room_password: "",
    room_password_edit: "",
    podium: false,
    track_list: {},
    is_admin: false,
    show_settings: false,
    connected: false,
    fullscreen: false,
    audio_allowed:
        window.AudioContext == undefined ||
        new AudioContext().state === "running",
    settings: {
        "title": "KaraKara",
        "theme": "metalghosts",
        "preview_volume": 0.2,
        "track_space": 10,
        "event_end": null,
    },

    // loading screen
    download_size: null,
    download_done: 0,

    // playlist screen
    queue: [],

    // video screen
    playing: false,
    paused: false,
    progress: 0,
};

const init: Dispatchable = [
    state,
    LocalStorageLoader("room_password", (state, x) => ({
        ...state,
        room_password_edit: x,
        room_password: x,
    })),
    ApiRequest({
        url: `${state.root}/files/tracks.json`,
        state: state,
        progress: (state, { done, size }): State => (
            {
                ...state,
                download_done: done,
                download_size: size,
            }
        ),
        action: (state, response: Dictionary<Track>): State => (
            {
                ...state,
                track_list: response,
                download_done: 0,
                download_size: null,
            }
        ),
    }),
];

const subscriptions = (state: State): Array<Subscription> => [
    HashStateManager(
        {
            push: ["root", "room_name"],
            replace: ["podium", "room_name_edit"],
        },
        state,
    ),
    LocalStorageSaver("room_password", state.room_password),
    KeyboardListener,
    getMQTTListener(state),
    state.audio_allowed &&
    !state.paused &&
    !state.playing &&
    state.settings["track_space"] !== 0 &&
    IntervalListener,
    BeLoggedIn(state.room_name, state.room_password),
];

app({
    init: init,
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
