/// <reference path='./player.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import { SurviveHMR } from "@shish2k/hyperapp-survive-hmr";

import { Root } from "./screens/root";
import {
    getOpenMQTTListener,
    IntervalListener,
    KeyboardListener,
    FetchTrackList,
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
    track_list: {},

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
        "karakara.player.autoplay.seconds": 0,
        "karakara.event.end": null,
    },

    // loading screen
    download_size: null,
    download_done: 0,

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
    Object.keys(state.track_list).length > 0 && getOpenMQTTListener(state),
    state.audio_allowed &&
    !state.paused &&
    !state.playing &&
    state.settings["karakara.player.autoplay.seconds"] !== 0 &&
    IntervalListener,
    FetchTrackList(state.room_name),
];

app({
    init: [state, SurviveHMR(module, [])],
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
