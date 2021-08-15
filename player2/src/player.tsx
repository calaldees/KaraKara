/// <reference path='./player.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";

import { Root } from "./screens/root";
import {
    getOpenMQTTListener,
    IntervalListener,
    KeyboardListener,
    FetchRandomImages,
} from "./subs";

// If we're running stand-alone, then use the main karakara.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.uk"
        : window.location.protocol + "//" + window.location.host;

const state: State = {
    // global persistent
    root: auto_root,
    root_edit: auto_root,
    room_name: "",
    room_name_edit: "",
    room_password: "",
    room_password_edit: "",
    podium: false,

    // global temporary
    show_settings: false,
    connected: false,
    fullscreen: false,
    audio_allowed:
        window.AudioContext == undefined ||
        new AudioContext().state === "running",
    settings: {
        "karakara.player.title": "KaraKara",
        "karakara.player.theme": "metalghosts",
        "karakara.player.video.preview_volume": 0.2,
        "karakara.player.video.skip.seconds": 20,
        "karakara.player.autoplay.seconds": 0, // Autoplay after X seconds
        "karakara.player.subs_on_screen": true, // Set false if using podium
        "karakara.event.end": null,
        "karakara.podium.video_lag": 0.5, // adjust to get podium and projector in sync
        "karakara.podium.soft_sub_lag": 0.35, // adjust to get soft-subs and hard-subs in sync
    },

    // title screen
    images: [],

    // playlist screen
    queue: [],

    // video screen
    playing: false,
    paused: false,
    progress: 0,
};

const subscriptions = (state: State) => [
    HashStateManager(
        {
            push: ["root", "room_name"],
            replace: ["podium", "room_name_edit"],
        },
        state,
    ),
    KeyboardListener,
    getOpenMQTTListener(state),
    state.audio_allowed &&
        !state.paused &&
        !state.playing &&
        state.settings["karakara.player.autoplay.seconds"] !== 0 &&
        IntervalListener,
    FetchRandomImages(state.room_name),
];

let dispatch = app({
    init: state,
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});

if (module && module.hot) {
    module.hot.dispose(function (data) {
        dispatch(function (state) {
            data.saved_state = state;
            return state;
        });
    });
    module.hot.accept(function (getParents) {
        dispatch(function (state) {
            return module.hot.data.saved_state;
        });
    });
}
