/// <reference path='./player.d.ts'/>
import {app, h} from "hyperapp";
import {Interval, Keyboard, WebSocketListen} from "hyperapp-fx";
import ReconnectingWebSocket from "reconnecting-websocket";

import {FetchRandomImages} from "./effects";
import {OnWsCommand, OnCountdown, OnKeyDown, OnWsOpen, OnWsClosed} from "./actions";
import {TitleScreen, VideoScreen, PodiumScreen, PreviewScreen, SettingsMenu} from "./screens";
import {http2ws} from "./utils";


const state: State = {
    // global persistent
    root: "https://karakara.org.uk",
    queue_id: new URLSearchParams(location.hash.slice(1)).get("queue_id") || "booth",
    is_podium: Boolean(new URLSearchParams(location.hash.slice(1)).get("podium")),

    // global temporary
    show_settings: false,
    connected: false,
    fullscreen: false,
    audio_allowed: window.AudioContext == undefined || (new AudioContext()).state === "running",
    settings: {
        "karakara.player.title"               : "KaraKara",
        "karakara.player.theme"               : "metalghosts",
        "karakara.player.video.preview_volume":  0.2,
        "karakara.player.video.skip.seconds"  : 20,
        "karakara.player.autoplay"            : 0, // Autoplay after X seconds
        "karakara.player.subs_on_screen"      : true, // Set false if using podium
        "karakara.event.end"                  : null,
        "karakara.podium.video_lag"           : 0.50,  // adjust to get podium and projector in sync
        "karakara.podium.soft_sub_lag"        : 0.35,  // adjust to get soft-subs and hard-subs in sync
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

    if(!state.audio_allowed && !state.is_podium)  // podium doesn't play sound
        screen = <section key="title" className={"screen_title"}><h1>Click to Activate</h1></section>;
    else if(state.queue.length === 0)
        screen = <TitleScreen state={state} />;
    else if(state.is_podium)
        screen = <PodiumScreen state={state} />;
    else if(state.queue.length > 0 && !state.playing)
        screen = <PreviewScreen state={state} />;
    else if(state.queue.length > 0 && state.playing)
        screen = <VideoScreen state={state} />;

    return <body
        onclick={(state) => ({...state, audio_allowed: true})}
        ondblclick={(state) => ({...state, show_settings: true})}
    >
        <main className={"theme-" + state.settings["karakara.player.theme"]}>
            {state.connected || <h1 id={"error"}>Not Connected To Server</h1>}
            {screen}
        </main>
        {state.show_settings && <SettingsMenu state={state} />}
    </body>;
}

function subscriptions(state: State) {
    return [
        Keyboard({
            downs: true,
            action: (_, event) => OnKeyDown(state, event),
        }),
        WebSocketListen({
            url: http2ws(state.root) + "/ws/",
            open: OnWsOpen,
            close: OnWsClosed,
            action: OnWsCommand,
            error: (state, error) => ({...state}),
            ws_constructor: ReconnectingWebSocket
        }),
        (
            state.audio_allowed &&
            !state.paused &&
            !state.playing &&
            state.settings["karakara.player.autoplay"] !== 0 &&
            Interval({
                every: 200,
                action: OnCountdown,
            })
        ),
    ];
}

app({
    init: [
        state,
        FetchRandomImages(state),
    ],
    view: view,
    subscriptions: subscriptions,
    node: document.body,
});
