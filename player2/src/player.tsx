/// <reference path='./player.d.ts'/>
import { app, h } from "hyperapp";
import { AutoHistory } from "hyperapp-auto-history";

import { FetchRandomImages } from "./effects";
import {
    PodiumScreen,
    PreviewScreen,
    SettingsMenu,
    TitleScreen,
    VideoScreen,
} from "./screens";
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

function view(state: State) {
    let screen = <section>Unknown state :(</section>;

    if (!state.audio_allowed && !state.podium)
        // podium doesn't play sound
        screen = (
            <section key="title" className={"screen_title"}>
                <h1>Click to Activate</h1>
            </section>
        );
    else if (state.queue.length === 0) screen = <TitleScreen state={state} />;
    else if (state.podium) screen = <PodiumScreen state={state} />;
    else if (state.queue.length > 0 && !state.playing)
        screen = <PreviewScreen state={state} />;
    else if (state.queue.length > 0 && state.playing)
        screen = <VideoScreen state={state} />;

    return (
        <body
            onclick={state => ({ ...state, audio_allowed: true })}
            ondblclick={state => ({ ...state, show_settings: true })}
        >
            <main
                className={"theme-" + state.settings["karakara.player.theme"]}
            >
                {state.connected || (
                    <h1 id={"error"}>Not Connected To Server</h1>
                )}
                {screen}
            </main>
            {state.show_settings && <SettingsMenu state={state} />}
        </body>
    );
}

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
    view: view,
    subscriptions: subscriptions,
    node: document.body,
});
