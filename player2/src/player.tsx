/// <reference path='./player.d.ts'/>
import { app } from "hyperapp";
import { AutoHistory } from "hyperapp-auto-history";

import { Root } from "./screens/root";
import { FetchRandomImages } from "./effects";
import {
    getOpenMQTTListener,
    IntervalListener,
    KeyboardListener,
} from "./subs";

// If we're running stand-alone, then use the main karakara.org.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.org.uk"
        : window.location.protocol + "//" + window.location.host;

const state: State = {
    // global persistent
    root: auto_root,
    queue_id: "demo",
    queue_password: "",
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
        "karakara.player.autoplay": 0, // Autoplay after X seconds
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

const HistoryManager = AutoHistory({
    init: state,
    push: ["root", "queue_id"],
    replace: ["podium"],
});

function subscriptions(state: State) {
    HistoryManager.push_state_if_changed(state);
    return [
        HistoryManager,
        KeyboardListener,
        getOpenMQTTListener(state),
        state.audio_allowed &&
            !state.paused &&
            !state.playing &&
            state.settings["karakara.player.autoplay"] !== 0 &&
            IntervalListener,
    ];
}

app({
    init: [state, FetchRandomImages(state)],
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
